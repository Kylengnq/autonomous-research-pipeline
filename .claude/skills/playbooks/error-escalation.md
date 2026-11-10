# Error escalation playbook

Every pipeline skill cites this playbook instead of restating it. It has two
parts: the escalation ladder for failures, and the harness survival rules
for anything that touches the shell, the network, or long-running jobs.

## The ladder

Applied at every step of every stage. No step silently proceeds past a
failure.

1. **Bounded retry.** Transient failures (rate limits, timeouts, network
   errors, compile errors with an obvious fix) retry with backoff, at most
   three attempts. Log each retry in the step's output.
2. **Flagged degradation.** If retries fail, write the gap where the result
   would have gone: `[MATERIAL GAP: <exactly what is missing and why>]`,
   or a checkpoint file describing where the job stopped. Continue only if
   the gap is non-blocking for the current stage; a gap in a machine-gate
   input is always blocking.
3. **Gate escalation.** Blocking gaps, judgment calls, and integrity
   surprises go to the nearest gate, with the options laid out. Judgment
   calls include: structural breaks in a series, coverage collapses,
   proxy failures, estimator-vs-library disagreement beyond tolerance,
   post-freeze specification deviations, and fatal referee findings that
   survive the fix loop. Who decides depends on `gate_mode` in
   `pipeline-config.md` (see `gate-modes.md` in this directory): in
   `human` mode the author decides; in `autonomous` mode the matching
   per-gate rule applies, and a call no rule covers PARKS the project
   rather than being guessed.

4. **Budget exhaustion**. When a stage reaches a declared limit
   before finishing, it **stops and reports**, and what it reports is fixed:
   the best current artifact, the work that completed, the issues left
   unresolved, and the reason it stopped. Two keys are honoured as stopping
   rules — `budget.max_wall_clock` (minutes per stage) and
   `driver_context_ceiling` (the driver splits at the next layer boundary when
   its context passes this, per `run-pipeline`'s driver discipline). The
   remaining `budget` keys are **reported counters, not stopping rules**.
   This rung is distinct from the three above because **nothing failed**:
   retry covers transient errors, degradation covers missing material, and
   escalation covers judgment, while running out of budget is a normal outcome
   that previously had no defined behaviour. It is the Material Gap rule
   pointed at budgets: **partial completion is never presented as a finished
   result**, and a stage that stopped on budget says so in its own output
   rather than leaving the next session to infer it.
   A budget is a declaration and a stopping rule, **not a gate**: it never sits
   in the integrity path, and a stage may not skip a machine gate because it
   ran out of budget. If the budget expires with a gate unrun, the stage stops
   *before* the gate and reports it as unrun; it does not pass it by default.

The Material Gap rule holds at every rung: a number, citation, quote, or
fact not present in a project artifact is never filled from model memory.

## Harness survival rules

Learned at real cost in the predecessor workflow; binding on every skill and
script.

- **Absolute paths in backgrounded commands.** A backgrounded shell starts
  in a different working directory; `./.venv/bin/python` exits 127. Resolve
  paths before backgrounding.
- **Single-threaded access to rate-limited APIs.** Two concurrent OpenAlex
  jobs rate-limit each other into returning nothing while burning 6x
  retries. One search job at a time, always.
- **Checkpoint anything longer than a session turn.** Long crawls write
  progress files and resume from them; a killed job must lose minutes, not
  hours. Detached jobs record a sentinel path (`*.DONE`) that the state
  file carries so the next session can poll it.
- **Progress prints.** Long scripts print progress so partial work is
  visible in logs; silence is indistinguishable from a hang.
- **Skills must work without slash registration.** Some skills fail to
  register as commands; reading the SKILL.md and following it manually is
  always a supported path, so skills never depend on invocation-time
  argument magic.
