#!/usr/bin/env python3
"""Export subagent conversations into the venue submission package.

the contribution record requires the full text of every AI conversation. `log-turn.py`
renders only the driver's transcript, and this pipeline deliberately routes most
of its reasoning into isolated subagents: the desk editors, the debate roles,
the decision audit, the G1 judges. One measured run held 53 subagent transcripts
totalling 6.7 MB, of which the driver transcript preserved only each spawn
prompt and each return text, both truncated at 2,000 characters.

Claude Code writes those conversations to

    ~/.claude/projects/<slug>/<session-id>/subagents/agent-<id>.jsonl
    ~/.claude/projects/<slug>/<session-id>/subagents/agent-<id>.meta.json

alongside the driver transcript `<session-id>.jsonl`. `tools/run_cost.py`
already reads that layout for cost; nothing in the compliance rail read it at
all until this script.

Two outputs, and they are not redundant:

- **Markdown** under `submission/conversations/subagents/` is the readable
  rendering, one file per subagent, carrying the agent's role, model and the
  `toolUseId` of the driver turn that spawned it. That id is what lets a
  discussant walk from a decision in the driver thread to the isolated
  conversation that produced it.
- **`--raw`** copies the driver transcript, every subagent transcript and the
  offloaded `tool-results/` payloads verbatim (scrubbed) into
  `submission/conversations/raw/`. This is the literal full text, and it is what
  actually satisfies the call. The Markdown is lossy by construction: the
  renderer truncates long tool payloads, and large tool results never appear in
  the transcript at all because the harness offloads them to separate files.

Usage:
    python3 submission/export_subagents.py                  # markdown, all sessions
    python3 submission/export_subagents.py --raw            # markdown + verbatim copies
    python3 submission/export_subagents.py --session <id>   # one session
    python3 submission/export_subagents.py --transcript P   # one driver transcript (hook mode)

Never raises: the Stop hook calls it, and a logging failure must not end a
research session. Problems are reported on stderr and the exit code stays 0
unless --strict is passed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


# Markdown truncation. Higher than log-turn.py's 2000: this file is an archival
# record rather than a reading aid, and --raw carries the untruncated text.
MAX_TOOL_RENDER = 20000


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_slug(root: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", str(root))


def load_log_turn(root: Path):
    """Import the Stop hook as a module so the scrubber and the renderers have a
    single definition. A fix to the credential patterns must reach both files;
    copying the regexes here is how they would drift apart."""
    path = root / ".claude" / "hooks" / "log-turn.py"
    spec = importlib.util.spec_from_file_location("afa_log_turn", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.MAX_TOOL_RENDER = MAX_TOOL_RENDER
    return mod


def slugify(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text or "").strip("-").lower()
    return s[:limit] or "agent"


def session_dirs(root: Path, session: str | None, transcript: str | None) -> list[Path]:
    """Driver transcripts to process, newest first."""
    if transcript:
        p = Path(transcript)
        return [p] if p.exists() else []
    slug_dir = Path.home() / ".claude" / "projects" / project_slug(root)
    if not slug_dir.is_dir():
        return []
    files = sorted(slug_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if session:
        files = [f for f in files if f.stem.startswith(session)]
    return files


def read_turns(path: Path) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    turns.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        return []
    return turns


def render_subagent(
    transcript: Path,
    meta: dict[str, Any],
    render_user: Callable[[Any], list[str]],
    render_assistant: Callable[[Any], list[str]],
) -> str:
    turns = read_turns(transcript)
    lines: list[str] = [
        "---",
        f"agent_id: {transcript.stem}",
        f"agent_type: {meta.get('agentType', 'unknown')}",
        f"description: {json.dumps(meta.get('description', ''))}",
        f"model: {meta.get('model', 'unknown')}",
        f"spawn_depth: {meta.get('spawnDepth', '')}",
        f"spawned_by_tool_use_id: {meta.get('toolUseId', '')}",
        f"source: {transcript}",
        f"exported: {datetime.now(timezone.utc).isoformat()}",
        "auto_logged: true",
        "---",
        "",
        f"# Subagent conversation — {meta.get('description', transcript.stem)}",
        "",
        "Isolated subagent spawned by the driver thread. `spawned_by_tool_use_id`",
        "is the driver turn that launched it: search the driver transcript for that",
        "id to see the prompt it was given and the text it returned.",
        "",
    ]
    for turn in turns:
        content = (turn.get("message") or {}).get("content", "")
        if turn.get("type") == "user":
            lines.extend(render_user(content))
        elif turn.get("type") == "assistant":
            lines.extend(render_assistant(content))
    return "\n".join(lines)


def export_markdown(driver: Path, out_root: Path, lt, verbose: bool) -> tuple[int, int]:
    """Render every subagent of one session. Returns (written, skipped)."""
    subdir = driver.parent / driver.stem / "subagents"
    if not subdir.is_dir():
        return (0, 0)

    stamp = datetime.fromtimestamp(driver.stat().st_mtime).strftime("%Y-%m-%d")
    dest = out_root / "subagents" / f"{stamp}_{driver.stem[:8]}"
    dest.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for meta_path in sorted(subdir.glob("*.meta.json")):
        transcript = meta_path.with_suffix("")
        transcript = transcript.with_suffix(".jsonl") if transcript.suffix != ".jsonl" else transcript
        transcript = Path(str(meta_path).replace(".meta.json", ".jsonl"))
        if not transcript.exists():
            continue
        try:
            meta = json.load(open(meta_path))
        except (ValueError, OSError):
            meta = {}

        name = f"{slugify(meta.get('description', ''))}_{transcript.stem.replace('agent-', '')[:8]}.md"
        out_path = dest / name

        # Incremental: an unchanged transcript is not re-rendered.
        if out_path.exists() and out_path.stat().st_mtime >= transcript.stat().st_mtime:
            skipped += 1
            continue

        body = render_subagent(transcript, meta, lt.render_user, lt.render_assistant)
        out_path.write_text(lt.scrub_credentials(body))
        written += 1
        if verbose:
            print(f"    {out_path.relative_to(out_root.parent.parent)}")
    return (written, skipped)


def export_raw(driver: Path, out_root: Path, lt, verbose: bool) -> int:
    """Verbatim scrubbed copies: the driver transcript, every subagent
    transcript, and the offloaded tool-result payloads.

    Scrubbing is applied line by line so the copies stay valid JSONL. This is
    the only transformation: nothing is truncated, dropped or reordered."""
    dest = out_root / "raw" / driver.stem[:8]
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0

    def copy_scrubbed(src: Path, target: Path) -> None:
        nonlocal copied
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(lt.scrub_credentials(src.read_text(errors="ignore")))
            copied += 1
        except OSError as exc:
            print(f"    could not copy {src}: {exc}", file=sys.stderr)

    copy_scrubbed(driver, dest / driver.name)

    session_dir = driver.parent / driver.stem
    for sub in sorted((session_dir / "subagents").glob("*")):
        if sub.suffix in (".jsonl", ".json"):
            copy_scrubbed(sub, dest / "subagents" / sub.name)
    for res in sorted((session_dir / "tool-results").glob("*")):
        if res.is_file():
            copy_scrubbed(res, dest / "tool-results" / res.name)

    if verbose:
        print(f"    raw: {copied} file(s) -> {dest}")
    return copied


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", action="store_true", help="also copy transcripts verbatim (scrubbed)")
    ap.add_argument("--session", help="session id prefix; default every session in this project")
    ap.add_argument("--transcript", help="path to one driver transcript (hook mode)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit nonzero when nothing was found")
    args = ap.parse_args()

    root = project_root()
    verbose = not args.quiet
    lt = load_log_turn(root)

    # Same fail-closed contract as the hooks: nothing is written before the
    # initial prompt exists, so the record cannot start before the venue rules allow.
    initial = root / "submission" / "initial_prompt.md"
    if not initial.exists() or "Paste the exact text of the initial prompt here" in initial.read_text(errors="ignore"):
        if verbose:
            print("initial_prompt.md still holds its placeholder — nothing exported (fail-closed).")
        return 1 if args.strict else 0
    if (root / ".no-session-logging").exists():
        return 0

    drivers = session_dirs(root, args.session, args.transcript)
    if not drivers:
        if verbose:
            print("No driver transcript found for this project.", file=sys.stderr)
        return 1 if args.strict else 0

    out_root = root / "submission" / "conversations"
    total_written = total_skipped = total_raw = 0
    for driver in drivers:
        if verbose:
            print(f"  session {driver.stem[:8]}")
        w, s = export_markdown(driver, out_root, lt, verbose)
        total_written += w
        total_skipped += s
        if args.raw:
            total_raw += export_raw(driver, out_root, lt, verbose)

    if verbose:
        print(
            f"\n{total_written} subagent transcript(s) written, {total_skipped} unchanged"
            + (f", {total_raw} raw file(s) copied" if args.raw else "")
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - a logging failure must not end a session
        print(f"export_subagents: {exc}", file=sys.stderr)
        sys.exit(0)
