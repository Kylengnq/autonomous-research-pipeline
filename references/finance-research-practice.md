# Finance research practice

The field norms an agent must follow to produce credible, top-journal (JF / JFE / RFS) empirical
finance research. This is the domain counterpart to [skill-authoring-guide.md](skill-authoring-guide.md):
that one says how to build skills; this one says what good finance research *is*, so the skills and
the agent default to field best practice. Prose-style rules here; sentence-level writing mechanics
live in [writing-norms.md](writing-norms.md) and [banned-words.md](banned-words.md).

## 1. Identification and research design (the credibility revolution)

Finance has internalized the credibility revolution: a result is judged first on identification, not
on the size of the t-statistic.

- **Lead with a clean source of variation.** A natural experiment, a shock, a discontinuity, or a
  predetermined instrument beats a kitchen-sink regression. Name the source of identifying variation
  in one sentence.
- **Predetermined treatment over realized choice.** A treatment built from pre-period characteristics
  (e.g. occupation-mix exposure) purges the selection that contaminates a realized-adoption
  regression. Showing the naive correlation collapse to zero under the predetermined design is often
  the contribution, not a nuisance.
- **Inspect pre-trends before reading the post.** Event-study pre-coefficients must be flat; a
  significant pre-trend means the design is not clean, and the result is labeled not-causal
  regardless of the headline estimate. First-difference when levels carry trends.
- **Control the obvious confounds explicitly:** COVID years, industry/factor composition, size. A
  finding that dies under a COVID-year drop is a composition artifact, not a finding.
- **Nulls need equivalence bounds.** A null result is publishable and valuable, but only if it is
  *precise*: report the 90% CI and the minimum detectable effect, and state the economically
  meaningful effect the interval rules out. An underpowered null is inconclusive, not a result.

## 2. Statistical discipline (multiple testing, replication, pre-commitment)

The field has lived through a replication reckoning; an AI workflow must not reintroduce the failures
it corrected.

- **Multiple testing is the default suspicion.** With hundreds of candidate predictors, conventional
  thresholds over-reject. Treat t > 2 as weak; the literature argues new factors should clear a
  higher bar (Harvey, Liu and Zhu 2016, "...and the Cross-Section of Expected Returns," RFS;
  Harvey 2017 JF Presidential Address, "The Scientific Outlook in Financial Economics"). Report how
  many specifications were tried.
- **Out-of-sample and replication.** Anomalies shrink out of sample and many do not replicate
  (Jensen, Kelly and Pedersen 2023, "Is There a Replication Crisis in Finance?", JF). Prefer designs
  that hold up out of sample or across subsamples; report subsample uniformity.
- **Pre-commit the specification.** Write the hypotheses, the primary spec, and the null *before*
  seeing results (`/pre-register` -> `submission/preregistration.md`, committed). This blocks HARKing
  (hypothesizing after results) and the post-hoc reframing through which AI pipelines amplify
  publication bias. Anything not pre-committed is labeled exploratory in the paper.
- **Two to three significant digits.** Report the precision the data support, not whatever the
  program prints.

## 3. Contribution and positioning

- **One central contribution, stated in a paragraph.** If you cannot write the single novel
  contribution concretely in one paragraph, the paper is not ready (Cochrane, "Writing Tips for
  Ph.D. Students").
- **Name the displacement target.** State which prior paper or belief the result displaces or
  overturns. A contribution that displaces nothing is a fact, not a paper. (Enforced by
  `finance-idea-screening`.)
- **Benchmark against the frontier, not against a strawman.** Position against the closest recent
  JF/JFE/RFS work, using the calibration anchor (`references/top_journal_calibration.json`); do not
  let the agent self-grade novelty, which it does over-optimistically.
- **Cite to support claims, not to name-drop.** Synthesize the literature by theme.

## 4. Writing (the punchline-first empirical paper)

Economists are writers; expect to spend a large share of effort on writing (Cochrane).

- **Open with the contribution, not throat-clearing.** No "Financial economists have long wondered."
  The first sentences state what the paper finds. Use the `empirical-intro` spine: dated anchor ->
  "in this paper we ..." -> identification tension -> design -> headline magnitude ->
  First/Second/Third contributions -> one-line roadmap.
- **Active voice; concrete nouns.** "We construct," not "the data were constructed."
- **Figures earn their space.** A good event-study figure communicates the identification better than
  a table; bad figures waste space.
- **Tables come from results files, not from memory.** Every printed number traces to a results JSON
  via the claim ledger (`/claim-ledger`); a number with no source does not appear.
- **No overclaim.** Honor `banned-words.md`: no "novel," "groundbreaking," no filler intensifiers, no
  em dashes. Flag title/abstract overclaim for author sign-off.

## 5. Data, reproducibility, and submission practice

- **Public, free, reproducible data (the venue requirement and good practice).** Prefer SEC EDGAR, OEWS,
  FRED, CRSP/Compustat where licensed, Ken French. A proprietary dataset is a validation benchmark,
  not a primary spine, because reviewers cannot re-collect it. State the retrieval path for every
  source.
- **Code-and-data availability.** Top journals (JF, JFE, RFS) and the AEA require a replication
  package. Build the pipeline to be re-runnable (`/data-pipeline`), with coverage and known parse
  failures reported honestly.
- **The claim ledger as an integrity gate.** Before submission, every load-bearing number passes
  `scripts/claim_ledger.py validate` with a mechanism check, so claim drift and wrong-mechanism
  claims are caught.
- **Document the human contribution.** For an AI-assisted submission, the gate log, time log, and
  workflow narrative are first-class deliverables (`/finalize-compliance`, `/gate-log`).

## 6. Honesty norms (non-negotiable)

- Report nulls as nulls; do not dress a null as a different finding.
- Label exploratory analysis as exploratory.
- Disclose the thinnest leg of the evidence and the failed robustness checks (the WARN-layoff
  COVID-control failure is the model: it stays in the paper as an explicit non-result).
- State power for every null; state the confounds controlled for every estimate.

## How this maps to the skills

| Norm | Enforced/served by |
|---|---|
| Identification, pre-trends, confounds | `run-analysis`, `robustness-suite` |
| Equivalence bounds for nulls | `robustness-suite` |
| Multiple-testing / pre-commitment | `pre-register` |
| Displacement target, frontier benchmarking, novelty cap | `finance-idea-screening`, `calibrate-rubric` |
| Punchline-first intro, theme synthesis | `empirical-intro`, `literature-review` |
| Numbers trace to source; integrity gate | `claim-ledger` |
| Public reproducible data | `data-pipeline` |
| Human-contribution documentation | `gate-log`, `finalize-compliance`, `contribution-report` |

## Journal-specific standards

This file states field norms. Per-journal standards for JF, JFE, and RFS
(desk criteria, identification bars, data-and-code policies, submission
mechanics, observed presentation norms from recent exemplars) live in
[journal-standards/](journal-standards/): one file per journal plus
[shared-norms.md](journal-standards/shared-norms.md), a sourced bibliography
([sources.md](journal-standards/sources.md)), and the gate-G6
[quality-checklist.md](journal-standards/quality-checklist.md).

## Key references (verify exact metadata before citing in a paper)

- Harvey, Liu, Zhu (2016), "... and the Cross-Section of Expected Returns," Review of Financial Studies.
- Harvey (2017), "Presidential Address: The Scientific Outlook in Financial Economics," Journal of Finance.
- Jensen, Kelly, Pedersen (2023), "Is There a Replication Crisis in Finance?", Journal of Finance.
- Fama, French (1992), "The Cross-Section of Expected Stock Returns," Journal of Finance.
- Cochrane, "Writing Tips for Ph.D. Students" (widely circulated note).
- Angrist, Pischke (2010), "The Credibility Revolution in Empirical Economics," Journal of Economic Perspectives.
