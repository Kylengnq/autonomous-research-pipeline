---
name: peer-review
description: "Simulates journal peer review at full rigor: integrity pre-gate (ledger, registry, citations, compile), advocate/skeptic contribution panel, calibrated editor desk review, four blind referees (two opposed dispositions, a replication referee re-deriving every number, and a standing opposition referee attacking methodology, literature, findings, contribution, and whole-paper coherence and logic), verification of referee findings before synthesis, fatal/addressable/taste triage, and a bounded critic-fixer loop. Modes: R&R continuation, hostile-editor stress, decision-distribution variance, and a fast pre-submission light check."
---

# Peer Review

Simulate the editorial pipeline of a target journal, at the rigor the
journal would apply. Author-invoked only. Reads the manuscript and the
project's verification artifacts; writes only to `reviews_dir`; never
edits analysis files.

Reference files (read the ones the run needs):

- `references/journal-profiles.md`: per-journal desk-reject standards,
  identification bar, expected robustness set, format norms, known peeves.
- `references/referee-dispositions.md`: the six dispositions, the
  replication-referee protocol, the opposition-referee protocol.
- `references/review-protocol.md`: finding-verification triage rules, R&R
  ledger format, decision-letter template.

## When to use

- Pre-submission dress rehearsal against the target journal.
- Choosing between target journals (run per profile and compare letters).
- After major revisions, in R&R mode.
- Quick pre-submission sanity pass (`--light`).

## Setup

Read `pipeline-config.md` for `main_tex`, `claim_ledger`, `registry_file`,
`bib_file`, `reviews_dir`, `field_profile`, `model_strong`, `python`,
`decisions_log`. Select the journal profile: the argument names a journal
(e.g. `JFE`); otherwise use the `field_profile` default. All referee and
editor agents run on `model_strong`.

## Pipeline (default mode)

1. **Integrity pre-gate.** Run the machine gates before any referee spends
   tokens: `claim_ledger.py validate` and `cross-ref`, the
   `verify-citations` audit, and a clean compile. Any failure returns a
   desk rejection consisting of the gate report; a paper whose numbers do
   not trace is not reviewable.
2. **Contribution panel.** Two independent agents assess the contribution
   claim against the positioning memo and a live literature probe: an
   advocate building the strongest honest case, a skeptic building the
   strongest honest case against. Both briefs go to the editor; neither
   sees the other.
3. **Editor desk review.** Against the journal profile: scope fit,
   contribution threshold, the mandatory novelty probe (search for papers
   that would kill the contribution), desk-reject standards. Output: desk
   decision (reject with reasons, or proceed) plus referee selection (the
   two dispositions most likely to stress this paper's weak points).
4. **Four blind referees**, each writing a full report to the journal's
   standards, blind to each other, every finding citing a manuscript
   location, the evidence-ladder check embedded (language capped at the
   rung the evidence reaches):
   - **Referee A and Referee B**: opposed dispositions from the six-way
     taxonomy (structural, credibility, measurement, policy, theory,
     skeptic), selected by the editor at step 3.
   - **Replication referee**: re-derives every table and figure number
     from the results JSON and the script registry; checks run order and
     that each results file traces to a registered script. Follows the
     protocol in `references/referee-dispositions.md`.
   - **Opposition referee**: the standing adversary. Briefed to find every
     flaw the paper could contain across methodology, literature use and
     coverage, findings, discussion, contribution, and significance, and
     to walk the paper end-to-end as one argument chain: does the
     introduction promise what the results deliver, do hypotheses follow
     from mechanisms, do results support the discussion, does the
     conclusion outrun the design, do any two sections contradict each
     other. Expected to over-flag; step 5 is the counterweight.
5. **Finding verification.** Referees hallucinate too. Every referee
   finding is a lead: confirm it against the manuscript and the artifacts
   (does the flagged passage exist, does the alleged mismatch hold, does
   the design already answer the objection) before it may enter the
   synthesis. Dismissed flags are logged one line each in the verification
   log so the triage is auditable.
6. **Editorial synthesis.** Verified findings triaged **fatal** (invalid
   inference, broken identification, untraceable numbers), **addressable**
   (fixable with bounded work), or **taste** (reasonable disagreement).
   Decision letter written to the profile's standards: decision, the
   triaged findings, and what a successful revision must do.
7. **Critic-fixer loop.** Apply fixes for addressable findings (routing
   prose to `draft-paper`, analysis gaps to `run-analysis` or
   `robustness-suite`); re-review the changed sections; exit after two
   consecutive clean rounds; hard cap at five rounds. A fatal finding that
   survives the loop escalates to the author with the referee report,
   possibly reopening the design (G3) or survival (G5) gates.

## Modes

- **default**: the pipeline above.
- **--rr N** (N = 2 or 3): revise-and-resubmit continuation. Reload the
  prior round's reports from `reviews_dir`; same referees and
  dispositions; classify each prior concern Resolved / Partial / Not
  addressed (ledger format in `references/review-protocol.md`); new
  findings only where the revision introduced them. Hard cap at round 3.
- **--stress**: hostile editor. All four referees forced to the skeptic
  disposition, the profile's peeves doubled, framing: find the reasons to
  reject. Output is a concern gauntlet, not a decision letter.
- **--variance N**: N dispositioned referees with independently sampled
  dispositions replace Referee A/B; the replication and opposition
  referees stay seated in every draw. The editor aggregates into a
  decision distribution (how many draws reject / major / minor), not a
  point estimate.
- **--light**: fast two-agent pre-submission check only: contribution
  (advocate/skeptic condensed to one adversarial brief) and
  identification/overclaim (causal language vs design, unsupported
  claims). No editor, no loop; a short flag list.

## Escalation

Per `<skills_root>/playbooks/error-escalation.md`: integrity pre-gate
failures are returned, not worked around; the loop caps are hard. A fatal
finding surviving the loop resolves per `gate_mode`: in `human` mode it
goes to the author with the referee report (possibly reopening G3 or G5);
in `autonomous` mode the G6 rule in
`<skills_root>/playbooks/gate-modes.md` applies — the manuscript is
archived as a documented reject with its decision letter, never spun. The
G6 title/overclaim decision after review is resolved the same way
(author sign-off, or the auto-mode rule) and is recorded in
`decisions_log`.

## Outputs

All under `reviews_dir`, dated per round: referee reports, contribution
briefs, verification log (confirmed and dismissed flags), decision letter,
fix log. A dated `lab_notebook` entry with the decision and round count.

## Validation

- The integrity pre-gate ran before any referee.
- Every finding in the decision letter cites a manuscript location and
  survived verification; every dismissed flag is logged.
- The loop terminated by two clean rounds or the cap, never by fiat.
- Nothing outside `reviews_dir` was written; analysis files untouched.
