# Journal profiles

Calibration profiles for `peer-review`. The finance profiles (JF/JFE/RFS)
are calibrated against primary sources and an exemplar sample: fields marked
Evidence cite the workspace dossier `references/journal-standards/` (source
tags resolve in its `sources.md`)
(2026-07, 90 recent articles + 17 deep reads). Quantitative-norms fields are
medians from that sample, subject to its selection-bias summary; they
calibrate the simulation and are not citable as facts in a paper without
checking the underlying source. The economics and econometrics profiles
remain working heuristics drafted from field norms; refine them the same way
as real decision letters accumulate.

Select by argument (journal code) or by `field_profile` default:
finance -> JFE, economics -> AER, econometrics -> JoE.

## Finance

### JF (Journal of Finance)
- Desk standards: broad-interest question; a first-order economic
  magnitude; framing accessible beyond the subfield. The editor desk
  rejects when there is no "reasonable chance that a submitted paper could
  eventually clear the bar."
- Identification bar: high; a credible design or an explicit, defended
  associational stance. Mechanism evidence expected, not just the effect.
- Expected robustness: alternative codings, subsample stability, placebo
  or pre-trend evidence for causal claims; robustness detail belongs in
  the internet appendix, summarized in text.
- Peeves: overclaimed novelty (the guidelines demand the intro "emphasize
  the incremental contributions" with minimal citations); magnitudes
  without economic anchors; papers padded past the 60-page cap
  (auto-rejected at submission); previewing results instead of stating
  them.
- Quantitative norms: desk-reject rate 43-45%; R&R 11.7% of initial
  submissions (16.5% past the desk); cumulative acceptance 5.6%; median
  first decision 43 days; 57% of acceptances after at most one revision,
  94.9% after at most two; 12-month resubmission window. Manuscript: 100
  -word abstract cap (binds: exemplar median 99.5), 60-page cap (exemplar
  median 44 published pages), median 6 main tables + 4-5 figures, intro
  ~10 paragraphs, internet appendix universal, numbered hypotheses rare.
- Exemplar anchors: W7161295280 (Retail Margin Trading: quantified-puzzle
  intro spine); W3125325149 (Dark Matter: methods paper argued in
  economics before notation); W4406976666 (Worker Runs: pure theory
  grounded in a dated institutional episode).
- Evidence: S1, S3, S4 in journal-standards/sources.md
  aggregates; journal-standards/jf.md.

### JFE (Journal of Financial Economics)
- Desk standards: sharp economic question; serious data work; tolerance
  for narrower questions than JF if execution is airtight.
- Identification bar: high; replication-package culture; numbers must
  trace end-to-end (the data editor reviews the full raw-data-to-output
  pipeline).
- Expected robustness: full gauntlet including equivalence bounds for
  nulls, era confounds addressed.
- Peeves: specification search patterns; robustness narrated column by
  column; missing closest-paper comparisons; long-winded intros (JFE
  exemplar intros are the shortest of the three, ~5 paragraphs, design by
  paragraph 2); non-anonymized manuscripts (returned unreviewed).
- Quantitative norms: fee $850, partial refund on desk rejection (max
  $400, 4 per author-year); decision set has no reject-and-resubmit;
  18-month resubmission window; 120-day refund clock. No public
  desk-reject or acceptance statistics (confidence LOW on any such
  number). Manuscript: 100-word abstract cap, no page cap, exemplar
  median 7-8 main tables + 6 figures on intros of ~2,600 words, roadmap
  paragraph in about half, numbered hypotheses absent in the sample.
- Exemplar anchors: W3046626997 (Pirates without Borders: one natural
  experiment carried through the intro with institutional depth);
  W4386147025 (Active Trading: displacement framed as measurement
  upgrade); W4413817169 (Resilience in Collective Bargaining:
  theory-anchored empirics with the mechanism lever named upfront).
- Evidence: S5, S6 in journal-standards/sources.md
  aggregates; journal-standards/jfe.md.

### RFS (Review of Financial Studies)
- Desk standards: methodological care weighted heavily; open to newer
  measures and text/ML methods when validated; editors desk reject to
  protect a 30-35 day median first decision, and desk rejection signals
  fit, not necessarily quality.
- Identification bar: high; new measures need validation against an
  incumbent measure; selection threats answered inside the intro in the
  exemplar sample.
- Expected robustness: measurement-error discussion mandatory for
  constructed variables.
- Peeves: unvalidated text measures; ML used without economic
  interpretation; effect sizes quoted without base rates; abstracts over
  100 words (submission returned unreviewed).
- Quantitative norms: acceptance 6.0-8.1% (2023-2026, 1,474-1,664
  submissions/year); median first decision 30-35 days; 120-day refund
  guarantee; decisions target 2-3 rounds; 18-month resubmission window.
  Manuscript: 100-word abstract cap, exemplar median 43 published pages,
  the heaviest table load of the three (median 8 main tables), intros
  ~11 paragraphs carrying the identification defense, magnitude anchors
  with base rates in every deep-read intro.
- Exemplar anchors: W4390954288 (Corporate Climate Risk: validation-first
  measurement paper, the RFS archetype); W3001289658 (Heterogeneous Real
  Estate Agents: micro evidence + structural model, base-rate magnitude
  quoting); W4400111611 (Firm Networks: structural asset pricing;
  working-paper version, treat spine as pre-review).
- Evidence: S7, S8, S9 in journal-standards/sources.md;
  journal-standards/rfs.md.

## Economics

### AER (American Economic Review)
- Desk standards: general-interest question; policy or welfare relevance;
  clean, transparent design.
- Identification bar: very high; design-based causal inference is the
  default expectation.
- Expected robustness: pre-registration or pre-analysis consistency where
  applicable; full replication package.
- Peeves: subfield jargon in the intro; mechanisms asserted, not tested.

### QJE (Quarterly Journal of Economics)
- Desk standards: big question, memorable answer; strong narrative arc.
- Identification bar: very high, with a premium on novel natural
  experiments.
- Expected robustness: heterogeneity analysis expected; magnitudes
  anchored to familiar quantities.
- Peeves: incremental questions however clean; weak first pages.

### JPE (Journal of Political Economy)
- Desk standards: theory-connected empirics valued; structural or
  mechanism-explicit work welcome.
- Identification bar: very high; structural assumptions must be stated
  and stress-tested.
- Expected robustness: sensitivity of structural estimates to key
  assumptions.
- Peeves: reduced-form work with no economics; calibration without
  identification discussion.

### ECMA (Econometrica)
- Desk standards: methodological or theoretical contribution alongside
  empirics; precision of statement.
- Identification bar: formal; assumptions stated as assumptions, proofs
  complete.
- Expected robustness: formal sensitivity analysis; estimator properties
  discussed, not assumed.
- Peeves: informal proofs; asymptotic claims without conditions.

### ReStud (Review of Economic Studies)
- Desk standards: ambitious question, rigorous execution; friendly to
  younger authors' best work.
- Identification bar: very high; both design and estimation scrutinized.
- Expected robustness: comparable to AER.
- Peeves: over-length papers; appendices doing load-bearing work the text
  hides.

## Econometrics

### JoE (Journal of Econometrics)
- Desk standards: an econometric contribution (estimator, test,
  identification result); an application alone does not clear the desk.
- Identification bar: formal; conditions, propositions, and proofs; Monte
  Carlo evidence expected.
- Expected robustness: simulation design covering the deviations that
  break the estimator; empirical illustration secondary but clean.
- Peeves: Monte Carlos that only show the estimator working; unstated
  regularity conditions.

### JAE (Journal of Applied Econometrics)
- Desk standards: careful application of appropriate methods to a real
  question; replication section exists and is used.
- Identification bar: high; method-application fit scrutinized.
- Expected robustness: full specification transparency; data and code
  deposited.
- Peeves: method misfit (fancier than the question needs); irreproducible
  results.

## Using a profile

The editor applies: desk standards at step 3, peeves as attention
priors for referee selection, the identification bar in synthesis triage
(a claim below the bar is fatal, not addressable), and format norms in
the decision letter. In `--stress` mode, peeves double and desk standards
apply at their strictest reading.
