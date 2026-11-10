---
name: pre-register
description: "Freezes the empirical specification before any estimate runs: hypotheses, primary spec, sample, decision rule, the null statement, pre-specified robustness, and a power/MDE block gated by an MDE<=bound refusal rule, committed so git timestamps the freeze. Labels retrospective registrations explicitly. Design gate G3; run-analysis refuses to run without it."
---

# Pre-register

Pre-commit the analysis plan before seeing results. Freezing the
specification blocks the post-hoc reframing through which AI pipelines
amplify publication bias; the artifact is one committed markdown file whose
git history is the tamper-evident timestamp.

## When to use

- After hypothesis development, before any estimation (stage S4, gate G3).
- Whenever a new primary outcome or treatment is introduced.
- Re-freezing after a design pivot: add a new dated block; never overwrite
  the old freeze.

## The freeze blocks

Write `prereg_file` (path from `pipeline-config.md`) with, for the primary
analysis:

1. **Question and directional hypotheses** (H1, H2, ...), each with its
   expected sign and the mechanism behind it.
2. **Primary specification**: unit, treatment definition, timing, outcome
   and its transform, fixed effects, controls, clustering, and — for any
   multi-period, staggered, or event-time design — **the aggregation
   weighting, written as a formula**. Naming the estimator is not enough:
   the same estimator aggregated by group size and aggregated uniformly are
   two different estimands, every package picks one by default, and the
   choice is invisible in the output. Left unfrozen it is made after the
   freeze by whichever package call `run-analysis` reaches for, which is
   exactly the post-hoc latitude the freeze exists to close. The formula
   written here is what `run-analysis` derives by hand as its
   `meta.reference` before any package runs.
3. **Sample**: universe, coverage target, inclusion/exclusion rules, time
   window.
4. **Decision rule**: what estimate and CI would count as support, what
   counts as a null, and the equivalence bound below which a null is
   "precise" rather than underpowered.
5. **The null statement**: the sentence that will be reported if the result
   is flat. Writing it now is the point.
6. **Pre-specified robustness**: the confound controls and placebos that
   run regardless of the result, so survival is not cherry-picked.
7. **Exploratory label**: anything not pre-committed is exploratory in the
   paper, not dressed as confirmatory.
8. **Power/MDE (required when block 4 sets an equivalence bound)**:
   expected effect size, minimum detectable effect at the planned sample,
   and an explicit underpowered-by-design warning if MDE exceeds the
   plausible effect. **Refusal rule:** if the ex-ante MDE exceeds the
   equivalence bound in block 4, refuse to present for G3 — the
   "underpowered null" verdict would be preordained at the freeze. Either
   the bound loosens, the sample grows, or the design changes; the skill
   does not freeze a spec whose headline is already decided.
   For any event that predates the freeze, block 8 may not cite realized
   behavior of the sample (observed repricing, observed returns, observed
   anything): plausible-effect ranges must come from prior literature or
   pre-event data only.
9. **Seed**: the integer seed every stochastic step runs under (bootstrap,
   permutation and placebo draws, simulation, any sampling or train/test
   split), frozen here so a resampled p-value is a fact about the design
   rather than about the draw. Pre-committing it also blocks the quietest
   form of specification search: rerunning a bootstrap until the interval
   clears zero. One project-level seed unless a step needs its own, in
   which case name the step and its seed. Mirror it as `seed` in
   `pipeline-config.md`, where the build graph reads it.

## Retrospective registration

When the event under study predates the freeze (the usual case for event
studies of past shocks), the registration is retrospective and must say
so: the artifact header carries an explicit **"Retrospective
registration"** label stating the event date and the freeze date.
`draft-paper` must carry this label into the title footnote or the
introduction — a reader may never mistake a retrospective freeze for a
prospective one. The outcome-blindness rule in block 8 (no realized-sample
references) is what makes a retrospective freeze worth anything.

## Workflow

1. Read the hypotheses from the hypothesis-development output and the
   design notes.
2. Fill `prereg_file`, all nine blocks, no placeholder left blank.
3. Resolve **gate G3** per `gate_mode` in `pipeline-config.md`. `human`:
   present to the author (pivot / kill / approve). `autonomous`: apply
   the G3 rule in `<skills_root>/playbooks/gate-modes.md` — auto-approve
   only when every refusal rule passes; a refusal allows one redesign
   loop, then PARK; refusal rules are never weakened to pass. In
   autonomous mode block 3 must also carry the ranked, liveness-probed
   source list the G4 rule consumes. Record the decision in
   `decisions_log` (date, gate, options considered, choice, rationale;
   `auto-mode` marker when autonomous).
4. On approval, commit (in `human` mode via the author activating
   `commit-session`, in `autonomous` mode directly, message
   "pre-register <outcome> spec") so the hash timestamps the freeze.
   `run-analysis` checks for this commit before running.
5. A later design change adds a new dated block; the diff is the audit
   trail. Post-freeze deviations without a dated amendment escalate per
   `<skills_root>/playbooks/error-escalation.md`.

## Outputs

- `prereg_file`, approved (author or auto-mode rule) and committed.
- A G3 entry in `decisions_log`; a dated `lab_notebook` entry.

## Validation

- Refuse to present for approval while the primary outcome, the decision
  rule, the null statement, or (when any step is stochastic) the seed is
  blank.
- Refuse to present for approval while a multi-period, staggered, or
  event-time design carries no aggregation-weighting formula in block 2.
  A package name is not a formula.
- Refuse to present for approval while block 8's MDE exceeds block 4's
  equivalence bound.
- For a past event: block 8 cites no realized behavior of the sample, and
  the artifact header carries the "Retrospective registration" label.
- Prior freezes stay visible in the file and in git history.
