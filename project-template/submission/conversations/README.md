# Conversations

Every AI conversation on this project, in three layers. the contribution record asks for
"a text of all conversations with AI"; this directory satisfies that
requirement, and it takes all three layers to do so.

```text
<date>_<session8>_<slug>.md      the driver thread, one file per session
subagents/<date>_<session8>/     one file per isolated subagent of that session
raw/<session8>/                  verbatim scrubbed .jsonl for driver and subagents
```

**Why three.** The pipeline routes most of its reasoning through isolated
subagents (desk editors, debate roles, the decision audit, the G1 judges), so
the driver thread alone is a small fraction of the record: one measured session
held 53 subagent conversations against a single driver transcript. And both
Markdown renderings truncate long tool payloads, while results the harness
offloaded to separate files never appear in a transcript at all. So the Markdown
is the readable rendering and **`raw/` is the literal full text**.

**Following one decision through.** Each subagent file's front matter carries
`spawned_by_tool_use_id`. Search the driver transcript for that id to find the
turn that launched the agent, the prompt it was given, and the text it returned.
The subagent file is what happened in between, which the driver never saw.

`subagents/` and `raw/` are written by `submission/export_subagents.py`, called
automatically by the Stop hook (Markdown) and run with `--raw` at each gate.
See `submission/HOOKS.md`.

Log the initial prompt conversation, research conversations, coding sessions,
analysis sessions, writing sessions, review sessions, failed attempts, and
autonomous runs. Do not omit a conversation because it produced no final
artifact.

## File naming

```
YYYY-MM-DD_HHMM_<short-slug>.md                    driver
subagents/YYYY-MM-DD_<session8>/<role>_<agent8>.md subagent, named for its role
```

Examples:
- `YYYY-MM-DD_0900_initial-prompt.md`
- `YYYY-MM-DD_1430_literature-positioning.md`
- `YYYY-MM-DD_2200_overnight-autonomous-run.md`

## File contents

Each conversation file should include:

1. **Frontmatter** with model, agent, stage, started, ended.
2. **Goal** — one or two sentences on what the conversation was trying to accomplish.
3. **Full transcript** — every user turn and every assistant turn, verbatim.
   Tool calls and tool results should be included or summarized in a
   collapsible block. If the conversation came from Claude Code or a similar
   CLI, paste the session log directly.
4. **Outputs produced** — paths to files written or modified by the conversation.
5. **Human interventions** — anywhere the human typed text directly into the
   tool stream or steered the agent mid-conversation.

## Index

Append a row for each conversation (newest at the bottom). `/log-conversation`
maintains this table automatically.

| File | Date | Stage | Model / agent | Goal |
|---|---|---|---|---|

## Privacy note

Per the call: organizers will not use non-public information from the
submission for their own research. Even so, scrub any credentials, personal
identifiers, or confidential data from transcripts before submission.

> **Note on where rows land.** The session-end hook appends its index rows at
> the end of this file rather than into the table above, so an index left as the
> hook wrote it will have rows below the privacy note carrying `(auto) session
> Xh Ym` in place of a goal. `/finalize-compliance` rewrites them into the table
> with a real one-line goal read from each transcript's opening turn. Run it
> before submission: `(auto)` is a placeholder, not a description of what the
> session was for.

