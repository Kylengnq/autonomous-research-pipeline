---
name: draft-paper
description: "Assembles or updates the full LaTeX manuscript: scaffold, generated booktabs tables and prose macros (numbers never typed), figures, delegated intro and hypotheses, banned-words pass. Done only when the paper rebuilds from source, compiles clean, the claim ledger validates, and the citation audit passes."
---

# Draft Paper

Build the manuscript end to end. Narrower writing skills own their
sections; this skill owns the whole document: scaffold, tables, figures,
and the triple exit gate. The non-negotiable rule: if a number is not in a
results file, it does not go in the paper.

## When to use

- Turning `run-analysis` / `robustness-suite` results into a first full
  draft.
- Updating the draft after results change, so tables stay in sync.

## Principles

- **Numbers come from JSON.** Read coefficients, SEs, and N from the
  results files; generate booktabs tables programmatically; cross-check
  every printed magnitude to the decimal. A number quoted in prose is
  quoted through a generated macro (`\BetaMain{}`, see `claim-ledger`), not
  typed, so it cannot be retyped wrong or left behind when results move.
- **Edit source, never generated.** `build/values.tex`, `build/tab_*.tex`,
  the figures, and the PDF are outputs. A wrong number on the page is fixed
  at the results key and the script that wrote it, then rebuilt; editing the
  generated file leaves a fix the next `make` silently reverts. The
  source/generated table is in the `paper-build` skill.
- **Headline = what survived.** The abstract and Section 1 lead with the
  finding that passed the most robustness checks; honest non-results are
  reported with their power bounds.
- **Disclosure labels travel.** The "Retrospective registration" label
  from the prereg header, and in `gate_mode: autonomous` the "Autonomous
  mode: gate decisions made by pre-specified rule, no human review"
  statement (see `<skills_root>/playbooks/gate-modes.md`), go into the
  title footnote or the introduction. Neither is ever dropped in a
  revision.
- **Sections delegate.** The introduction goes to the empirical-intro
  skill and the hypotheses to hypothesis-development (P2 builds; until
  then, follow `references/writing-norms.md` §Introduction directly).
  The introduction follows the paragraph formula: motivation plus the
  knowledge gap, what the paper does, what it finds and what that implies,
  extensions, at most two literature-contribution paragraphs, roadmap.
  **The result lands in paragraph 3**, and there is no separate
  literature-review section.
  This skill writes Data, Design, Results, Robustness, Discussion,
  Conclusion, and stitches the document.
- **House style.** Enforce the workspace `references/writing-norms.md` and
  `references/banned-words.md`: no em dashes, no filler intensifiers, no
  promotional language, synthesize by theme. Where `pipeline-config.md` sets
  `writing_hub`, draft each section with it: per-section vocabulary, the moves a
  section is expected to make, and whatever prose measurement it provides.
- **Presentation norms.** Check the draft against sections 1 and 4 of the
  workspace `references/journal-standards/quality-checklist.md` (abstract
  cap, intro spine, table and figure rules, length discipline); when the
  config names a target journal, also apply that journal's Observed-norms
  section in `references/journal-standards/`.

## Workflow

1. Read `pipeline-config.md` for `paper_dir`, `main_tex`, `bib_file`,
   `results_dir`, `claim_ledger`, `registry_file`, `build_dir`,
   `values_tex`, `python`.
2. **Scaffold.** Create or open `main_tex`; confirm the section order:
   Abstract, Introduction, Background, Data, Design, Hypotheses, Results,
   Robustness, Discussion, Conclusion, References, Appendix. The preamble
   carries `\usepackage{siunitx}` and `\input{<values_tex>}`; if the project
   has no build graph yet, run `paper-build` first.
3. **Tables and figures.** For each results JSON, emit a booktabs table
   from a script registered in the build graph; insert figures by path; add
   a `claim-ledger` entry for every printed number as it lands, with a
   `macro` when the number is also quoted in prose.
4. **Delegate** the introduction and hypotheses; splice their output and
   fix cross-references.
5. **Prose pass.** Banned-words and AI-tells sweep over all prose
   (LaTeX macros exempt).
6. **The exit gates.** The draft is done only when all four pass:
   a. rebuilds from source: `make verify` (clean rebuild plus `make check`)
      exits 0. Where no build graph exists yet, a full manual rerun of every
      producing script substitutes, and `paper-build` is the next task;
   b. compile clean: zero undefined references or citations;
   c. `claim_ledger.py validate` and `cross-ref` exit 0, and
      `claim_macros.py emit --fail-on-change` and `check` exit 0;
   d. `verify-citations` reports no MISMATCH, MISSING, or PARTIAL.
   A failing gate stops the skill; report which gate blocked and what
   remains. Gate (a) subsumes (c)'s macro commands when `make check` runs
   them; run them directly only when there is no graph.
7. **Author sign-off.** Flag the title and any borderline claim strength
   for gate G6; never choose silently. Record in `decisions_log`.
8. Dated `lab_notebook` entry with the draft snapshot (pages, tables,
   figures, references).

## Outputs

- A compiling `main_tex` (+ `bib_file`) with tables traceable to results
  files.
- Updated `claim_ledger`.
- A dated `lab_notebook` entry.

## Validation

- All four exit gates pass before the skill reports done.
- Every table number matches its results JSON; any number without a source
  is removed or flagged `[MATERIAL GAP: ...]`.
- No numeric literal in the prose that a macro could carry; no generated
  file edited by hand.
- Title and overclaim decisions belong to the author at G6.
