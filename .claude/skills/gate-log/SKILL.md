---
name: gate-log
description: "Record a human-gate decision in submission/human_gate_log.md using a fixed schema (gate, decision, options considered, choice, rationale). Run whenever the author makes one of the six pipeline gate decisions (idea, framing, design/pivot, data calls, what-survives, title/overclaim). This log is both the reliability lever and the documentation exhibit documenting the nature of human labor."
---

# Gate Log

Capture the decisions only the author can make, in one auditable place. Holding the model fixed, a
decision architecture of explicit human gates cut research-failure rates from 72% to 16% (Zhu et al.
2026); separately, this log is the single most direct answer to the reviewers' question about
"the nature of human labor embodied in each paper." The two purposes coincide: the gates that make
the research reliable are exactly the human contribution the call asks you to document.

## The six gates

| Gate | Stage | The decision |
|---|---|---|
| `idea` | 1 | which idea to pursue (taste) |
| `framing` | 2 | the positioning and the closest-paper contrast |
| `design` | 3 | pivot / kill / approve the design; sign the pre-registration |
| `data` | 4 | proxy and source calls (e.g. a sample-construction proxy) |
| `survival` | 6 | which findings survive robustness and at what evidence bar |
| `title` | 7 | title and any overclaim sign-off |

## When to use

- Immediately after the author makes any gate decision, while the rationale is fresh.
- During `/finalize-compliance`, to back-fill gate rows from the transcripts and handoff if live
  logging was missed.

## Entry schema (fixed)

Append one block to `submission/human_gate_log.md`:

```
### <YYYY-MM-DD> · <gate> · <one-line title>
- Decision: <pivot | approve | kill | choose X | ...>
- Options considered: <the alternatives that were on the table>
- Choice + why: <the option taken and the reasoning, including what evidence or taste drove it>
- Made by: <author name>
- Read from: <the gate's review packet, e.g. ideas/G1_review.pdf>
- Carried into: <the next stage, and what the decision constrains there>
- Links: <preregistration.md freeze / results JSON / conversation file, as relevant>
```

The "options considered" line matters: a gate where only one option existed is not a real decision.

**"Read from" names the PDF the author actually read**, which
is what every gate is presented as. It is not decoration: a discussant assessing
the nature of the human labour is asking what was in front of the person when
they decided, and a decision record that points at a directory of Markdown the
author never opened answers a different question. Name the packet, not the
sources bound into it; the packet's own cover lists those.

## Workflow

1. Identify which of the six gates this is.
2. Append a block using the schema above. Be specific about the alternatives and the reasoning, not
   just the outcome.
3. For the `design` gate, link the `submission/preregistration.md` freeze; for `survival`, link the
   robustness verdicts; for `title`, note the alternatives considered.
4. Fill **Read from** with the gate's review packet. If the author decided from
   something other than the packet, say which file and why, rather than naming
   the packet because it exists.
5. Optionally note the decision in `notes/lab_notebook.md` if it is a milestone.

## Outputs

- Updated `submission/human_gate_log.md`.

## Validation

- Every block names the alternatives that were considered, not only the choice.
- Every block's **Read from** names a file that exists and is a PDF. A `.md`
  path here means the gate was presented in the wrong format, which is a defect
  in the checkpoint rather than in this log, and is worth fixing upstream.
- The `design` gate block exists before `/run-analysis` runs (the spec was frozen and signed).
- At submission, the log should contain at least the gates that actually occurred; pivots and kills
  are the most valuable entries, not omissions.
