---
name: idea-variants
description: "Funnel layer F1-T (themed path): turns one general theme into 8-12 deliberate versions of it, varied along mechanism, outcome variable, identification strategy, and unit of observation, so the design space of a single question is covered rather than a topic space searched. Reserves 2-3 theme-blind cells as a control against the theme itself being wrong. Runs after F0-narrowed and before the up-front feasibility pilot; issues no scores and no ranks. In data_mode: anchored every variant carries verified anchor fields and a data capability digest whose every line carries its counts. Replaces idea-swarm plus idea-scoring when pipeline-config.md sets a theme."
---

# Idea Variants (F1-T, themed path)

The generator of the themed path (S1).
Runs when `pipeline-config.md` sets `theme`; `idea-swarm` and
`idea-scoring` run instead when it does not.

Read `pipeline-config.md` first: `theme`, `ideas_dir`, `idea_pool`,
`field_profile`, `gate_mode`, `model_default`, `data_mode` (plus
`data_profile` and `peek_log` when `data_mode: anchored`).


## When to use

Driven by `run-pipeline` as stage S1 on the themed path, or named directly by
the author to regenerate a variant set after a re-theme. Not a brainstorming
tool: it expands one `theme` sentence into deliberate variants against a fixed
cell plan, and its output is a pool for F2, not a menu for a reader.

Do not run it when `theme` is unset. The swarm path (`idea-swarm` then
`idea-scoring`) is the generator in that case, and running both produces two
pools that no later layer knows how to reconcile.

## Why this is not the swarm with a topic attached

The swarm and this layer optimize opposite things, which is why they are
separate skills with separate prompts rather than one skill with a flag.

| | `idea-swarm` | `idea-variants` |
|---|---|---|
| Given | a field and a lens grid | one question area |
| Maximizes | **spread** across a topic space | **coverage** of one question's design space |
| Good output | 100-120 cards that disagree about what to study | 8-12 designs that agree on what to study and disagree on how |
| Failure it fights | every cell converging on the same obvious margin | every variant being the same design reworded |

A swarm pointed at a theme generates 60-120 cards to find variants of
something already in hand, and then pays a rubric cut to get back to a
dozen. That is the machinery the themed path exists to skip.

## Step 1: read the theme, and do not improve it

The theme is the author's. Do not narrow it to something easier to
execute, do not broaden it to something easier to defend, and do not
resolve an ambiguity in it silently — an ambiguity that changes what the
variants would be is a question for the author (human) or a PARK
(autonomous).

Write the theme verbatim into `ideas_dir/theme.md` with the date, and
record any ambiguity found and how it was resolved. Every later layer
reads the theme from that file, so a theme that drifts mid-run is visible
rather than inferred.

## Step 2: the variation grid

Build 8-12 cells. Each cell is a **deliberate variation of the theme along
one or two axes**, and the axes are fixed:

1. **Mechanism** — which friction or force is doing the work. Two variants
   of one question that name the same mechanism are one variant.
2. **Outcome variable** — what is measured. Prices, quantities, spreads,
   entry and exit, survival, composition.
3. **Identification strategy** — what makes the comparison credible. A
   discontinuity, a staggered rollout, a cross-sectional exposure
   difference, a within-unit switch, a structural restriction.
4. **Unit of observation** — the level the design runs at. This axis is
   the one most often skipped and the one that most often kills a design
   later: a question posed at the event level and identified at the
   contract level is a different paper from the same question at both.

Record the grid before generating: cell id, the axis or axes it varies,
and what it holds fixed. A grid that cannot say what a cell holds fixed
has not varied anything on purpose.

**Reserve 2-3 theme-blind cells.** Those generators receive the field
profile, the F0 brief, and the data capability digest — and **not the
theme**. They generate as the swarm would.

This reservation is the only structural guard against the risk the whole
themed path carries, and it is a partial guard, not a cure:

> **A themed entry cannot tell you the theme is wrong.** The open funnel at
> least searches elsewhere; this path optimizes within the author's
> premise. If the theme is a bad bet, this path will find the best
> available version of a bad bet and will do it efficiently.

So the theme-blind cells' output is never discarded for being off-theme,
and their fate is reported at G1 alongside the menu. A run where a
theme-blind card outranks every themed variant on feasibility is telling
the author something about the theme, and that signal is destroyed if the
off-theme cards are quietly dropped.

The theme-blind reservation and anchored mode's unanchored reservation are
**independent draws** over the same grid, exactly as in `idea-swarm`. A
cell may be both, one, or neither.

## Step 3: generation

One generator per cell, a fresh subagent on `model_default`, isolated: it
sees the theme (unless theme-blind), its own cell's axis assignment, the
field profile, the F0 brief's occupied-margin blocklist, and — in anchored
mode — the data capability digest. Never another cell's output, the state
file, or any judgment about any idea.

Each generator returns **one to two cards**, not eight to ten. This is the
other half of the difference from the swarm: a themed cell that returns
ten cards has produced ten rewordings of one design, which is the failure
mode this layer is built to prevent. Ask for few, and require that they
differ on the named axis.

**Card schema is unchanged** from `idea-swarm`, so every downstream layer
reads the same fields: `id`, `question`, `mechanism`, `displacement_hunch`,
`data_route`, `lens`, `cell`. Anchored mode replaces `data_hunch` with
`data_anchor`, `data_extension`, and `data_class`, and requires
`public_counterfactual`. Two fields are added here:

- **`varies`** — the axis or axes this card varies from the theme's
  default reading, and what it holds fixed.
- **`theme_blind`** — true for cards from reserved cells.

**The data capability digest carries counts on every line** (N units, N
periods, N clusters, coverage window, and match rate for a join-dependent
line), copied from `handoff/data_profile_extract.md` and never recomputed.
A generator that cannot see a population size will design against an
imagined one: that has already cost four cards and a full four-role
debate on a family of **12 markets over 2 meetings**.

## Step 4: dedup on design, not wording

Cluster on **(mechanism, outcome, identification, unit)**, not on question
text. Two cards that share all four are one variant however differently
they are phrased; two cards that share a question sentence but differ on
identification are two variants and both survive.

This is the inverse of the swarm's dedup problem. The swarm merges cards
that say the same thing differently; here the risk is *failing* to merge
cards that say the same thing in different words, because the theme makes
them all sound alike. Log every merge as `kept <id> <- merged <ids>` with
the shared tuple named.

If dedup takes the pool below 8, generate again on the axes that collapsed
rather than accepting a thin grid. Report the regeneration in the counts
block.

## Step 5: the contrast pass

**The grid varies designs. Nothing recombines them, and that is where the
benchmark says the misses are.**

Every partial rediscovery in the head-to-head benchmark is the same failure:
the pipeline generated *both halves* of a human idea in separate cells and
never posed the contrast. One card asked whether a leading indicator predicts
an outcome while two others carried the outcome half and the activity half
separately, and no card put activity against outcome on one axis. Another card
took the anticipation half of a mechanism and a fourth took the staleness half,
and no card put the two windows on one axis. Four of eight human ideas were
partially rediscovered and none cleanly, and this is why.

Isolation is what produces the halves — each generator sees one cell — so the
fix cannot be to relax isolation. It is to add one pass that reads the grid's
*output* after dedup, when isolation has already done its work.

**One agent, after dedup, on `model_mid` or better.** It receives the distinct
cards' **`(mechanism, outcome, identification, unit)` codes and nothing else**
— no card prose, no question text, no F0 blocklist, no displacement targets, no
theme. It returns 2-4 **contrast cards**, each of which puts two existing
cards' halves on one axis, naming both parents.

Contrast cards enter the pool as ordinary cards, credited to their parents, and
are piloted with the rest. They are not privileged and not exempt from
anything.

The code-only input is the guard, and it is not optional. Handing this agent
prose or a target list would reproduce the shared-menu attractor at exactly the
point in the funnel where a shared menu does the most damage — one agent seeing
every card is the one place a target menu could capture the whole pool at once.
Codes cannot carry a target. **A contrast card that names a displacement target
is a validation failure**, not a card to be edited.

The pass runs once. If it returns nothing — no two cards' halves meet on an
axis — that is a finding about the grid and goes in the counts block; it is not
a reason to run it again with more input.

## What this layer does not do

- **No scores.** There is no rubric cut in the themed path. Cards are
  unranked leaving here, and the next layer is the pilot.
- **No verdicts, no kills.** The F0 blocklist can mark a card threatened;
  it cannot retire one from inside this layer.
- **No feasibility judgment.** Sizing is the pilot's job and it runs next,
  on every variant. A generator that writes "sample should be adequate"
  has asserted the thing the next layer exists to count.

## Output

- `idea_pool` with every card, its `varies` and `theme_blind` fields, the
  grid, the dedup log, and a counts block: cells run, cards raw, cards
  distinct, theme-blind count, anchored/extended/unanchored mix, any
  regeneration, and **contrast cards returned with their parent pairs** (or
  zero, with the observation that no two cards' halves met on an axis).
- `ideas_dir/theme.md`, the grid record, and the per-cell digests written
  out individually and kept — a run that hands one shared digest to every
  cell has not varied the assignment, and keeping them is what makes that
  checkable after the fact.
- Lab-notebook entry: date, theme, grid shape, distinct count, which axes
  collapsed in dedup.

## Validation

Done when: `theme.md` exists and matches `pipeline-config.md` verbatim;
the grid record exists and every cell names the axis it varies and what it
holds fixed; the pool has **8-12 distinct cards** after dedup, or the
regeneration is logged; every card carries `varies`; at least **2 cells
are theme-blind** and their generators provably received no theme; the
dedup log names the shared tuple for every merge; no card carries a score,
rank, or verdict; every card names a `data_route`.

For the contrast pass: it ran once after dedup; **its input
transcript contains design codes only** — grep it for card prose, question
text, the theme string, and any blocklist or target line, and a hit is a
validation failure; every contrast card names two parents that exist in the
pool; **no contrast card names a displacement target**; and the counts block
reports how many were returned, zero included.

In anchored mode also: the profile is present and within its refresh
cadence; every card carries `data_class`; every anchored or extended
card's fields resolve in `field_index` or the card was downgraded and
logged; every anchored or extended card has a non-empty
`public_counterfactual`; the reserved unanchored share is drawn
independently of the theme-blind draw; and **every capability line in
every digest carries its counts**, matching the profile extract exactly.
