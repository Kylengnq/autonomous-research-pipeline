---
name: edmans-audit
description: "Audits inference quality and spin after review, before sign-off: each load-bearing claim placed on the evidence ladder (statement, fact, representative data, causal proof) with language capped at its rung; importance, displacement, spin, and falsification path checked over the abstract and intro."
disable-model-invocation: true
---

# Edmans Audit

Audit the paper's reasoning, not its arithmetic. `claim-ledger` confirms
each number traces to a results file; this skill checks that the claims
built on those numbers are warranted and unsold. It operationalizes Alex
Edmans' evidence-ladder framework for an empirical manuscript. Runs after
the peer-review loop and before gate G6.

## When to use

- After `peer-review` converges, before the author's title/overclaim
  sign-off (G6).
- Any time the abstract or introduction is rewritten; overclaim creeps in
  there first.

## The evidence ladder (the core check)

For every load-bearing claim, ask which rung the evidence reaches and flag
any claim stated a rung higher:

1. **Statement**: an assertion or narrative. Not yet evidence.
2. **Fact**: a specific true observation. Flag a fact generalized to a
   population without representative data.
3. **Data**: representative measurement across the relevant sample. Data
   shows association; flag a correlation described in causal language.
4. **Proof (causal)**: a credible counterfactual supports the causal
   claim. Only here may causal language be used, and only within the
   design's scope.

## The other dimensions

- **Importance.** One sentence on why the question matters to a
  top-journal reader; if the paper cannot say it, that is a framing
  problem.
- **Displacement.** The paper names what it displaces; cross-check the
  threat list from the positioning memo. A contribution that displaces
  nothing is a fact, not a paper.
- **No spin.** Abstract and intro match the evidence: nulls reported as
  nulls, exploratory results labeled, magnitudes not rounded up,
  `references/banned-words.md` honored.
- **Falsification path.** The paper states what evidence would have
  overturned its claim (the pre-registered null, the failed-robustness
  disclosure). No falsification path means confirmation-bias risk.

## Workflow

1. Read `pipeline-config.md` for `claim_ledger`, `main_tex`,
   `reviews_dir`, `decisions_log`.
2. Pull the load-bearing claims from `claim_ledger` plus the abstract and
   the introduction's headline sentences.
3. For each claim, record the rung the evidence reaches and the rung the
   language asserts; flag every gap.
4. Run the four other dimensions over the abstract and intro. When the
   config names a target journal, calibrate the importance and no-spin
   checks against that journal's file in the workspace
   `references/journal-standards/` (desk criteria, magnitude-anchoring
   norms, abstract cap) and the shared
   `references/journal-standards/quality-checklist.md` sections 1 and 5;
   without a target journal, apply the shared norms alone.
5. Optional adversarial pass: hand the claims to a fresh sub-agent briefed
   to attack every inference. Triage its flags (leads, not verdicts):
   confirm each against the evidence before it changes the paper; log
   dismissed flags in one line each.
6. Write the audit to `<reviews_dir>/edmans_audit.md`: one row per issue
   with location, problem, and a concrete fix. Hand flagged claims back to
   `draft-paper`; re-run until clean.
7. Resolve **gate G6** per `gate_mode` in `pipeline-config.md`. `human`:
   present the clean audit to the author for title/overclaim sign-off.
   `autonomous`: apply the G6 rule in
   `<skills_root>/playbooks/gate-modes.md` — the title and abstract must
   pass with zero rung violations, claim strength is capped at the
   audit's assessed rung, and the audit's wording is adopted as-is.
   Record the decision in `decisions_log` (`auto-mode` marker when
   autonomous). Dated `lab_notebook` entry.

## Outputs

- `<reviews_dir>/edmans_audit.md` (issues, fixes, dismissed-flag log).
- A G6 entry in `decisions_log`; a dated `lab_notebook` entry.

## Validation

- Every causal sentence is backed by rung-4 evidence or rewritten to
  associational language.
- The abstract states importance, contribution, and magnitude without
  overclaim.
- The paper states what would have changed its conclusion.
- Pairs with `claim-ledger` (numbers) and `verify-citations` (sources);
  all three pass before submission.
