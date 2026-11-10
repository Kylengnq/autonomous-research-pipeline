#!/usr/bin/env python3
"""Gate: the contribution hooks write to exactly one paper, or to none and say so.

WHY THIS EXISTS

Claude Code resolves skills, `.mcp.json` and hooks from the session root and
only from there. The hooks used to live beside the paper project while the
skills lived at the repository root, so a session could satisfy one or the
other and never both -- and launching from the root failed SILENTLY, which is
the part that matters. A compliance record that is quietly empty is worse than
one that is missing, because nothing tells you to look.

The hooks now live at the root and find the paper underneath. That introduces a
different hazard: more than one paper under one root, where a wrong guess files
one project's transcripts into another's record. So the resolver must refuse,
not choose.

This checks the three outcomes a hook can have, against a planted tree:
  --expect none     no configured paper: resolve quietly to nothing
  --expect one      exactly one: resolve to it
  --expect refuse   several: resolve to nothing AND say why

Exit 0 when the resolver behaves as declared, 1 otherwise.
"""
import argparse
import os
import pathlib
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", required=True, help="planted session root")
    ap.add_argument("--expect", required=True, choices=["none", "one", "refuse"])
    ap.add_argument("--name", help="with --expect one, the directory it must choose")
    a = ap.parse_args()

    # Absolute before the cwd change below, or the interpreter looks for the
    # script relative to --root and "not found" reads as "no paper", which
    # passed the no-paper case for entirely the wrong reason.
    root = pathlib.Path(a.root).resolve()
    resolver = root / ".claude" / "hooks" / "project_root.py"
    if not resolver.is_file():
        print(f"FAIL hook target: no resolver at {resolver}")
        return 1

    # CLAUDE_PROJECT_DIR from the surrounding session would override the planted
    # tree and silently make every fixture a test of the wrong directory.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    proc = subprocess.run([sys.executable, str(resolver), "--doctor"],
                          capture_output=True, text=True, cwd=root, env=env)
    out = proc.stdout + proc.stderr

    # A resolver that crashed is not a resolver that decided. Without this, any
    # breakage reads as "chose nothing" and quietly satisfies the none/refuse
    # cases -- a checker agreeing with itself, which is the defect this suite
    # exists to catch.
    if proc.returncode not in (0, 1) or "project:" not in out:
        print(f"FAIL hook target: resolver did not run (exit {proc.returncode}):\n{out}")
        return 1

    chose = proc.returncode == 0

    if a.expect == "one":
        if not chose:
            print(f"FAIL hook target: expected one paper, resolver chose nothing\n{out}")
            return 1
        if a.name and a.name not in out:
            print(f"FAIL hook target: expected {a.name!r}, got:\n{out}")
            return 1
        print(f"hook target OK: resolved to {a.name or 'the single paper'}")
        return 0

    if chose:
        print(f"FAIL hook target: expected no target for --expect {a.expect}, "
              f"resolver chose one:\n{out}")
        return 1

    if a.expect == "refuse":
        # Silence is the defect. The refusal has to name the reason.
        for needle in ("Refusing to guess", "paper projects"):
            if needle.lower() not in out.lower():
                print(f"FAIL hook target: refused without saying why, "
                      f"never names {needle!r}:\n{out}")
                return 1
        print("hook target OK: several papers, refused and said why")
        return 0

    print("hook target OK: no configured paper, resolved to nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
