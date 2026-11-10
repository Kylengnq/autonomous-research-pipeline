---
name: idea-swarm
description: "Funnel layer F1: runs one topic-level literature landscape scan (F0 pre-step, awareness of prior work at generation time), then builds a raw pool of 100-120 candidate research ideas using a swarm of mutually isolated generator agents, one per lens-by-field cell, then deduplicates by clustering on question, mechanism, and setting with logged merges. Generation only — no scoring, no verdicts. Enforces the funnel-floor machine gate (pool >= 100, one retry). In data_mode: anchored it runs after data-profile (F-1): a reserved quarter of cells generate blind to the held data, the rest carry verified anchor fields, and the anchor-existence gate downgrades any card naming a field the profile does not contain. Use at the start of idea selection, before idea-scoring."
---

# Idea Swarm (F1)

Breadth layer of the idea funnel (S1).
Builds the pool; never judges it. Downstream: `idea-scoring` (F2) cuts
the pool, `idea-debate` (F3) applies full rigor to the cut.

Read `pipeline-config.md` first: `field_profile`, `ideas_dir`,
`idea_pool`, `model_default`, `gate_mode`, `paper_set`, `search_log`,
`calibration_file`, `data_access`, and `data_mode` (plus `data_profile`
when `data_mode: anchored`). Missing keys: stop and ask (human mode) or PARK
(autonomous), per `playbooks/error-escalation.md`.

Anchored mode (`data_mode: anchored`) changes three things below — what
F0 is steered by, how cells are assigned, and what a card must name.
Everything else in this skill is identical in both modes. In anchored
mode `data-profile` (F-1) runs first; refuse to generate against a
profile older than the manifest's refresh cadence, or with no profile at
all (profile-freshness gate).

## Literature landscape (F0 pre-step, directed exploration)

Before any generator launches, run ONE topic-level literature scan so
generation is aware of prior work — awareness enters the funnel at the
front, not only at F3. This is a single scan for the whole run
(amortized across 100+ ideas), not a per-idea search. Reuse the
workspace `literature-review` / `literature-landscape` skills in shallow
mode (read them in place); do not rebuild search machinery. Prefer
OpenAlex (unmetered) as the primary source and reserve metered search
(Corbis/Consensus) for confirmation, to protect the quota.

Output `ideas_dir/landscape_brief.md` with four blocks, every claim
citing a logged search (Material Gap rule):

1. **Occupied-margin blocklist** — questions/mechanisms a named recent
   paper already answers; generators must avoid these.
2. **Open-margin / displacement-target menu** — adjacent margins the
   scan found genuinely open, phrased as targets to displace.
   Cardinality: aim for **one target per
   steered cell**, not a short list for everyone. A three-item menu handed
   to twelve cells is an attractor no framing rule can defuse: in the
   one full-scale run the menu's three targets became the pool's
   three largest semantic clusters, 28 of 102 cards, one cluster per menu
   item. If the scan cannot honestly support that many open margins, log
   the shortfall and convert the unserved cells to menu-blind (below).
   Never satisfy the count by inventing targets or by splitting one margin
   into near-identical phrasings, and never let two steered cells draw the
   same target.
3. **Recent-acceptance archetypes** — question/mechanism/identification
   shapes that landed lately (draw from `calibration_file` where it
   overlaps; supplement with the scan).
4. **Threat papers** — the closest prior work, so F3 does not restart
   from zero.
5. **Trajectory** — where this literature is *going*,
   over roughly the last three to five years, in two explicitly separated
   halves:
   - **Saturating** — mechanisms, settings, and identification strategies
     that are crowding, and methods that have become table stakes rather
     than a contribution. A design can be unoccupied and still be late.
   - **Rising** — what is gaining ground: newly available data sources,
     methods moving from novel to expected, questions attracting entrants.

   Every claim in both halves cites a logged search, like every other
   block. Reuse the workspace `literature-landscape` skill (read in place)
   where a real trend read is wanted; do not rebuild trend machinery.

   **The two halves are routed differently, and that is the whole design.**
   This pipeline has documented twice that *positive* steering handed to
   many cells becomes an attractor, while *negative* steering does not: in
   one full-scale run the brief's three displacement targets
   became the pool's three largest semantic clusters, 28 of 102 cards, one
   cluster per menu item — while the shared blocklist produced 0 of 21
   cards on an occupied margin in the same session. A "here is what is
   hot" list handed to every generator is the menu failure with a new
   label, and it buys the worst version of trend-following: everyone
   chasing the same rise at once.

   So:
   - **Saturating goes to every cell**, both paths, shared like the
     blocklist. Its steering is negative and negative steering has never
     produced an attractor here.
   - **Rising is never shared across cells.** On the swarm path it is
     partitioned exactly like the displacement-target menu — at most one
     rising item per steered cell, no item in two cells, unserved cells go
     without. On the themed path it does **not** reach generators at all:
     the themed grid varies design axes rather than topics, so there is no
     topic steering to attach it to, and 8-12 cells sharing one rising
     list is the attractor with nothing to break it. It goes instead to
     the desk reach simulation as a currency check, and to G1 as context
     the author reads beside the menu.

   The block is a **saturation warning and a currency check, never a topic
   menu.** A trajectory block that reads as "promising areas to work in"
   has become a gaps-to-fill list wearing a chart, which is the Lens 6
   failure this brief exists to fight.

Anti-anchoring rule (binding): the brief is a **displacement-target
menu and an occupied-margin blocklist, never a "gaps to fill" list.**
Framing it as gaps collapses generators into marginal literature-gap
extensions (the Lens 6 failure). Diversity still comes from
lens/subfield isolation, not from the brief. Log every scan query to
`search_log`; seed the papers found into `paper_set` so S2 inherits
them.

Framing is not enough, and a full-scale run has proved it. That run's brief carried this rule verbatim and its three
menu targets still became the pool's three largest clusters. The rule
governs what the menu is *called*; the pull comes from how many targets
there are and how many cells see each one. So the menu is now
partitioned and a share of cells never sees it at all, per the grid
rules below. The blocklist is not partitioned and stays shared with
every cell: its steering is negative, it showed no such failure (0 of 21
cards hit an occupied margin in the same run), and splitting it would
only let cells re-generate margins other cells were told to avoid.

Anchored mode: the scan takes the F-1 profile's handoff extract as a
second input and targets margins where a held-data capability — a key,
a frequency, a population, a measure — is the lever. The anti-anchoring
rule extends with it: the profile is a capability menu, never a list of
regressions the data would support. A brief that reads as "questions our
data can answer" has made the same mistake as a gaps-to-fill list.

### F0 on the themed path

When `pipeline-config.md` sets `theme`, F0 still runs first and still
writes `landscape_brief.md`, but its job changes and shrinks. It produces
**two lists, not four blocks**:

1. **What is occupied** — the blocklist, scoped to the theme.
2. **The three closest papers** — the threat list `idea-variants` and the
   debate both inherit.
3. **Recent-acceptance archetypes, scoped to the theme** — the
   question/mechanism/identification shapes that have landed lately in and
   around this theme, drawn from `calibration_file` where it overlaps and
   supplemented by the scan.
4. **Trajectory, saturating half only** — what is crowding in and around
   the theme, and which methods have become table stakes. A variant can be
   unoccupied and still be late, and on this path every variant shares the
   author's topic, so a saturation warning applies to all of them at once.

   The **rising** half is built but withheld from generators here, per the
   routing rule above: it reaches the desk reach simulation as a currency
   check and G1 as author context. Eight to twelve cells sharing one list
   of what is gaining ground is the shared-menu attractor with no
   partition available to break it.

The displacement-target menu is not built, because there are no cells to
steer: the variation grid varies design axes, not topics, and a menu of
open margins would pull variants off the theme the author chose.

**The archetypes block is built on this path**. It was briefly dropped on the reasoning that it fed the F2 rubric and
the rubric does not run here. That reasoning was wrong: archetypes feed the
*generator* as well as the scorer, and they are the only block that carries
what a current paper in this area looks like. Without them a themed
generator sees what is **occupied** and what is **closest** — pure novelty
defence, no sense of direction — and will happily produce a well-defended
variant in a shape that stopped being publishable three years ago.
Blocklist and threats say where not to go; archetypes are the only signal
about where the field is going.

**Multi-source abstract retrieval from the start**, on this path and on
the swarm path alike. In one run the F0 blocklist carried entries
resolved by title only, and when the abstracts were finally retrieved the
biggest threat in the run turned out to say something different from what
its title implied. Title-only entries are barred from carrying a kill by
the Material Gap rule, which is what prevented a wrong retirement — but a
threat that cannot carry a kill also cannot do its job. Retrieve the
abstract; if it cannot be retrieved, mark the entry `TITLE-ONLY` and it
stays barred.

## The grid

Cells are lens x subfield. Lenses come from the workspace
`research-idea-generator` skill's heuristic lens list (read it in
place; interim reuse until a pipeline-native list exists). Subfields
come from `field_profile` (finance: corporate, asset pricing,
intermediation, household, real estate; economics and econometrics
per their profile lists). Target 12-15 cells so that 8-10 ideas per
cell reaches the 100-120 pool.

## Menu assignment and menu-blind cells

Two rules, both binding, both about the F0 menu and neither about the
blocklist.

1. **Partition.** Reserve at least a quarter of the cells (round up; at
   12 cells that is 3) as **menu-blind**: those generators receive the
   blocklist and no displacement target at all. Every remaining cell is
   *steered* and receives **exactly one** target from the menu, and no
   two steered cells receive the same one. A steered cell never sees the
   rest of the menu, only its own target.
2. **Shortfall converts to blindness, never to doubling.** If F0's menu
   carries fewer targets than there are steered cells, the unserved cells
   become menu-blind rather than sharing a target with another cell. At
   12 cells with a 3-target menu that is 3 steered and 9 menu-blind. This
   is the honest resolution of a thin menu and it is what should have
   already happened: a menu too short for the grid is evidence the
   literature offers few open margins, and the response to that is to
   generate more freely, not to point nine agents at the same three
   places.

Record the assignment with the grid. A run that quietly reshares the
menu has recreated the attractor this rule exists to break, and the
per-cell target is what makes that checkable after the fact.

The menu-blind reservation and anchored mode's unanchored reservation
are independent draws over the same grid, not the same cells renamed. A
cell may be both (blind to the menu and blind to the held data), one, or
neither; assign them separately rather than collapsing them, since
collapsing produces one fully blind group and leaves every other cell
steered on both dimensions at once.

Anchored mode adds a data class per cell. Reserve a quarter of the cells
(round up; at 12 cells that is 3) as **unanchored**: those generators
receive the landscape brief and nothing about the held data, so the pool
keeps a supply of ideas the data did not suggest. The rest are anchored
or extended cells and receive the data capability digest. Record the
class assignment with the grid, because the reserved share is checked at
validation and reported in the counts block — a run that quietly drops
it has turned the funnel into a query planner.

## Swarm rules

1. One generator agent per cell, launched as a fresh subagent on
   `model_default`. Isolation is the point: a generator sees its own
   lens definition, its subfield, the field profile, and the
   constraint digest (below) — never another cell's output, the main
   session, or the state file. Diversity comes from independence.
2. Constraint digest (directed exploration): before launching, read
   the blocked registry and graveyard summaries in `ideas_dir` if they
   exist, AND the `landscape_brief.md` from the F0 pre-step. If prior
   kills cluster on one failure type, the digest states the constraint
   (e.g. "name an access route for every idea's data"); it lists topics to
   avoid re-generating (graveyard questions + the brief's occupied-
   margin blocklist) as constraints, never verdicts, scores, or a
   gap-fill list. Each generator sees the digest, never the raw brief's
   citations (facts stay in the brief; the digest carries the distilled
   blocklist).
   The digest is **per cell, not one shared document**. Its blocklist and constraint sections are identical
   across cells; its target section carries that cell's single assigned
   displacement target, or nothing at all for a menu-blind cell. Writing
   one digest and handing it to every generator is the exact defect the
   partition rule above removes, so the per-cell digests are written out
   individually and kept, which is what makes the assignment auditable
   rather than asserted.
   Anchored mode: anchored and extended cells also receive a **data
   capability digest** — distilled verified facts from the profile's
   handoff extract (what the data covers, which keys join and at what
   match rate, what varies and over how many clusters, which
   measurement caveats bind). Distilled, never raw query output, on the
   same principle that keeps the brief's citations out of the
   constraint digest. Reserved unanchored cells receive no part of it.

   **Every capability line in the digest carries its counts**: N units, N periods, N clusters, the coverage window, and
   for a join-dependent capability its match rate. These are copied from
   `handoff/data_profile_extract.md`, which is now required to carry them
   (`data-profile`); the digest never recomputes a count and never states
   one the extract does not.

   This is not a completeness preference. In one run four cards and a
   full four-role debate were spent on a contract family of **12 markets
   over 2 meetings** — a number F-1 had already computed and the digest
   did not pass on. A generator cannot size a design it cannot see, and
   an unsized design costs its full price at F3 before anyone counts.
   A capability line without counts does not go in the digest.
3. Each generator returns 8-10 idea cards. Card schema (one card is
   4-6 lines): `id`, `question` (one sentence, question first — never
   "Using novel data..."), `mechanism` (the friction or force),
   `displacement_hunch` (what it would displace, unverified),
   `data_hunch` (source guess, unverified), `data_route` (`held`,
   `public`, `licensed`, `purchasable`, or `restricted` — how this data
   would actually be obtained), `lens`, `cell`.
   Hunches are labeled hunches; the Material Gap rule bars dressing
   them as facts.
   Anchored mode replaces `data_hunch` with three fields:
   `data_anchor` (the held tables and fields the design would use,
   named as `source.table.field`), `data_extension` (external source,
   the join key, and the expansion-map probe supporting it, or `none`),
   and `data_class` (`anchored`, `extended`, or `unanchored`). Cards
   from reserved cells are `unanchored` and keep the `data_hunch`
   semantics. Every anchored or extended card also carries one line,
   `public_counterfactual`: why the question still matters if everyone
   held this data. That line is the guard against data-first framing,
   which the desk-reject simulation kills as additive-not-novel — a
   card that cannot fill it has no question, only an asset.

## Dedup

Cluster the raw pool on question + mechanism + setting similarity.
Merge clusters into one card each (keep the sharpest phrasing; union
the hunches); log every merge as `kept <id> <- merged <ids>` so the
distinct count is auditable. Rephrasings of one idea are the swarm's
most predictable failure; the dedup log is the proof it was handled.

## Anchor existence (machine gate, anchored mode)

Before any card enters the pool, check every name in its `data_anchor`
and every join key in its `data_extension` against `field_index` in
`data_profile`. A card naming a field the profile does not contain is
**downgraded to `unanchored`** — its `data_anchor` moves to
`data_hunch` verbatim — and the missing field is logged with the card
id. It is never scored as anchored and never silently dropped.

An extension whose probe is absent or unverified in the expansion map is
recorded as a candidate: the card stays `extended`, but F2 and F3 read
the join as unverified. A hallucinated column is the exact failure this
mode exists to prevent, and it is cheapest to catch here, before two
scorers and four debaters spend anything on it.

## Funnel floor (machine gate)

Raw pool >= 100. Short: one retry pass on the empty or weakest cells
(new agents, same isolation). Still short: proceed and log the
shortfall in the pool file and lab notebook — never silently.
Distinct-after-dedup has no floor, but a distinct/raw ratio under 0.6
is flagged (the lenses are collapsing onto each other).

Concentration flag. The ratio above is not sufficient
and a full-scale run is why: it scored 0.70 and passed while its three
largest clusters absorbed 28 of 102 cards. A ratio counts cards left
after merging and cannot see how the merged cards were distributed, so a
pool with many singletons and a few very large clusters looks healthy to
it. Report alongside it: **top-cluster share** (largest cluster over raw)
and **top-three share**. Flag a top-three share above 0.20. Also report,
for every flagged cluster, whether its mechanism matches an F0 menu
target and which cell each member card came from. A cluster that spans
many cells and matches a menu target is menu pull; a cluster inside one
cell is a generator repeating itself; a cluster spanning cells with no
menu match is genuine independent convergence and is a finding worth
keeping rather than a defect. These three read very differently and the
counts block should not blur them.

## Output

- `idea_pool` (JSON): all distinct cards, statuses `pooled`, plus the
  dedup log and the counts block (raw, distinct, per-cell, retries,
  top-cluster share, top-three share, and per-flagged-cluster the cell
  spread and whether it matches a menu target). In
  anchored mode the counts block also carries the class mix (anchored,
  extended, unanchored) and the downgrade log.
- Menu assignment record: which target each steered cell drew, which
  cells were menu-blind, and the menu shortfall if the menu was shorter
  than the steered-cell count.
- Lab-notebook entry: date, counts, the menu assignment and any menu
  shortfall, shortfall if any; in anchored mode the profile's
  `generated` date, the class mix, and the number of downgraded cards.

Merge-safe write (binding). Downstream stages (F2 scoring, F3 debate)
write per-card status changes (`cut`, `scored-out`, `graveyard`,
`benched`, ...) back into this same file. So the pool writer must never
blindly regenerate from the raw pool: on any re-run, if `idea_pool`
already exists, preserve every card whose status is not `pooled` and
only add newly generated or re-run cards (`--merge` semantics, as in
`script-registry`). A regenerate-from-raw that clobbers downstream
statuses is a reproducibility defect — refuse it. The raw pool
(`pool_raw`) stays the immutable generation record.

## Validation

Done when: pool file exists and parses; every card has all schema
fields; counts block present; every cell in the grid appears (or its
emptiness is logged); dedup log non-empty or explicitly `no merges`.
Menu rules: at least a quarter of cells are
menu-blind and their digests contain no displacement target; every
steered cell's digest carries exactly one target; no target appears in
two steered cells; the per-cell digests were written out and kept, not
generated from one shared document; the menu assignment record exists
and its steered count plus blind count equals the grid; a menu shorter
than the steered-cell count shows the surplus cells as menu-blind and
the shortfall logged, never two cells sharing a target. Concentration:
top-cluster and top-three shares are reported, and a top-three share
above 0.20 is flagged with each flagged cluster's cell spread and
menu-match status recorded.
No card carries a score, rank, or verdict — F1 output is unranked by
design. Every card names a `data_route`; a card with none is flagged
`[MATERIAL GAP: no access route named]` and cannot be scored as
anything but a 1 on data plausibility. Under `data_access: free_only`
the only admissible route is `public`, and a card naming another is
flagged the same way — the point is that the route is stated, not that
the data is cheap. In anchored mode also: the profile is present and within its
refresh cadence; the reserved unanchored share is at least a quarter of
the cells; every card carries `data_class`; every anchored or extended
card's fields resolve in `field_index` or the card was downgraded and
logged; every anchored or extended card has a non-empty
`public_counterfactual`.
the block exists with its
**saturating and rising halves explicitly separated**, every claim in each
citing a logged search; **no generator digest contains any rising item**
on the themed path, and on the swarm path no rising item appears in two
cells and no cell carries more than one; the saturating half appears in
every cell's digest on both paths; and the block reached the desk
simulation and the G1 checkpoint. A trajectory block phrased as areas to
work in, rather than as saturation and currency, is a validation failure —
it has become a gaps-to-fill list wearing a chart.

**every capability line in every data capability digest
carries N units, N periods, N clusters and a coverage window**, and a
join-dependent line carries its match rate. A digest line without counts
is a validation failure. The counts must match
`handoff/data_profile_extract.md` exactly — a digest that states a count
the extract does not is a firewall breach, since it means something was
queried outside the profile.
