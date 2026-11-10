---
name: text-measure-builder
description: "Build or expand a dictionary-based text measure (e.g. a 10-K AI-adoption word list) using word/sentence embeddings, with a validation gate against the incumbent measure before adoption. Expands a seed term list by embedding-nearest-neighbor ranking, filters false positives, then checks correlation, monotonicity, and time profile vs the existing measure. Use to grow a keyword measure's coverage and variation without breaking validation."
---

# Text Measure Builder

Expand a dictionary/keyword text measure with embeddings, then prove the expansion is an
improvement before it replaces or supplements the incumbent. The discipline here is the validation
gate: an expanded word list that adds false positives or breaks the measure's time profile is
rejected, even if it raises raw counts. The incumbent (hand-curated, validated) measure stays the
primary unless the expansion clears the gate and the user opts to switch.

## When to use

- A text-based measure (AI adoption, sentiment, risk, ESG) needs broader term coverage.
- A review asks to "expand the word list" or "use embeddings" to raise variation in a measure.
- A new dictionary measure is being built from a small seed set of terms.

## Principles

- Seed quality first: start from a short, high-precision seed list of terms that unambiguously
  denote the construct.
- Expansion is additive by default: keep the incumbent measure intact; report the expanded measure
  as a sensitivity. Switch the primary only after the gate passes and the user agrees.
- Every candidate term is reviewed: embedding similarity proposes, a human/threshold rule disposes.
  Names and polysemous tokens (e.g. "Claude", "Gemini") are common false positives.
- Re-aggregation is cheap, re-crawling is not: if the crawler stores per-phrase counts, prefer
  re-aggregating stored hits; only genuinely new phrases require a new crawl pass.

## Workflow

1. **Assemble the seed list and context corpus.** Take the existing high-precision terms (e.g.
   `AI_BREADTH_PHRASES` in `scripts/pipeline_config.py`). Gather a candidate vocabulary from the
   target corpus (n-grams from a sample of the actual filings), so candidates are terms that really
   occur in the documents, not generic synonyms.
2. **Embed and rank.** Embed seed terms and candidate terms with a local model
   (`sentence-transformers`, e.g. `all-MiniLM-L6-v2`; install into `.venv` if absent). Score each
   candidate by max (or mean) cosine similarity to the seed set. Rank descending.
3. **Filter false positives.** Apply a similarity threshold, then review the shortlist by hand:
   drop proper names, polysemous tokens, and terms that denote a different construct. Record kept
   and rejected terms with the reason.
4. **Extend the measure.** Add kept terms to the phrase list. Re-aggregate stored per-phrase counts
   if available; otherwise schedule a crawl pass for the new phrases (fold into any other crawl in
   flight to avoid a second pass).
5. **Validation gate (must pass before adoption).** Compare the expanded measure to the incumbent:
   - **Correlation**: Pearson/Spearman of expanded vs incumbent across firm-years (expect high
     positive; a low or negative correlation means the expansion changed the construct).
   - **Monotonicity**: expanded measure rises monotonically across deciles of the incumbent.
   - **Time profile**: the expansion preserves the known temporal signature (for gen-AI adoption:
     near-zero pre-2021, sharp rise in 2023 filings). A term that fires uniformly across years is a
     boilerplate false positive.
   - **External benchmark** (if available): correlation with an independent measure does not fall
     (e.g. Babina 2024 resume measure, Pearson ~0.56 baseline) and ideally improves.
   - **Variation**: report whether cross-firm variance / the first-stage gradient increases, which
     is usually the point of the expansion.
6. **Decide and document.** If the gate passes, adopt the expanded list as an additive sensitivity
   (or, with user consent, the primary). If it fails, report which check failed and keep the
   incumbent. Write the kept/rejected term table and gate results to `output/`.

## Output

- Updated phrase list (in `scripts/pipeline_config.py` or the measure's config), with new terms
  clearly delimited from the validated seed set.
- A short report in `output/` listing candidate terms, similarity scores, kept/rejected decisions,
  and the validation-gate table (correlation, monotonicity, time profile, benchmark, variation).
- An entry in.

## Notes

- A local sentence-transformers model keeps the pipeline reproducible without an API key, which is
  the cheapest route and the sensible default. It is no longer a requirement: the
  pipeline admits any source or model with a named access route, and a project that needs the
  strict rule back sets `data_access: free_only` in `pipeline-config.md`. A hosted or licensed
  embedding model is admissible, but it must be named and versioned, because a measure nobody can
  regenerate is worse than a cheaper one that they can.
- Keep the seed list and expansion separable so reviewers can see exactly what the embeddings added.
