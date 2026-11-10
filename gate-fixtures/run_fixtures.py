#!/usr/bin/env python3
"""Planted-failure harness for the pipeline's machine gates (stdlib only).

Every gate in `workflow/pipeline-design.md` §4 asserts that something cannot
pass. Until now nothing asserted that the gate itself works: a checker that
shares an assumption with the artifact it checks passes silently, which is
what happened once when a recount's adjacency test was built on the same
expression as the count it was auditing, so the two agreed and both were wrong.

Each fixture is a small planted artifact plus a `fixture.json` declaring the
gate, the defect class, the expected exit status, and the text the failure
report must name. A positive fixture the gate passes is a hole in the gate. A
negative fixture the gate fails is a gate that cries wolf, which is the same
defect wearing different clothes -- both directions are tested, for the same
reason the decision audit audits advances as well as kills.

Fixtures run in a temp copy, so a fixture that mutates mtimes or stamps a
registry cannot dirty the source tree.

Usage:
    python3 run_fixtures.py [--skills-root DIR] [--only SUBSTRING] [-v]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_root(start: Path) -> Path:
    """Walk up for the directory holding `.claude/skills` and `tools`.

    This used to be `HERE.parents[2]`, which encodes one layout's depth. Moving
    the suite one level shallower then pointed `{tools}` at a directory that does
    not exist, and the fixture that resolves journal names failed for a reason
    that had nothing to do with the gate it tests. Searching upward survives a
    move; counting parents does not.
    """
    for d in [start, *start.parents]:
        if (d / ".claude" / "skills").is_dir() and (d / "tools").is_dir():
            return d
    return start.parents[1] if len(start.parents) > 1 else start


ROOT = _find_root(HERE)
DEFAULT_SKILLS = ROOT / ".claude" / "skills"


def substitute(value, mapping):
    if isinstance(value, str):
        for k, v in mapping.items():
            value = value.replace("{" + k + "}", v)
        return value
    if isinstance(value, list):
        return [substitute(v, mapping) for v in value]
    return value


def run_fixture(fx_dir: Path, skills_root: Path, verbose: bool) -> dict:
    spec = json.loads((fx_dir / "fixture.json").read_text(encoding="utf-8"))
    result = {
        "name": fx_dir.name,
        "gate": spec["gate"],
        "defect_class": spec.get("defect_class", "-"),
        "expect": spec["expect"],
        "requires": spec.get("requires"),
        "ok": False,
        "why": "",
    }

    with tempfile.TemporaryDirectory(prefix="gatefx-") as tmp:
        work = Path(tmp) / fx_dir.name
        shutil.copytree(fx_dir, work)
        mapping = {
            "python": sys.executable,
            "skills": str(skills_root),
            "checkers": str(HERE / "checkers"),
            "tools": str(ROOT / "tools"),
            "dir": str(work),
        }
        env = dict(os.environ)
        env.update({
            "SKILLS_ROOT": str(skills_root),
            "FIXTURE_DIR": str(work),
            "PYTHON": sys.executable,
        })

        setup = work / "setup.py"
        if setup.is_file():
            proc = subprocess.run([sys.executable, "setup.py"], cwd=work, env=env,
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                result["why"] = f"setup failed: {proc.stdout}{proc.stderr}".strip()
                return result

        cmd = substitute(spec["cmd"], mapping)
        proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True)
        output = proc.stdout + proc.stderr
        if verbose:
            print(f"\n--- {fx_dir.name} (exit {proc.returncode}) ---\n{output}")

    # Exit 2 is a checker saying it could not run -- an unreachable network, not
    # a verdict about the gate. Report it as skipped rather than as a defect.
    if proc.returncode == 2 and spec.get("requires") == "network":
        result["ok"] = True
        result["skipped"] = True
        result["why"] = "skipped: environment unavailable"
        return result

    failed = proc.returncode != 0
    want_failure = spec["expect"] == "fail"
    if failed != want_failure:
        result["why"] = (f"expected {'nonzero' if want_failure else 'zero'} exit, "
                         f"got {proc.returncode}")
        return result

    for needle in spec.get("must_mention", []):
        if needle.lower() not in output.lower():
            result["why"] = f"report never names {needle!r}"
            return result
    for needle in spec.get("must_not_mention", []):
        if needle.lower() in output.lower():
            result["why"] = f"report wrongly names {needle!r}"
            return result

    result["ok"] = True
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-root", default=str(DEFAULT_SKILLS),
                    help="directory holding the promoted skill folders")
    ap.add_argument("--only", help="run only fixtures whose name contains this")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print each gate's full output")
    args = ap.parse_args()

    skills_root = Path(args.skills_root).resolve()
    if not skills_root.is_dir():
        print(f"FAIL: skills root not found: {skills_root}")
        return 1

    fixtures = sorted(p.parent for p in (HERE / "fixtures").glob("*/fixture.json"))
    if args.only:
        fixtures = [f for f in fixtures if args.only in f.name]
    if not fixtures:
        print("FAIL: no fixtures found")
        return 1

    results = [run_fixture(f, skills_root, args.verbose) for f in fixtures]

    width = max(len(r["name"]) for r in results)
    print(f"{'fixture'.ljust(width)}  expect  gate")
    skipped = 0
    for r in results:
        if r.get("skipped"):
            mark, skipped = "skip", skipped + 1
        else:
            mark = "ok  " if r["ok"] else "MISS"
        net = " [net]" if r.get("requires") == "network" else ""
        print(f"{mark} {r['name'].ljust(width)}  {r['expect']:<6}  {r['gate']}{net}")
        if not r["ok"] or r.get("skipped"):
            print(f"     -> {r['why']}")
    if any(r.get("requires") == "network" for r in results):
        print("\n[net] fixtures reach OpenAlex. An unreachable API reports as "
              "skipped, never as a gate failure — a suite that\ncries wolf on "
              "the environment is the same defect it exists to catch in the "
              "gates.")

    bad = [r for r in results if not r["ok"]]
    positives = sum(1 for r in results if r["expect"] == "fail")
    print(f"\n{len(results) - len(bad)}/{len(results)} fixtures behaved as declared "
          f"({positives} planted defects, {len(results) - positives} clean cases)")
    if bad:
        print("A planted defect that passes is a hole in that gate; a clean case "
              "that fails is a gate that cries wolf. Both are defects in the gate, "
              "not in the fixture.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
