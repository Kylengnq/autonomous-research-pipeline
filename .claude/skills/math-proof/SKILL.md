---
name: math-proof
description: "Write a complete, gap-free mathematical proof for the analytical model or proposition of a finance paper. Use only after hypothesis-development determined a formal model IS warranted (structural parameters, a quantitative bound, or a model-implied identifying restriction). Trigger on prove, derive, show analytically, justify mathematically, expand a proof sketch, or write a proof for a proposition/lemma. Enforces single-pass rigor: state before showing, sign every term, prove the general case not examples, no clearly/obviously."
---

# Math proof

Write a rigorous proof suitable for a top finance journal appendix: every step explicit enough that a
referee verifies it without filling gaps. A proof, not a sketch. Adapted for this repo from the
Theorist Toolbox `math-proof` skill (Moran Koren, BGU).

## When to use (when not)

Use this only when a paper genuinely carries an analytical result. Most empirical finance papers do
not: `hypothesis-development` develops predictions in prose, and its "When a formal model IS
warranted" gate is the decision to check first. Invoke `math-proof` when that gate passed, i.e. the
paper estimates structural parameters, states a quantitative bound or comparative static that prose
cannot deliver, or its identification depends on a model-implied restriction. The choice to include a
model is a framing/design decision: record it via `/gate-log` before writing the proof, not after.

## Anti-hallucination (the Material Gap rule applies to proofs too)

Never invoke a lemma, theorem, or closed form you cannot state and justify. Only cite well-known
results (rule of thumb: famous enough for a Wikipedia page or a standard first-year course). If you
need a non-standard result, prove it inline. If a step is genuinely beyond reach, do not paper over
it: write `[MATERIAL GAP: <the step that is unproven>]` and surface it, exactly as with a missing
number or citation. A proof with an honest open step beats a proof with an invented lemma.

## Core discipline

- **No gaps between steps.** Every transition is justified at the line where it happens: name the
  rule (quotient rule, envelope theorem), the definition substituted, or the assumption used. The
  referee should never reconstruct an intermediate line.
- **State what you will show before showing it.** Open each step with the goal in a plain sentence
  ("We show the threshold decreases in rho"), then deliver the algebra.
- **Sign every term.** When a derivative or expression appears, state its sign and the reason at
  once. "Negative, since each factor is positive and (2q-1) > 0", never a bare "the expression is
  positive."
- **Show intermediate algebra.** At least one line where products are expanded but not yet
  simplified. Do not jump from a quotient-rule setup to the final simplified form.
- **Bridge definitions to usage.** When you define a quantity and then differentiate it, say so in a
  sentence: "Define t(K,rho) as the smallest integer Y satisfying this inequality."
- **Prove the general case, not examples.** Verifying n = 1,2,3 is evidence, not a proof. Give an
  argument covering the full generality, or state the boundary explicitly ("verified for n <= 5; the
  general case remains open" -> that is a `[MATERIAL GAP]`).
- **One intuition sentence after each key derivation**, connecting the math to the economics. Keep it
  literally defensible, not merely morally true.

## Proof structure

1. **Setup.** Define all notation; state model primitives (distributions, parameters, decision
   rules); write the key quantities as explicit functions of the parameters.
2. **Numbered steps.** Each step opens with what it shows, derives it with full intermediate algebra,
   signs every derivative, and closes with boundary or limiting values where useful.
3. **Connecting steps.** When one step feeds the next, say so: "Substituting the result of Step 1
   into c_K ...". Do not assume the reader tracks which results carry forward.
4. **Edge and case analysis.** Enumerate cases explicitly, confirm they are exhaustive and mutually
   exclusive, and handle each. Check boundary behavior (x = 0, x -> infinity) for any "for all x > 0"
   claim. Never "the other case is similar" unless the symmetry is genuine and you state it.
5. **QED.** End with a box and, for a composite result, a one-sentence wrap-up naming which lemmas
   combine ("Combining Lemmas 1-3 establishes Theorem 2").

## Common patterns

- **Ratio f/g:** apply the quotient rule explicitly; compute f' and g' separately first, then
  substitute, then expand the numerator on its own line.
- **Signing a log:** if beta = log(a/b) is claimed negative, show a < b first with an explicit
  inequality.
- **Chain rule through a CDF:** when both a threshold and a distribution parameter move,
  differentiate each channel, sign each separately, then discuss which dominates.

## Placement and output

- The proof lives in an appendix; the main text carries the statement, a short sketch, and an
  intuition paragraph outside the proof environment. Reference the appendix in words
  ("The proof of Proposition 3 is in Appendix C").
- Write directly into the target `.tex` with Edit. Use `\citet`/`\citep` for any cited theorem, with
  a precise pointer ("[12, Theorem 3.1]", never "by [12]").
- After writing, run a banned-words and grammar pass against `references/banned-words.md` and
  `references/grammar-punctuation.md` (no em dashes; equations are part of the sentence and take
  terminal punctuation).
- Once the proof is written and its correctness accepted, hand exposition to
  `proof-readability` for the content-preserving polish pass. Do not skip straight to readability on
  an unverified proof.
- Append a dated entry to.
