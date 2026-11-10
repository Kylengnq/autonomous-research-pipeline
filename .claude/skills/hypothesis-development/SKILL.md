---
name: hypothesis-development
description: "Write a Hypothesis Development section for an empirical finance or accounting paper: turn economic mechanisms into numbered, directional, literature-backed hypotheses (H1, H2, ...), each argued from 2-4 supporting papers found via Corbis. Defaults to prose hypotheses, not a formal model. Use to replace or avoid an unnecessary formal-theory section in an empirical paper."
---

# Hypothesis Development

Build the section of an empirical paper that motivates the tests: each hypothesis stated as a
directional, falsifiable prediction, argued from prior literature rather than derived from a formal
model. This is the empirical-paper counterpart to a theory section. Most empirical finance and
accounting papers in top journals develop hypotheses this way (Damle & Sinha 2026 §2 is the model);
a formal model belongs only where identification or a quantitative bound genuinely needs one.

## When to use

- An empirical paper needs a "Hypothesis Development" or "Hypotheses" section.
- A review says the theory/model section is "unrelated," "abundant," or "not needed" for an
  empirical paper, and wants hypotheses with supportive literature instead.
- The mechanism is clear in prose and a formal model would add notation without adding identification.

## When a formal model IS warranted (do not force prose)

Keep or write a formal model only if at least one holds: the paper estimates structural parameters;
the contribution is a quantitative bound or comparative static that prose cannot deliver; or
identification depends on a model-implied restriction. Otherwise, develop hypotheses in prose and,
if useful, move any accounting identities to a short appendix.

## Read first

- `references/writing-norms.md` ("Theory and model exposition": lead with the economic story,
  notation in parentheses; state the testable implication in words before any equation).
- `references/banned-words.md`.
- The writing hub named by `writing_hub` in `pipeline-config.md`, when the config
  sets one: the claim-strength ladder, tone, and prediction-before-test templates.
  With no hub configured, state each prediction as a direction with a sign before
  any notation, and keep claim strength at what the design can support.
- `output/paper_set.json` and any positioning memo: reuse papers already collected before searching.

## Workflow

1. **Name the mechanisms.** List the economic forces the empirical design will test, in plain
   language. For each, decide the sign it predicts for the outcome. A paper whose answer is a null
   states competing forces (H1 one direction, H2 the offset) so the net sign is an empirical
   question, which is itself the motivation, not a hedge.
2. **Find support per mechanism.** For each hypothesis, use Corbis `search_papers` (`compact: true`,
   `sortBy: "citedByCount"`) to find 2-4 papers that establish the force. Merge results into
   `output/paper_set.json` (dedupe by `id`) and log queries in `output/search_log.md` per the
   repo's shared-data rules. Prefer the closest, most-cited work; cite to support the claim, not to
   name-drop.
3. **Write each hypothesis as a subsection.** Structure per mechanism (model on Damle & Sinha 2.1,
   2.2):
   - Open with the mechanism in one or two plain sentences.
   - Argue it from the cited literature (synthesize, do not enumerate paper by paper).
   - Close with the directional prediction in italics or a labeled statement:
     *H1: Higher [treatment] is associated with [direction] [outcome].*
4. **Reconcile competing hypotheses.** If H1 and H2 push opposite ways, state explicitly that the
   net effect is an empirical question the design resolves, and what magnitude would favor each.
5. **Banned-words and AI-tell pass.** Check against `references/banned-words.md` and the structural
   AI-tells checklist before returning. No formal notation introduced before its economic meaning.

## Style rules

- Directional and falsifiable: every Hn names a sign or a bound, not "X may relate to Y."
- Lead with intuition; put any Greek letters in parentheses after the plain-language meaning.
- Synthesize the support by theme; do not write "Author (2015) finds... Author (2016) finds...".
- No symmetric hedge ("could be positive or negative") unless you immediately frame it as the
  empirical question the paper answers.
- Keep it short: hypothesis development motivates tests, it is not a literature review.

## Output

- Write the section into the target `.tex`/`.md` file with Edit, updating any cross-references
  (e.g. a `sec:theory` label becoming `sec:hypotheses`) and the related-work text that referred to
  the old model.
- If equations are retained, place them in an appendix and reference them from the body in words.
- Update `output/paper_set.json` and `output/search_log.md`; append a entry.
