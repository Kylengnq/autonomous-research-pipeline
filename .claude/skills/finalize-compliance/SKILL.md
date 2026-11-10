---
name: finalize-compliance
description: "Turn the machine-owned session queue into a real the venue submission record: reclassify auto-logged sessions into human-time rows, fill submission/workflow.md stage-by-stage from the transcripts and lab notebook, rewrite the conversation index with real goals, and flag everything that needs human confirmation. Run before submission, and periodically to keep the package honest."
---

# Finalize Compliance

Reconcile the automated session log with a submission-grade record. The session-end hook is
deliberately non-destructive: it appends one machine row per session to
`submission/.session_queue.jsonl` and never edits human-authored files. This skill is the bridge
that turns that queue into the three artifacts the contribution record actually grades: a credible human time
log, a filled `workflow.md`, and a real conversation index.

## Why this exists

The old failure mode (do not repeat it): the hook wrote `auto-review` rows with wall-clock
durations straight into `human_time_log.md`, nobody reclassified them, and the log ended up full of
`12h 26m` overnight-gap rows while the running totals read near-zero. The queue + this skill
separate machine capture from the human-authored record so neither corrupts the other.

## When to use

- Preparing the final submission package (run last, after the paper is frozen).
- A periodic checkpoint (e.g. weekly) to keep `workflow.md` and the index from drifting.
- After a stretch of sessions where `/log-human-time` was not run live.

## Inputs to collect

| Input | Required? | Notes |
|---|---|---|
| Authors | Yes | Names that count as human (for the time log). Default to the issuing user. |
| Through-date | No | Only finalize sessions on or before this date. Default: all queued. |
| Active-time policy | No | How to estimate human minutes per session: `transcript` (gap-capped, default), `wallclock`, or `ask`. |

## Workflow

1. **Read the queue.** Parse `submission/.session_queue.jsonl` (one JSON object per session:
   `session_id`, `start_ts`, `end_ts`, `wallclock_min`, `transcript`, `conv_file`, `git_head`).
   Skip sessions already marked `finalized: true`.
2. **Estimate active time, not wall time.** For each session, read its transcript and sum the gaps
   between consecutive turns, capping any single gap at 10 minutes (a longer gap is idle, not work).
   This kills the overnight-gap inflation. If the policy is `ask`, present the wall-clock and the
   gap-capped estimate and let the human pick.
3. **Classify the stage.** Infer the dominant `stage` (`idea`/`literature`/`design`/`data`/
   `analysis`/`robustness`/`writing`/`revision`/`submission-prep`/`meta`) from the transcript: which
   skills ran, which files were written, what the user asked for. Write a one-line `activity` verb
   phrase and the main deliverable path.
4. **Write real human-time rows.** Append one reclassified row per session to the **Sessions** table
   in `submission/human_time_log.md`, in chronological order, attributed to a real author (not
   `auto-review`). Recompute the **Running totals**. Flag any session you could not confidently
   attribute and ask the human to confirm before it counts.
5. **Rewrite the conversation index.** Replace the `(auto) session …` rows in
   `submission/conversations/README.md` with one row per conversation file carrying a real one-line
   **goal** (read it from the transcript's first user turn and the outputs produced).
6. **Fill `submission/workflow.md`.** For each of the eight stages, write the AI work, the human
   work, and the artifacts, drawn from `notes/` (lab notebook, handoff/STATE) and the transcripts.
   Fill the **Direct human contributions** and **Decisions the human made** tables from the pivot and
   build-vs-drop calls recorded in the handoff. Fill the **Notes on autonomy** table for any
   long unattended runs (start, stop, artifacts, transcript).
7. **Mark sessions finalized.** Set `finalized: true` on each processed queue entry (rewrite the
   JSONL) so re-running the skill is idempotent.
8. **Report gaps.** List what still needs a human: unconfirmed durations, sessions with no transcript,
   and any credential that the scrubber may have missed (grep the transcripts for token-shaped
   strings and surface them).

## Outputs

- Updated `submission/human_time_log.md`, `submission/conversations/README.md`,
  `submission/workflow.md`.
- Queue marked finalized.
- A short gaps-and-confirmations list printed to the user.

## Validation

- Never invent human time. If active time cannot be estimated, leave the duration blank and flag it.
- Refuse to write rows dated before the venue's eligibility floor, declared in
  `submission/call_requirements.md`.
- Do not delete the queue; mark entries finalized so the audit trail survives.
- After running, remind the user to run `/contribution-report` and `/verify-citations`, and to scrub
  any flagged credentials.
