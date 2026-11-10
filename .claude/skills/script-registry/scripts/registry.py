#!/usr/bin/env python3
"""Replication manifest builder and auditor (stdlib only, Python 3.9+).

build: scan script directories, write a registry JSON + readable md table.
build --merge: same scan, but curated fields (purpose, inputs, outputs,
files_referenced) of entries already in the registry are preserved; only
mechanical fields (loc, todos, packages) refresh. Use for every rebuild
after the first curation pass.
build --makefile: read inputs/outputs from the build graph's explicit rules
instead of guessing them. Make prerequisites are a dependency declaration
that also executes, so they beat the AST heuristic and survive every rebuild.
audit: check the registry against disk; exit nonzero on drift.
stamp: after a successful build, record sha256 of every script and declared
output. audit uses those hashes to decide staleness; without them it falls
back to mtime, which git resets on clone and which therefore cannot answer
"was this output built from this script?" in a fresh checkout.

Heuristics are honest but limited: only string-literal paths are detected;
paths built from config constants are invisible and must be curated by hand
(the SKILL.md makes curation a required step) or declared in a Makefile.
"""

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

# Path-like string literal: contains a slash or ends in a data extension.
PATH_RE = re.compile(
    r"^[\w./-]+\.(csv|json|jsonl|parquet|pkl|txt|md|tex|bib|png|pdf|dta|xlsx?)$"
)
# Write-side call markers on the same line as the literal.
WRITE_MARKERS = (".to_csv(", ".to_parquet(", ".to_pickle(", ".savefig(",
                 "json.dump", ".write(", ".to_latex(", ".to_excel(",
                 '"w"', "'w'", '"wb"', "'wb'", '"a"', "'a'")
READ_MARKERS = ("read_csv", "read_parquet", "read_pickle", "json.load",
                "read_excel", "read_stata", '"r"', "'r'", '"rb"', "'rb'")

# Minimal stdlib set for 3.9 compatibility (sys.stdlib_module_names is 3.10+).
STDLIB = set(getattr(sys, "stdlib_module_names", (
    "argparse ast collections csv dataclasses datetime functools glob io "
    "itertools json logging math os pathlib pickle random re shutil sqlite3 "
    "statistics string subprocess sys tempfile time typing unittest urllib "
    "warnings zoneinfo hashlib gzip zipfile textwrap enum abc copy signal"
).split()))


def scan_script(path: Path) -> dict:
    src = path.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()
    entry = {
        "script": str(path),
        "purpose": "(no docstring)",
        "inputs": [],
        "outputs": [],
        "files_referenced": [],
        "packages": [],
        "loc": sum(1 for l in lines if l.strip()),
        "todos": sum(1 for l in lines if "TODO" in l or "FIXME" in l),
    }
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        entry["purpose"] = f"(unparseable: {exc.msg})"
        return entry

    doc = ast.get_docstring(tree)
    if doc:
        entry["purpose"] = doc.strip().splitlines()[0]

    pkgs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            pkgs.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            pkgs.add(node.module.split(".")[0])
    entry["packages"] = sorted(p for p in pkgs if p not in STDLIB)

    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value.strip()
            if not PATH_RE.match(s) or s in seen:
                continue
            seen.add(s)
            line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            if any(m in line for m in WRITE_MARKERS):
                entry["outputs"].append(s)
            elif any(m in line for m in READ_MARKERS):
                entry["inputs"].append(s)
            else:
                entry["files_referenced"].append(s)
    return entry


VAR_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:+?]?=\s*(.*)$")
RULE_RE = re.compile(r"^([^\t#][^:=]*?):(?!=)\s*(.*)$")
NOT_A_TARGET = {".PHONY", ".DELETE_ON_ERROR", ".SECONDARY", ".SECONDEXPANSION",
                ".PRECIOUS", ".SUFFIXES", ".DEFAULT_GOAL", ".NOTPARALLEL"}


def _join_continuations(text):
    return re.sub(r"\\\n\s*", " ", text)


def _expand(value, variables, depth=0):
    if depth > 10 or "$" not in value:
        return value
    def sub(m):
        return variables.get(m.group(1) or m.group(2), "")
    expanded = re.sub(r"\$\(([A-Za-z_][A-Za-z0-9_]*)\)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
                      sub, value)
    return _expand(expanded, variables, depth + 1) if expanded != value else expanded


def parse_makefile(path: Path):
    """Map script path -> {inputs, outputs} from explicit Make rules.

    The Makefile's prerequisites are a dependency declaration that also
    executes, so they are better evidence than the AST path heuristic. Only
    explicit rules are read: pattern rules, phony targets, and anything whose
    recipe names no registered-looking script are skipped.
    """
    lines = _join_continuations(path.read_text(encoding="utf-8")).splitlines()
    variables, rules, current = {}, [], None
    for raw in lines:
        if raw.startswith("\t"):
            if current is not None:
                current["recipe"].append(raw.strip())
            continue
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        rule = RULE_RE.match(line)
        if rule:
            current = {"targets": rule.group(1), "prereqs": rule.group(2), "recipe": []}
            rules.append(current)
            continue
        var = VAR_RE.match(line)
        if var:
            current = None
            variables[var.group(1)] = var.group(2).split("#", 1)[0].strip()

    for name, value in list(variables.items()):
        variables[name] = _expand(value, variables)

    declared = {}
    for rule in rules:
        targets = _expand(rule["targets"], variables).split()
        prereqs = _expand(rule["prereqs"], variables).split("|")[0].split()
        recipe = " ".join(_expand(r, variables) for r in rule["recipe"])
        if not targets or any(t in NOT_A_TARGET or "%" in t for t in targets):
            continue
        scripts = [p for p in prereqs if p.endswith(".py")]
        if not scripts:
            scripts = [t for t in recipe.split() if t.endswith(".py")]
        if len(scripts) != 1:
            continue  # ambiguous ownership; leave it to hand curation
        script = str(Path(scripts[0]))
        entry = declared.setdefault(script, {"inputs": [], "outputs": []})
        for out in targets:
            if str(Path(out)) not in entry["outputs"]:
                entry["outputs"].append(str(Path(out)))
        for src in prereqs:
            src = str(Path(src))
            if src != script and src not in entry["inputs"]:
                entry["inputs"].append(src)
    return declared


def apply_makefile(entries, declared):
    n = 0
    for e in entries:
        d = declared.get(str(Path(e["script"])))
        if not d:
            continue
        e["inputs"], e["outputs"] = list(d["inputs"]), list(d["outputs"])
        e["declared_by"] = "makefile"
        n += 1
    unmatched = sorted(set(declared) - {str(Path(e["script"])) for e in entries})
    if unmatched:
        print("warn: Makefile names scripts outside --dirs: " + ", ".join(unmatched))
    print(f"makefile: {n} entries took inputs/outputs from the build graph")
    return entries


def find_scripts(dirs):
    for d in dirs:
        root = Path(d)
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.py")):
            if "__pycache__" not in p.parts:
                yield p


def merge_entries(fresh, existing):
    """Preserve hand-curated fields of existing entries; refresh mechanical ones.

    Curated fields (purpose, inputs, outputs, files_referenced) survive the
    rebuild; loc/todos/packages always come from the fresh scan. Existing
    entries whose script vanished from disk are kept so audit surfaces the
    retirement decision instead of build silently dropping it.

    Exception: an entry the Makefile declares takes its inputs and outputs
    from the build graph on every rebuild. The graph is the curation, and a
    stale hand-edit that disagrees with it would describe a build that does
    not happen.
    """
    by_script = {e["script"]: e for e in existing}
    merged, preserved, added = [], 0, 0
    for f in fresh:
        old = by_script.pop(f["script"], None)
        if old is None:
            added += 1
            merged.append(f)
            continue
        preserved += 1
        e = dict(old)
        for k in ("loc", "todos", "packages"):
            e[k] = f[k]
        if f.get("declared_by") == "makefile":
            e["inputs"], e["outputs"] = f["inputs"], f["outputs"]
            e["declared_by"] = "makefile"
        elif old.get("declared_by") == "makefile":
            # Was in the graph, is no longer: fall back to curation and say so.
            e.pop("declared_by", None)
            print(f"warn: {f['script']} left the Makefile graph; its inputs and "
                  f"outputs are hand-curated again")
        if e.get("purpose") == "(no docstring)":
            e["purpose"] = f["purpose"]
        merged.append(e)
    kept_orphans = list(by_script.values())
    merged.extend(kept_orphans)
    print(f"merge: {preserved} curated entries preserved, {added} new, "
          f"{len(kept_orphans)} kept without a file on disk (audit will flag)")
    return merged


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def code_sha(path: Path):
    """Hash what the script *does*, not how it reads.

    Hashing raw bytes makes a comment or reformat look like a reason to
    rerun an estimation, and a staleness alarm that fires on inert edits
    gets ignored. The parsed tree ignores comments and whitespace. Falls
    back to the byte hash for anything unparseable or non-Python.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, ValueError):
        return sha256(path)
    return hashlib.sha256(ast.dump(tree).encode("utf-8")).hexdigest()


def stamp(args) -> int:
    """Record content hashes of scripts and their outputs after a good build.

    mtime cannot answer "was this output built from this script?" after a
    fresh clone: git stamps every file with the checkout time, so the
    comparison audit relies on is arbitrary. Hashes travel in the registry,
    which is committed, so the question stays answerable anywhere.
    """
    reg_path = Path(args.registry)
    if not reg_path.is_file():
        print(f"FAIL: registry not found: {reg_path}")
        return 1
    entries = json.loads(reg_path.read_text(encoding="utf-8"))
    stamped, skipped = 0, []
    for e in entries:
        script = Path(e["script"])
        if not script.is_file():
            continue
        outs = {}
        missing = [o for o in e.get("outputs", []) if not Path(o).is_file()]
        if missing:
            skipped.append(f"{e['script']} (outputs not built: {', '.join(missing)})")
            continue
        for o in e.get("outputs", []):
            outs[o] = sha256(Path(o))
        e["script_sha"] = code_sha(script)
        e["output_shas"] = outs
        stamped += 1
    reg_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"stamp: {stamped} entries hashed -> {reg_path}")
    for s in skipped:
        print("warn: not stamped:", s)
    return 0


def build(args) -> int:
    entries = [scan_script(p) for p in find_scripts(args.dirs)]
    if args.makefile:
        mk = Path(args.makefile)
        if not mk.is_file():
            print(f"FAIL: Makefile not found: {mk}")
            return 1
        entries = apply_makefile(entries, parse_makefile(mk))
    out = Path(args.out)
    if args.merge and out.is_file():
        existing = json.loads(out.read_text(encoding="utf-8"))
        entries = merge_entries(entries, existing)
    elif args.merge:
        print(f"merge: no existing registry at {out}, building fresh")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

    md = out.with_suffix(".md")
    rows = ["| Script | Purpose | Inputs | Outputs | Packages | LOC |",
            "|---|---|---|---|---|---|"]
    for e in entries:
        rows.append("| {script} | {purpose} | {i} | {o} | {p} | {loc} |".format(
            script=e["script"], purpose=e["purpose"].replace("|", "/"),
            i=", ".join(e["inputs"]) or "-", o=", ".join(e["outputs"]) or "-",
            p=", ".join(e["packages"]) or "-", loc=e["loc"]))
    md.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"registry: {len(entries)} scripts -> {out} (+ {md.name})")
    missing_doc = [e["script"] for e in entries if e["purpose"] == "(no docstring)"]
    if missing_doc:
        print("warn: no docstring: " + ", ".join(missing_doc))
    return 0


def audit(args) -> int:
    reg_path = Path(args.registry)
    if not reg_path.is_file():
        print(f"FAIL: registry not found: {reg_path}")
        return 1
    entries = json.loads(reg_path.read_text(encoding="utf-8"))
    by_script = {e["script"]: e for e in entries}
    on_disk = {str(p) for p in find_scripts(args.dirs)}

    failures, warnings = [], []

    for s in sorted(on_disk - set(by_script)):
        failures.append(f"unregistered script: {s}")
    for s in sorted(set(by_script) - on_disk):
        failures.append(f"registry entry with no file on disk: {s}")

    unstamped = []
    for e in entries:
        script = Path(e["script"])
        if not script.is_file():
            continue
        recorded = e.get("script_sha")
        if recorded:
            script_changed = code_sha(script) != recorded
            shas = e.get("output_shas", {})
            for out in e.get("outputs", []):
                op = Path(out)
                if not op.is_file():
                    failures.append(f"declared output missing: {out} "
                                    f"(from {e['script']})")
                    continue
                if out not in shas:
                    warnings.append(f"output added since the last stamp: {out}; "
                                    f"rebuild and re-stamp")
                    continue
                out_changed = sha256(op) != shas[out]
                if script_changed and not out_changed:
                    failures.append(f"stale output: {out} was produced by an older "
                                    f"{e['script']}; rerun it")
                elif out_changed and not script_changed:
                    warnings.append(f"{out} changed with no change to "
                                    f"{e['script']}: an input moved, or the "
                                    f"generated file was edited by hand. Verify, "
                                    f"then re-stamp.")
                elif out_changed and script_changed:
                    warnings.append(f"{out} and {e['script']} both changed; "
                                    f"re-stamp to record the new pair")
        else:
            unstamped.append(e["script"])
            smtime = script.stat().st_mtime
            for out in e.get("outputs", []):
                op = Path(out)
                if not op.is_file():
                    failures.append(f"declared output missing: {out} "
                                    f"(from {e['script']})")
                elif op.stat().st_mtime < smtime:
                    failures.append(f"stale output: {out} older than {e['script']}")

        # Per entry, not per audit. These two once sat inside the `if unstamped:`
        # block below, where they read the loop variable after
        # the loop had ended: they reported at most one script, always the last,
        # and only when some entry happened to be unstamped. Found by the
        # planted-failure fixture `registry_no_docstring`.
        if e.get("purpose") == "(no docstring)":
            warnings.append(f"no docstring: {e['script']}")
        if e.get("todos"):
            warnings.append(f"{e['todos']} TODO/FIXME in {e['script']}")

    if unstamped:
        warnings.append(f"{len(unstamped)} entries have no content hashes, so "
                        f"staleness falls back to mtime, which git resets on "
                        f"clone. Run `stamp` after a good build.")

    for w in warnings:
        print("warn:", w)
    for f in failures:
        print("FAIL:", f)

    if not failures:
        print(f"audit OK: {len(entries)} entries, {len(warnings)} warnings")
        print("\n## Replication README section\n")
        for e in entries:
            print(f"- `{e['script']}`: {e['purpose']}")
            if e.get("inputs"):
                print(f"  - reads: {', '.join(e['inputs'])}")
            if e.get("outputs"):
                print(f"  - writes: {', '.join(e['outputs'])}")
            if e.get("packages"):
                print(f"  - requires: {', '.join(e['packages'])}")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--dirs", nargs="+", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--merge", action="store_true",
                   help="preserve curated fields of entries already in --out")
    b.add_argument("--makefile",
                   help="take inputs/outputs from this Makefile's explicit rules")
    a = sub.add_parser("audit")
    a.add_argument("--registry", required=True)
    a.add_argument("--dirs", nargs="+", required=True)

    s = sub.add_parser("stamp",
                       help="record content hashes of scripts and outputs "
                            "after a successful build")
    s.add_argument("--registry", required=True)

    args = ap.parse_args()
    return {"build": build, "audit": audit, "stamp": stamp}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
