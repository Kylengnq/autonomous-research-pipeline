#!/usr/bin/env python3
"""SessionStart hook for the submission submission logging.

Records a session-start sentinel under submission/ so the SessionEnd hook can
compute duration. Skips silently if the venue cutoff has not arrived, if the
opt-out file exists, or if the submission package has not been initialized.

Never blocks the session: always exits 0.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Venue eligibility floor: no session dated before this may be logged.
# The default admits everything. Set it to the date your call declares, and
# keep it identical across all three hooks.
ELIGIBILITY_FLOOR = datetime(1970, 1, 1, tzinfo=timezone.utc).date()


def resolve_project_dir() -> Path:
    """Locate the repo root robustly.

    CLAUDE_PROJECT_DIR can point at a parent directory when `claude` is launched from
    above this repo, which silently breaks logging. Prefer it only when it actually
    contains a submission/ package; otherwise fall back to the root inferred from this
    hook's own location (<root>/.claude/hooks/<file>.py)."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and (Path(env) / "submission").is_dir():
        return Path(env)
    return Path(__file__).resolve().parents[2]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    session_id = str(data.get("session_id", "unknown"))
    project_dir = resolve_project_dir()

    if datetime.now(timezone.utc).date() < ELIGIBILITY_FLOOR:
        return

    if (project_dir / ".no-session-logging").exists():
        return

    initial = project_dir / "submission" / "initial_prompt.md"
    if not initial.exists():
        return
    try:
        if "Paste the exact text of the initial prompt here" in initial.read_text(errors="ignore"):
            return
    except Exception:
        return

    sentinel = project_dir / "submission" / f".session-{session_id[:8]}.start"
    sentinel.parent.mkdir(parents=True, exist_ok=True)

    git_head = "none"
    try:
        git_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=project_dir,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass

    sentinel.write_text(
        f"session_id={session_id}\n"
        f"start_ts={datetime.now(timezone.utc).isoformat()}\n"
        f"git_head={git_head}\n"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
