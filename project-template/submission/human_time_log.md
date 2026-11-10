# Human Time Log

A running record of every human work session on this project. the contribution record
requires "a time log of human activity"; this is that log.

Append a row with `/log-human-time` after each block of direct human work, or
run `/finalize-compliance` to reclassify queued sessions in bulk. Keep entries
in chronological order. Nothing dated before may be logged.

> **The failure mode this format exists to prevent.** An earlier version of this
> template let the session-end hook write `auto-review` rows with wall-clock
> durations straight into this table. Nobody reclassified them, and the log
> ended up full of twelve-hour overnight-gap rows while the running totals read
> near zero — a record that was both inflated and empty, and worse than none.
> The hook now appends machine rows to `submission/.session_queue.jsonl`
> instead, and `/finalize-compliance` is the only thing that turns them into
> rows here. **Do not paste queue rows into this table by hand.**

## Sessions

| Date | Start | End | Duration | Author | Stage | Activity | Deliverable touched |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Running totals

Recomputed by `/finalize-compliance`. Do not hand-edit.

| Author | Total hours | Sessions |
|---|---|---|
| | | |

## Unattributed sessions

Sessions in the queue that could not be confidently attributed to an author or a
duration. These are listed rather than estimated, and each needs a human answer
before submission. An empty table here is a claim that every session was
classified, so leave a row in place until it genuinely is.

| Session id | Date | Why it could not be attributed |
|---|---|---|
| | | |

## Conventions

- **Duration is active time, not wall time.** `/finalize-compliance` sums the
  gaps between consecutive turns and caps any single gap at 10 minutes: a longer
  gap is idle, not work. Wall clock across an overnight session is not a
  measure of human effort and must not be logged as one.
- **Stage**: one of `idea`, `literature`, `design`, `data`, `analysis`,
  `robustness`, `writing`, `revision`, `submission-prep`, `meta`.
- **Activity**: short verb phrase ("chose spec B over spec A," "reviewed agent
  output," "wrote intro paragraph 3"). Supervising an agent is human activity
  and is logged; say so in the phrase.
- **Deliverable touched**: file path relative to repo root.
- If a session interleaves AI prompting and direct human work, log the human
  clock time and note the interleave in **Activity**.
- Never invent a duration. If active time cannot be estimated, leave it blank
  and add the session to *Unattributed sessions*.
