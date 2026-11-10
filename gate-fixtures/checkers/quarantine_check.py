#!/usr/bin/env python3
"""Quarantine check: the clean-room wall, made executable (stdlib only).

`workflow/pipeline-design.md` S1b wall 2 says no downstream artifact may
reference a `quarantine/` path or quote the debate transcript, and the gate
table calls it a grep-level check at S4 entry and inside S7. It was prose. A
gate nobody can run is a gate nobody knows the state of, so this is it:

  path leak   -- a file outside quarantine/ naming a quarantine/ path.
  quote leak  -- a long sentence from a quarantine file appearing verbatim in
                 a downstream file, which is how advocacy crosses the wall
                 when the path is not named.

Exit 0 only when neither fires.

Usage:
    python3 quarantine_check.py --root DIR [--min-words N]
"""

import argparse
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".tex", ".json", ".yaml", ".yml", ".py"}
PATH_RE = re.compile(r"quarantine/[\w./-]*")


def is_quarantined(path: Path) -> bool:
    return "quarantine" in path.parts


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sentences(text: str, min_words: int):
    for raw in re.split(r"(?<=[.!?])\s+|\n", text):
        norm = re.sub(r"\s+", " ", raw).strip()
        if len(norm.split()) >= min_words:
            yield norm


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--min-words", type=int, default=12,
                    help="shortest sentence treated as a quotable span")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"FAIL: root not found: {root}")
        return 1

    files = [p for p in sorted(root.rglob("*"))
             if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES]
    quarantined = [p for p in files if is_quarantined(p)]
    downstream = [p for p in files if not is_quarantined(p)]

    banned = {}
    for q in quarantined:
        for s in sentences(read(q), args.min_words):
            banned.setdefault(s, q)

    failures = []
    for d in downstream:
        text = read(d)
        for hit in PATH_RE.findall(text):
            failures.append(f"path leak: {d} references {hit}")
        flat = re.sub(r"\s+", " ", text)
        for s, src in banned.items():
            if s in flat:
                failures.append(f"quote leak: {d} reproduces a sentence from {src}: "
                                f"{s[:70]!r}...")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"quarantine: {len(failures)} leaks across {len(downstream)} "
              f"downstream files")
        return 1
    print(f"quarantine OK: {len(downstream)} downstream files clean against "
          f"{len(quarantined)} quarantined files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
