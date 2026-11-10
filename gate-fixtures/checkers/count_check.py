#!/usr/bin/env python3
"""Counting gate: re-execute every reported count, made executable.

`idea-pilot` requires that every reported count carry a ```count block whose
`expression` is the literal source line that produced `value`, that the
harness re-execute it, and that any count carrying a terminal verdict or a
menu number be derived twice by *independent* expressions. Both of an earlier run's
confirmed arithmetic defects were a count computed at one unit and labelled
at another, with the prose accurate about intent.

The independence requirement is the part a checker earns its keep on: the
a recount once ran the same expression twice and agreed with itself.

Block schema (fenced ```count in any markdown file):

    name: usable_units
    unit: trader-meetings
    value: 80
    source: pilot_data.py          # defines `df` when exec'd
    expression: df.groupby(["taker","meeting"]).ngroups
    terminal: true                 # optional; requires expression_b
    expression_b: len(set(zip(df.taker, df.meeting)))

Exit 0 only when every block re-executes to its stated value, every terminal
block carries a second expression, the two agree, and the two are not the
same string.

Usage:
    python3 count_check.py --report FILE [--report FILE ...]
"""

import argparse
import re
import sys
from pathlib import Path

BLOCK_RE = re.compile(r"```count\s*\n(.*?)```", re.DOTALL)


def parse_block(body: str) -> dict:
    fields = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        if not _:
            continue
        fields[key.strip()] = value.split("  #")[0].strip()
    return fields


def evaluate(expression: str, source: Path, failures: list, label: str):
    namespace: dict = {}
    try:
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"),
             namespace)
    except Exception as exc:  # the fixture's own data script is under test too
        failures.append(f"{label}: source {source} failed to run: {exc}")
        return None
    try:
        return eval(expression, namespace)
    except Exception as exc:
        failures.append(f"{label}: expression did not evaluate: {expression!r} "
                        f"({exc})")
        return None


def check_report(path: Path, failures: list) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = BLOCK_RE.findall(text)
    if not blocks:
        failures.append(f"{path}: no ```count block; every reported count carries "
                        f"a machine-readable definition")
        return 0
    for body in blocks:
        f = parse_block(body)
        label = f"{path}:{f.get('name', '?')}"
        for required in ("name", "unit", "value", "source", "expression"):
            if required not in f:
                failures.append(f"{label}: block is missing `{required}`")
        if "expression" not in f or "source" not in f or "value" not in f:
            continue
        if "[MATERIAL GAP" in f["expression"]:
            print(f"warn: {label}: expression not isolable, declared as a gap")
            continue

        source = (path.parent / f["source"]).resolve()
        if not source.is_file():
            failures.append(f"{label}: source not found: {f['source']}")
            continue

        stated = float(f["value"])
        got = evaluate(f["expression"], source, failures, label)
        if got is not None and float(got) != stated:
            failures.append(f"{label}: re-execution gives {got}, block states "
                            f"{f['value']} (unit: {f.get('unit')}). A count "
                            f"computed at one unit and labelled at another is "
                            f"an earlier run defect class.")

        terminal = str(f.get("terminal", "")).lower() in {"true", "yes", "1"}
        if not terminal:
            continue
        second = f.get("expression_b")
        if not second:
            failures.append(f"{label}: carries a terminal verdict or a menu number "
                            f"and has only one derivation; a second independent "
                            f"expression is required before the verdict stands")
            continue
        if second.strip() == f["expression"].strip():
            failures.append(f"{label}: the two derivations are the same expression "
                            f"run twice; that agrees with itself by construction")
            continue
        got_b = evaluate(second, source, failures, label + "/b")
        if got is not None and got_b is not None and float(got) != float(got_b):
            failures.append(f"{label}: the two independent derivations disagree "
                            f"({got} vs {got_b}); the verdict is blocked rather "
                            f"than resolved by picking one")
    return len(blocks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="append", required=True)
    args = ap.parse_args()

    failures: list = []
    total = 0
    for r in args.report:
        path = Path(r)
        if not path.is_file():
            failures.append(f"report not found: {r}")
            continue
        total += check_report(path, failures)

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"counts: {len(failures)} problems across {total} blocks")
        return 1
    print(f"counts OK: {total} blocks re-executed and matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
