# Automatic the venue Documentation Hooks

Three Claude Code hooks at `.claude/hooks/` automate the parts of the submission
submission logging that can be captured mechanically: conversation transcripts
and rough session durations. The hooks fire on Claude Code session events and
write directly into `submission/`.

## What the hooks capture

| Hook | Event | What it does |
|---|---|---|
| `session-start.py` | SessionStart | Records a sentinel at `submission/.session-<id>.start` with the start timestamp and the git HEAD at session open |
| `log-turn.py` | Stop (after every assistant turn) | Re-renders the **driver** transcript JSONL to `submission/conversations/<date>_<sessionid8>_<slug>.md`, then invokes `submission/export_subagents.py`. Idempotent: rewrites the same file each turn so it always reflects the current session |
| `submission/export_subagents.py` | called by `log-turn.py` | Renders every **subagent** conversation to `submission/conversations/subagents/<date>_<sessionid8>/<role>_<agent8>.md`. Incremental, out-of-process, hard 20s timeout, failures ignored |
| `session-end.py` | SessionEnd | Computes session duration and appends a machine row to `submission/.session_queue.jsonl` (non-destructive: it never edits `human_time_log.md` or the conversation index), removes the sentinel |

## Why subagent capture is a separate step

the contribution record requires the full text of **every** AI conversation, and the driver
transcript is not that. This pipeline routes its reasoning through isolated
subagents on purpose: the desk editors, the debate roles, the decision audit and
the G1 judges each run in their own context, and the clean-room isolation that
makes their judgments independent is exactly what keeps their conversations out
of the driver's transcript. One measured run held **53 subagent transcripts,
6.7 MB**, of which the driver transcript preserved only each spawn prompt and
each return text, both truncated at 2,000 characters.

Claude Code writes them beside the driver transcript:

```text
~/.claude/projects/<slug>/<session-id>.jsonl              driver
~/.claude/projects/<slug>/<session-id>/subagents/         one .jsonl + .meta.json per subagent
~/.claude/projects/<slug>/<session-id>/tool-results/      payloads too large to inline
```

`export_subagents.py` reads that layout (the same one `tools/run_cost.py` uses
for cost) and writes two things:

- **Markdown**, one file per subagent, named for the agent's role, with front
  matter carrying `agent_type`, `model`, `spawn_depth` and
  `spawned_by_tool_use_id`. That last field is the link back: search the driver
  transcript for the id to find the turn that spawned the agent, the prompt it
  was given, and the text it returned.
- **`--raw`**, verbatim scrubbed copies of the driver transcript, every subagent
  transcript, and the `tool-results/` payloads, under
  `submission/conversations/raw/<session8>/`. Scrubbing is applied line by line
  so the copies stay valid JSONL; nothing else is changed.

**The Markdown is not sufficient on its own and `raw/` is what satisfies the
call.** Both renderers truncate long tool payloads, and results the harness
offloaded to `tool-results/` never appear in a transcript at all. Run

```bash
python3 submission/export_subagents.py --raw
```

at every gate and before submission.

## What the hooks do not capture

- **The verbatim assistant prose remains in the transcript even if you delete the conversation file.** The hooks read from the Claude Code transcript JSONL, which is the source of truth.
- **Direct human contributions outside Claude Code sessions** (typing into files in another editor, data pulled by hand, decisions made offline) are not visible to the hooks. Record those in `submission/workflow.md` and `submission/human_time_log.md` manually.
- **"Meaningful" vs trivial sessions.** The hooks log every session that meets the activation gates. Prune the trivial ones from `submission/conversations/` before submission.
- **Contribution percentages.** `/contribution-report` computes those from git history and conversation content. Hooks do not run it automatically.
- **Sessions in other tools.** Hooks fire only in Claude Code. Use `/log-conversation` for Codex, Cursor, web UI, or other interfaces.
- **Any session not launched from this project directory.** Claude Code loads `.claude/settings.json` only when this project is the session's project directory. Started from the workspace root, the hooks are never registered, nothing is written, and no error appears anywhere. `run-ledger` cannot detect it either, because it reconciles the session queue against `submission/conversations/` and both are written by these hooks. Run `python3 submission/preflight.py` as the first act of every session: it checks the harness state on disk, outside this rail.

## Activation gates

A hook returns immediately and writes nothing if any of these are true:

1. **Today is before.** the contribution record forbids logging project work before the start date.
2. **A `.no-session-logging` file exists at the repo root.** Opt-out switch for exploratory or unrelated sessions:
   ```bash
   touch .no-session-logging     # disable
   rm   .no-session-logging      # re-enable
   ```
3. **`submission/initial_prompt.md` does not exist, or still contains the unedited template text.** The hooks assume the project has not officially begun until `/init-submission` has populated this file.

The hooks always exit 0 even on internal errors, so they never block Claude Code.

## What the auto-captured files look like

A conversation file rendered by `log-turn.py`:

```markdown
---
session_id: abc12345-...
started: YYYY-MM-DDT14:30:00+00:00
last_updated: YYYY-MM-DDT15:42:18+00:00
transcript_source: <path>/<id>.jsonl
auto_logged: true
---

# Conversation transcript

Auto-generated by `.claude/hooks/log-turn.py` from the Claude Code transcript.
Review and edit before submission. Trivial sessions can be deleted.

## User

Run /brainstorm on private credit and distressed CRE.

## Assistant

I'll run the brainstorm now.

<details><summary>Tool: search_papers</summary>

```json
{
  "query": "private credit distressed commercial real estate",
  "matchCount": 15
}
```
</details>

...
```

A machine queue row appended by `session-end.py` (one JSON object per line in `submission/.session_queue.jsonl`):

```
{"session_id": "abc12345-...", "date": "", "start_ts": "...", "end_ts": "...", "wallclock_min": 72, "conv_file": "submission/conversations/YYYY-MM-DD_1430_abc12345_brainstorm-private-credit.md", "finalized": false}
```

The hook captures, it does not classify. `wallclock_min` is a raw upper bound (it includes idle gaps, so it can read absurdly large for a session left open overnight). Run `/finalize-compliance` to turn the queue into real `human_time_log.md` rows: it estimates *active* time (capping any single between-turn gap at 10 minutes), infers the real `idea` / `literature` / `analysis` / etc. stage from the transcript, fills `submission/workflow.md`, cleans the conversation index, and marks each queue entry `finalized`. The hook never touches human-authored files, so the queue can never corrupt the submission record.

## Credentials scrubbing

`log-turn.py` runs a regex pass before writing, replacing common credential patterns with `REDACTED`:

- `corbis_mcp_<key>` → `corbis_mcp_REDACTED`
- `sk-<openai-key>` → `sk-REDACTED`
- `Bearer <token>` → `Bearer REDACTED`
- `AKIA<aws-key>` → `AWS_KEY_REDACTED`
- `token`/`api_key`/`apikey`/`secret`/`password` = `<value>` → key kept, value `REDACTED` (this is the shape the CourtListener token leaked through)
- bare 40-hex tokens (CourtListener / GitHub-style) → `REDACTED_TOKEN` (also redacts git SHAs in transcript text; an acceptable trade for not leaking a key)

This is best-effort. Review transcripts before submission and remove any
remaining secrets, personal identifiers, or confidential data. The scrubber only
runs when a transcript is re-rendered, so it does not retroactively clean
transcripts already written by an older version of the hook.

## Disabling the hooks

Three options, in order of granularity:

1. **For a single session**: `touch .no-session-logging` before launching Claude Code, then remove it after.
2. **Permanently**: remove the `SessionStart`, `Stop`, and `SessionEnd` blocks from `.claude/settings.json`.
3. **For an entire project**: delete `.claude/hooks/` and the matching settings blocks.

## Dependencies

The hooks use:

- `python3` (3.9+ — comes with macOS, install on Linux if missing).
- Claude Code 1.x with hook support enabled.

No third-party Python packages required.

## Troubleshooting

- **No conversation files appearing**: confirm Claude Code is running from the repo root (check `$CLAUDE_PROJECT_DIR`), confirm `submission/initial_prompt.md` no longer contains the placeholder text, and confirm today is on or after.
- **Hooks blocking the session**: shouldn't happen; the scripts `exit 0` on every code path. If a hook is misbehaving, comment out its block in `.claude/settings.json`.
- **Wrong file timestamps**: the hooks use UTC for filenames. If you want local-time filenames, edit `log-turn.py` and `session-end.py` to use `datetime.now` instead of `datetime.now(timezone.utc)`.
- **Sessions in worktrees not logging**: hooks pin to the main project dir via `$CLAUDE_PROJECT_DIR`. Worktree-local sessions write back to the parent repo's `submission/`.
