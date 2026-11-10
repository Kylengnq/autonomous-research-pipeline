---
name: init-submission
description: "Bootstrap the submission package. Captures the initial prompt, model configuration, and data-access plan into submission/ artifacts and validates the start date against the call's eligibility floor."
---

# Init Submission

Bootstraps the `submission/` directory for an the submission special-session entry. Run
this once, on the day the project starts.

## When to use

- The user is starting a new project intended for the submission call.
- The user wants to backfill the `submission/` artifacts on an in-flight project.
- The user asks to "set up the submission template," "initialize the venue
  package," or "capture the seed prompt."

## Inputs to collect

| Input | Required? | Notes |
|---|---|---|
| Initial prompt text | Yes | Verbatim; paste, do not paraphrase |
| Date and time the prompt was issued | Yes | Must be on or after the eligibility floor |
| Target model and version | Yes | e.g., claude-opus-4-7 |
| Interface or CLI used | Yes | e.g., Claude Code, Codex CLI, ChatGPT web |
| Issuing author | Yes | Name as it will appear on the paper |
| Named authors | Yes | All humans who may perform project work |
| New-project confirmation | Yes | Must confirm no investigation before the floor |
| Lead-author submission confirmation | Yes | Issuing lead author has no other lead-author submission |
| Total-submission confirmation | Yes | Each listed author appears on at most three submissions |
| Attached materials | No | Files, links, datasets given to the agent |
| MCP servers planned | No | List the servers in `.mcp.json` |
| Planned data sources | No | Corbis, WRDS, FRED, etc. |
| Subagents or skills planned | No | Custom or stock skills the project will use |

## Steps

1. Confirm the project is genuinely intended for the submission call.
   If unclear, ask.
2. Validate the issuance date against the eligibility floor declared in
   `submission/call_requirements.md`. If earlier,
   refuse to proceed and explain the call's rule.
3. Validate eligibility:
   - The project is entirely new.
   - The initial prompt is the first project act.
   - Only named authors will perform human work.
   - The lead-author and total-submission caps are satisfied.
4. Populate `submission/initial_prompt.md`:
   - Fill the metadata table with the inputs.
   - Fill the eligibility gate table.
   - Paste the prompt text verbatim under "Prompt text."
   - Ask the user for the one-or-two sentence "Why this question" rationale.
5. Populate `submission/model_config.md` with the model, version, settings,
   MCP servers, planned agents, and instruction files (`CLAUDE.md`,
   `AGENTS.md`), including the expected AI role by project stage.
6. Populate `submission/data_access.md` with the planned data sources,
   credential scope, and access method.
7. Confirm `submission/call_requirements.md` exists and points to the populated
   artifacts. If it does not exist, create it from the call requirements.
8. If `submission/human_time_log.md` is empty (only the header), add a first
   entry covering the time the human spent issuing the initial prompt.
9. If the first AI response exists, immediately invoke the `log-conversation`
   skill so `submission/conversations/` has its first transcript.
10. Append a dated entry to `notes/lab_notebook.md`:
   `## YYYY-MM-DD — init-submission` followed by a one-line summary.
11. **Verify the logging rail actually switched on.** Populating
   `initial_prompt.md` is what releases the hooks from fail-closed, so this is
   the moment to check that they are firing rather than assume it. If
   `submission/preflight.py` exists, run it and report every line:

   ```bash
   python3 submission/preflight.py
   ```

   A FAIL on the harness-logging check means this session is not running under
   the project directory, so no hook is registered and nothing is being
   written. **Stop and tell the author to relaunch from the project root** —
   do not continue the session, because everything done in it will be absent
   from the submission record with no error anywhere to show for it.

## Outputs

- `submission/initial_prompt.md` (populated)
- `submission/model_config.md` (populated)
- `submission/data_access.md` (populated)
- `submission/call_requirements.md` (confirmed)
- `submission/human_time_log.md` (first row added)
- Optional: first transcript file in `submission/conversations/`
- Entry in `notes/lab_notebook.md`

## Validation

- Reject any issuance date earlier than the venue's declared eligibility floor.
- If the prompt being recorded is a single line or names no question area, say so
  before populating the file. It is preserved verbatim and read by a discussant
  assessing the nature of the human contribution, and it is the one artifact
  that cannot be improved later without falsifying the record. Point at the
  project's initial-prompt template if it has one. Record what the author
  decides either way: this is advice, not a refusal.
- Warn if the user lists more than three projects they intend to submit (the
  call caps each author at three submissions).
- Warn if any non-author humans are listed as contributors (the call requires
  that no humans outside the named authors perform work on the project).
- Refuse to proceed unless the user confirms the paper is an entirely new
  project and the initial prompt is the first project act.
- After populating `initial_prompt.md`, confirm the rail is live: a
  `submission/.session-*.start` sentinel exists and a transcript for this
  session appears under `submission/conversations/`. Both absent means the
  hooks are not registered. Report it as a blocking failure rather than a
  warning: a compliance record that is silently empty is the one defect this
  package cannot recover from after the fact.

## Next steps to suggest

After completing this skill, explicitly tell the user what to do next:

1. **If `references/top_journal_calibration.json` does not exist**: "Next, run `/calibrate-rubric` to build the top-3 journal anchor. Without it, idea screening will cap at Strong Field Candidate. Takes ~5-10 minutes and only needs to run once every ~6 months."
2. **If the calibration set exists and the user has a vague topic**: "Next, run `/brainstorm <your topic>` to generate ten ranked ideas with gate verdicts."
3. **If the calibration set exists and the user has a specific question**: "Next, run `/idea <your question>` to screen it end-to-end."
4. **If a first AI response is available but unlogged**: "I haven't yet captured the opening AI exchange. Run `/log-conversation` and paste the transcript so the submission's `conversations/` directory has its first entry."
