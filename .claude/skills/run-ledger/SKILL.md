---
name: run-ledger
description: "Produces the submission-ready run record: per-session runtime and token usage with a labelled cost-equivalent, the human-time reconciliation, a data-file inventory with hashes and producing scripts, and a reproduction document stating exactly which commands rebuild which numbers. Composes log-conversation, log-human-time, finalize-compliance and contribution-report rather than replacing them, then writes the three artifacts none of them produce. Reports by default so it is usable mid-run; --final turns it into a gate that refuses an incomplete package. Run at milestones and before submission."
---

# Run Ledger

The submission package answers "what did the AI do". This skill answers the
three questions it could not: **how long did it take, what did it consume, and
how would someone else reproduce the numbers.**

It aggregates and computes. It authors no fact: every number in its output
traces to the session queue, a transcript, the script registry, or the
filesystem (Material Gap rule).

## What it does not do

It **composes** the existing logging skills rather than replacing them, because
their hook integration and their date guards are load-bearing and tested:

| Already owned by | Do not reimplement |
|---|---|
| `log-conversation`, and the `Stop` hook | transcript capture |
| `log-human-time`, `finalize-compliance` | the human time log and the queue reconciliation |
| `contribution-report` | the human-versus-AI line tally |
| `script-registry` | the per-script manifest and staleness by content hash |
| `paper-build` | the build graph and the `make verify` claim |

This skill calls them, reads their outputs, and writes what none of them does.

## When to use

- A milestone checkpoint, to see what the record is missing while there is still
  time to fix it.
- Before submission, with `--final`, as the gate.
- After a stretch of sessions where the queue was not reconciled.

## Modes

- **Default: report.** Runs any time, prints the readiness table, refuses
  nothing. A project mid-run is incomplete by definition and that is not an
  error.
- **`--final`: gate.** Exits nonzero if any required artifact is absent, stale,
  or unreconciled, and names each one. This is the pre-submission check.

## Workflow

1. **Read `pipeline-config.md`** for `state_file`, `run_log`, `tools_dir`,
   `results_dir`, `registry_file`, `scripts_dirs`, `makefile`.

2. **Reconcile sessions.** Parse `submission/.session_queue.jsonl`. For each
   session: date, `start_ts`/`end_ts`, `wallclock_min`, `git_head`, `conv_file`.
   Cross-check every `conv_file` against `submission/conversations/` on disk.
   **A queue row with no transcript, and a transcript in no queue row, are both
   reported.** They are different defects: the first is a session whose record
   is missing, the second is a session the queue never saw.

   **This reconciliation is circular and cannot close on its own.** Both sides
   are written by the same three hooks, so a session that ran without them
   appears in neither and the check reports clean on an empty record. The hooks
   are registered only when the project is the session's project directory; a
   session started from a parent directory writes nothing and raises nothing.
   So reconcile against the harness as well:

   ```bash
   ls ~/.claude/projects/<project-slug>/*.jsonl        # one per session, ever
   ```

   where `<project-slug>` is the project's absolute path with each run of
   non-alphanumeric characters replaced by a dash. **Report the count of
   transcripts on disk beside the count of queue rows and the count of files in
   `submission/conversations/`.** Three numbers that disagree name a real
   defect; two numbers that agree because both are empty name nothing.
   `submission/preflight.py` performs this check for the current session.

3. **Reconcile subagent conversations.** For each session transcript, count the
   files in `<transcript-dir>/<session-id>/subagents/*.jsonl` and compare
   against `submission/conversations/subagents/<date>_<session8>/*.md`. A
   shortfall means `export_subagents.py` did not run or ran before the last
   agents finished. the contribution record asks for every AI conversation, and on this
   pipeline the subagents are most of them by count, so **report the two totals
   explicitly rather than reporting only that transcripts exist.** Also report
   whether `submission/conversations/raw/` is present and how many sessions it
   covers: the Markdown renderings truncate long tool payloads, so `raw/` is
   what makes the full-text claim true.

4. **Runtime, both measures.** Report wall-clock *and* gap-capped active time
   (consecutive-turn gaps, each capped at 10 minutes), and label which is which.
   Wall clock across an overnight session is not a measure of effort, and a
   record that reports only wall clock inflates the human contribution — the
   failure `finalize-compliance` exists to prevent.

5. **Tokens.** Run `python3 <tools_dir>/run_cost.py --json` over the project's
   sessions. Report **tokens by type — input, output, cache read, cache write —
   as the primary figure**, per session and in total, because they are
   verifiable from the transcripts.

   **The cost-equivalent carries a label, always.** Claude Code plans bill
   against usage limits, so a list-rate dollar figure compares layers against
   each other and **is not an invoice**. It is reported beside the tokens with
   that sentence attached. A submission artifact that presents it as spend is a
   misstatement, and this is the easiest place in the package to make one.

   Deduplicate by assistant message id. A naive sum over usage records
   overstates by roughly 3x, and that is the single trap in the measurement.

6. **Human time.** Read the totals from `submission/human_time_log.md`. Report
   how many queue rows are still `finalized: false`, and how many sessions are
   unattributed. **Never estimate a human duration here** — that is
   `finalize-compliance`'s job and it asks before it writes.

7. **Data-file inventory.** Walk the data directories and the registry's
   declared outputs. Per file: path, bytes, **sha256**, the registered script
   that produced it, and whether it ships with the submission or cannot, with
   the reason. A file on disk that no registered script produces is reported as
   unattributed provenance, which is the same defect
   `crossref_unregistered_output` catches one layer along.

8. **Reproduction document.** Render from `registry_file` and the `makefile`:
   the ordered command sequence, what each step consumes and produces, and the
   `make verify` claim (`distclean all check` — from source alone everything
   rebuilds and every gate still passes).

   **State the boundary plainly.** Data collection sits outside the build graph
   by design, so `make verify` reproduces estimation through PDF and **not** the
   crawls. Name the registered collection scripts separately, with their access
   routes and roughly what they cost in time. A reproduction claim that lets a
   reader infer the crawls are covered is exactly the overclaim the rest of this
   pipeline exists to prevent.

9. **Readiness table.** One row per item the call requires, each naming its
   artifact and a status of `present` / `stale` / `missing` / `unreconciled`.
   Stale means the artifact exists but predates the work it describes — a
   contribution report generated before the last twenty commits is stale, not
   present.

10. **Write** `submission/run_ledger.md` and `submission/reproduction.md`, and
   append a dated `lab_notebook` entry.

11. **In `--final`**, exit nonzero on any row that is not `present`, and print
    the failing rows only.

## Output shape

`submission/run_ledger.md`:

```
## Sessions
| Date | Session | Wall clock | Active (gap-capped) | Tokens in/out/cache | git head | Transcript |

## Totals
sessions, wall-clock hours, active hours, tokens by type,
cost-equivalent (list rates, NOT an invoice)

## Human time
totals by author, from human_time_log.md; unfinalized queue rows; unattributed

## Readiness
| Required item | Artifact | Status |
```

`submission/reproduction.md`:

```
## What make verify covers, and what it does not
## Build sequence          (ordered, from the graph)
## Data collection         (outside the graph — scripts, routes, time)
## Data files              | path | bytes | sha256 | produced by | ships? |
## Environment             (interpreter, pinned packages, seed)
```

## Validation

- Every session in the queue appears in the ledger, and every transcript on disk
  is matched to a session or reported as orphaned.
- **Three session counts are reported, not one**: transcripts under the
  project's harness slug, rows in `.session_queue.jsonl`, and files in
  `submission/conversations/`. Agreement between the last two proves nothing on
  its own — both are written by the same hooks — so the first is what makes the
  check non-circular.
- Subagent conversations on disk are counted against those exported, per
  session, and `raw/` coverage is stated. A package whose transcript record
  covers driver threads only does not meet the call's full-text requirement.
- Token totals reconcile with `run_cost.py --json` for the same session set.
- The cost-equivalent never appears without its not-an-invoice label. Grep the
  rendered artifact for the figure and confirm the label is in the same block.
- Every data-file row's sha256 recomputes from the file on disk.
- Every producing script named exists in `registry_file`.
- `reproduction.md` contains the crawls-outside-`make verify` statement.
- **No human duration is invented.** A session whose active time cannot be
  estimated is listed as unattributed, never filled with wall clock.
- `--final` exits nonzero on an incomplete package. A `--final` that passes on a
  scaffold with no research in it is an inert gate, not a clean one.
