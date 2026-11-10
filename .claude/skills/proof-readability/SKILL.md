---
name: proof-readability
description: "Content-preserving exposition pass for a mathematical proof that is ALREADY verified correct: improve readability without changing the mathematics. Use after math-proof (or a co-author) has written and accepted a proof, when asked to polish, edit, or improve the readability/exposition/presentation of a proof, lemma, or appendix. Runs the six-layer pass (architecture, signposting, line-level justification, notation, intuition, grammar). If it finds a real gap, it stops and routes the proof back to math-proof rather than patching."
---

# Proof readability

Edit a verified proof so a referee follows it without reconstructing steps, chasing broken
references, or decoding notation. This sits above the prover: it runs after `math-proof` has written
a proof and after its correctness is accepted (by a co-author, a numerical check, or the author). It
is an exposition pass, not a proving pass. Adapted for this repo from the Theorist Toolbox
`proof-readability` skill (Moran Koren, BGU).

## Position in the pipeline

```
math-proof            ->  acceptance (co-author / numerical check / author)  ->  proof-readability
   (correctness)                    (verification)                                (exposition only)
```

**The prime invariant: never change the mathematics.** Every edit is content-preserving: reorder,
signpost, expand, annotate, rename consistently, fix references and typos. Do not strengthen, weaken,
or "simplify" any claim; do not swap in a different argument; do not silently fill a believed gap
with new mathematics.

**If you find an actual gap or error, stop editing and flag it.** Report the suspect step precisely
("the inequality in Eq. (3) silently uses FOSD via Eq. (1); I cannot verify it from the stated
assumptions") and route it back to `math-proof` as a `[MATERIAL GAP]`. A readability pass that
quietly patches math defeats the verification that already happened.

## The six-layer pass

Work in order. Layers 1-2 are structural (read the whole proof first); layers 3-6 are local.

### Layer 1 - Architecture
- **Three-layer presentation for main results:** main-text statement + short sketch + an intuition
  paragraph outside the proof environment; the formal proof in the appendix; state where each proof
  lives.
- **Restate before proving.** When a proof is deferred to an appendix, restate the result verbatim
  immediately before it. Open a proofs appendix with a notation recap.
- **Gloss-then-state.** Precede every lemma with one or two plain sentences: what it says and its
  role ("this lemma shows the threshold is monotone in q; it is the engine of Theorem 2").
- **Close composite proofs explicitly:** a wrap-up sentence naming which lemmas combine, then QED.
- **Factor exact duplicates** into one symmetric lemma instantiated twice.
- **Prose order = logical order,** or motivate the inversion so a hard auxiliary lemma does not seem
  magical.
- **Self-contained statements:** a lemma is readable in isolation; restate its objects and
  quantifiers rather than inheriting them silently. Bundle piled-up hypotheses into a named
  definition ("a regular economy is one satisfying ...").
- **Labels signal role:** Theorem (important), Proposition (lesser), Lemma (a tool), Corollary
  (follows easily). Check each label matches.

### Layer 2 - Signposting
- **Architecture opener:** the first sentence states method and plan ("established in two steps ...",
  "we prove the contrapositive"). Any non-direct method is declared in the first lines.
- **Named steps for long proofs** (over ~half a page), each opening with what it shows, and a closing
  recap of which step delivered which piece.
- **Roadmap counts must match the body:** "three cases" then four cases is worse than no roadmap.
  Verify every announced count and every "by Step 1" pointer.
- **Enumerate cases up front,** confirm exhaustive and mutually exclusive, label them.
- **Mark where assumptions open and close** ("we temporarily assume x > 0 ... this concludes the case
  x > 0"), with reminders in long branches.
- **Goal statements before algebra:** the reader knows the destination before wading in.

### Layer 3 - Line-level justification
- **Every assertion has a visible status:** assumption, previous step, prior result, definition,
  axiom, or well-known fact. The reader can tell which one each line uses.
- **Every inequality gets a named reason at its line** (an assumption, lemma, equation number, or a
  one-clause argument). A trailing "the second and third inequalities follow from ..." is fine only
  if it covers every relation in the chain.
- **Every sign / monotonicity / limit claim gets a one-clause justification.** "The derivative is
  negative" -> "negative, since each factor is positive and (2q-1) > 0." Bare "positive for every q"
  is the most common stumbling block.
- **Instantiate cited theorems at the call site:** say what each quantified variable is in the
  present context; restate the imported result in this paper's notation; cite with precise pointers.
- **Narrated algebra:** one display per transformation, each prefaced by an active-voice sentence
  ("Rearranging", "Substituting m = alpha n", "As n -> infinity the second term vanishes").
- **Display and number key derived quantities** the proof leans on; show the one-line derivation.

### Layer 4 - Notation hygiene
- **Dual-code definitions:** in symbols and in words ("let P := {x in R : x > 0} be the positive
  reals").
- **Define before use, once, in a visible place.** Proof-local objects get an explicit displayed
  definition, ideally collected at the proof's start.
- **No notation dumps:** introduce one symbol at a time with a purpose clause.
- **Restate object types on reuse** ("the vector x solves (2)", not "x solves (2)"); recall decorated
  notation when it reappears pages later.
- **Naming hygiene:** names stable across sections; parallel names for parallel objects; never
  double-book a letter; do not name what is used once.
- **Audit consistency mechanically:** argument orders, epsilon variants, subscript slips, bounds that
  differ between a statement and its appendix restatement, variant spellings.
- **Abbreviate repeated parameter lists** after their first full appearance.

### Layer 5 - Intuition
- **One intuition sentence after each key derivation,** connecting math to the model.
- **An intuition paragraph after every main theorem,** outside the proof environment, possibly with a
  concrete narrative or a toy example.
- **"In words" translations** after dense formal statements.
- Keep intuition **segregated from the formal argument** (before the proof or after QED), and every
  informal gloss must be literally defensible (no "close to" when the true statement is a limit).

### Layer 6 - Sentence and formula grammar
Defer to `references/grammar-punctuation.md` for the house rules; the proof-specific mechanics:
- **Complete sentences:** every formula is a noun or a clause; it cannot stand alone as a sentence; a
  sentence-ending display takes a period.
- **Never begin a sentence with a symbol:** "The function f is continuous", not "f is continuous".
- **Never let two formulas meet with only punctuation:** "if x != 0, then x^2 > 0".
- **Relation symbols connect formulas, not words:** "a number greater than 2", not "a number that is
  > 2".
- **Logical symbols become English in prose** ("for every", "there exists", "implies").
- **No blackboard abbreviations** (s.t., w.r.t., w.l.o.g., iff) and **no computer notation**
  (* for product, ^ for powers) in formal text.
- **No ambiguous pronouns:** every "it"/"this" has an unmistakable antecedent.
- **Knuth's blah test:** replace each formula with "blah"; if the prose collapses, add connective
  words.

## Banned phrases and their replacements

| Found | Replace with |
|---|---|
| "Clearly," / "Obviously," / "It is easy to see" | the one-line argument or a pointer to the definition/lemma that makes it immediate, or delete the word |
| "It is straightforward to show" | the displayed computation (usually one line) |
| "It can be seen that ..." | delete the filler; state the fact with its reason |
| "naturally / readily follows" | "follows from [named result] because [one clause]" |
| "The proof of (b) is similar and omitted" | one sentence naming exactly what changes (the substitution or sign flip) |

Also run the general `references/banned-words.md` pass; no em dashes anywhere.

## Output

- Edit the proof in place in the target `.tex`. Changes are exposition only; the mathematics is
  byte-for-byte equivalent in content.
- If a real gap surfaced, do not edit around it: flag it as a `[MATERIAL GAP]` and route the proof
  back to `math-proof`.
- Append a dated entry to noting the readability pass and any routed-back gap.
