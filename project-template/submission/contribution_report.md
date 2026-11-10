# Contribution Report

Tally of human versus AI contributions across the project. the contribution record requires
"a report on the fraction of project lines (code, writing, documentation)
contributed by humans versus AI."

**Regenerate with `/contribution-report` against the final repository state
before submitting.** It refuses to run on a dirty tree, so commit first. A report
generated mid-project is a checkpoint and must say so on its face.

## Headline numbers

| Category | Human | AI | Total | Human share |
|---|---|---|---|---|
| Code lines (non-blank) | | | | |
| Writing words (paper body) | | | | |
| Documentation lines (non-blank) | | | | |

Date generated: (YYYY-MM-DD) — (final / checkpoint)

## How to read this number

A near-zero human *line* share is the expected pattern for a generative-AI
workflow and is **not** the figure the call treats as the quality signal. The
call asks for the highest research quality per unit of human expertise and
effort, not for a minimal human share. Where the human contribution actually
sits — the question, the pivots, the rejected directions, the judgment calls at
each gate — is recorded as time in `human_time_log.md`, as decisions in
`human_gate_log.md`, and in the workflow narrative, not as authored lines.

State that plainly here rather than letting a reader infer that a 0% human share
means an absent human.

## Scope

Counts cover project deliverables authored during the investigation (begun
YYYY-MM-DD):

- **Code**: (paths and file counts)
- **Writing**: the body of the manuscript between `\begin{document}` and
  `\bibliography`, LaTeX macros stripped
- **Documentation**: (paths)

Excluded from the tally, and why:

- **Conversation transcripts** (`submission/conversations/`). Auto-generated
  logs of AI sessions, not project deliverables; 100% process output. Report the
  line count for completeness but do not count them as authored lines.
- (anything else excluded, with the reason)

## Method

State which attribution method was used and why, because the two disagree:

- **Commit-author attribution** (`git blame`) cannot distinguish AI from human
  work when every commit is authored under one human git identity.
- **Conversation-log attribution** cross-references authored files against the
  transcripts that produced them.

## Edge cases

| Case | How it was counted |
|---|---|
| Human pasted AI-drafted text into a file | |
| AI edited a human-written passage | |
| Human hand-corrected an AI-generated number | |
| Code generated, then substantially rewritten by hand | |
