---
name: run-pipeline
description: "Drives a full pipeline run S0 through S8 from a single instruction: chains the stage skills in order, batches all work between judgment gates into uninterrupted stretches, resolves gates per gate_mode, records a stage cursor so a continuation session resumes mid-run without re-prompting, and keeps a prompt ledger. Ends every run in exactly one state: CHECKPOINT (human gate), PARKED, ARCHIVED (documented reject), or DONE."
---

# Run Pipeline

The conductor. Every stage skill exists and enforces its own gates; what
costs prompts is that nothing chains them. This skill turns one
instruction into an uninterrupted run that stops only where a decision is
genuinely owed: at judgment gates in `human` mode, never in `autonomous`
mode (rules decide, or the run parks).

It is a conductor, not a worker: it never performs stage work, never
restates a stage skill's rules, and never resolves a gate itself. It
invokes skills, routes their outputs, and enforces the stop states.

## When to use

- Starting a paper project from a kickoff instruction (question, topic
  area, or idea-screening output).
- Continuing a run in progress: the stage cursor in `state_file` says
  where to pick up.
- Not for invoking a single stage in isolation; call that skill directly.

## Stage sequence

Read `pipeline-config.md` first (`gate_mode`, `data_mode`, paths,
models). Then, from the cursor position:

| Cursor | Runs | Ends with |
|---|---|---|
| S0 | `resume` | brief; stale/sentinel checks |
| S1 | **themed path** (`theme` set): F-1 `data-profile` in anchored mode -> F0 narrowed to the theme -> `idea-variants` (8-12 variants, 2-3 theme-blind) | variants advance, **no F2 cut** |
| S1 | **swarm path** (no `theme`): F-1 `data-profile` in anchored mode -> F0 literature landscape brief -> F1 swarm pool (100-120, dedup) + F2 `idea-scoring` | 20-25 cut advances |
| S1b (F3) | themed: **pilot every variant first**, then novelty audit + reach sim + **`idea-novelty` contribution judge (step 1.5)** + debate on survivors only, decision audit, comparative final. Swarm: as before, pilots after the debate gate | slate (+ fallthrough tier if empty) + one `research_proposal.md` per presented card + `data_requests.md` → **G1** |
| S2 | literature, positioning memo, `verify-citations` | **G2** |
| S3-S4 | hypotheses; `pre-register` | **G3**, freeze commit |
| S5 | data build; `script-registry` | coverage report → **G4** if a data call arises (always in anchored mode: spine tag + replication plan) |
| S6 | `run-analysis`; `robustness-suite` | verdicts → **G5** |
| S7 | `draft-paper` (+ `claim-ledger`, `verify-citations`, compile) | manuscript behind the triple gate |
| S8 | `peer-review` default; `edmans-audit` | decision letter → **G6** |
| close | `handoff` (+ commit per mode) | STATE with cursor |

S1 and S1b run on the pipeline's own funnel skills (`data-profile` at
F-1 in anchored mode, then `idea-variants` or `idea-swarm`+`idea-scoring`,
then `idea-debate`, `idea-novelty`, `idea-pilot`); S3 still uses the workspace
`hypothesis-development` until a pipeline-native version exists, and the
driver notes that in the run log.

## Path selection at S1

**`theme` in `pipeline-config.md` decides the path, and the driver records
which ran.** A theme is the expected input: the pipeline's contract is
*give it a general theme, get back detailed research designs the data can
carry*.

- **`theme` set — themed path.** F0 narrows to the theme, `idea-variants`
  produces 8-12 deliberate versions of it, and every one is piloted before
  any debate. `idea-scoring` does not run: 8-12 variants give a 100-to-22
  cut nothing to do.
- **`theme` absent — swarm path.** The open-search funnel, unchanged.
  Use it when the project is starting from nothing rather than from a
  question area.

The driver never invents a theme, never narrows a broad one to make the
run easier, and never drops the theme-blind reservation to save agents.
If `theme` is set but empty or a single word with no question area in it,
that is a missing key: stop and ask (human) or PARK (autonomous), per
`playbooks/error-escalation.md`.

**The paths differ in more than which generator runs**, and the driver's
routing must reflect it: on the themed path the pilot is a *universal
screen* that runs before the debate, so the briefing packs for the debate
carry pilot reports. On the swarm path the pilot is a *reward* for
clearing the debate's no-KILL gate and runs after it. Do not mix the two
orderings in one run.

In `data_mode: anchored` the driver runs `data-profile` before F0 and
refuses to enter F1 on a profile older than the manifest's refresh
cadence. Held-data queries belong to the skills that own them: the
driver routes paths and never queries the data itself.

S1b clean-room duties (the driver is the isolation boundary's keeper):
assemble each debater's briefing pack (idea card stripped of F2 scores
and desk-reject verdicts, plus the novelty-audit fact sheet, plus the
F-1 profile extract in anchored mode — never a data-availability memo,
which is the feasibility assessor's own output, and **never step 1.5's
`novelty_verdict.md`**, which is a judgment on the very grounds the advocate and
skeptic are about to argue; the card's `REFRAME` framing note travels, the
verdict does not) and launch each role as
a fresh subagent — never inline in the driver's own context, which has
seen the screen and the state file; hold rebuttals until all round-one
positions are filed; after S1b, pass later-stage skills only `handoff/`
paths, never `quarantine/`; and keep run-log and cursor lines to
verdicts and pointers, never debate substance. The quarantine check
runs at S4 entry and inside S7 per the gate table.

Bench duty: on a downstream kill (killer paper at S2, failed G3 pivot,
fatal S8 finding) the driver re-enters at G1 with the bench of
runners-up (**feasibility and occupancy re-checks first if stale** — a paper
published since the run can close a benched card's question, which is a harder
kill than any sample change), never at S1 from scratch, and logs the turn-back
cost as one gate decision in the run ledger.

## G1 duties: the pick, the empty slate, and the decline

G1 is the one gate that can end in something other than "proceed", and each
outcome needs routing the driver owns.

**Before either branch**, two artifacts are assembled for the checkpoint.

**Research proposals, one per presented card.** `idea-debate` step 4b writes
`<ideas_dir>/<card>/handoff/research_proposal.md` for every card on the slate and
every card in the fallthrough tier — four presented cards means four proposals.
The driver checks each exists and routes it to the checkpoint beside the card's
verdict; it does **not** write them and does not edit them. A proposal is a
rendering of that card's verified `handoff/` artifacts, so authoring one in the
driver's context — which has seen the screen, the state file and every other
card — is exactly the contamination the clean room exists to prevent.

**A single review packet.** Once both artifacts below exist and the slate is
settled, the driver renders `<ideas_dir>/G1_review.pdf` with `review_pdf.py` and
presents that path. G1 is the checkpoint with the most to read — a slate, a
fallthrough tier, a proposal per card, and a data-request list — and it is the
one where handing over seven Markdown paths guarantees that some of them are not
read.

**Data requests.** The driver aggregates every pilot report's
```data_request block into `<ideas_dir>/data_requests.md` —
one section per card, ordered by `status` then by G1 verdict, each carrying the
quantity, why it matters, the candidate sources with route and probe, and the
fallback. It is a G1 output and is presented **with** the slate and with the
fallthrough tier, because a capped card's cheapest clearing action is often one
acquisition on that list. The driver aggregates and never authors: a request
that is not in a pilot report does not enter the file (Material Gap rule).

**On a pick**, the driver writes `ideas/<card>/handoff/g1_acceptance.md` before
any later stage starts — the picked card, every surviving objection with its
disposition (discharged / accepted as a limitation / deferred to S4), every
audit dispute and its resolution, the step 1.5 `REFRAME` note, and the
retrospective-disclosure line. It also moves the novelty verdict's *facts* into
`handoff/novelty_facts.md`, leaving the judgment quarantined. **S2 refuses to
start without the acceptance record**, on the same logic as the
pre-registration commit gate: a decision that lives only in conversation cannot
be audited by the next session. The driver writes the record and never resolves
the dispositions itself — those are the author's, taken at the checkpoint.

**On an empty slate** — no card cleared `g1_threshold` — the
driver does **not** end the run on its own. It states the zero, reports the
DECLINE diagnosis from the run's counters, and then presents `idea-debate`'s
**fallthrough tier** as the third part of one checkpoint, in the order that
skill fixes: count first, diagnosis second, labelled tier third. The run stops
at **CHECKPOINT**. The driver never merges the tiers, never renumbers them into
one ranking, never reports a combined count, and never describes a fallthrough
card as having cleared anything. If `g1_fallthrough: none`, or the fallthrough
tier is also empty, the driver falls through to the decline branch below.

**On a decline** — the author reads the slate, or the fallthrough tier, and
takes none of it — the driver does not re-run anything on its own judgment. It
reads the run's counters, reports which of the three slate diagnoses in
`idea-debate`'s slate-level triage they support (contribution-thin → re-theme;
feasibility-thin → blocked registry plus a data question; execution-thin →
clinic), and presents that as the next decision. The route is the author's call,
logged with `gate-log`, and the run then ends **ARCHIVED**, not PARKED — a
declined slate is finished work with a negative result, and PARKED would tell
the next session that something is still owed.

**If the author takes a fallthrough card forward**, the `handoff/g1_acceptance.md`
the driver writes must state in its own words that the card **did not clear
`g1_threshold`**, name the gate that capped it, and record the author's reason
for proceeding anyway. That line travels with the card through S2-S8 and into
the paper's limitations. A card carried forward on an acceptance record that
omits it is a validation failure, and it is the one way the fallthrough tier
could quietly become the old always-returns-items menu.

Autonomous mode reaches neither branch: it PARKs at G1 by rule, which is
unchanged.

## Review documents are delivered as PDF, never as Markdown

**Author decision.** Every artifact a checkpoint puts in front of the
author for a decision is rendered to PDF, and the checkpoint message gives the
**PDF paths**. The Markdown stays where it is: it is the machine-readable source
the skills read, the ledger traces, and the next session parses. It is not what
the author is asked to read.

The reason is the reading, not the format. A gate document is read once,
carefully, by someone deciding something, and often away from the terminal.
Markdown in a terminal renders a slate's tables as pipes, loses the structure
the document was written to carry, and cannot be annotated or carried out of the
session.

```bash
python3 <tools_dir>/review_pdf.py --packet <out.pdf> --title "<gate>" \
    --subtitle "<project> · decisions owed <date>" <file.md> ...
```

`review_pdf.py` is stdlib-only and compiles with `xelatex`; it needs no pandoc
and no package install. One PDF per file by default, or `--packet` to bind a
gate's whole review set into one document with a cover and a table of contents.

**Bind per gate, one packet, in the order the checkpoint presents them.** The
author reads one document, not seven attachments. Render into the run's own
tree, beside the sources, so the packet is an artifact of the run rather than a
temporary file:

| Gate | Packet | Bound in this order |
|---|---|---|
| G1 | `<ideas_dir>/G1_review.pdf` | slate count and diagnosis, `comparative_final.md`, one `research_proposal.md` per presented card, `data_requests.md`, `novelty_positioning.md` |
| G2 | `<results_dir>/G2_review.pdf` | positioning memo, threat list |
| G3 | `<paper_dir>/../G3_review.pdf` | `prereg_file`, the power/MDE block |
| G4 | `<results_dir>/G4_review.pdf` | coverage report, source and proxy list, spine tag and replication plan |
| G5 | `<results_dir>/G5_review.pdf` | per-finding robustness verdicts, equivalence bounds for any null |
| G6 | `<reviews_dir>/G6_review.pdf` | decision letter, fix log, final audit (the manuscript PDF travels beside it, not inside it) |

Four rules, each a validation failure when broken:

- **The driver renders and never authors.** The packet is a rendering of files
  that already exist; a fact that is in the PDF and in no source file is a
  Material Gap violation, and the fix is at the source, then re-render.
- **The checkpoint message names PDF paths.** Naming the `.md` instead is the
  failure this rule exists to prevent, and it is the easy one to make because
  the driver has just written those paths into the run log.
- **A failed render is reported, never worked around.** If `xelatex` is missing
  or the render fails, say so and hand over the Markdown paths with that
  sentence attached. Silently presenting Markdown as though it were the intended
  delivery is worse than the missing PDF.
- **Re-render after any change to a source file.** A stale packet is a document
  the author is deciding from that no longer matches the record. Render as the
  last act before presenting the checkpoint, not when the first file lands.

The manuscript is already a PDF by S7 and is not re-rendered by this tool.

## Gate handling

- **`gate_mode: human` — batch to checkpoints.** Run everything between
  two gates without stopping, then present one consolidated checkpoint.
  Default bundles: G1+G2 (run S1b for the top candidates, then S2
  provisionally for the top-ranked survivor, and present debate records,
  pilot reports, and positioning together; an author redirect to a
  different idea reopens S2 and costs one extra checkpoint), G4 only
  when a real data call arises (otherwise report sources in the G5
  checkpoint; in anchored mode G4 always runs, because the spine tag
  and replication plan are a decision the author owns), G6 presented
  with the decision letter and the ready archive. Target: a full run in at most 6 author inputs; the ledger
  (below) measures it.
- **`gate_mode: autonomous` — never ask.** Each gate resolves by its rule
  in `<skills_root>/playbooks/gate-modes.md`; the driver's job is only to
  keep going until DONE, PARKED, or ARCHIVED.
- The driver never answers a gate itself in human mode and never weakens
  a stage skill's refusal rule in either mode.

## Author approval advances the run

**A gate is a decision point, not an endpoint.** The moment the author gives a
decision at any of the six gates, the driver applies it and continues into the
next stage. It does not stop, does not ask for a second confirmation, and does
not wait for a fresh session. If the author is at the keyboard, an approval at G1
carries straight into S2, an approval at G3 into S5, and so on to G6 and DONE.

Two things happen before the next stage starts, in this order:

1. **Record the decision** with `gate-log`: the gate, the options considered, the
   choice, and the reason. At G1 also write the acceptance record naming any
   capped card taken forward and why.
2. **Carry it forward as an input.** The decision constrains the next stage
   rather than merely unlocking it:
   - **G1** the picked card and any `REFRAME` note are what S2 positions.
   - **G2** the approved framing and threat list bound S3's hypotheses.
   - **G3** the signed pre-registration is the specification S6 must run; no
     later stage may quietly change it.
   - **G4** the approved proxies and sources scope what S5 collects.
   - **G5** the author's evidence bar decides which findings S7 may write as
     results and which become limitations.
   - **G6** the signed title, abstract and claim strength bound the final text.

**What approval does not do.** It never weakens a machine gate. The author
decides *which* idea, framing, design, sources, findings and claims; the author
does not waive the pre-registration, the synthetic-first check, the claim ledger,
the citation audit, or any other integrity gate. A stage whose machine gate
refuses stays refused after a human approval, and the driver reports it as unrun
rather than passed. This is what keeps a fast run an honest one.

Approval may be partial. "Take card 2 but drop the second mechanism" is a
decision: record it, apply it, and continue. Ask again only where the instruction
is genuinely ambiguous about what the next stage should do.

## Stop states

Every run ends in exactly one:

- **CHECKPOINT** (human mode only): a gate bundle is awaiting the author, and the
  run is paused rather than finished. The checkpoint message lists the decisions
  owed and the default recommendation. On the author's answer the run resumes
  into the next stage under the rule above, in the same session where possible
  and otherwise through `resume` and the stage cursor.
- **PARKED**: a refusal rule fired twice, a rule gap arose in autonomous
  mode, or the escalation ladder exhausted. STATE names the gap.
- **ARCHIVED**: a fatal S8 finding survived the fix loop; the manuscript
  is archived with its decision letter per the G6 rule. An honest end.
- **DONE**: the manuscript survived S8 with no fatal findings, G6 is
  resolved, machine gates all exit 0. The run log records the final
  audit chain.

## Driver discipline

**The driver's own thread is the most expensive thing in a run.** Measured on
a full run with `<tools_dir>/run_cost.py`: **63% of total spend**, against 37%
for all 65 subagents combined. It appears in no subagent count, which is why
early cost discussions never mentioned it. The mechanism is simple: the driver's
context ran a **344K median and 786K maximum**, and every turn re-reads all of it
before doing anything, so a driver request costs something before it does any
work. At that context size, 129 Bash calls in one session is roughly a quarter of
the whole run's cost in round-trips.

Four rules follow. None of them adds machinery; three apply machinery that
already exists on a schedule instead of only at session end.

**1. Split the run at layer boundaries.** Run `handoff` and start the next layer
in a fresh session re-entering via `resume` and the stage cursor — the existing
continuation protocol below, run deliberately rather than only when a session
ends. Boundaries: F0/F1 | pilots | desk + novelty | debate | audit | G1. Also
split when context passes `driver_context_ceiling` (`pipeline-config.md`,
suggested 250K) mid-layer. The cursor and the artifacts are the state; nothing
is lost across a boundary that was not already required to survive one.

**2. Fact-extraction reads go to a subagent; only edit-reads stay.** A read
whose purpose is to *extract a fact* returns the fact from a subagent. A read
whose purpose is to *edit the file* stays on the driver, because an edit needs
the exact bytes. In one measured session 29 `Read` calls put **1.32 MB (~329K
tokens)** into a context that every later request then re-read; an extractor on
the cheapest model costs a fraction of a single driver request. The comparison is
not close, and it gets less close the longer the layer runs.

**3. Batch tool calls.** The twenty pilots run as one registered script emitting
one JSON, not twenty invocations. `script-registry audit`, the peek-log check,
and the quarantine grep run as one pre-flight script. Every avoided round trip
is a full-context read avoided, so batching pays at the *context* rate, not at
the cost of the command.

**4. Hand the audit its bundle.** The decision audit is the most expensive layer
per agent, roughly 56 times the cheapest, *because* each auditor reads a whole
layer, and that batching is what buys its overturns, so **do not cut it**. Cut its redundant
reading instead: give each auditor the pre-built bundle the run already
produces rather than letting each re-grep twenty scripts.

**5. Read the two stopping-rule budget keys.** The `budget` block was for a
long time declared in every config and read by nothing. At each layer
boundary the driver checks two keys and acts:

- `driver_context_ceiling` — when the driver's context passes it, split at the
  **next** layer boundary rather than mid-layer: run `handoff`, write the cursor,
  and re-enter through `resume` in a fresh session. This is rule 1 applied on a
  measurement instead of on judgment.
- `budget.max_wall_clock` — when a stage reaches it, stop and report under rung
  4 of `playbooks/error-escalation.md`: best current artifact, work completed,
  issues unresolved, reason stopped. **Never** report partial work as finished,
  and never skip a machine gate because the budget expired — stop *before* the
  gate and record it as unrun.

Every other `budget` key is a **reported counter**, not a stopping rule, and
`max_subagents` is explicitly retired as a budget key while surviving as a
counter: it would have fired at the debate, which is 62% of the agent count and
12% of the cost, and never touched the driver thread that was 63% of it.

**What is not a rule, and why.** The desk editors and G1 judges run
`model_strong` to produce `panel_reach`, the one output this pipeline states it
cannot calibrate. Whether that judgment survives on `model_mid` is a validity
question, not a cost question, and it is recorded as an open experiment in
the `decisions_log` rather than settled here on price.

## Long work and session breaks

- Long stages (crawls, estimation sweeps) follow the detached-job rules
  in `<skills_root>/playbooks/error-escalation.md`: checkpoint files,
  sentinel paths, absolute paths, progress prints.
- Before any long detached job and at every stop state, the driver runs
  `handoff` so `state_file` carries the **stage cursor** line:
  `pipeline_cursor: <stage> — <what is running or owed> — <sentinel if any>`.
- A continuation session starts with `resume`, reads the cursor, and
  re-enters the sequence at that row. In autonomous mode continuation
  needs no prompt content beyond being started; in human mode "continue"
  is not charged to the gate budget but is counted in the ledger.

## Run log and prompt ledger

Append-only `run_log`: one dated line per stage transition
(stage, skill, outcome, artifact), one line per gate resolution (mode,
decision), and a **prompt ledger**: every human input during the run,
numbered, with one line on what it decided. The ledger is the measurement
for the fewer-than-N-prompts goal and feeds the gated-vs-autonomous
comparison.

**Two cost tables, not one**. At every stop state the driver
runs `python3 <tools_dir>/run_cost.py --session <id>` and pastes its per-layer table
into the run log beside the per-layer **subagent count**. Both stay, because
they answer different questions: the count says how many isolated judgments the
run bought, which is the clean-room question, and the cost says what they cost,
which is the budget question. One run answered only the first and drew a budget
conclusion from it.

The driver adds no interpretation to either table — Material Gap rule — but the
postmortem must **state where the two rank the layers differently**, because
that disagreement is the finding. On one measured run the count ranked the debate first
by a wide margin and the cost ranked it third, behind a layer with a sixth as
many agents and behind the driver thread, which the count cannot see at all.

## Validation

- The driver adds no numbers, citations, or claims of its own anywhere;
  it only routes stage outputs (Material Gap rule).
- Every checkpoint in `human` mode names a PDF that exists on disk and is newer
  than every source file bound into it. A checkpoint naming a `.md` path, or a
  packet older than its sources, fails.
- No gate is ever resolved by the driver in human mode; no prompt is ever
  issued in autonomous mode.
- After every stop state, `state_file` contains the cursor and is
  regenerated by `handoff`, not hand-edited.
- A machine-gate failure inside a stage stops the run at that stage's
  rung of the ladder; the driver never routes around a failing gate.
