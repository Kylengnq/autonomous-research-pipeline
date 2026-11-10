#!/usr/bin/env python3
"""Stop hook for the submission submission logging.

Re-renders the Claude Code session transcript to a Markdown file under
submission/conversations/. Idempotent: rewrites the same file on every Stop
event so the file always reflects the current session state.

Reads the JSONL transcript at the path provided in the hook input, formats
user/assistant turns and tool calls into Markdown, scrubs common credential
patterns, and writes to submission/conversations/<date>_<sessionid8>_<slug>.md.

This file renders the DRIVER thread only. Subagent conversations live in a
separate directory the harness writes beside the transcript, and this pipeline
routes most of its reasoning through them, so the driver render on its own is
not the record the contribution record asks for. After writing, this hook invokes
submission/export_subagents.py, which renders each subagent conversation with
its role and the tool_use_id of the driver turn that spawned it. That call is
incremental (~0.2s for 53 subagents cold, ~2ms when nothing changed) and can
never block: it runs in a subprocess with a hard timeout and its failures are
ignored.

Never blocks the session: always exits 0.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AFA_CUTOFF = datetime(2026, 6, 1, tzinfo=timezone.utc).date()
MAX_TOOL_RENDER = 2000  # chars before truncation


def resolve_project_dir():
    """Delegate to project_root.py, which handles both layouts and refuses to
    guess when a session root holds more than one paper project. Falls back to
    the old inference if that module is missing, so a hook never dies on an
    import."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from project_root import resolve_or_none
        return resolve_or_none(__file__)
    except Exception:
        env = os.environ.get("CLAUDE_PROJECT_DIR")
        if env and (Path(env) / "submission").is_dir():
            return Path(env)
        return Path(__file__).resolve().parents[2]


def load_turns(transcript_path: Path) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    turns.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return turns


def extract_text(content: Any) -> str:
    """Pull plain text out of either a string or a list-of-blocks content field."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return " ".join(parts)
    return ""


def render_user(content: Any) -> list[str]:
    out = ["## User", ""]
    if isinstance(content, str):
        out.append(content)
    elif isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                out.append(str(item))
                continue
            t = item.get("type")
            if t == "text":
                out.append(item.get("text", ""))
            elif t == "tool_result":
                tid = str(item.get("tool_use_id", "?"))[:8]
                raw = item.get("content", "")
                if isinstance(raw, list):
                    raw = "\n".join(
                        x.get("text", "") if isinstance(x, dict) else str(x)
                        for x in raw
                    )
                txt = str(raw)
                if len(txt) > MAX_TOOL_RENDER:
                    txt = txt[:MAX_TOOL_RENDER] + "\n...[truncated]"
                out.append(
                    f"<details><summary>Tool result ({tid})</summary>\n\n```\n{txt}\n```\n</details>"
                )
    out.append("")
    return out


def render_assistant(content: Any) -> list[str]:
    out = ["## Assistant", ""]
    if isinstance(content, str):
        out.append(content)
    elif isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                out.append(str(item))
                continue
            t = item.get("type")
            if t == "text":
                out.append(item.get("text", ""))
            elif t == "tool_use":
                name = str(item.get("name", "?"))
                inp = item.get("input", {})
                try:
                    inp_str = json.dumps(inp, indent=2)
                except Exception:
                    inp_str = str(inp)
                if len(inp_str) > MAX_TOOL_RENDER:
                    inp_str = inp_str[:MAX_TOOL_RENDER] + "\n...[truncated]"
                out.append(
                    f"<details><summary>Tool: {name}</summary>\n\n```json\n{inp_str}\n```\n</details>"
                )
            elif t == "thinking":
                txt = item.get("thinking", "")
                if len(txt) > MAX_TOOL_RENDER:
                    txt = txt[:MAX_TOOL_RENDER] + "\n...[truncated]"
                out.append(f"<details><summary>Thinking</summary>\n\n{txt}\n\n</details>")
    out.append("")
    return out


def scrub_credentials(text: str) -> str:
    text = re.sub(r"corbis_mcp_[A-Za-z0-9_-]+", "corbis_mcp_REDACTED", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_\-]{20,}", "sk-REDACTED", text)
    text = re.sub(r"\bBearer\s+[A-Za-z0-9_.\-]+", "Bearer REDACTED", text)
    text = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "AWS_KEY_REDACTED", text)
    # CourtListener / generic API tokens: a token-like value assigned to a key whose name
    # contains token/api_key/apikey/secret/password (the CourtListener token leaked this way).
    text = re.sub(
        r"(?i)\b(token|api[_-]?key|apikey|secret|password)\b(\s*[:=]\s*|\s+)['\"]?[A-Za-z0-9_\-]{16,}['\"]?",
        r"\1\2REDACTED",
        text,
    )
    # 40-hex tokens (CourtListener/GitHub-style), when not obviously a git SHA context.
    text = re.sub(r"\b[0-9a-f]{40}\b", "REDACTED_TOKEN", text)
    return text


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    session_id = str(data.get("session_id", "unknown"))
    transcript_path = data.get("transcript_path", "")
    project_dir = resolve_project_dir()
    if project_dir is None:
        return  # resolution said why on stderr

    if datetime.now(timezone.utc).date() < AFA_CUTOFF:
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

    if not transcript_path or not Path(transcript_path).exists():
        return

    turns = load_turns(Path(transcript_path))
    if not turns:
        return

    # Recover start time from sentinel if available
    sentinel = project_dir / "submission" / f".session-{session_id[:8]}.start"
    start_ts: str | None = None
    if sentinel.exists():
        for line in sentinel.read_text().splitlines():
            if line.startswith("start_ts="):
                start_ts = line.split("=", 1)[1].strip()

    if start_ts:
        try:
            dt = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
            file_ts = dt.strftime("%Y-%m-%d_%H%M")
        except Exception:
            file_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    else:
        file_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")

    # Slug from first user turn
    slug = "session"
    for turn in turns:
        if turn.get("type") == "user":
            text = extract_text(turn.get("message", {}).get("content", ""))
            candidate = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()[:40]
            if candidate:
                slug = candidate
            break

    conv_dir = project_dir / "submission" / "conversations"
    conv_dir.mkdir(parents=True, exist_ok=True)
    out_path = conv_dir / f"{file_ts}_{session_id[:8]}_{slug}.md"

    lines: list[str] = [
        "---",
        f"session_id: {session_id}",
        f"started: {start_ts or 'unknown'}",
        f"last_updated: {datetime.now(timezone.utc).isoformat()}",
        f"transcript_source: {transcript_path}",
        "auto_logged: true",
        "---",
        "",
        "# Conversation transcript",
        "",
        "Auto-generated by `.claude/hooks/log-turn.py` from the Claude Code transcript.",
        "Review and edit before submission. Trivial sessions can be deleted.",
        "",
    ]

    for turn in turns:
        ttype = turn.get("type")
        content = turn.get("message", {}).get("content", "")
        if ttype == "user":
            lines.extend(render_user(content))
        elif ttype == "assistant":
            lines.extend(render_assistant(content))

    output = "\n".join(lines)
    output = scrub_credentials(output)

    try:
        out_path.write_text(output)
    except Exception:
        return

    export_subagents(project_dir, transcript_path)


def export_subagents(project_dir: Path, transcript_path: str) -> None:
    """Render this session's subagent conversations into the submission package.

    Runs out-of-process with a hard timeout so that neither a slow render nor a
    crash in the exporter can stall or fail a research session. Every failure
    here is silent by design, which is why submission/preflight.py and
    run-ledger check the resulting files rather than trusting this call."""
    script = project_dir / "submission" / "export_subagents.py"
    if not script.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(script), "--transcript", transcript_path, "--quiet"],
            timeout=20,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
