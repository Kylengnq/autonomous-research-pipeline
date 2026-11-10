#!/usr/bin/env python3
"""SessionEnd hook for the submission submission logging.

Closes out a session: reads the start sentinel, computes duration, appends a
row to submission/human_time_log.md (flagged for human review), updates the
conversation index, and removes the sentinel.

Never blocks the session: always exits 0.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# Venue eligibility floor: no session dated before this may be logged.
# The default admits everything. Set it to the date your call declares, and
# keep it identical across all three hooks.
ELIGIBILITY_FLOOR = datetime(1970, 1, 1, tzinfo=timezone.utc).date()


def resolve_project_dir() -> Path:
    """Prefer CLAUDE_PROJECT_DIR only when it contains a submission/ package; otherwise fall
    back to the root inferred from this hook's own path. Guards against CLAUDE_PROJECT_DIR
    pointing at a parent directory, which silently breaks logging."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and (Path(env) / "submission").is_dir():
        return Path(env)
    return Path(__file__).resolve().parents[2]


def git_head_from_sentinel(sentinel: Path) -> str:
    """Read the git_head recorded by session-start, if present."""
    try:
        for line in sentinel.read_text().splitlines():
            if line.startswith("git_head="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "none"


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

    sentinel = project_dir / "submission" / f".session-{session_id[:8]}.start"
    if not sentinel.exists():
        return

    start_ts: str | None = None
    for line in sentinel.read_text().splitlines():
        if line.startswith("start_ts="):
            start_ts = line.split("=", 1)[1].strip()

    if not start_ts:
        try:
            sentinel.unlink()
        except Exception:
            pass
        return

    try:
        start_dt = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
    except Exception:
        try:
            sentinel.unlink()
        except Exception:
            pass
        return

    end_dt = datetime.now(timezone.utc)
    duration_min = max(0, int((end_dt - start_dt).total_seconds() / 60))
    h, m = divmod(duration_min, 60)
    duration_str = f"{h}h {m:02d}m"

    date_str = start_dt.strftime("%Y-%m-%d")
    start_hm = start_dt.strftime("%H:%M")
    end_hm = end_dt.strftime("%H:%M")

    conv_dir = project_dir / "submission" / "conversations"
    conv_files = sorted(conv_dir.glob(f"*_{session_id[:8]}_*.md")) if conv_dir.exists() else []
    conv_rel = ""
    conv_name = ""
    if conv_files:
        conv_rel = f"submission/conversations/{conv_files[-1].name}"
        conv_name = conv_files[-1].name

    # Append one machine-owned row to the session queue. This hook is deliberately
    # NON-DESTRUCTIVE: it never edits human-authored files (human_time_log.md or the
    # conversations index). The /finalize-compliance skill reads this queue, estimates
    # *active* time (gap-capped, not wall clock), classifies the stage, and writes the
    # real rows. Wall-clock duration is recorded here only as a raw upper bound.
    queue = project_dir / "submission" / ".session_queue.jsonl"
    entry = {
        "session_id": session_id,
        "date": date_str,
        "start_ts": start_ts,
        "end_ts": end_dt.isoformat(),
        "start_hm": start_hm,
        "end_hm": end_hm,
        "wallclock_min": duration_min,
        "conv_file": conv_rel,
        "conv_name": conv_name,
        "git_head": git_head_from_sentinel(sentinel),
        "finalized": False,
    }
    try:
        with open(queue, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    try:
        sentinel.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
