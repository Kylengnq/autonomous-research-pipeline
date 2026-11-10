---
name: resume
description: "Starts a session by reading the canonical state file and lab-notebook tail, checks in-flight jobs and state staleness, and produces a 5-line brief: status, live findings, in-flight work, next action, blockers. Run first in any continuation session."
---

# Resume

Re-establish project state in one read. `handoff` keeps `state_file`
current at every session close; this skill reads it at session open so no
session starts by re-deriving state from scattered documents.

## When to use

- The first action in any continuation session on a paper project.
- Any time a fast, accurate "where are we" is needed without reading the
  whole notebook.

## Workflow

1. **Read `pipeline-config.md`** at the paper project's root for
   `state_file`, `lab_notebook`, and `decisions_log`. If the config is
   missing, stop and offer to create it from
   `pipeline-config.template.md`, which sits next to this skill's folder
   in the skills directory.
2. **Read `state_file`.** If it does not exist, do not guess: propose
   running `handoff` to create it, and stop.
3. **Staleness check.** Compare the state file's date and mtime against the
   last git commit touching the project. If the state file predates that
   commit, flag it stale and show the commit summary; the brief must say
   state may be behind.
4. **Read the tail** of `lab_notebook` (last ~30 lines) and the last entry
   of `decisions_log`.
5. **Check in-flight work.** If the state file names a detached job and a
   sentinel path, check whether the sentinel landed and report the job as
   done or still running.
6. **Produce the brief**, at most 5 lines: (a) question and current status,
   (b) live result with its number, (c) in-flight work and job status,
   (d) the next concrete action, (e) blockers. Open the brief by naming
   the project's `gate_mode`. In `human` mode, end by asking the author
   to confirm the next action or redirect; in `autonomous` mode, proceed
   to the next action (or report PARKED status and what gap caused it).

## Outputs

- The on-screen brief only. Read-only: this skill writes nothing.

## Validation

- Never summarize from memory of a previous session when `state_file`
  exists; the file wins.
- If the state file and the notebook tail disagree, surface the conflict in
  the brief rather than picking silently.
- A sentinel that has not landed is reported as still running, never as
  done.
