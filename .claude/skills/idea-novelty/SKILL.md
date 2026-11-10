---
name: idea-novelty
description: "Funnel layer F3 step 1.5: the contribution judge. Asks the question the occupancy audit cannot — not *has someone done this design* but *what would we learn, from which theory, and does that theory have supportive evidence yet*. Four blocks per surviving card: the literature strand the empirical question joins; the theoretical prediction it bears on, on an established/contested/untested/none ladder where `untested` must name the observability barrier and carry the searches that failed; an outcome-conditional contribution table stating what the paper says under the predicted sign, a null, and a reversal, where no live cell is a terminal contribution-null; and verification of the card's generator-asserted displacement hunch against the target's actual claim. Searches the mechanism's literature rather than the theme's, which is how the occupancy pass misses a paper occupying the design in a different asset class. Verdicts PROCEED / REFRAME / CONTRIBUTION-NULL; the kill is the only irreversible verdict and needs a second independent confirmer, may never rest on a TITLE-ONLY citation, and is audited by the decision audit under defect class 7. Output is judgment-bearing and quarantined; factual corrections route into novelty_facts.md."
disable-model-invocation: true
---

# Idea Novelty (F3, step 1.5)

The contribution judge (S1b). Runs only when
explicitly invoked, after the desk simulation and **before the debate**.

Read `pipeline-config.md` first: `theme`, `ideas_dir`, `field_profile`,
`gate_mode`, `model_strong`, `paper_set`/`search_log` keys, `data_mode`.
All judgment roles run on `model_strong`. Escalation per
`playbooks/error-escalation.md`.

## Why this layer exists

Step 1.1's novelty audit is an **occupancy** check and is deliberately
facts-only: `novelty_facts.md` enters the debate briefing pack, so a judgment
placed there anchors all four roles. It can retire a card only on an occupied
margin with no open adjacent margin.

That leaves the funnel with no answer to the question an editor asks first.
Measured on a themed run:

- The occupancy audit killed **0 of 12**.
- The funnel graveyarded **0 of 8** on contribution grounds — "no role argued a
  contribution failure" — while the incrementality desk editor was
  simultaneously reporting that **8 of 12 cards aimed at one sentence in one
  2026 working paper**, four of them the same paper with the partition variable
  renamed. That finding moved a `panel_reach` rung and arrived at the menu as an
  annotation.
- A **pilot count** was terminal. A contribution judgment was not.

So the pipeline could retire a design for a sample size and not for being
pointless. This layer closes that, and closes it with authority, because an
advisory verdict is what the incrementality editor already had.

## Where it sits, and why not somewhere cheaper

**After the desk, before the debate.** The debate is **the only layer linear in
surviving cards** — every other layer is roughly constant — so it is the layer
whose size the funnel can actually control, and controlling it means killing
before it rather than inside it.

**A correction to the original rationale, which was written before anything
measured cost**. That rationale said the debate "cost 40 of 61
subagents" and that a judge here therefore "pays for itself in debate agents
never spent". The first half is true and the second does not follow. Measured:
the debate was 62% of the agent count and **12% of the run's cost**, because a
debate role costs roughly an eighth of a batched auditor, and the driver's own
thread was 63% of the total. A card killed here saves the four debate roles that
card would have run, and this judge costs more than those four roles.

The placement still stands, on two grounds that survive the measurement:
**linearity** — the debate is the one layer that grows with the slate, so a
smaller slate is the only lever on it — and **the clean room**, since four
isolated roles per card cannot be batched without breaking the isolation that
makes them worth having, and agent count is the right instrument for that
question even though it is the wrong one for budget. What does not survive is
the claim that this is the cheapest kill available. It is the *earliest*
authoritative kill available, which is a different and better argument.

- **Not before the pilot.** The pilot is the funnel's cheapest layer (0 subagents,
  driver-run) and its counts are what a contribution judgment weighs. A
  contribution table written before the sample exists cannot say whether a live
  cell is reachable.
- **Not folded into step 1.1.** That file must stay judgment-free; this one is a
  judgment.
- **Not a fourth desk editor.** The desk returns `panel_reach`, which this
  pipeline labels *judged, not calibrated* everywhere it appears, because there
  is no held-out evidence connecting any rung to an editorial outcome. A novelty
  verdict is different in kind — **it is checkable against sources**. Folding it
  into the reach ladder buries the one judgment in this stage that can be
  verified inside the one that cannot.

## The search rule — and the correction that changed what it is for

**Search the mechanism's literature, not the theme's.** That rule stands. What
was wrong was the evidence given for it, and the correction moves this layer's
centre of gravity.

**As originally recorded.** Two of the four cards that reached the menu
had a directly-occupying refereed paper, and F0's 219-paper scan, six novelty
searches, three desk editors, four debate roles, a decision audit and three G1
judges "all missed" both, because F0 was scoped to the theme.

**What the artifacts showed.** Both papers had in fact been **retrieved by
step 1.1's own searches**, verified, and written into each card's
`handoff/novelty_facts.md` as **"Closest work" item 1** — filed a full day
*before* the retrofit that reported them missing. Each was a heavily-cited
paper in a top field journal, and each stated a finding that directly answered
the card's question: one reported the very effect the card proposed to look
for, and the other measured the same quantity at a **finer resolution than the
card's best case**, so the card could not have detected anything the paper had
not already shown.

The entries were correct, verified, and sitting under the heading "Closest
work". Nothing marked either as *occupying*.

**So the failure was adjudication, not retrieval.** The funnel found both
papers, verified them, and put them in front of every downstream role under the
heading "Closest work" — and four debate roles per card, three desk editors, an
audit and three G1 judges each read that and none moved the paper from *related*
to *occupying*. A second search arm re-solves a problem that was already solved.

That is a **stronger** argument for this layer than the one it replaces. This
layer's demonstrated value on that run was not finding anything new. It was
being the first to say what a paper already in the record implied. Block 1 is
therefore the load-bearing block, and it reads `paper_set` and
`novelty_facts.md` as a set of **claims to adjudicate**, not as a reading list.

**The search rule survives on its own merits, not on that evidence.** Nothing
shows a theme-scoped scan is sufficient in general — only that it was not the
binding constraint on this run. Every query here is still built from the card's
**`mechanism`, `outcome` and `identification` codes**, deliberately without the
theme's nouns, and at least one query per card must be written so that it
*could* return work from a different asset class. What changes is the
expectation: a run where the mechanism-scoped queries return nothing new is a
normal run, not a failed layer, and the counters report new-work-found and
already-held-adjudicated **separately** so the two are never confused again.

Queries append to `search_log` and works to `paper_set` like every other layer,
so S2 inherits them. Log the mechanism-scoped queries in their own block, marked
as such — they answer a different question from step 1.1's and mixing them makes
neither block readable.

## The four blocks

One judge per surviving card, a fresh subagent on `model_strong`, never a role
that has voted on it. It reads `handoff/idea_card.md`, `handoff/novelty_facts.md`,
`handoff/pilot_report.md`, the F0 `landscape_brief.md`, and `paper_set` — and
**nothing from any `quarantine/`**, including the desk verdicts, so its judgment
is not anchored on the reach rung it will be reported beside.

### Block 1 — Question-to-literature link

Which strand the empirical question joins, and **what each named paper actually
claims** — the claim, not the topic. Start from `novelty_facts.md` and the F0
threat list; extend with mechanism-scoped searches.

A strand is named only when the judge can state what the design would add to it
in one sentence. "Related to the microstructure literature" is not a link.

**Adjudicate every closest-work entry, and this is the block's first job**. For each work already in `novelty_facts.md` or `paper_set`
that the card names or that the mechanism-scoped search returns, return one of:

| Call | Meaning |
|---|---|
| `occupies` | the work answers this card's question for this card's quantity, at a resolution, population or frequency the card does not improve on. **Quote the claim.** |
| `adjacent` | same mechanism or setting, different quantity or a materially different design |
| `context` | motivates or frames, and answers nothing the card asks |

A `context` call on a paper whose stated finding covers the card's own quantity
is the defect this block exists to catch, and it is the defect that put two
occupied designs on a themed menu. The call is made **against the card's
design parameters** — what it measures, at what resolution, on which
population — not against its topic. Where the work is already in `paper_set`,
say so; an `occupies` call on a held work is this layer's most common real
finding and is not a lesser one than a new discovery.

### Block 2 — Theory link and evidence status

Which theoretical prediction the design bears on, and that prediction's current
evidential status:

| Rung | Meaning | What it demands of the design |
|---|---|---|
| `established` | direct supportive evidence exists in a refereed setting | the contribution must come from setting or identification, **not** from the prediction. Re-establishing it at coarser resolution is a replication and must be argued as one |
| `contested` | direct evidence on both sides | **adjudicating** is a contribution; adding one more observation to one side is not. The design must say which side its result would move and why this setting arbitrates |
| `untested` | stated in theory, no direct empirical test found — usually an observability barrier | must **name the barrier** and say why *this* setting removes it. The highest-value rung and the most fragile |
| `none` | tests no stated theoretical prediction; the design is descriptive | not a kill — archetype A5 exists — but the contribution must then be carried by **measurement or first documentation**, stated as such, and the design is judged on whether that measurement is sound |

Three rules, all learned the hard way:

- **The rung is argued from a named theoretical source**, returned by a search,
  never asserted. A rung with no source is a validation failure.
- **`untested` is a negative claim about a literature** and is the single most
  likely output of this layer to be wrong. It carries **the queries that failed
  to find a test**, written into the verdict beside it, plus the standing caveat
  that a test not found is not a test absent. It may never carry a kill on its
  own.
- **A distinction that repeatedly decides the rung: the theory may predict the
  intensive margin while the design measures the extensive one, or predict
  turnover while the design measures direction.** Those are different
  predictions. A design whose theory predicts *volume* and whose outcome is
  *signed flow* is not confirming that theory — it is posing a puzzle for it,
  which is usually the better paper and is never what the card says.

### Block 3 — Outcome-conditional contribution

The block nothing else in the funnel does, and the one that answers *what would
the finding mean*:

| Outcome | What the paper then says | To which strand | A contribution on its own? |
|---|---|---|---|
| predicted sign | | | yes / no |
| null | | | yes / no |
| reversed sign | | | yes / no |

- Each cell names a **strand**, not a sentiment. "Interesting" is not a cell.
- A cell may be marked *conditional*, with the condition stated as something
  checkable — "yes, but only at a sample this design's scope does not reach" is
  a legitimate and frequently correct entry, and it is what separates a design
  that is pointless from a design that is merely mis-scoped.
- **The kill rule: if no cell is a contribution, the design is
  `CONTRIBUTION-NULL` and dies regardless of feasibility.** This is the layer's
  reason to exist. It catches the design that is well-identified, well-powered
  and pointless, which no other gate can see.
- **Cross the table against the card's pre-registration.** A design whose only
  live cell is excluded by its own one-sided hypothesis has a defect this layer
  must name — it is the cheapest real finding available here, and it is invisible
  to every other layer because each reads only one of the two documents.

### Block 4 — Displacement verification

The card's `displacement_hunch` is a generator assertion that nothing has ever
checked. On one themed run **9 of 20 cards named the same target** and no
layer retrieved it. Retrieve the target's actual claim and return one of:

| Label | Meaning |
|---|---|
| `verified` | the target claims what the card says it claims, **and** the card's finding would change it |
| `additive` | the finding adds something the target does not contain but overturns nothing it claims — the most common honest label, and one rung below what hunches assert |
| `misread` | the target claims something else. Quote both |
| `unverifiable` | the target is TITLE-ONLY, or **the hunch names only artifacts internal to this run** — a cell id, an archetype label, another card. A displacement target drawn from the run's own scaffolding is not a displacement target |

A `misread` is not fatal on its own; the usual remedy is deleting the
displacement sentence, not the card. Record which.

## Verdicts

| Verdict | Meaning | Route |
|---|---|---|
| `PROCEED` | at least one live contribution cell, positioning defensible | into the debate unchanged |
| `REFRAME` | a contribution exists but not the one the card names | the reframe is written into `handoff/idea_card.md` as a required framing note and the card proceeds. **It does not enter the revision clinic**, so it never spends that budget |
| `CONTRIBUTION-NULL` | no live cell | graveyard |

**`REFRAME` never silently becomes a new card.** If the reframe changes the data
scope or the source, the pipeline's standing rule applies — *a source or scope
swap is a different idea and re-enters as one* — so the judge says so explicitly
and the reframe is routed as a new card crediting the parent, exactly as the
fallback triage handles a named setting swap.

### The confirmer rule

**`CONTRIBUTION-NULL` is the only irreversible verdict and requires a second
independent judge to confirm it**, on a fresh context, from the same inputs, with
no sight of the first verdict. Both must reach `CONTRIBUTION-NULL` or the card
routes on the more conservative verdict.

This is not caution for its own sake. Every terminal layer this pipeline has
left unreviewed has been measured wrong at scale — the pilot's kills came back
**55% disturbed** the first time anything audited them, and a wrong kill is
invisible forever because nobody reads the paper that was never written. The
expensive path is therefore rare and sits exactly on the irreversible decision.

Three further constraints on a kill:

- It must **quote the occupying paper's verified claim**. A TITLE-ONLY citation
  can never carry one (Material Gap rule).
- It may not rest on an `untested` rung — a negative claim about a literature is
  not evidence that a design is pointless.
- It is **in scope for the decision audit** under defect class 7, with a
  layer-matched control drawn from the novelty-cleared cards.

## What this layer must never do

- **Never hand a theory list to a generator.** In one run the occupied-margin
  blocklist became a displacement-target menu — 9 of 20 cards named one target —
  because the generator pack required naming one from an eight-item list. A
  theory list would reproduce that attractor with theories, and there is no
  partition available to break it. **Theory and contribution assessment is
  judge-side only. The card schema does not change**, and `idea-variants` and
  `idea-swarm` are deliberately untouched by this layer.
- **Never put its verdict in a briefing pack.** Same anchoring rule that keeps
  `novelty_facts.md` judgment-free.
- **Never report a theory rung without its source, or an `untested` rung without
  its failed queries.**
- **Never re-argue feasibility.** Sample size is the pilot's, identification is
  the methods referee's. A verdict that rests on "the sample is small" is out of
  scope — except as a *condition* inside a contribution cell, where the honest
  entry is that a cell is live only at a sample this design does not reach.

## Artifacts

- `quarantine/novelty_verdict.md` — the four blocks, the verdict, the confirmer's
  verdict where one ran. Judgment-bearing; never enters a briefing pack.
- Factual corrections land in `handoff/novelty_facts.md`, following the decision
  audit's existing rule that a factual finding belongs in the facts file so a
  re-entering card carries the corrected fact and none of the argument.
- A required framing note appended to `handoff/idea_card.md` on `REFRAME`.
- Machine-readable block at the end of `novelty_verdict.md`, mirroring the
  `verdicts` block convention — downstream gates read this, never the prose:

      ```novelty
      theory_status: untested
      theory_source: <returned citation carrying the rung>
      displacement: additive
      contribution_cells: 1
      verdict: REFRAME
      confirmer: n/a
      ```

  `contribution_cells` is the count of live cells out of three and **must match
  the table above it**. `confirmer` is `n/a` unless the verdict is
  `CONTRIBUTION-NULL`, where it is that judge's verdict.

## Counters

Append to `ideas_dir/comparative_final.md` alongside the existing counters
block: the verdict distribution across the slate; the theory-status distribution;
the displacement-label distribution (`verified` / `additive` / `misread` /
`unverifiable`); the contribution-cell histogram; **debate agents saved and
debate cost saved**, as cards killed here times the measured per-card debate
agent count and per-card debate cost; and this layer's subagent count **and
cost**, kills confirmed and kills reversed by the confirmer reported separately.

**Report cost beside agents, and be honest about what it says.** A card killed
here saves the four debate roles that card would have run. This layer's own
judge costs more than those four roles. On cost alone the layer does not pay for
itself, and a counters block that reported only agents saved would imply it
does.

That is not an argument against the layer, and the placement does not change.
It is an argument that **the layer is bought for what it catches, not for what
it saves** — it is the only gate in the funnel that can retire a design for
being pointless, and on that run the funnel graveyarded 0 of 8 on contribution
grounds while a pilot count was terminal. Record both numbers so the next
design decision argues from the real one. The claim this replaces — that a kill
here is the cheapest kill available because the debate is the expensive layer —
was true about agent counts and false about cost.

**Report new work found and held work adjudicated as two numbers, never one**. The `occupies` / `adjacent` / `context` distribution from
Block 1, split by whether the work was already in `paper_set` before this layer
ran. One run's record collapsed the two and reported an adjudication as a
discovery, which is how a retrieval diagnosis got written from an adjudication
defect. A run that finds no new work and reclassifies two held ones is a
productive run, and the counters have to be able to say so.

**Report the novelty ordering of the menu against the feasibility ordering, with
their rank correlation.** A run where they coincide exactly is a run where this
layer added no information to G1, and that must be visible rather than inferred.
On the first retrofit trial ρ = 0.6 with every adjacent pair swapped.

**Report the displacement-label distribution at the run level, beside the menu**. The per-card label already lives in each lineage directory,
and that is where it goes to die: on the retrofit trial there were **zero
`verified` labels across four cards whose hunches all asserted displacement**,
and that fact was only visible to someone who opened four files and compared
them. A run that displaces nothing is making a statement about its **theme**,
not about four cards — it is the same signal the DECLINE triage reads as a
contribution-thin slate — and the author sees it at G1 or not at all.

One line beside the menu: `displacement: 0 verified / 2 additive / 1 misread /
1 unverifiable across 4 items`. No interpretation from this layer; the
distribution is the finding.

Each menu item in `comparative_final.md` carries its novelty verdict beside its
advisory reach, **stated as the checkable judgment against the uncalibrated
one**.

## Validation

Done when:

- Every card entering this layer has a `novelty_verdict.md` with all four blocks
  and a parseable ```novelty block whose `contribution_cells` matches its table.
- Every theory rung names a **returned** source; every `untested` rung carries
  the queries that failed and the caveat; no rung is asserted.
- **Every closest-work entry carries an `occupies` / `adjacent` / `context`
  call** against the card's design parameters, every `occupies` call quotes the
  claim, and each call records whether the work was already in `paper_set`. An
  entry summarised without a call is a validation failure — that is the state
  the whole funnel was in.
- At least one **mechanism-scoped** query per card appears in `search_log`,
  written without the theme's nouns, in its own marked block; every work found
  is in `paper_set`.
- Every `displacement_hunch` carries one of the four labels, and a `verified` or
  `misread` label quotes the target's own text.
- **No `CONTRIBUTION-NULL` without a second confirmer**, and none resting on a
  TITLE-ONLY citation or on an `untested` rung. A kill quotes the occupying
  paper's verified claim.
- **`grep -rn "novelty_verdict" <ideas_dir>/*/handoff/` returns nothing** — the
  verdict never crossed the quarantine boundary, and no briefing pack contains it.
- Every `REFRAME` that changes data scope or source is routed as a new card
  crediting the parent, not as a repair.
- Every terminal `CONTRIBUTION-NULL` carries a decision-audit verdict under
  defect class 7, and the layer-matched control (a novelty-cleared card) was
  audited.
- The counters block is present, including the novelty-versus-feasibility rank
  correlation and the debate-agents-saved figure.
- Lab-notebook entry written: date, cards judged, verdict distribution, which
  occupying papers the mechanism-scoped search found that step 1.1 did not.
