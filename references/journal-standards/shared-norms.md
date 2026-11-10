# Shared norms across JF, JFE, and RFS

What all three top finance journals demand, so the per-journal files can stay
short and hold only what differs. Source tags resolve in [sources.md](sources.md).
Claims with no tag are marked `[field norm, unsourced]`.

## 1. Novelty and desk criteria

- All three journals desk reject a large share of submissions to spare authors
  a slow death: JF desk rejected 43% of submissions in 2023 and the editor
  expects roughly 45% going forward [S3]; RFS turns around a median first
  decision in 30-35 days precisely because editors reject quickly without
  referees when a paper is "very unlikely to meet the journal's publication
  criteria" [S8, S9].
- Acceptance rates sit in the mid single digits: JF's cumulative acceptance
  rate since July 2016 is 5.6% (630 of 11,193 decisions) [S4]; RFS reported
  6.0%-8.1% across 2023-2026 [S9]. JFE publishes no equivalent statistic
  [sources.md, "not found"].
- The desk question is contribution, not correctness: JF instructs that "the
  introductory section of your manuscript should emphasize the incremental
  contributions of your research" [S1]. A paper that cannot state what it adds
  over the two or three closest papers does not reach referees
  [field norm, unsourced].
- The contribution must be stated in one concrete paragraph; "I analyzed data
  on executive compensation and found many interesting results" fails the test
  [S10].

## 2. Methods and identification

- Identification is the first-order evaluation criterion for empirical work:
  "What are the three most important things for empirical work? Identification,
  Identification, Identification" [S10]. The author must name the source of
  variation in the right-hand variable, the economics of the error term, and
  why the two are uncorrelated [S10].
- Statistical discipline post-replication-crisis: with widespread multiple
  testing and p-hacking, "many of the results being published will fail to
  hold up in the future"; conventional t > 2 thresholds over-reject and
  effects supported only by a t-statistic near 2 in a large panel are
  economically tiny [S11, S10]. New empirical claims are expected to survive
  a higher evidential bar and to disclose the specification search [S11, S15].
- Out-of-sample durability is now a named concern; the replication-crisis
  debate itself is top-3 material (Jensen-Kelly-Pedersen won a JF
  Distinguished Paper prize in 2023) [S16, S3].
- Economic magnitude ranks with statistical significance: "Explain the economic
  magnitude of the central numbers, not just their statistical significance"
  [S10]. A result without an economic anchor (per-SD effect, dollar value,
  benchmark comparison) is incomplete [field norm, unsourced].
- Claims may not be stated above their evidence rung: a statement is not a
  fact, a fact is not representative data, data are not conclusive evidence,
  and evidence in one setting is not universal proof [S12]. Causal language
  requires a credible counterfactual design [field norm, unsourced].

## 3. Data and reproducibility

- All three journals now run a data-and-code regime with a named data editor
  or equivalent review:
  - JF appointed its first data editor in 2023 "who will verify that code
    submitted to the Journal cleanly reproduces the results in the paper" [S3].
    Accepted papers must deliver all programs, computation details, log files,
    and the actual data (or pseudo data when data cannot be shared), generally
    within 30 days of conditional acceptance, with a disclosure plan due at
    initial submission [S2].
  - JFE requires "data, programs, and details for the computations necessary
    for replication" uploaded to Mendeley Data or a domain repository as soon
    as possible after acceptance; a JFE data editor reviews all code for
    completeness [S6].
  - Code documentation must state OS, software versions, non-core packages,
    random seeds, and execution order at both JF and JFE [S2, S6].
- Proprietary data does not exempt the pipeline: JF requires an authorization
  letter from each proprietary source [S1] and pseudo data sufficient to run
  every program [S2]; JFE requires a pseudo data set "so that all of the
  programs can be run successfully, including any data cleaning programs" [S6].
- Hand-collected data can be embargoed only briefly (JF: two years from
  submission [S2]; JFE: confidentiality period "not exceeding two years" [S6]).

## 4. Writing and presentation

- Triangular structure: "put the punchline right up front and then slowly
  explain the joke"; nothing appears before the main result that the reader
  does not need to understand the main result [S10].
- Abstracts are hard-capped at 100 words at all three journals [S1, S5, S7]
  and must state what the paper finds, not what it looks for [S10].
- Introductions open with the contribution, not throat-clearing ("Financial
  economists have long wondered..." is the canonical failure); three pages is
  a good upper limit [S10]. JF codifies this: emphasize incremental
  contributions, keep citations to the minimum that clarifies them [S1].
- The literature review is brief, placed after the contribution, and positions
  the paper against the 2-3 closest papers rather than surveying the field
  [S10].
- Tables: self-contained captions, the regression equation in the caption,
  no number in a table that is not discussed in the text, 2-3 significant
  digits, sensible units [S10]. Figures earn space only when they communicate
  patterns better than tables; label axes, self-contained captions [S10].
- Style: active voice, subject-verb-object, no adjectives on one's own work
  ("striking results" invites deletion), simple words, no naked "this",
  present tense, spelled-out author names [S10].
- Length discipline: "Final papers should be no more than 40 pages. Drafts
  should be shorter" [S10]; JF enforces a hard 60-page cap including internal
  appendices, references, figures, and tables [S1]. Robustness material
  belongs in the internet appendix, summarized in a sentence or two in text
  [S10, S1].

## 5. Referee reality (calibration for simulated review)

- Referee judgments carry a large idiosyncratic component: the
  referee-specific component of recommendations is about twice as important
  as the paper-common component, and referees disagree enough that one
  referee's R&R barely raises the odds the other recommends the same [S13].
  A simulated panel should therefore draw dispositions with real variance
  rather than converge on one verdict.
- Review speed norms: JF median turnaround 43 days in 2023, 71.2% of decisions
  within 70 days [S3]; RFS median 30-35 days with a 120-day money-back
  guarantee [S8, S9]; JFE refunds part of the fee after 120 days [S5].
- Revision cadence: at JF, 57% of 2023 acceptances came after at most one
  revision and 94.9% after at most two [S3]; JF caps resubmission windows at
  12 months [S3], JFE and RFS at 18 months [S5, S7/S8]. A simulated R&R
  process that runs past round 3 is off-calibration [S3].
- JFE issues no reject-and-resubmit decisions: desk reject, reject, R&R,
  conditional accept, or accept only [S5].
