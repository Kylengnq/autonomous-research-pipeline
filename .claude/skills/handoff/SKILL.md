---
name: handoff
description: "Ends a session by regenerating the canonical state file from the lab notebook, git, and the session's artifacts: status, findings with numbers, in-flight jobs with sentinels, a runnable next action, blockers. Author-activated: the closing stage of every session, followed by commit-session."
disable-model-invocation: true
---

# Handoff

Write the next session's starting point into one file. In `gate_mode:
human` (the default) the session close is human-activated: suggest it when
the session's work is done, run it only when the author says so. In
`gate_mode: autonomous` it runs automatically at the end of every session,
followed by a git commit with the standard trailer (see
`<skills_root>/playbooks/gate-modes.md`). `state_file` is the single
source of truth that `resume` reads; everything else is history.

## When to use

- The author closes a working session that changed project state.
- Before `commit-session`, so the committed snapshot includes a current
  handoff.

## What the state file must contain

Overwrite, do not append; the lab notebook is the history. Seven blocks:

1. **Date and one-line status.**
2. **Research question** and where it stands (alive / pivoting / null /
   reframed).
3. **Live findings** with numbers (estimate, SE or t, sample), one line
   each, each traceable to a results file.
4. **In flight**: any detached job, its orchestrator, and the sentinel path
   to poll; anything half-done.
5. **Next action**, written as a runnable instruction: a command, or a
   skill name plus its argument. Not "continue the analysis."
6. **Blockers and caveats**: data gaps, fragile results, decisions awaiting
   the author.
7. **Pointers**: paths to the paper, the results files, the key memos.

## Workflow

1. Read `pipeline-config.md` for `state_file`, `lab_notebook`,
   `results_dir`.
2. Gather what changed this session from the notebook's recent entries,
   `git status` and `git log`, and the results files touched.
3. Overwrite `state_file` with the seven blocks. Convert relative dates to
   absolute. Keep it under 40 lines; detail lives in the notebook.
4. Append a one-line dated entry to `lab_notebook` pointing at this
   handoff.
5. Suggest `commit-session` next.

## Outputs

- Overwritten `state_file`.
- A dated pointer line in `lab_notebook`.

## Validation

- Every number in the state file traces to a results file, not to memory.
- Every in-flight detached job has its sentinel path recorded, or the next
  session cannot resume it.
- The next action is runnable as written.
