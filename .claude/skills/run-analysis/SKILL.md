---
name: run-analysis
description: "Runs an empirical estimation (event study, DiD, IV/2SLS, cross-section) behind two machine gates: a committed pre-registration and a synthetic-first check that recovers a planted effect and reproduces a hand-derived reference value. The estimand is derived twice by hand before any estimation package runs, and the package is then tested against that reference rather than trusted as the authority. Writes keyed results JSON and figures that draft-paper splices."
---

# Run Analysis

Execute an empirical specification so the result is trustworthy before it
is interpreted. A regression you cannot first make lie on purpose is a
regression you cannot trust when it tells the truth.

## When to use

- Estimating the headline specification (event study, DiD, IV/2SLS,
  cross-section).
- Adding a new outcome or treatment to an existing design.
- Any result that will appear in a table in the paper.

## Principles

- **Freeze first.** No estimation without the committed pre-registration.
- **Synthetic before real.** Ship a synthetic data generator with a planted
  effect and confirm the estimator recovers it (sign, rough magnitude,
  coverage) before real data.
- **Manual-first reference, then the package.** The estimand is a
  mathematical object stated in the pre-registration, and the reference
  value for it is derived by hand — means, merges, and arithmetic only, no
  estimation package — on the locked case. Two independent implementations
  must agree to floating-point tolerance before the value is registered as
  the reference. Only then is the package call run, and it is run *against*
  that reference: `linearmodels`, `did::att_gt`, `plm::pgmm` and their
  equivalents are the thing under test, not the authority. Cross-checking one
  package against another cannot see the failure that matters, because
  packages disagree about the estimand and not only about the arithmetic —
  `aggte(type="simple")` aggregates cohort-time effects with group-size
  weights, so it answers a different question from a uniformly weighted ATT
  and answers it without erroring. A disagreement beyond tolerance stops the
  stage (ladder step 3 in `<skills_root>/playbooks/error-escalation.md`) and
  is resolved by naming the convention that differs — aggregation weights,
  instrument set, degrees-of-freedom rule — never by preferring the package
  number. This is the counting gate's two-independent-derivations rule
  (`idea-pilot`) pointed at estimands rather than at counts.
- **Seeded randomness.** Every stochastic step (synthetic generation,
  bootstrap, permutation and placebo-start draws, any sampling) takes the
  seed frozen in block 9 of the pre-registration, passed in as
  `--seed <seed>` and recorded in the results JSON as `meta.seed`. A seed
  hardcoded inside the script is not reproducible from the build graph, and
  an unseeded bootstrap makes a re-run that moves the interval
  indistinguishable from one that was re-rolled until it cleared zero.
- **Pre-trends before post.** Inspect pre-period coefficients first; report
  the event-study path, not just the static point. First-difference when
  levels show pre-trends.
- **Numerical hygiene.** Cast boolean co-occurrence matrices to float
  before matmul; drop zero-variance regressors and use `pinv` on singular
  X'X; silence spurious macOS Accelerate matmul warnings with
  `np.seterr(...)`. Estimation windows must fail loudly when truncated or
  empty: `lstsq` on an empty system silently returns a zero solution (a
  (0, 0) market model turns "abnormal" returns into raw returns), so
  assert the realized window length meets the specified minimum before
  fitting. Small-N confidence intervals use t(n-1) critical values, never
  1.96.
- **Coverage per analysis window, not per file.** Size the data download
  from every pre-registered event date — placebos included — and check
  coverage for each estimation window separately. A file-level "100%
  coverage" report can hide a placebo window that starts before the data
  does.
- **Dependence rule for clustered event dates.** When event dates cluster
  (a thematic portfolio, a single common shock), the cross-sectional t is
  not a valid test: primary inference is the calendar-time portfolio SE
  (or an equivalent dependence-valid method), and a placebo-start
  distribution (empirical size at nominal 5%) is a required diagnostic,
  not an optional one. Both are a few lines of code.

## Workflow

0. **Freeze check.** Read `pipeline-config.md` for `prereg_file` and `seed`.
   Confirm the freeze exists, is committed (`git log -- <prereg_file>` shows
   a commit), and the specification about to run matches it or a dated
   amendment. Confirm the config `seed` matches the frozen block 9. Missing
   or mismatched: stop and name the gate.
1. **State the specification** in one paragraph: unit, treatment, timing,
   outcome, fixed effects, clustering, and the null that could be rejected.
2. **Synthetic test.** Generate data with a known planted effect; run the
   estimator; confirm recovery. Fail loudly if it does not.
3. **Manual-first reference.** In order:
   1. Write the estimand as a formula, copied from the pre-registration's
      block 2 (which states the aggregation weighting explicitly).
   2. Implement it on the locked toy real-shaped case with means, merges,
      and arithmetic only. No estimation package, no aggregator helper.
   3. Implement it a second time by an independent route — count the pairs
      and count the units and multiply through, rather than running the same
      expression twice — and confirm the two agree to floating-point
      tolerance. A disagreement blocks the stage; it is not resolved by
      picking one.
   4. Record the agreed value in the results JSON `meta.reference` block
      with the formula, the two expressions, and the locked case's seed.
   5. Run the package call and test it against `meta.reference`. Agreement
      within tolerance documents that call as canonical for this estimand.
      Disagreement is reported with the convention that explains it named,
      and the package call is not used until a call that reproduces the
      reference is found.
4. **Run real.** Confirm per-window data coverage for every registered
   event date first; then estimate on the panel and produce the
   event-study path and the static estimate with dependence-valid
   standard errors (calendar-time SEs when event dates cluster) plus the
   empirical-size diagnostic.
5. **Write machine-readable results** to `<results_dir>/<design>_results.json`:
   coefficients, SEs, t-stats, N, CIs, keyed so `draft-paper` and
   `claim_macros.py` read them without retyping, plus a `meta` block holding
   the seed and the input paths; figures as PDF (vector) or PNG. Register
   the script's rule in the build graph (`paper-build`) so the results file
   rebuilds from its inputs.
6. **Record** in `lab_notebook`: the numbers, the synthetic-recovery and
   library-verification outcomes, and a one-line verdict (clean /
   confounded / underpowered).

## Outputs

- Estimation script under a registered scripts dir (register it via
  `script-registry`).
- Results JSON and figures under `results_dir`.
- A dated `lab_notebook` entry with the headline numbers.

## Validation

- No real-data result is reported until the freeze check, the synthetic
  recovery, and the manual-first reference check all pass.
- No package output is reported as the estimand until it has reproduced a
  hand-derived reference on the locked case. `meta.reference` carries the
  formula, both derivation expressions, and the agreed value; a results JSON
  without it is incomplete. A package call that disagrees with the reference
  is recorded with the differing convention named and is not the reported
  number.
- No estimation window runs truncated: window-length assertions are in
  the script, and coverage is verified per registered event date.
- Every stochastic step took the frozen seed as an argument, and the results
  JSON records it. Re-running the script reproduces the numbers exactly.
- Clustered event dates never headline a cross-sectional t; the
  calendar-time (or equivalent) estimate is the primary inference and the
  empirical-size diagnostic is reported.
- A result with dirty pre-trends is labeled not-causal, never headline.
- A null goes to `robustness-suite` for equivalence/MDE bounds before being
  called precise.
