#!/usr/bin/env python3
"""Claim-ledger macro emitter and manuscript checker (stdlib, Python 3.9+).

emit:   read every ledger claim carrying a `macro` field, pull its value from
        the results file it names, and write a LaTeX macro file. The value
        printed in the paper is then generated, not typed, so a number cannot
        drift out of sync with its source. Reports every macro that moved
        since the last accepted baseline; never writes the baseline itself,
        so a build cannot quietly accept a result it just changed.
accept: record the current values as the accepted baseline. The one command
        that writes the lock, run by a person who has read the diff.
check:  the manuscript actually uses each macro, no macro-backed value is
        also typed as a literal somewhere in the prose, and no macro claim
        keeps a second copy of its value in `reported_value`.

Exit 0 only when every check passes.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_ledger import resolve_key  # noqa: E402

MACRO_RE = re.compile(r"^[A-Za-z]+$")
# A literal short enough to collide with section numbers, years in citations,
# or ordinary counts is not worth scanning for.
MIN_LITERAL_LEN = 3
HEADER = ("% GENERATED FILE - do not edit.\n"
          "% Written by claim_macros.py from the claim ledger.\n"
          "% Edit the results file or the producing script, then re-run emit.\n"
          "% Requires \\usepackage{siunitx} in the preamble.\n")


def load_ledger(path: Path):
    if not path.is_file():
        print(f"FAIL: ledger not found: {path}")
        return None
    claims = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(claims, list) or not claims:
        print("FAIL: ledger is not a non-empty JSON list")
        return None
    return claims


def macro_claims(claims):
    return [c for c in claims if str(c.get("macro", "")).strip()]


def infer_precision(claim):
    """Decimals to round to: explicit, else inferred from reported_value, else 3."""
    if claim.get("precision") is not None:
        return int(claim["precision"])
    rep = claim.get("reported_value")
    if rep is not None and "." in str(rep):
        return len(str(rep).split(".")[1])
    return 3


def render(value, precision, unit):
    """Format a number as a siunitx call at fixed precision."""
    text = f"{value:.{precision}f}"
    if precision == 0:
        text = str(int(round(value)))
    return f"\\qty{{{text}}}{{{unit}}}" if unit else f"\\num{{{text}}}"


def numeric_text(value, precision):
    if precision == 0:
        return str(int(round(value)))
    return f"{value:.{precision}f}"


def resolve_macro_values(claims, errors):
    """Return {macro: record} pulled from the results files the ledger names."""
    out = {}
    for claim in claims:
        cid = claim.get("id", "?")
        name = str(claim["macro"]).strip()
        if not MACRO_RE.match(name):
            errors.append(f"[{cid}] macro name must be letters only: {name!r}")
            continue
        if name in out:
            errors.append(f"[{cid}] duplicate macro name: {name}")
            continue
        rf_raw = claim.get("results_file")
        if not rf_raw or not claim.get("results_key"):
            errors.append(f"[{cid}] macro claim needs results_file and results_key")
            continue
        rf = Path(rf_raw)
        if not rf.is_file():
            errors.append(f"[{cid}] results file missing: {rf}")
            continue
        try:
            data = json.loads(rf.read_text(encoding="utf-8"))
            value = resolve_key(data, claim["results_key"])
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"[{cid}] results file unreadable: {rf} ({exc})")
            continue
        except (KeyError, IndexError, ValueError):
            errors.append(f"[{cid}] key does not resolve: {claim['results_key']} in {rf}")
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"[{cid}] key resolves to non-numeric "
                          f"{type(value).__name__}: {claim['results_key']}")
            continue
        unit = str(claim.get("unit", "")).strip()
        if unit and "\\" not in unit:
            print(f"warn: [{cid}] unit {unit!r} has no backslash; siunitx units are "
                  f"macros (\\percent, \\million), and a bare word will not compile")
        scale = float(claim.get("scale", 1))
        precision = infer_precision(claim)
        scaled = float(value) * scale
        out[name] = {
            "id": cid,
            "value": round(scaled, precision),
            "text": numeric_text(scaled, precision),
            "rendered": render(scaled, precision, unit),
            "results_file": str(rf),
            "results_key": claim["results_key"],
        }
    return out


def diff_lock(new, old):
    """Report macros added, removed, or moved since the last emit."""
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(n for n in set(new) & set(old)
                     if new[n]["text"] != old[n].get("text"))
    for n in added:
        print(f"new:     \\{n} = {new[n]['text']}")
    for n in removed:
        print(f"dropped: \\{n} (was {old[n].get('text')})")
    for n in changed:
        print(f"moved:   \\{n}: {old[n].get('text')} -> {new[n]['text']} "
              f"[{new[n]['results_key']}]")
    return added, removed, changed


def lock_path_for(args):
    """Where the accepted baseline lives.

    Beside the ledger, never beside --out: the macro file is generated and
    lives in a build directory that `make clean` wipes, but the baseline is
    an accepted decision. It is source, and it belongs in version control.
    """
    if args.lock:
        return Path(args.lock)
    return Path(args.ledger).parent / (Path(args.out).stem + ".lock.json")


def read_lock(path):
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("macros", {})


def resolve_or_fail(args):
    """Shared front half of emit and accept: ledger -> {macro: record}."""
    claims = load_ledger(Path(args.ledger))
    if claims is None:
        return None
    selected = macro_claims(claims)
    if not selected:
        return {}
    errors = []
    macros = resolve_macro_values(selected, errors)
    for e in errors:
        print("FAIL:", e)
    if errors:
        print(f"{len(errors)} macro claims unresolved")
        return None
    return macros


def emit(args) -> int:
    macros = resolve_or_fail(args)
    if macros is None:
        return 1
    if not macros:
        print("emit: no claims carry a `macro` field; nothing to generate")
        return 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [HEADER]
    for name in sorted(macros):
        lines.append(f"\\newcommand{{\\{name}}}{{{macros[name]['rendered']}}}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"emit: {len(macros)} macros -> {out}")

    # emit never writes the lock. A build step that accepted the numbers it
    # just changed would make the gate below unfalsifiable.
    lock = lock_path_for(args)
    old = read_lock(lock)
    if old is None:
        print(f"lock: no accepted baseline at {lock}")
        if args.fail_on_change:
            print("FAIL: nothing has been accepted yet; run `accept` once you "
                  "have read the values.")
            return 1
        return 0
    added, removed, changed = diff_lock(macros, old)
    if not (added or removed or changed):
        print("lock: no macro moved since the accepted baseline")
        return 0
    print(f"lock: {len(added)} new, {len(removed)} dropped, {len(changed)} moved; "
          f"{lock} unchanged")
    if args.fail_on_change:
        print("FAIL: the paper's numbers moved. Read the diff above; run "
              "`accept` to make it the new baseline.")
        return 1
    return 0


def accept(args) -> int:
    macros = resolve_or_fail(args)
    if macros is None:
        return 1
    if not macros:
        print("accept: no claims carry a `macro` field; nothing to accept")
        return 0
    lock = lock_path_for(args)
    old = read_lock(lock)
    if old is None:
        print(f"accept: baseline for {len(macros)} macros -> {lock}")
    else:
        diff_lock(macros, old)
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({"macros": macros}, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    print(f"accept: {lock} updated")
    return 0


def scan_literals(macros, tex_files, exclude):
    """Find macro-backed values typed as literals in manuscript source."""
    hits = []
    excluded = {Path(p).resolve() for p in exclude}
    targets = {n: m for n, m in macros.items()
               if len(m["text"].lstrip("-")) >= MIN_LITERAL_LEN}
    for tf in tex_files:
        path = Path(tf)
        if not path.is_file() or path.resolve() in excluded:
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            for name, m in targets.items():
                pat = r"(?<![\d.])" + re.escape(m["text"]) + r"(?![\d])"
                if re.search(pat, line):
                    hits.append((str(path), lineno, name, m["text"]))
    return hits


def check(args) -> int:
    claims = load_ledger(Path(args.ledger))
    if claims is None:
        return 1
    selected = macro_claims(claims)
    if not selected:
        print("check: no claims carry a `macro` field; nothing to check")
        return 0

    failures = []
    macros = resolve_macro_values(selected, failures)

    for claim in selected:
        if claim.get("reported_value") is not None:
            failures.append(
                f"[{claim.get('id', '?')}] macro claim also carries "
                f"reported_value={claim['reported_value']}; a macro-backed number "
                f"has one source. Set reported_value to null; the lock file "
                f"records what the paper printed.")

    body = [t for t in args.tex if Path(t).is_file()]
    missing_files = [t for t in args.tex if not Path(t).is_file()]
    for t in missing_files:
        failures.append(f"manuscript file not found: {t}")
    corpus = {t: Path(t).read_text(encoding="utf-8", errors="replace") for t in body}

    for name in sorted(macros):
        pat = re.compile(r"\\" + name + r"(?![A-Za-z])")
        if not any(pat.search(text) for text in corpus.values()):
            failures.append(f"\\{name} is defined but never used in the manuscript "
                            f"(claim {macros[name]['id']} left the paper?)")

    exclude = list(args.generated)
    if args.values:
        exclude.append(args.values)
    for path, lineno, name, text in scan_literals(macros, body, exclude):
        failures.append(f"{path}:{lineno}: literal {text} duplicates \\{name}; "
                        f"use the macro")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"check: {len(failures)} problems")
        return 1
    print(f"check OK: {len(macros)} macros, all used, no duplicated literals")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("emit", help="generate the LaTeX macro file from the ledger")
    e.add_argument("ledger")
    e.add_argument("--out", required=True, help="e.g. build/values.tex")
    e.add_argument("--lock", help="default: <out>.lock.json")
    e.add_argument("--fail-on-change", action="store_true",
                   help="exit nonzero if any macro moved from the accepted baseline")

    a = sub.add_parser("accept", help="record the current values as the baseline")
    a.add_argument("ledger")
    a.add_argument("--out", required=True, help="the same --out emit writes")
    a.add_argument("--lock", help="default: <out>.lock.json")

    c = sub.add_parser("check", help="check the manuscript against the macros")
    c.add_argument("ledger")
    c.add_argument("--tex", nargs="+", required=True, help="manuscript source files")
    c.add_argument("--generated", nargs="*", default=[],
                   help="generated files exempt from the literal scan (tables)")
    c.add_argument("--values", help="the emitted macro file, exempt from the scan")

    args = ap.parse_args()
    return {"emit": emit, "accept": accept, "check": check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
