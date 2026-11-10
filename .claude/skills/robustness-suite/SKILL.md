---
name: robustness-suite
description: "Runs a finding through a fixed gauntlet before it enters the paper: pre-trends and placebos, setting-specific confounds, equivalence/MDE bounds for nulls, alternative codings, subsample uniformity, selection-vs-causation, plus an optional adversarial break attempt. Verdict per finding: robust, confounded, or underpowered."
---

# Robustness Suite

Subject every candidate finding to the same gauntlet so the paper reports
what survives, not what first looked significant. The verdicts feed the
survival gate (G5) and the discussion section writes itself from them.

## When to use

- A `run-analysis` result is about to enter a table or the abstract.
- The author or a referee asks how robust a finding is.
- Triaging which finding is the headline and which are honest non-results.

## The checklist (run all that apply; record pass/fail for each)

1. **Pre-trend / placebo.** Event-study pre-coefficients flat? A pre-period
   placebo shock null? A significant pre-trend downgrades the finding to
   not-causal regardless of the post estimate.
2. **Setting-specific confounds.** Name the era, composition, and exposure
   confounds for this setting and re-estimate dropping or controlling
   each. Worked example: COVID years (2020-21) and tech-industry
   composition sank a headline layoff result in a prior project; every
   setting has its equivalents. A finding that dies under a confound
   control is a composition artifact.
3. **Equivalence / MDE bounds (for nulls).** A null is only precise if the
   equivalence interval rules out economically meaningful effects. Report
   the 90% CI and the minimum detectable effect; an underpowered null is
   inconclusive, not a result.
4. **Alternative treatments and outcomes.** Swap the treatment definition
   and the outcome transform (levels vs first-difference, log vs log1p).
   A finding that only appears under one arbitrary coding is fragile.
4b. **Aggregation convention** (any multi-period, staggered, or event-time
   design). Report which aggregation the headline estimate uses, and
   re-derive it under the alternative weighting. The default is rarely
   neutral: `aggte(type="simple")` weights cohort-time effects by group
   size, `csdid`'s and `did2s`'s defaults differ again, and the uniform
   average over supported cells is a third number. All of them run without
   erroring. An estimate that moves materially between conventions is a
   reported design choice belonging in the specification section, not a
   robustness pass; the pre-registered weighting is the headline and the
   alternative is the check. Where `run-analysis` registered a
   `meta.reference` for the estimand, this check re-uses it rather than
   deriving a second one.
5. **Subsample uniformity.** Re-run across sector, size, and exposure
   subsamples. A uniform null is stronger; an effect loading on one
   subsample belongs to that subsample, not the full panel.
6. **Selection vs causation.** Where a naive correlation exists, show
   whether the predetermined-exposure design purges it. The contrast
   (dirty correlation to clean zero) is often the real contribution.

## Workflow

1. Read `pipeline-config.md` for `results_dir`, `decisions_log`.
2. List the candidate findings and the checks that apply to each.
3. Run each check by re-using the `run-analysis` estimator with modified
   samples and controls; record the spec and the number for every check.
4. Assign each finding a verdict: **robust**, **confounded** (name the
   confound), or **underpowered** (give the bound).
5. Write the robustness table and a one-paragraph verdict per finding to
   `results_dir`, plus the through-line for the paper (the clean result,
   the honest non-results).
6. Resolve **gate G5** (what survives, at what evidence bar) per
   `gate_mode` in `pipeline-config.md`. `human`: present the verdicts to
   the author. `autonomous`: apply the G5 rule in
   `<skills_root>/playbooks/gate-modes.md` — verdicts adopt mechanically,
   the headline is what passes the most checks, confounded and
   underpowered findings never headline, and a clean nothing means the
   pre-registered null statement is the paper. Record the decision in
   `decisions_log` (`auto-mode` marker when autonomous).
7. Dated `lab_notebook` entry with the verdicts.

## Optional: adversarial break attempt

For a headline finding, hand the spec and result to a fresh sub-agent
briefed only to propose a confound, coding choice, or subsample that would
overturn it. The adversary is an erratic genius: each proposed break is a
lead, not a verdict. Confirm the break by running it through the estimator
before downgrading the finding; a proposed confound the design already
purges is a false positive, not a failed check.

## Outputs

- A robustness script (registered) and a results table under
  `results_dir`.
- Per-finding verdict blocks that `draft-paper` turns into the robustness
  subsection.
- A G5 entry in `decisions_log`; a dated `lab_notebook` entry.

## Validation

- No finding with dirty pre-trends or a failed confound control is
  described as causal.
- Power is stated explicitly for every null.
- The headline is the finding that passes the most checks, not the largest
  t-stat.
