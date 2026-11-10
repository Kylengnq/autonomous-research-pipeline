---
name: log-human-time
description: "Append a single human work session to submission/human_time_log.md and update the running totals. Use after any block of direct human work on the submission project."
---

# Log Human Time

Appends one human work session to the submission submission's time log. The call
requires "a time log of human activity"; this skill maintains it.

## When to use

- A human just finished a session of direct work on the project (typing,
  reading agent output, decision-making) and the session has not been logged.
- The user dictates a session ("log 45 minutes of revision work on the
  intro").

## Inputs to collect

| Input | Required? | Notes |
|---|---|---|
| Date | Yes | YYYY-MM-DD; default to today if not given |
| Start time | Yes | HH:MM, 24h, with timezone if non-local |
| End time | Yes | HH:MM, 24h |
| Author | Yes | Name; default to the issuing user if known |
| Stage | Yes | one of `idea`, `literature`, `design`, `data`, `analysis`, `robustness`, `writing`, `revision`, `submission-prep`, `meta` |
| Activity | Yes | Short verb phrase |
| Deliverable touched | No | Repo-relative file path(s) |

## Steps

1. Parse the inputs and compute `duration` (rounded to the nearest 5 minutes).
2. Read `submission/human_time_log.md`.
3. Append a new row to the **Sessions** table in chronological position.
4. Recompute the **Running totals** table by re-summing all rows grouped by
   author.
5. Append a dated entry to only if this session
   represents a deliverable milestone; otherwise skip the lab note (avoid
   flooding the notebook with routine session logs).

## Outputs

- Updated `submission/human_time_log.md`.

## Validation

- Refuse to log a session whose date is before the venue's eligibility floor,
  where the project declares one.
- Reject `end < start`.
- Warn if a single session is longer than 6 hours (likely an error; ask to
  confirm).
- If multiple sessions overlap for the same author on the same day, warn and
  ask the user to confirm.
