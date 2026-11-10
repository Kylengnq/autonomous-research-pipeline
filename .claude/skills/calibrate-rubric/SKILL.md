---
name: calibrate-rubric
description: "Build the held-out calibration set that anchors /brainstorm and /idea scoring against actual top-3 journal outcomes. Pulls ~40 recent JF/JFE/RFS acceptances and ~40 stalled working-paper analogs via Corbis, tags each with question, mechanism, identification style, displacement target, failure modes, field tags, and calibration confidence, and writes references/top_journal_calibration.json."
---

# Calibrate Rubric

Build the external anchor that `/brainstorm` and `/idea` use to gate "Top
Generalist Go" labels. Without this file, those skills cannot do archetype
benchmarking and will fall back to internal scoring only.

## When to use

- First time running the skills in this repo (initial build).
- Periodic refresh (recommended every 6 months — top-journal frontier moves).
- When the user notices the rubric calling too many ideas "top generalist"
  (under-calibrated) or too few (over-calibrated).

## Inputs to collect

| Input | Required? | Default |
|---|---|---|
| Target journals | No | `["Journal of Finance", "Journal of Financial Economics", "Review of Financial Studies"]` |
| Acceptance window | No | Last 24 months from today |
| Stalled-paper age threshold | No | 24+ months on SSRN with no top-3 placement |
| Topic areas to cover | No | All of corporate finance, asset pricing, household finance, intermediaries, real estate |
| Target acceptances per area | No | 8 (≈40 total) |
| Target stalled per area | No | 8 (≈40 total) |

## Steps

### Phase 0: Pin the source ids, and never resolve a journal by name

**From the defect that produced an earlier build.** Journal
name resolution took the first fuzzy search hit with no check that the hit was
the journal asked for, so `Review of Finance` returned *International Review of
Economics & Finance* — a different journal with 5,991 works — and everything
downstream ran against it without complaint. The resolver in
`tools/free_corbis_mcp.py` is fixed, and a build still does not rely on it.

Pin the ids and **verify each against `sources/<id>.display_name` before
pulling a single work**. A mismatch is fatal, not a warning.

| Class | Journal | OpenAlex id |
|---|---|---|
| `top3_finance` | The Journal of Finance | `S5353659` |
| | Journal of Financial Economics | `S149240962` |
| | Review of Financial Studies | `S170137484` |
| `strong_field` | Journal of Financial and Quantitative Analysis | `S193228710` |
| | Journal of Corporate Finance | `S152282257` |
| | Journal of Banking & Finance | `S2876017` |
| | Financial Management | `S157946625` |
| | Real Estate Economics | `S129086836` |
| | The Journal of Real Estate Finance and Economics | `S202178085` |
| | Journal of Financial Markets | `S127646213` |
| | The Review of Corporate Finance Studies | `S2736251538` |
| | Journal of Financial Intermediation | `S5984737` |
| | The Review of Asset Pricing Studies | `S2735409286` |

Review of Finance (`S131117787`) is deliberately excluded: OpenAlex splits it
across a 54-work record and its former name *European Finance Review*, so it
contributes noise rather than coverage. Record the omission.

**Two query mechanics, both learned by getting them wrong.** `default.search`
ANDs its terms, so a five-phrase topic string returned 3 papers out of 642 —
use short single phrases, or pull broad pages and classify locally. And the
anonymous OpenAlex pool throttles bursts: roughly 90 queries got the IP blocked
for over an hour. Prefer few large pages (`per_page=200`) over many small
queries, cache to disk, and back off on 429.

### Phase 1: Pull recent top-3 acceptances

For each target journal:

1. `top_cited_articles` with `journalNames: ["<journal>"]`, `minYear: <today - 24mo>`, `matchCount: 25`.
2. `search_papers` with `journalNames: ["<journal>"]`, `minYear: <today - 24mo>`, `sortBy: "citedByCount"`, `matchCount: 25`. (Catches papers not yet highly cited.)

Deduplicate by `id`. Filter to recent (post-acceptance, not just SSRN-posted).
Sample to roughly equal coverage across the topic areas listed in the inputs.
Target ~40 papers total.

### Phase 1b: Pull the middle class — finance field journals

**This is the most important part of the build.** A
threshold that admits only top-3 candidates lives at the boundary between
**top-3 and strong field**, not between top-3 and abandoned. Calibrating the
top rung against stalled papers sets the bar at "better than a paper that went
nowhere", which is not the bar anyone is trying to clear.

Pull ~40, balanced across topic areas, from published finance field journals:
JFQA, Journal of Corporate Finance, Review of Finance, Journal of Financial
Intermediation, Journal of Banking & Finance, Financial Management, Journal of
Financial Markets, RAPS, RCFS. Same window as Phase 1. Label
`outcome: strong_field`.

These are also **easier to get than stalled papers and a better contrast**: a
field-journal paper is a finished project that a top-3 did not take, where an
unplaced SSRN paper may simply be new. The v2026-06 build had no middle class
of this kind at all — its 16 `strong_field` entries are top *accounting*
journals, carried over from a themed build and marked `field_fit: accounting`.

### Phase 2: Pull stalled analogs

The third class, and no longer the load-bearing one. It remains useful for the
failure-mode taxonomy, which the middle class does not supply.

**The construct changed, and it is labelled rather than swapped.**
The original definition — SSRN papers 24+ months old with no top-3 placement —
is unbuildable on this backend, for a reason the v2026-06 note got half right.
SSRN *is* reachable (source `S4210172589`, 364k works in a 24-month window), but
**OpenAlex carries no abstracts for it**: 0 of 125 sampled. Every Phase 3 field
is derived from the abstract, so an SSRN class would be a list of titles.

Use instead: **finance field journals, 24-48 months old, fewer than 5
citations.** Published, old enough to have been noticed, and not noticed. That
is a different claim from "never placed" and must be written as such wherever
the class is reported — it is a weaker contrast in one way (these papers cleared
a real referee) and a stronger one in another (you can read what they actually
did, which is what the failure-mode tags require).

**Do not fill this class with whatever a query returns.** If the pull is thin or
off-field, say so in `selection_bias_summary` and let Phase 5's field-fit gate
cap the downstream verdicts. v2026-06 filled it, and the result was 17 "stalled
analogs" of which **zero were finance papers**: 14 out of scope entirely
(*Sustainability*, Yale Law School, *Journal of Disability Policy Studies*,
*Business Ethics Quarterly*, *Human Resource Management Review*), 2 economics,
1 accounting. A contrast class that exists by label and not by field is worse
than an empty one, because downstream it reads as evidence.

If the original SSRN construct is ever wanted, it needs a backend that carries
abstracts — Crossref, OpenAlex full-text, or a paid source — not a different
query.

For each topic area covered by the acceptances:

1. Pick the 2–3 main accepted papers in that area.
2. `search_papers` with their question phrased as a research query, `minYear: <today - 48mo>`, `maxYear: <today - 24mo>`, `matchCount: 20`. The age window selects papers that were drafted 2+ years ago and would have had time to land at a top-3 by now.
3. Filter to papers with `citedByCount < 30` and no `journal` field set to JF/JFE/RFS — i.e., still working papers or placed at field journals.
4. Pick ~8 per area as stalled analogs (~40 total).

This is heuristic, not exact — the goal is a contrast set, not a clean
ground truth. Note when the classification is uncertain.

### Phase 3: Extract per-paper fields

For all ~80 papers, run `get_paper_details_batch` (in groups of 25) and
extract for each:

| Field | Source | Notes |
|---|---|---|
| `id` | Corbis ID | |
| `title` | abstract | |
| `authors` | abstract | |
| `year`, `journal` | abstract | |
| `cited_by_count` | Corbis | |
| `outcome` | manual | `top3_finance`, `strong_field`, `stalled`, or `uncertain` (three-class scheme — see below) |
| `field_fit` | derived | `finance`, `accounting`, `economics`, or `out_of_scope`, from the venue. A run under `field_profile: finance` uses only `finance` entries as analogs |
| `archetype_eligible` | manual | `false` for econometric-methods papers. "Using and Interpreting Fixed Effects Models" is a real JAR placement and not an empirical archetype; four such entries were anchoring parity comparisons in v2026-06 |
| `topic_area` | manual | one of `corporate`, `asset_pricing`, `household`, `intermediaries`, `real_estate`, `other` |
| `field_tags` | manual | array of finer-grained subfield labels (e.g., `governance`, `cross_section`, `banking`, `mortgages`, `entrepreneurial_finance`, `behavioral`). A paper can carry multiple tags — many recent JF papers sit across two fields. |
| `question` | one sentence | derived from abstract, question-first phrasing |
| `contribution_claim` | one sentence | the paper's stated novelty |
| `mechanism` | one phrase | the economic friction or force |
| `identification_style` | label | one of `quasi-experiment`, `structural`, `measurement`, `theory`, `descriptive`, `cross-sectional`, `asset_pricing_test` |
| `generating_lens` | label | best-guess Lens 1–11 from the research-idea-generator taxonomy |
| `displacement_target` | one sentence | what model, paper, or empirical regularity this displaces (best-guess if not stated explicitly) |
| `displacement_category` | label | which of the four categories the target fits: `paper`, `model_claim`, `empirical_regularity`, `assumption_convention_or_belief` |
| `closest_papers_at_writing` | array of IDs | 3–5 closest works cited in the abstract or known from the area |
| `failure_modes` | array (stalled only) | up to 2 tags from the failure-mode taxonomy below; first tag is the *dominant* cause. Empty for accepted. |
| `calibration_confidence` | int 1-5 | how confident this entry is correctly classified (5 = clear top-3 acceptance, displacement target obvious; 1 = uncertain inclusion, may be misread) |
| `selection_bias_note` | one sentence | a one-line note on what could be wrong about including this paper (e.g., "field-cycle peak — area was hot during the acceptance window," "small-sample stalled — may simply be too recent for top-3 timing") |

**Failure-mode taxonomy** (use for stalled papers; up to 2 tags, first is dominant):

| Tag | Meaning |
|---|---|
| `setting_variation_only` | The contribution is "X but in country/industry/period Y" without new economics |
| `unclear_mechanism` | Empirical result documented; underlying economic channel not identified or distinguished |
| `weak_identification` | The design cannot support the causal claim made; pre-trends, weak first-stage, etc. |
| `no_displacement_target` | The paper does not name a specific belief, model, or paper it displaces |
| `incremental_data_extension` | New data on an old question without changing identification or measurement in a first-order way |
| `hard_to_interpret_null` | The paper's value depends on a particular sign; a null teaches nothing |
| `insufficient_external_validity` | Results are local to a narrow population that doesn't generalize |
| `execution_too_complex` | Design is so elaborate that referees can't audit it; or data construction is unreplicable |

For accepted papers, derive `displacement_target` and `displacement_category`
from the abstract's "we show that..." or "contrary to..." statements. For
stalled papers, derive it the same way and note if it's weak — the absence of
a sharp displacement target is often *why* the paper stalled, in which case
`no_displacement_target` should be the dominant failure tag.

When uncertain about the outcome label (e.g., the paper may still be under
review at a top-3), mark `outcome: "uncertain"` and exclude from the
calibration archetype-parity gate downstream.

### Phase 4: Write the calibration file with prebuilt indexes

Write `references/top_journal_calibration.json` with this schema. The three index fields at the end let `/brainstorm` and `/idea` look up archetype anchors in O(1) without scanning the `papers` array.

```json
{
  "version": "2026-05",
  "built_at": "YYYY-MM-DD",
  "window_months": 24,
  "target_journals": ["Journal of Finance", "Journal of Financial Economics", "Review of Financial Studies"],
  "selection_bias_summary": "One-paragraph note on systematic biases in this build: which areas are overweight relative to recent acceptances, which journals are underrepresented, what time window was active.",
  "papers": [
    {
      "id": "W...",
      "title": "...",
      "authors": ["..."],
      "year": 2024,
      "journal": "Journal of Finance",
      "cited_by_count": 42,
      "outcome": "accepted",
      "topic_area": "corporate",
      "field_tags": ["governance", "intermediaries"],
      "question": "...",
      "contribution_claim": "...",
      "mechanism": "...",
      "identification_style": "quasi-experiment",
      "generating_lens": 1,
      "displacement_target": "...",
      "displacement_category": "paper",
      "closest_papers_at_writing": ["W...", "W..."],
      "failure_modes": [],
      "calibration_confidence": 5,
      "selection_bias_note": "Clear top-3 acceptance with stated displacement; no flags."
    }
  ],
  "mechanism_index": {
    "limited_attention": ["W...", "W..."],
    "moral_hazard": ["W..."],
    "search_cost": ["W..."]
  },
  "topic_area_index": {
    "corporate": ["W...", "W..."],
    "asset_pricing": ["W..."],
    "household": ["W..."],
    "intermediaries": ["W..."],
    "real_estate": ["W..."]
  },
  "field_tag_index": {
    "governance": ["W...", "W..."],
    "cross_section": ["W..."],
    "banking": ["W..."],
    "mortgages": ["W..."],
    "entrepreneurial_finance": ["W..."],
    "behavioral": ["W..."]
  },
  "identification_style_index": {
    "quasi-experiment": ["W..."],
    "structural": ["W..."],
    "measurement": ["W..."],
    "theory": ["W..."],
    "asset_pricing_test": ["W..."]
  },
  "failure_mode_index": {
    "setting_variation_only": ["W..."],
    "unclear_mechanism": ["W..."],
    "weak_identification": ["W..."],
    "no_displacement_target": ["W..."],
    "incremental_data_extension": ["W..."],
    "hard_to_interpret_null": ["W..."],
    "insufficient_external_validity": ["W..."],
    "execution_too_complex": ["W..."]
  }
}
```

Order the `papers` array: accepted first, then stalled. Within each, group by `topic_area`.

### Phase 4.5: Build the indexes

After populating the `papers` array, derive five indexes by iterating once over the papers:

- `mechanism_index[m]` = list of paper IDs where `mechanism` is `m` (or contains `m` as a substring for compound mechanisms).
- `topic_area_index[t]` = list of paper IDs where `topic_area` is `t`.
- `field_tag_index[ft]` = list of paper IDs where `ft` appears in the paper's `field_tags` array.
- `identification_style_index[i]` = list of paper IDs where `identification_style` is `i`.
- `failure_mode_index[fm]` = list of paper IDs (stalled only) where `fm` appears in the paper's `failure_modes` array. Papers contribute to one entry per tag they carry.

Normalize keys to lowercase snake_case before indexing (e.g., "Limited Attention" → `limited_attention`). All papers (accepted, stalled, uncertain) go into the topic, field-tag, mechanism, and identification indexes — downstream skills split by `outcome` after the lookup. Only stalled papers appear in `failure_mode_index`.

### Phase 5: Sanity check

Before declaring the calibration set built, verify:

- **Field-fit gate, and it is the one that matters.** For the
  `field_profile` this set will anchor, count entries with a matching
  `field_fit` **in each of the three classes**. A class with fewer than 8
  in-field entries is **not usable for that profile**, and the file must say so
  in `selection_bias_summary` by name. Downstream, `finance-idea-screening`
  caps its verdict when a class is unusable rather than awarding a rung on
  parity evidence it does not have. v2026-06 failed this and nothing caught it:
  it carried 17 stalled entries of which **zero** were finance.
- At least 30 in-field `top3_finance`, 30 in-field `strong_field`, and 20
  `stalled` papers extracted.
- Each topic area has at least 4 `top3_finance` and 4 `strong_field` papers.
  **Report `real_estate` explicitly** — v2026-06 had 0 and the count was not
  visible anywhere.
- `archetype_eligible` is `false` on every econometric-methods paper. A parity
  comparison against "Using and Interpreting Fixed Effects Models" is not a
  comparison against an archetype.
- The 11 lens categories collectively cover at least 7 of the accepted
  papers (no single lens dominates; if Lens 5 — policy shock — accounts for
  more than 35% of acceptances, the topic coverage is biased and should be
  rebalanced).
- Stalled papers' `displacement_target` is empty or weak for at least half
  the sample. (If stalled papers all have sharp displacement targets, the
  classification probably misidentified them.)
- At least 4 of the 8 failure-mode tags appear at least twice. (A taxonomy
  collapsing to one or two tags is unhealthy — the differentiation gate
  downstream becomes useless if every stalled paper carries the same tag.)
- `selection_bias_summary` is populated and names specific overweight areas
  or time-window quirks.
- At least 70% of papers have `calibration_confidence ≥ 3`. If most entries
  are below 3, the calibration set is too speculative to anchor verdicts.

### Phase 6: Log

Append a dated entry to: build date, counts of
accepted and stalled papers, lens distribution. Append all Corbis queries
used to `output/search_log.md`.

## Outputs

- `references/top_journal_calibration.json` (new or refreshed).
- Entry in.
- Queries logged to `output/search_log.md`.

## How downstream skills use this file

`/brainstorm` and `/idea` read `references/top_journal_calibration.json`
during their archetype benchmarking phase. For each candidate idea, they pick
**3 `top3_finance` analogs, 2 `strong_field` analogs, and 2 `stalled` analogs**
— all filtered to `field_fit` matching the run's `field_profile` and to
`archetype_eligible: true` — sharing the candidate's `mechanism`,
`identification_style`, or `topic_area`, and write a one-line parity claim
("at parity / below / above") against each. The parity verdict is Gate D, one
of the gates for the "Top Generalist Candidate" label, and it
is also the gate G1's `top-generalist-candidate` rung depends on.

**The `strong_field` comparison is the one that decides the rung.** Being above
parity with stalled papers is nearly free; being above parity with published
field-journal work is the claim the top rung actually makes.

If the file does not exist, **or a class has fewer than 8 in-field entries**,
both skills warn the user, skip the affected comparison, and cap the verdict at
"Strong Field Candidate" with the reason named. A missing anchor and an
unusable one produce the same cap on purpose: awarding a top rung on parity
evidence that does not exist is the failure the cap prevents, and it does not
matter whether the evidence is absent or merely off-field.

## Tool integration (Corbis MCP)

- `top_cited_articles` filtered to JF/JFE/RFS for the acceptance pull.
- `search_papers` with journal and date filters for both pulls.
- `get_paper_details_batch` (up to 25 IDs per call) for abstract extraction.

## Refresh policy

The frontier moves. Refresh the calibration set:

- Every 6 months as routine maintenance.
- After any paper in `references/top_journal_calibration.json` reaches 200+
  citations (it's no longer "recent frontier" — move it to a separate
  `accepted_landmarks` section if you want to keep the comparison).
- When `/brainstorm` or `/idea` repeatedly flags candidates as "above
  parity with every accepted analog" — that means the anchors are too old.

## Guardrails

- Do not include the user's own working papers as anchors (avoid
  contaminating the gate with self-judgment).
- Do not include papers from this repo's `output/paper_set.json` directly —
  the calibration set is a separate, journal-outcome-anchored dataset.
- When classifying `generating_lens`, prefer the more rigorous lenses
  (1, 3, 4) when ambiguous — these are the lenses the skill rewards.
- Stalled-paper classification is heuristic. Mark uncertain cases as
  `outcome: "uncertain"` rather than forcing a binary label, and exclude
  them from the gate computation.

## Next steps to suggest

After completing this skill, explicitly tell the user what to do next:

1. **If this was the first calibration build**: "The calibration anchor is now built. Next, run `/brainstorm <your topic>` to generate ten ranked ideas calibrated against the anchor, or `/idea <your specific question>` if you already have one to screen."
2. **If this was a refresh of an older calibration set**: "The calibration set has been refreshed against the recent frontier. Any prior `/brainstorm` or `/idea` verdicts may be slightly recalibrated if you re-run them."
3. **If the calibration set failed sanity checks** (e.g., fewer than 15 accepted papers found): "Calibration coverage is thin in <area>. Re-run with broader topic coverage or wait for more recent acceptances before relying on Top Generalist labels in that area."
