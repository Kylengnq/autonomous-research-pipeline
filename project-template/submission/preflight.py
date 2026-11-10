#!/usr/bin/env python3
"""Pre-flight check for an the submission research session.

Run this as the FIRST act of every session in this project. It answers one
question the rest of the compliance rail cannot answer about itself: **is this
session being recorded at all?**

The failure it exists to catch. Claude Code loads a project's
`.claude/settings.json` only when that project is the session's project
directory. Launched from the workspace root, `the submission project/.claude/settings.json`
is never read, the three logging hooks are never registered, and nothing is
written. All three hooks also `sys.exit(0)` unconditionally by design, so a
session that is not being logged looks exactly like a session that is.

`run-ledger` cannot see this either: it reconciles `submission/.session_queue.jsonl`
against `submission/conversations/`, and both are written by the same hooks. A
session that ran outside the project directory appears in neither side, so the
reconciliation reports clean on an empty record.

This script breaks that circle by checking the harness state on disk, outside
the compliance rail.

Usage:
    python3 submission/preflight.py            # exits 1 on any FAIL
    python3 submission/preflight.py --quiet    # only print FAIL/WARN lines

Exit codes: 0 all checks passed, 1 at least one FAIL, 2 the script could not run.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path


# A session's transcript must be this fresh for the harness check to count it as
# "this session". Generous: a session can sit idle before anyone runs preflight.
TRANSCRIPT_MAX_AGE_S = 6 * 3600

PLACEHOLDER = "Paste the exact text of the initial prompt here"


def project_root() -> Path:
    """<root>/submission/preflight.py -> <root>."""
    return Path(__file__).resolve().parents[1]


def project_slug(root: Path) -> str:
    """Claude Code's directory name for a project: the absolute path with every
    non-alphanumeric run collapsed to a single dash."""
    return re.sub(r"[^A-Za-z0-9]+", "-", str(root))


class Report:
    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet
        self.failed = 0
        self.warned = 0

    def ok(self, name: str, detail: str = "") -> None:
        if not self.quiet:
            print(f"  PASS  {name}" + (f" — {detail}" if detail else ""))

    def warn(self, name: str, detail: str) -> None:
        self.warned += 1
        print(f"  WARN  {name} — {detail}")

    def fail(self, name: str, detail: str, fix: str) -> None:
        self.failed += 1
        print(f"  FAIL  {name} — {detail}")
        print(f"        fix: {fix}")


def check_harness_logging(root: Path, r: Report) -> None:
    """The load-bearing check: is this session's transcript landing under this
    project's slug? If not, the hooks are not registered and nothing is logged."""
    name = "harness logging (session runs under the project directory)"
    slug_dir = Path.home() / ".claude" / "projects" / project_slug(root)
    relaunch = (
        f'exit, then `cd "{root}" && claude`. '
        "Launching from the workspace root silently disables every logging hook."
    )

    if not slug_dir.is_dir():
        r.fail(
            name,
            f"no transcript directory at {slug_dir}",
            relaunch,
        )
        return

    transcripts = list(slug_dir.glob("*.jsonl"))
    if not transcripts:
        r.fail(name, f"{slug_dir} exists but holds no transcript", relaunch)
        return

    newest = max(transcripts, key=lambda p: p.stat().st_mtime)
    age = time.time() - newest.stat().st_mtime
    if age > TRANSCRIPT_MAX_AGE_S:
        r.fail(
            name,
            f"newest transcript {newest.name} is {age / 3600:.1f}h old, "
            "so it is not this session",
            relaunch,
        )
        return

    r.ok(name, f"{newest.name}, {age / 60:.0f}m old")


def check_sentinel(root: Path, r: Report) -> None:
    """session-start.py writes one sentinel per session. Its absence means the
    SessionStart hook did not run, or the rail is still fail-closed."""
    name = "SessionStart hook fired (sentinel present)"
    sentinels = list((root / "submission").glob(".session-*.start"))
    if not sentinels:
        r.fail(
            name,
            "no submission/.session-*.start sentinel",
            "confirm the harness-logging check above passes, then confirm "
            "submission/initial_prompt.md no longer holds its placeholder. "
            "The hooks fail closed until /init-submission populates it.",
        )
        return
    if len(sentinels) > 1:
        r.warn(
            name,
            f"{len(sentinels)} sentinels present ({', '.join(s.name for s in sentinels)}); "
            "a stale one means an earlier session ended without its SessionEnd hook",
        )
        return
    r.ok(name, sentinels[0].name)


def check_initial_prompt(root: Path, r: Report) -> None:
    name = "initial prompt populated (logging switch on)"
    path = root / "submission" / "initial_prompt.md"
    if not path.exists():
        r.fail(name, "submission/initial_prompt.md is missing", "restore it from the template")
        return
    if PLACEHOLDER in path.read_text(errors="ignore"):
        r.fail(
            name,
            "still holds the placeholder line, so every hook is skipping",
            "run /init-submission — it validates the floor and "
            "populates the file in the same step. Do not edit the placeholder by hand.",
        )
        return
    r.ok(name)


def check_python(root: Path, r: Report) -> None:
    name = "interpreter (pipeline-config `python` key)"
    venv = root / ".venv" / "bin" / "python"
    if not venv.exists():
        r.fail(
            name,
            ".venv/bin/python does not exist",
            f'cd "{root}" && python3 -m venv .venv && '
            ".venv/bin/pip install -r requirements.txt",
        )
        return
    import subprocess

    try:
        v = subprocess.check_output([str(venv), "--version"], stderr=subprocess.STDOUT)
        r.ok(name, v.decode().strip())
    except Exception as exc:  # noqa: BLE001 - report, never raise
        r.fail(name, f".venv/bin/python will not run ({exc})", "rebuild the virtualenv")


def check_config_keys(root: Path, r: Report) -> None:
    """`theme` and `usable_min` both stop the run when unset, at different layers."""
    path = root / "pipeline-config.md"
    if not path.exists():
        r.fail("pipeline-config.md", "missing", "restore it from the template")
        return
    text = path.read_text(errors="ignore")
    for key, why in (
        ("theme", "an unset theme routes S1 to the open swarm path, which is not what this project intends"),
        ("usable_min", "three gates read it; the run stops at the first pilot without it"),
    ):
        m = re.search(rf"^{key}:\s*(.*)$", text, re.M)
        name = f"pipeline-config `{key}`"
        if not m:
            r.fail(name, "key absent", f"add `{key}:` to pipeline-config.md — {why}")
            continue
        value = m.group(1).strip()
        if not value or value.startswith("<"):
            r.fail(name, f"unset ({value or 'empty'})", f"set it from the initial prompt — {why}")
            continue
        r.ok(name, value)


def check_no_optout(root: Path, r: Report) -> None:
    name = "logging not opted out"
    if (root / ".no-session-logging").exists():
        r.fail(
            name,
            ".no-session-logging is present, so every hook is skipping this session",
            "delete it if this session is part of the submitted project",
        )
        return
    r.ok(name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true", help="print only FAIL and WARN lines")
    args = ap.parse_args()

    root = project_root()
    r = Report(quiet=args.quiet)

    if not args.quiet:
        print(f"the submission pre-flight — {root}\n")

    check_harness_logging(root, r)
    check_no_optout(root, r)
    check_initial_prompt(root, r)
    check_sentinel(root, r)
    check_python(root, r)
    check_config_keys(root, r)

    print()
    if r.failed:
        print(
            f"{r.failed} check(s) FAILED. This session is not safe to do research in: "
            "fix the failures above before any research act, or the work will not "
            "reach the submission record."
        )
        return 1
    if r.warned:
        print(f"All checks passed with {r.warned} warning(s).")
        return 0
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"preflight could not run: {exc}", file=sys.stderr)
        sys.exit(2)
