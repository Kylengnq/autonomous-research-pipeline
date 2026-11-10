# Top-3 paper-quality checklist

The gate-G6 checklist distilled from the journal-standards dossier
([jf.md](jf.md), [jfe.md](jfe.md), [rfs.md](rfs.md),
[shared-norms.md](shared-norms.md)).
Used by `draft-paper` (presentation norms), `edmans-audit` (per-journal
importance and spin bars), and `peer-review` (desk simulation). Each item is
checkable against the manuscript alone; items marked (journal) vary by
target, so set the target journal first.

## 1. Desk survival (the first 5 minutes)

- [ ] The one central contribution is stated concretely in one paragraph of
      the introduction; a reader can repeat it after one pass.
- [ ] Paragraph 1 opens with a dated anecdote, quantified stylized fact,
      theory tension, or measurement gap. It does not open with "the
      literature," a cute quotation, or policy throat-clearing.
- [ ] "In this paper, we..." (or equivalent) appears by paragraph 3.
- [ ] The abstract is at most 100 words (hard cap at all three journals) and
      states findings, not intentions.
- [ ] The introduction names the 2-3 closest papers and what this paper
      displaces; the literature paragraph comes after the contribution.
- [ ] (JF) The framing is legible to finance readers outside the subfield,
      and the question survives "why would a JF reader care?" in one
      sentence.
- [ ] (JFE) The design or dataset wedge is on the first page; execution
      depth is visible early.
- [ ] (RFS) Any new measure's validation is previewed in the intro;
      selection threats get their answer inside the intro.

## 2. Identification and inference

- [ ] The source of identifying variation is named in one sentence, with
      the economics of the error term and why they are uncorrelated.
- [ ] Every causal sentence is backed by a credible counterfactual design;
      otherwise the language is associational (evidence-ladder rule).
- [ ] Pre-trends inspected and flat where the design needs them; obvious
      confounds (COVID years, industry/factor composition, size) controlled
      explicitly.
- [ ] Nulls carry equivalence bounds or MDE; no underpowered null is sold
      as a finding.
- [ ] Multiple-testing exposure is disclosed; a t-statistic near 2 is not
      the paper's load-bearing wall.
- [ ] Magnitudes are anchored economically (per-SD, dollars, percentage
      points against base rates) in the introduction, not just in tables.
- [ ] (RFS) Constructed variables come with measurement-error discussion
      and validation against an incumbent measure.

## 3. Data and reproducibility

- [ ] Every printed number traces to a results file (claim ledger passes);
      the full raw-data-to-output pipeline is scripted and registered.
- [ ] Code documentation states OS, package versions, seeds, and execution
      order (JF and JFE data editors check exactly this).
- [ ] Proprietary or restricted data has a disclosure plan and pseudo-data
      that runs the full pipeline; retrieval paths stated for every source.
- [ ] The paper is self-contained without the internet appendix; robustness
      lives in the appendix, summarized in a sentence or two in text.

## 4. Writing and presentation

- [ ] Triangular structure: nothing before the main result that the reader
      does not need to understand the main result.
- [ ] Length: draft at or under 40 pages of text before appendices; JF
      submissions never exceed 60 total pages (auto-reject).
- [ ] Tables: self-contained captions with the regression equation; no
      number in a table that the text never discusses; 2-3 significant
      digits; sensible units.
- [ ] Figures: labeled axes, self-contained captions; each figure earns its
      space (an event-study figure over a coefficient table).
- [ ] Style: active voice, no adjectives on own work, no "in other words,"
      no naked "this," banned-words list honored end to end.
- [ ] Hypotheses argued in prose unless the field expects numbered ones
      (2 of 17 recent top-3 papers numbered them).
- [ ] Conclusion is short, restates nothing at length, and does not open a
      grant application.

## 5. Honesty and sign-off (author gate G6)

- [ ] Nulls reported as nulls; exploratory analysis labeled; the thinnest
      leg of the evidence disclosed.
- [ ] The paper states what evidence would have overturned its claim.
- [ ] Title and abstract claim strength approved by the author, with any
      borderline overclaim flagged rather than silently chosen.
- [ ] Simulated review has run at the target journal's calibration
      (peer-review skill) and its fatal findings are resolved, not argued
      away.
