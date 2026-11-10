---
name: log-conversation
description: "Capture the full transcript of an AI conversation into submission/conversations/ as a timestamped Markdown file and update the conversation index. Run after every meaningful AI session for the submission submission."
---

# Log Conversation

Captures one AI conversation for the submission submission record. The call
requires "a text of all conversations with AI"; this skill is how that record
gets built.

## When to use

- A meaningful AI conversation just ended and has not been logged yet.
- The user pastes a transcript and asks to file it.
- The user names a session log file (e.g., a Claude Code export) and asks to
  add it to the submission record.

## Inputs to collect

| Input | Required? | Notes |
|---|---|---|
| Transcript source | Yes | Pasted text, path to a file, or a CLI session log |
| Model or agent | Yes | e.g., `claude-opus-4-7`, `gpt-5`, `paper-reader` subagent |
| Project stage | Yes | one of `idea`, `literature`, `design`, `data`, `analysis`, `robustness`, `writing`, `revision`, `submission-prep`, `meta` |
| Goal | Yes | One or two sentences |
| Start and end timestamp | Yes | ISO 8601, with timezone |
| Issuing author | Yes | Name |
| Files written or modified | No | Repo-relative paths |
| Human interventions mid-conversation | No | Where the human steered the agent |

## Steps

1. Resolve the transcript source. If it is a file path, read the file. If it
   is pasted text, use the text as-is. Do not paraphrase or trim turns.
2. Compute the filename: `submission/conversations/YYYY-MM-DD_HHMM_<slug>.md`,
   where `<slug>` is a short kebab-case summary of the goal.
3. Write the conversation file with:
   - YAML frontmatter (`model`, `agent`, `stage`, `started`, `ended`, `author`).
   - `## Goal` section.
   - `## Transcript` section with the verbatim transcript. Tool calls and tool
     results go inside fenced blocks. If the source is a Claude Code session
     log, preserve the structure.
   - `## Outputs` listing files written or modified.
   - `## Human interventions` listing where the human typed text directly into
     the agent stream or steered the agent mid-conversation.
4. Append a row to the index table in `submission/conversations/README.md`:
   `| file | date | stage | model / agent | goal |`. Sort the table
   chronologically (oldest first).
5. Append a dated entry to `notes/lab_notebook.md` noting the conversation
   was logged.

## Outputs

- `submission/conversations/YYYY-MM-DD_HHMM_<slug>.md` (new file).
- Updated index in `submission/conversations/README.md`.
- Entry in `notes/lab_notebook.md`.

## Validation

- Refuse to write if the start timestamp is earlier than the venue's eligibility
  floor, where the project declares one.
- Warn if the transcript appears to contain credentials, API keys, or
  personal identifiers; ask the user to confirm before writing.
- If the proposed filename already exists, append `-2`, `-3`, etc.
