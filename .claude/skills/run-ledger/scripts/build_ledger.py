#!/usr/bin/env python3
"""Build the submission run ledger and reproduction document (stdlib only).

Answers the three questions the rest of the submission package does not: how long
the work took, what it consumed, and how someone else reproduces the numbers.

It aggregates and computes. It authors no fact: every number traces to the
session queue, a transcript, the script registry, or the filesystem.

Token accounting reuses `run_cost.py` rather than reimplementing it, because the
deduplication rule there is load-bearing -- a naive sum over usage records
overstates by roughly 3x, and that is the single trap in the measurement.

Usage:
    python3 build_ledger.py --project DIR [--final] [--tools-dir DIR]
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

GAP_CAP_S = 600          # a turn gap longer than this is idle, not work
REQUIRED = [
    ("Initial prompt",        "submission/initial_prompt.md"),
    ("Conversations",         "submission/conversations"),
    ("Human time log",        "submission/human_time_log.md"),
    ("Contribution report",   "submission/contribution_report.md"),
    ("Model configuration",   "submission/model_config.md"),
    ("Data access",           "submission/data_access.md"),
    ("Workflow narrative",    "submission/workflow.md"),
    ("Human gate log",        "submission/human_gate_log.md"),
    ("Run ledger",            "submission/run_ledger.md"),
    ("Reproduction",          "submission/reproduction.md"),
]
PLACEHOLDER = "Paste the exact text of the initial prompt here"
NOT_AN_INVOICE = (
    "List-rate cost-equivalent, **not an invoice**: Claude Code plans bill "
    "against usage limits, so this figure compares layers against each other "
    "and is not spend."
)


def load_run_cost(tools_dir: Path):
    """Import run_cost.py so its dedup and pricing logic is reused, not copied."""
    p = tools_dir / "run_cost.py"
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location("run_cost", p)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def read_config(root: Path) -> dict:
    cfg, p = {}, root / "pipeline-config.md"
    if not p.is_file():
        return cfg
    inside = False
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("```"):
            inside = not inside
            continue
        if not inside or line.strip().startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        if k.strip() and not k.startswith(" "):
            cfg[k.strip()] = v.strip()
    return cfg


def queue_rows(root: Path) -> list:
    p = root / "submission" / ".session_queue.jsonl"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def active_minutes(transcript: Path) -> int | None:
    """Gap-capped active time. Wall clock across an overnight session is not a
    measure of effort, and reporting it as one inflates the human contribution."""
    if not transcript or not transcript.is_file():
        return None
    stamps = []
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', line)
        if m:
            try:
                stamps.append(dt.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")))
            except ValueError:
                pass
    if len(stamps) < 2:
        return None
    stamps.sort()
    total = 0.0
    for a, b in zip(stamps, stamps[1:]):
        total += min((b - a).total_seconds(), GAP_CAP_S)
    return int(round(total / 60))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def registry_outputs(root: Path, cfg: dict) -> dict:
    """Map declared output path -> producing script, from the registry."""
    rel = cfg.get("registry_file", "output/script_registry.json")
    p = root / rel
    if not p.is_file():
        return {}
    try:
        reg = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except ValueError:
        return {}
    entries = reg.get("scripts") or reg.get("entries") or reg
    out = {}
    if isinstance(entries, dict):
        entries = [dict(v, path=k) for k, v in entries.items()]
    for e in entries if isinstance(entries, list) else []:
        script = e.get("path") or e.get("script") or "?"
        for o in e.get("outputs", []) or []:
            out[str(o).lstrip("./")] = script
    return out


# Config keys naming the pipeline's own bookkeeping. These are metadata about
# the build, not outputs of it, so demanding a producing script for them would
# make the unattributed count noise. Read from config rather than hardcoded, so
# a project that relocates them is still handled.
BOOKKEEPING_KEYS = ("registry_file", "claim_ledger", "values_lock", "run_log",
                    "idea_pool", "peek_log", "data_profile", "search_log")


def bookkeeping(cfg: dict) -> set:
    return {str(cfg[k]).lstrip("./") for k in BOOKKEEPING_KEYS if cfg.get(k)}


def data_files(root: Path, produced: dict, skip: set) -> list:
    rows, seen = [], set()
    for d in ("data", "output"):
        base = root / d
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            # Prose in output/ is documentation, not data. A run log or a memo
            # has no producing script and demanding one would make the
            # unattributed count meaningless noise.
            if f.suffix.lower() in {".md", ".txt", ".log"}:
                continue
            rel = str(f.relative_to(root))
            if rel in seen or rel in skip:
                continue
            seen.add(rel)
            rows.append({
                "path": rel,
                "bytes": f.stat().st_size,
                "sha256": sha256(f)[:16],
                "produced_by": produced.get(rel, "UNATTRIBUTED"),
            })
    return rows


def status_of(root: Path, rel: str) -> str:
    p = root / rel
    if not p.exists():
        return "missing"
    if p.is_dir():
        return "present" if any(p.iterdir()) else "missing"
    if p.name == "initial_prompt.md" and PLACEHOLDER in p.read_text(
            encoding="utf-8", errors="replace"):
        return "missing"          # placeholder standing = not yet populated
    return "present"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--tools-dir")
    ap.add_argument("--final", action="store_true",
                    help="gate mode: exit nonzero if the package is incomplete")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"FAIL: no project at {root}")
        return 1
    cfg = read_config(root)
    tools = Path(args.tools_dir) if args.tools_dir else (root / cfg.get("tools_dir", "../tools"))
    rc = load_run_cost(tools.resolve())

    rows = queue_rows(root)
    conv_dir = root / "submission" / "conversations"
    on_disk = {p.name for p in conv_dir.glob("*.md")} if conv_dir.is_dir() else set()
    on_disk.discard("README.md")
    referenced = {Path(r["conv_file"]).name for r in rows if r.get("conv_file")}

    orphan_transcripts = sorted(on_disk - referenced)
    sessions_no_transcript = [r["session_id"][:8] for r in rows if not r.get("conv_file")]
    unfinalized = sum(1 for r in rows if not r.get("finalized"))

    # --- tokens, reusing run_cost's dedup ---
    tok = collections.Counter()
    cost = 0.0
    if rc is not None:
        proj_glob = os.path.expanduser("~/.claude/projects/*/")
        slug = "-".join(str(root).strip("/").split("/"))
        for d in sorted(Path(os.path.expanduser("~/.claude/projects")).glob("*")):
            if slug.lower().endswith(d.name.lower().lstrip("-")) or d.name.lower().endswith(slug.lower()):
                for j in sorted(d.glob("*.jsonl")):
                    try:
                        counts, c, _, _ = rc.read_usage(str(j))
                    except Exception:
                        continue
                    for k in ("input", "output", "cache_write", "cache_read"):
                        tok[k] += counts[k]
                    cost += c

    wall = sum(int(r.get("wallclock_min") or 0) for r in rows)
    active = 0
    for r in rows:
        cf = r.get("conv_file")
        a = active_minutes(root / cf) if cf else None
        active += a if a is not None else 0

    produced = registry_outputs(root, cfg)
    files = data_files(root, produced, bookkeeping(cfg))

    # This script writes run_ledger.md and reproduction.md, so by the time the
    # table is read they exist. Evaluating them before the write would print a
    # falsehood inside the very file whose absence it reports.
    SELF = {"submission/run_ledger.md", "submission/reproduction.md"}
    ready = [(label, rel, "present" if rel in SELF else status_of(root, rel))
             for label, rel in REQUIRED]

    # ---------------- render ----------------
    L = ["# Run ledger", "",
         "Runtime, consumption and reconciliation for the submission record.",
         "Generated by `run-ledger`. Every number traces to the session queue, a",
         "transcript, the script registry, or the filesystem; none is authored here.",
         "", "## Sessions", "",
         "| Date | Session | Wall clock (min) | Active, gap-capped (min) | git head | Transcript |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        cf = r.get("conv_file") or ""
        a = active_minutes(root / cf) if cf else None
        L.append("| %s | `%s` | %s | %s | `%s` | %s |" % (
            r.get("date", "?"), (r.get("session_id") or "?")[:8],
            r.get("wallclock_min", "?"), a if a is not None else "—",
            (r.get("git_head") or "none")[:8], Path(cf).name if cf else "**none**"))
    if not rows:
        L.append("| — | — | — | — | — | *no sessions recorded yet* |")

    L += ["", "## Totals", "",
          "| Measure | Value |", "|---|---|",
          "| Sessions | %d |" % len(rows),
          "| Wall clock | %d min (%.1f h) |" % (wall, wall / 60.0),
          "| Active, gap-capped | %d min (%.1f h) |" % (active, active / 60.0),
          "| Tokens in | {:,} |".format(tok["input"]),
          "| Tokens out | {:,} |".format(tok["output"]),
          "| Cache write | {:,} |".format(tok["cache_write"]),
          "| Cache read | {:,} |".format(tok["cache_read"]),
          "| Cost-equivalent | $%.2f |" % cost, "",
          NOT_AN_INVOICE, "",
          "Wall clock and active time are both reported because they answer",
          "different questions. Wall clock across an overnight session is not a",
          "measure of effort, and a record giving only wall clock inflates the",
          "human contribution.", "",
          "## Reconciliation", "",
          "| Check | Count |", "|---|---|",
          "| Queue rows not finalized | %d |" % unfinalized,
          "| Sessions with no transcript | %d |" % len(sessions_no_transcript),
          "| Transcripts in no queue row | %d |" % len(orphan_transcripts)]
    if sessions_no_transcript:
        L += ["", "Sessions with no transcript: " +
              ", ".join("`%s`" % s for s in sessions_no_transcript)]
    if orphan_transcripts:
        L += ["", "Orphaned transcripts: " +
              ", ".join("`%s`" % s for s in orphan_transcripts)]

    L += ["", "## Readiness", "",
          "| Required item | Artifact | Status |", "|---|---|---|"]
    for label, rel, st in ready:
        L.append("| %s | `%s` | %s |" % (label, rel, st))

    (root / "submission").mkdir(parents=True, exist_ok=True)
    (root / "submission" / "run_ledger.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    R = ["# Reproduction", "",
         "How to rebuild every number in the paper, and what that does and does",
         "not cover.", "",
         "## What `make verify` covers, and what it does not", "",
         "`make verify` is `distclean all check`: from source alone, everything",
         "rebuilds and every integrity gate still passes.", "",
         "**Data collection sits outside the build graph by design.** So",
         "`make verify` reproduces estimation through the PDF and **not** the",
         "crawls. The collection scripts are registered and re-runnable, and are",
         "listed separately below. A reader should not infer that running",
         "`make verify` re-downloads anything.", "",
         "## Data files", "",
         "| Path | Bytes | sha256 (16) | Produced by |", "|---|---|---|---|"]
    for f in files:
        R.append("| `%s` | %d | `%s` | %s |" % (
            f["path"], f["bytes"], f["sha256"],
            "`%s`" % f["produced_by"] if f["produced_by"] != "UNATTRIBUTED"
            else "**UNATTRIBUTED**"))
    if not files:
        R.append("| — | — | — | *no data files yet* |")
    unattributed = [f for f in files if f["produced_by"] == "UNATTRIBUTED"]
    if unattributed:
        R += ["", "**%d file(s) have no registered producing script.** A file no"
              % len(unattributed),
              "script claims cannot be reproduced from source and cannot be",
              "audited; register the script or remove the file."]

    R += ["", "## Environment", "",
          "| Field | Value |", "|---|---|",
          "| Python | `%s` |" % cfg.get("python", "(unset)"),
          "| Seed | `%s` |" % cfg.get("seed", "(unset)"),
          "| Makefile | `%s` |" % cfg.get("makefile", "(unset)"),
          "| Registry | `%s` |" % cfg.get("registry_file", "(unset)")]
    (root / "submission" / "reproduction.md").write_text("\n".join(R) + "\n", encoding="utf-8")

    # ---------------- report / gate ----------------
    missing = [(l, r) for l, r, st in ready if st != "present"]
    print("run-ledger: %d sessions, %d min wall / %d min active, "
          "%s tokens out, $%.2f cost-equivalent (not an invoice)"
          % (len(rows), wall, active, format(tok["output"], ","), cost))
    print("wrote submission/run_ledger.md and submission/reproduction.md")

    if args.final:
        problems = list(missing)
        if unfinalized:
            problems.append(("Queue reconciliation",
                             "%d row(s) not finalized — run /finalize-compliance" % unfinalized))
        if sessions_no_transcript:
            problems.append(("Transcripts",
                             "%d session(s) with no transcript" % len(sessions_no_transcript)))
        if unattributed:
            problems.append(("Data provenance",
                             "%d file(s) with no registered producing script" % len(unattributed)))
        for label, detail in problems:
            print("FAIL: %s — %s" % (label, detail))
        if problems:
            print("run-ledger --final: %d problem(s); package is not submittable"
                  % len(problems))
            return 1
        print("run-ledger --final: package complete")
        return 0

    if missing:
        print("not yet present: " + ", ".join(l for l, _ in missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
