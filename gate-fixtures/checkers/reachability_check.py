#!/usr/bin/env python3
"""Gate: every stage the conductor names must be reachable by the conductor.

WHY THIS EXISTS

`run-pipeline` is a skill, so when it drives a stage it is making a
model-initiated call. A skill carrying `disable-model-invocation: true` refuses
exactly that call, and the harness also forbids the documented fallback of
reading the SKILL.md and following it manually. The two settings are individually
reasonable and jointly fatal: the conductor names a stage it can never enter.

A cold run of the published pipeline hit this. Four funnel layers carried the
flag, `/run-pipeline` could not reach S1, and every other check in this suite
passed, because the suite tested what gates do and nothing tested whether a
stage can be called at all. The swarm path makes it worse than it sounds: the
two layers before the wall ARE invocable, so a run generates and scores a full
pool, spends most of the funnel budget, and fails afterwards.

The check is deliberately shallow. It does not reason about stage order or about
whether a skill works. It asserts one property: a skill the conductor names in
backticks exists and does not refuse the conductor.

Exit 0 when every named stage is reachable, 1 otherwise.

Usage:
    reachability_check.py --skills-root DIR [--conductor run-pipeline]
"""
import argparse
import pathlib
import re
import sys

FLAG = re.compile(r"^disable-model-invocation:\s*true\s*$", re.M)
# Any backticked lowercase token. Intersecting with the directories that exist
# does the filtering, so the pattern does not need to be clever -- and must not
# be: requiring a hyphen silently skipped `handoff`, which is one word and is
# named by the conductor at every layer boundary.
NAME = re.compile(r"`([a-z][a-z0-9-]*)`")


def frontmatter(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-root", required=True)
    ap.add_argument("--conductor", default="run-pipeline")
    a = ap.parse_args()

    root = pathlib.Path(a.skills_root)
    conductor = root / a.conductor / "SKILL.md"
    if not conductor.is_file():
        print(f"FAIL reachability: conductor {a.conductor}/SKILL.md not found under {root}")
        return 1

    existing = {d.name for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}
    named = set(NAME.findall(conductor.read_text(encoding="utf-8", errors="ignore")))
    stages = sorted(named & existing)

    if not stages:
        print(f"FAIL reachability: {a.conductor} names no stage skill at all; "
              f"either the conductor is empty or the skills root is wrong")
        return 1

    blocked = [s for s in stages if FLAG.search(frontmatter(root / s / "SKILL.md"))]

    if blocked:
        print(f"FAIL reachability: {a.conductor} names {len(blocked)} stage(s) that "
              f"refuse model invocation, so the conductor cannot enter them:")
        for s in blocked:
            print(f"  {s}: disable-model-invocation: true")
        print("A stage the conductor drives must stay model-invocable. Put the "
              "discipline in the skill's 'When to use' instead.")
        return 1

    print(f"reachability OK: {len(stages)} stage skill(s) named by {a.conductor}, "
          f"all model-invocable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
