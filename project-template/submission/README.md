# Contribution record

What this directory is for: a defensible account of who did what on a project an
AI agent largely ran. Not a disclosure form for one venue. Several journals and
conferences now ask some version of the same four questions, and a project that
answers them after the fact answers them badly, because the evidence is a
conversation history nobody kept.

The four questions, and the file that answers each:

| Question | File |
|---|---|
| What was the agent asked to do at the start? | `initial_prompt_template.md` |
| Which model, which version, configured how? | `model_config.md` |
| What did the human actually do, and for how long? | `human_time_log.md`, `human_gate_log.md` |
| How much of the output is human and how much is machine? | `contribution_report.md` |

Supporting the four: `conversations/` holds the transcripts, `workflow.md`
narrates the run stage by stage, `data_access.md` records what data was reached
and under what terms, `run_ledger.md` carries runtime and consumption, and
`reproduction.md` states which commands rebuild which numbers.

## How it stays honest

The record is built as the project runs, by hooks in `.claude/hooks/`, not
reconstructed at the end. `HOOKS.md` documents them. Three properties matter:

- **The hooks capture, they do not classify.** A hook writes a raw queue entry.
  Turning that into a human-time row with a stage label is a separate step
  (`/finalize-compliance`), so a mechanical capture can never overstate what a
  person did.
- **Wall-clock is an upper bound, and says so.** A session left open overnight
  reads as hours. The finalize step caps any single gap between turns, which is
  the difference between time at the keyboard and time elapsed.
- **Nothing human-authored is machine-written.** The hooks never edit a file a
  person wrote, so a misfiring hook cannot corrupt the record.

Opt a session out with a `.no-session-logging` file at the project root: useful
for exploratory work that is not part of this project.

## The gate log is the interesting one

`human_gate_log.md` is where the six judgment gates are recorded: what was
decided, which options were on the table, and why. It is the smallest file here
and the one a reader learns the most from, because it is the only place that
shows where human expertise actually entered. An agent that ran unattended
between G1 and G6 produced the paper; the gate log is the record of the
judgment that shaped it.

Write it at the gate, not afterwards. A rationale reconstructed a week later is
a rationalization.
