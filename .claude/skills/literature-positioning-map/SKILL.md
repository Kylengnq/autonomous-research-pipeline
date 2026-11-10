---
name: literature-positioning-map
description: "Map the closest literature and sharpen contribution claims for finance or real-estate papers. Use for related-literature sections, novelty maps, and closest-paper comparisons."
---

# Literature Positioning Map

Your job is not to summarize everything ever written. Your job is to help the paper occupy a precise place in the literature.

## Workflow

1. Identify the paper's exact question, mechanism, setting, and design.
2. Search for truly close papers using available tools before expanding outward.
3. Build concentric rings: closest papers (direct competitors), near papers (shared mechanism or method), and contextual papers (broader field).
4. Group papers by the dimension of comparison: mechanism, identification strategy, setting, data, or prediction.
5. Identify the comparison set that a referee would naturally invoke.
6. Write a positioning argument that is specific enough to survive scrutiny.

## Tool integration (Corbis MCP) — this is critical

**Always search before writing.** Do not rely on parametric knowledge alone. Corbis searches 250,000+ papers via hybrid semantic+keyword search.

### Mandatory search sequence (execute in order)

**Step 0 — Check existing data and run architecture + frontier searches:**
- If `output/paper_set.json` exists, read it first. Papers already collected for this topic can inform the positioning without redundant searches.
- `search_papers` (query: the core topic, `sortBy: "citedByCount"`, `matchCount: 15`) → immediately see the field's citation hierarchy. The most-cited papers are what referees will compare you to.
- `search_papers` (query: core topic, `minYear: 2020`, `matchCount: 15`) → the recent frontier and scooping risks.
- These two searches frame everything that follows. Save results to `output/paper_set.json` (merge if exists) and append queries to `output/search_log.md`.

**Step 1 — Inner ring (direct competitors), paper-set-first:**

Step 0 populated `output/paper_set.json` with ~30 papers from the topic area. Before firing a fresh search, scan that set for direct competitors — papers whose abstract or title plausibly addresses the exact question + method. Classify the situation:

- **Paper set has 3+ plausible direct competitors.** No fresh inner-ring search needed. Run `get_paper_details_batch` on those 3+ IDs to confirm true overlap (one call, not a new search).
- **Paper set has 1-2 plausible competitors but coverage feels thin.** Fire one supplemental `search_papers` (query: the exact question + method, `matchCount: 10`, `compact: true`). Combine results with the existing paper_set hits before running `get_paper_details_batch`.
- **Paper set has no plausible direct competitors.** Fire the full inner-ring search: `search_papers` (query: the exact question + method, `matchCount: 15`, `compact: true`), then `get_paper_details_batch` on top 5.

Expected savings: ~50% of inner-ring searches collapse to a batch-detail call against existing IDs.

**Step 2 — Middle ring (parallel pair):**

The two middle-ring queries are independent and should fire in a single message as parallel tool calls, not sequentially:
- `search_papers` (query: the same question with alternative methods, `matchCount: 10`, `compact: true`)
- `search_papers` (query: the same method applied to related questions, `matchCount: 10`, `compact: true`)

Wait for both before merging into the paper set.

**Step 3 — Outer ring (seminal and contextual):**
- `top_cited_articles` (journalNames + query: topic) → identify canonical papers within key journals that may not have appeared in keyword searches. If the paper_set already contains 5+ papers with `citedByCount > 500` in the area, skip this step.

**Step 4 — Verify specific papers:**
- `get_paper_details` or `get_paper_details_batch` (paper IDs) → when the user mentions a specific paper or when you need to verify what a close paper actually does vs. what its title suggests.

### Citation-aware comparison set

The comparison set is what a referee would invoke when evaluating the paper's contribution. This is heavily correlated with citation count:

- **High-citation close papers (500+ citations)** are the biggest positioning challenge. If your paper is close to one of these, the referee already knows that paper and will ask "what's new?" You must differentiate explicitly.
- **Medium-citation close papers (100-499)** define the active conversation. Your contribution must be stated relative to these.
- **Low-citation close papers (<100, especially recent)** represent scooping risk. A 2024 paper with 20 citations doing nearly the same thing is a bigger threat to your submission than a 2005 paper with 2,000 citations, because the 2024 paper hasn't been absorbed yet and the referee may not know it.

When identifying the "closest 3-5 papers," include at least one high-citation anchor and at least one recent paper. Do not let the comparison set consist entirely of niche recent work that a referee has never heard of.

### Threat search (the referee's weapons)

Reframe the closest papers as adversaries, not neighbors. The question is not "what is related" but
**"which papers would a referee cite *against* this paper to reject it?"** Produce an explicit threat
list of the 3 papers a hostile referee reaches for first, and for each:

- **URL / DOI mandatory.** Every threat paper carries a working link (DOI, journal URL, or arXiv).
  A closest-paper claim without a verifiable link is treated as unverified and must not be asserted;
  this is the cheapest guard against hallucinated competitors. (Confirm with `/verify-citations`.)
- **The threat in one line:** what this paper already does that overlaps the present contribution.
- **Survival in one line:** the specific dimension (mechanism / identification / data / scope / time /
  prediction) on which the present paper still stands, or an honest "does not survive -> reposition."

A threat that the paper cannot survive is a kill/pivot signal, not something to bury. If two threat
papers together cover most of the contribution, say so and route to `/idea` or `/brainstorm`.

### Citation management
- `format_citation` (paper ID, style: `apa` or `chicago`) → generate properly formatted citations for individual papers.
- `export_citations` (list of paper IDs, format: `bibtex`) → batch export references for the LaTeX bibliography file. Use this after completing the literature map to give the user a ready-to-use .bib file.


## What to avoid

- Laundry-list literature reviews ("this paper relates to several strands")
- Empty novelty claims such as "few papers study" or "the literature is silent on"
- Citing a paper only because it shares a noun with the current paper
- Claiming novelty without having searched
- Treating every cited paper as equally relevant

## Dimensions of differentiation

When comparing the current paper to the closest work, be specific about which dimension the novelty lies in:

| Dimension | Example claim |
|---|---|
| Mechanism | "Unlike X who study channel A, we identify channel B using..." |
| Identification | "X documents the correlation; we provide causal evidence using..." |
| Data/Setting | "X studies large public firms; we use novel private-credit data that reveals..." |
| Scope | "X examines one state; our national sample allows us to..." |
| Time period | "X's sample ends in 2005; we study the post-crisis regime where..." |
| Prediction | "X predicts effect A; our mechanism predicts the opposite in subgroup..." |
| Method | "X uses hedonic regressions; our repeat-sales design differences out..." |

**Weak differentiators** (be cautious):
- "We use more recent data" alone is rarely sufficient
- "We study a different country" needs a reason the setting matters
- "We use a different empirical method" needs a reason the method matters for the answer

## Contribution writing rules

- State the closest paper or papers by name in the first sentence.
- Explain whether the difference is in mechanism, data, identification, setting, or implication.
- Say what the present paper can claim that the closest papers cannot.
- Use cautious language unless the gap is truly verified ("we contribute to" not "we are the first to").
- If two or three papers together cover most of what you do, explain what the combination still misses.

## Related-literature section structure

Organize by intellectual contribution, not by topic label:

**Option A — By disagreement**: Group papers by which side of a debate they support, then explain where the current paper enters.

**Option B — By mechanism**: Group papers by the economic channel they emphasize, then explain the new channel or evidence.

**Option C — By method/setting**: Group papers by empirical approach, then explain why the new approach changes the answer.

**Never use Option D — By topic label** ("this paper relates to the literature on X, the literature on Y, and the literature on Z" with no differentiation within each bucket).

## Required deliverables

Produce:
- a literature matrix using assets/literature-matrix-template.md (populated with actual papers from searches)
- a closest-paper list (3-5 papers with specific differentiation for each)
- a contribution paragraph ready for the introduction
- a related-literature section outline organized by one of the structures above

## Output format

```
# Literature positioning memo
## Threat list (3 papers a referee cites against you, each with URL + threat + survival)
## Closest papers (3-5, with specific differentiation)
## Comparison dimensions (which dimension of novelty is strongest)
## Where this paper overlaps (be honest)
## Where this paper differs (be specific)
## What claim is safe
## What claim is too strong
## Draft contribution paragraph
## Draft related-literature outline (organized by disagreement, mechanism, or method)
## Papers to watch (recent working papers that could scoop or complement)
```

## Reference files
Read if needed:
- references/writing-norms.md

## Guardrails

- "To our knowledge" requires real verification effort — search before using this phrase.
- A literature section should reduce, not increase, ambiguity about the paper's contribution.
- If the paper is too close to an existing one, say that directly and propose a repositioning.
- Do not pad the literature review with tangentially related papers.
- If you find a paper that substantially overlaps, tell the user immediately.
- Verify claims about what prior papers do or do not do by reading their abstracts.
- Always check `output/paper_set.json` before firing a fresh `search_papers` call. Step 0's architecture and frontier searches usually populate enough of the inner ring that Step 1 collapses to a batch-detail lookup.
- When Step 2's two queries are both needed, send them in a single message as parallel tool calls.
- Use `compact: true` on every `search_papers` call. The full payload is only needed for the 5-10 papers being read in detail via `get_paper_details_batch`.

## Next steps to suggest

After delivering the positioning memo, explicitly tell the user what to do next:

1. **If 1-2 papers turn out to be very close**: "The positioning is tight against <paper>. Run `/idea` to stress-test whether your differentiation survives the displacement-target and archetype gates. If it doesn't, consider a pivot via `/brainstorm`."
2. **If positioning is clean with no direct competitor**: "Positioning is clean. Next, draft the contribution paragraph using the structured output, and run `/verify-citations` once your `.bib` is in place."
3. **If recent working papers (post-2020, low citation) showed up**: "Watch the recent working papers flagged in the memo — these are the scooping risks. Set a reminder to re-run `/lit-search` 3-6 months from now."
4. **Always remind**: "Log this positioning conversation with `/log-conversation` and the time spent reviewing the memo with `/log-human-time`."

## Example prompts
- "Position this corporate-finance paper against the payout and investment literatures."
- "Draft a related-literature roadmap for a commercial real-estate distress paper."
- "What is the nearest paper to this anomaly paper, and how do I differentiate mine?"
- "Search for any recent working papers on mortgage forbearance and housing supply."
- "Build a literature matrix for a paper on climate risk and property values."
