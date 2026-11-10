---
name: idea-scoring
description: "Funnel layer F2: cuts the F1 idea pool (100-120) to 20-25 survivors by calibrated rubric scoring. Two independent mid-tier scorers per idea on four dimensions anchored to the held-out top-journal calibration set (archetype match, displacement plausibility, data plausibility, desk-reject risk); a third scorer on band disagreement. Deliberately search-free; scores are labeled unaudited and stripped from downstream briefing packs. In data_mode: anchored the data dimension becomes data leverage, read from the card's F-1-verified anchor fields rather than guessed. Use after idea-swarm, before idea-debate."
---

# Idea Scoring (F2)

Cheap-cut layer of the idea funnel (S1).
Concentrates quality; issues no verdicts. The full novelty audit and
desk-reject simulation run later, in F3, on survivors only.

## Status: swarm path only, and unvalidated

**This layer does not run in the themed path.** When `theme` is set the
stage generates 8-12 deliberate variants, and a 100-to-22 cut has nothing
to do. F2 runs only in the no-theme swarm fallback.

**It has never been shown to predict anything.** A retrospective check
across the runs completed so far found ρ = 0.16 against the comparative
ranking and ρ = 0.09 against the binary desk run, both consistent with
zero at the sample available. F2's *lowest*-scored card that run
finished 2nd of 8; the four cards it tied at 14.0 ended at terminal ranks
4, 7, 10 and 10.

The layer was nonetheless **kept**, for a reason that binds against the
recommendation: the check was underpowered by construction. At n = 11 with
heavy ties the permutation null band runs to ±0.61, so it could not tell
ρ = 0 from ρ = 0.4. Detecting ρ = 0.4 at 80% power needs about 47 terminal
outcomes and a run yields about 11. *No evidence of predictive validity is
not evidence of no predictive validity*, and deleting a layer on an
underpowered null is the error the phase-3 review caught in the 2.0pp
equivalence bound.

Two consequences, both binding:

1. **No layer may select into deep F3 by F2 rank.** Rationing depth by
   score has already made one run unmeasurable: the three cards given deep
   F3 were the top three by F2, so the sample was truncated by the variable
   under test. Ration by a rule independent of F2 — random
   within the cut, or by `data_class` — or the accumulating record never
   becomes readable.
2. **Every run appends its `(f2_score, terminal_rank)` rows**, with the
   brief regime, to the cross-run record (see `idea-debate`'s counters).
   That accumulation is the only route to an answer.

Until that answer exists, describe F2 as a cheap concentrator and nothing
more. It issues no verdicts, and its rank is not a prediction.

Read `pipeline-config.md` first: `idea_pool`, `ideas_dir`,
`calibration_file`, `model_mid` (falls back to `model_default`),
`gate_mode`, `data_mode`, `data_access`. The calibration set is a hard dependency: missing or
stale (older than six months) blocks scoring entirely — stop and ask
(human) or PARK (autonomous). There is no capped-verdict fallback
here; an uncalibrated cut would shape everything downstream.

## Scoring protocol

1. Two scorer agents per idea, fresh subagents on `model_mid`,
   mutually isolated, each given: the idea card, the calibration
   set's archetype summaries, and the rubric below. Neither sees the
   other's sheet, the pool ranking so far, or which cell produced the
   card.
   **The two scorers carry distinct dispositions**
   from `peer-review/references/referee-dispositions.md`, and the third
   on a band disagreement carries a third. Identical briefs have produced
   33 of 33 agreement where diverse dispositions produced 4 of 11 on the
   same cards: a panel on one brief is manufacturing
   confidence, and two scorers who agree because they were given the same
   instructions have not independently confirmed anything. This changes
   the band-disagreement rate by construction, so it is a **brief regime
   change** and every row it produces is tagged accordingly in the
   cross-run record.
2. Rubric, four dimensions, each 1-5 anchored to calibration
   archetypes (5 = matches accepted-paper archetypes; 1 = matches
   stalled-paper failure modes):
   - archetype match: question and mechanism shape vs recent
     acceptances in the field profile;
   - displacement plausibility: how likely the displacement hunch
     survives the F3 audit (plausibility, not verification);
   - data plausibility: how likely the card's named source, by its
     named access route, covers the design (plausibility, not a coverage
     count). Price is not the question; obtainability is. A card whose
     `data_route` is blank scores 1, whatever source it names. Under
     `data_access: free_only` a route other than `public` scores 1 as
     well. In `data_mode: anchored`
     this dimension becomes **data leverage**: does the held data
     supply identifying variation the literature lacks, and is the
     extension join verified in the expansion map. Whether a source
     exists is no longer a guess in anchored mode, so the dimension
     stops scoring it. An `unanchored` card in an anchored run is
     scored on plausibility as above, and a card whose extension is a
     candidate rather than a probe-verified join cannot score above 3;
   - desk-reject risk, reverse-scored: framing, question-first test,
     zero-result value. In anchored mode the question-first test
     includes the card's `public_counterfactual`: an idea whose
     interest rests on holding the data rather than on the question is
     the additive-not-novel desk reject, and scores accordingly.
3. Search-free rule (hard): scorers run no literature or data
   searches. Every sheet carries the header `UNAUDITED SCREENING
   SCORE — plausibility only, novelty and data unverified`. A scorer
   that cites a specific paper or dataset as fact has violated the
   Material Gap rule; the sheet is regenerated.
   Anchored mode does not relax this. Scorers read the verified anchor
   fields already on the card and never query the held data themselves:
   the card's facts came from F-1, which logged them. The header
   becomes `UNAUDITED SCREENING SCORE — plausibility only, novelty
   unverified; data facts from the F-1 profile`, so a downstream reader
   knows which half was checked.
4. Composite = sum (4-20). Disagreement beyond one band (composites
   differing by more than 2, or any dimension by more than 2) seats a
   third scorer; the final score is the median composite.
5. Sheet-schema check (before any sheet is used). Each returned sheet
   must carry all four dimension scores as integers 1-5, the UNAUDITED
   header, a `composite` equal to the sum of the four dimensions, and
   in anchored mode the card's `data_class` copied verbatim. A
   sheet that is missing a field, out of range, or whose composite does
   not equal the sum is regenerated once by a fresh scorer; a second
   failure is flagged `[MATERIAL GAP: scorer sheet malformed]` and that
   scorer is excluded (its slot re-seated), never hand-patched. Do not
   trust the agent's JSON — validate it.

## The cut (machine gate: funnel floor)

Rank by final composite. Keep 20-25: cut at the largest score gap
whose keep-side count lands in 20-25; no gap, keep 22. Ties at the
boundary: keep both only if the count stays within 25, else drop by
worse desk-reject-risk score. The cut size outside 20-25 is a gate
failure — fix the cut, never the scores.

## Output

- Survivors: a lineage directory per idea under `ideas_dir`
  (`ideas/<slug>/` with `handoff/` and `quarantine/` subdirs), the
  idea card copied into `handoff/idea_card.md` WITHOUT its scores —
  F3 briefing packs are score-blind by the clean-room rule.
- Scoring sheets: `ideas_dir/scoring/` (outside every lineage dir;
  readable for audit, never for briefing packs).
- Pool file updated: statuses `cut` / `scored-out`, counts block
  extended (cut size, third-scorer rate, score distribution). In
  anchored mode the counts block also reports the cut's class mix
  against the pool's, so capture by the held data is visible rather
  than silent: a cut that is entirely anchored when a quarter of the
  pool was not is a finding for the run log, not a gate failure.
- Lab-notebook entry: date, cut size, third-scorer rate, boundary
  decisions, and in anchored mode the class mix.

## Validation

Done when: every pooled idea has two (or three) sheets; every sheet
passes the schema check (four integer dimensions 1-5, UNAUDITED header,
composite = sum) or is flagged and re-seated; the cut count is within
20-25; every survivor has a lineage dir whose `handoff/idea_card.md`
contains no score, rank, or scorer text; the pool counts block
reconciles (raw = cut + scored-out). In anchored mode also: every sheet
carries `data_class`; no sheet reports a query the scorer ran; the cut's
class mix is recorded.

Also blocking: the run has no `theme` set (F2 does not run in the
themed path); the scorers carried **distinct dispositions**, recorded by
name; **no downstream layer selected into deep F3 by F2 rank**, and the
rule actually used to ration depth is recorded; and the run appended its
`(f2_score, terminal_rank)` rows with their brief regime to the cross-run
record.
