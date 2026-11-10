---
name: idea-debate
description: "Funnel layer F3: runs the surviving idea set through the pipeline's deepest layers: a novelty audit that positions each idea against the closest literature and verifies its citations (seeding the S2 paper set) and a three-editor desk simulation that returns a panel_reach estimate rather than a binary (only a median reach of none kills), then the contribution judge (`idea-novelty`, step 1.5) which asks what the finding would mean under each possible result and can retire a design that is feasible and pointless, then a four-role clean-room debate (advocate, skeptic, feasibility assessor, methods referee) at adaptive depth, feasibility pilots whenever no role voted KILL, a decision audit that reviews every terminal decision — kills and advances alike, pilot verdicts included on the themed path — for literature error, missed remedy, category error, role capture, unverified premise, or a counting definition that does not match what the design requires, and a G1 verdict step that scores every surviving card on the finance-idea-screening ladder (top-generalist-candidate / strong-field-candidate / revise / kill) against a declared `g1_threshold` and returns however many clear it — none, one, or many. G1 is two-sided: it refuses cards below the bar and hands every strong-field card the gate that capped it plus the cheapest action that would clear it, for author-triggered rework. When nothing clears the bar, the stage states that count first, reports the DECLINE diagnosis, and then presents a separately-labelled g1_fallthrough tier for author review rather than ending the run; the tiers are never merged and ARCHIVED now needs both tiers empty. Every presented card, slate or fallthrough, also carries a 1-2 page research_proposal.md on the seven-section Bayes outline (working title, background naming the discipline, research questions answering what is new, focused literature review, data and methodology, implications, references) — written as a rendering of the card's verified handoff artifacts, never as new generation, with a fallthrough proposal stating on its face that the card did not clear the bar. Feasibility is Gate F, hard, and can refuse a card at any score. Every gate is marked checkable or judged, and a rung asserts gate clearance and never a predicted placement. Enforces role isolation, the quarantine/handoff artifact split, measure-before-repair routing (the revision clinic runs only downstream of an infeasible pilot), dispositional diversity on every panel that votes, and fallback triage by failure type. Each slate item carries its computed usable sample, its named binding constraint, and the cheapest action that would relax it; reach is advisory and always labelled judged-not-calibrated. In data_mode: anchored the feasibility assessor queries the held data instead of arguing about it, and access failures route separately from data failures."
disable-model-invocation: true
---

# Idea Debate (F3)

The funnel's last layer (S1b). Runs only
when explicitly invoked. Sequencing is cheapest-first: audit and desk
screen kill before the panel spends tokens; the panel routes before
pilots run code; the decision audit then reviews what the deciding layers
did, before the comparative final ranks what survived them.

Read `pipeline-config.md` first: `theme`, `ideas_dir`, `field_profile`,
`gate_mode`, `model_strong`, `paper_set`/`search_log` keys,
`calibration_file`, `data_mode` (plus `data_profile` and `peek_log`
when `data_mode: anchored`). All judgment roles run on `model_strong` (L11).
Escalation per `playbooks/error-escalation.md`; gate resolution per
`playbooks/gate-modes.md`.

## What arrives here, by path

| | Themed path (`theme` set) | Swarm path (no `theme`) |
|---|---|---|
| Arrives from | `idea-variants`, 8-12 cards | `idea-scoring`, a 20-25 cut |
| Already piloted? | **yes, all of them** | no |
| Steps 1-2 run on | **pilot survivors only**, typically 2-3 | every card in the cut |
| Pilot's place | before this skill, as a universal screen | inside step 2's routing, as a gate |

On the themed path the expensive layers are spent only on designs already
known to be executable, which is the whole economy of that path: the
one run spent 23 subagents on the first pass, and this ordering
targets 12-15.

Two rules that come with it, both learned from the first decision audit:

- **Every debate briefing pack carries the card's pilot report.** It is a
  statement about sample size and nothing else.
- **A `feasible` pilot verdict carries no weight on identification.** The
  audit found a card advanced because three roles' estimand objection was
  routed to a pilot, which then answered a count the record had already
  answered while the identification defect went unaddressed. The pilot
  removes the infeasible; this layer is still where credibility is
  attacked, and a card that cleared a pilot arrives here unexamined on
  every question the pilot does not ask.

## Step 1: kill layers (per idea, cheapest first)

1. Novelty audit + positioning: logged literature searches
   (OpenAlex-primary/Corbis-confirm, queries into the search log) for
   the closest papers, starting from the F0 `landscape_brief.md` threat
   list rather than a cold search. Every novelty claim backed by a
   logged search (Material Gap rule). Then two hardening steps that make
   the audit a real positioning pass, not just an occupancy check:
   - **Position it** (reuse workspace `literature-positioning-map`
     ex-ante, read in place): place the idea against the closest strands
     with an explicit threat list and the exact differences it claims.
   - **Verify what it cites** (reuse workspace `verify-citations`, read
     in place): every paper `novelty_facts.md` names is verified
     field-by-field against search before it enters the file; an
     unverifiable entry is marked `[MATERIAL GAP: unverified citation]`
     and never asserted as fact (the Palmon-Sun-Tang failure the gated
     arm hit).
   Occupied margin with no open adjacent margin: graveyard, record the
   occupying paper. Output either way: `novelty_facts.md` — closest
   papers, positioning, exact differences, verified findings only, no
   judgments — into `handoff/`. **Each closest-work entry states the
   design-relevant comparison against the card**: the quantity the work
   measures, at what resolution, on which population and at what frequency,
   set against what the card proposes to measure. Facts, not a verdict — but
   facts chosen so the reader cannot miss an occupancy. Accumulate every paper found into
   `paper_set` and every query into `search_log`, so S2's literature
   review inherits the idealization stage's work instead of restarting.
2. Desk simulation: the three-editor pass from the workspace
   `finance-idea-screening` skill (read in place), calibrated to
   `field_profile`. Verdicts go to `quarantine/desk_verdicts.md` —
   judgments anchor, so they stay out of briefing packs.

   **Calibration freshness (machine gate).** Before any
   editor runs, check `calibration_file` exists and is newer than six
   months. Missing or stale blocks the desk simulation entirely — stop and
   ask (human) or PARK (autonomous). There is no capped-verdict fallback:
   an uncalibrated reach estimate shapes the whole menu, and a calibration
   set two years old is a claim about a literature that has moved.

   This gate previously lived only in `idea-scoring`, which does not run on
   the themed path — so removing F2 from that path silently removed the
   only freshness check on the calibration set. Duplicated here on purpose:
   both paths reach this layer, so this is where the check belongs.

   **Currency check.** The editors also receive F0's
   trajectory block — **both halves**, since this is where the rising half
   is safe to read: three editors judging one finished design cannot turn a
   list of gaining areas into a generation attractor, which is why it is
   withheld upstream and delivered here.

   The question it adds is *would this still read as current to an editor
   two years from now* — the lag between a design being chosen and a paper
   being read. A design can be unoccupied, feasible, and well identified
   and still arrive into a margin that has since crowded, or lean on a
   method that has become table stakes rather than a contribution. That
   judgment belongs in reach, not in a kill: it moves a rung, it does not
   retire a card, and an editor citing trajectory must name the specific
   saturating margin or method rather than gesturing at fashion.

   **Each editor returns a reach estimate, not a binary**: how far it judges
   this paper would carry before an editor stopped sending it to referees.

   | `panel_reach` | Meaning |
   |---|---|
   | `very-high` | would go to referees at the most selective outlets in the `field_profile` |
   | `high` | below those, at the strongest specialist outlets |
   | `moderate` | a solid specialist paper |
   | `low` | carries as a note, comment, or replication |
   | `none` | would not go to referees anywhere |

   The card's reach is the **median** of the three editors. Only a median
   of `none` kills; everything else survives carrying its reach, which the
   comparative final and G1 both report.

   Why this replaced a binary: the pipeline had exactly one bar, so "would a
   top-3 editor desk reject this" was the only question ever asked and "not
   top-3" was indistinguishable from "dead". Across four runs that produced
   nothing. A ladder lets the stage say what an idea *is* rather than only what
   it fails to be.
   **The reason once recorded here was "the calibration set is all top-3", and
   it was wrong twice over.** An early build did have empty contrast classes
   in-field, so the pipeline had one bar not because the set was all top-3 but
   because nothing in it sat below the top for that field. That was a defect in
   the *build*, not a property of the design, and rebuilding the set fixed it.
   **Read the in-field per-class counts from `calibration_file` at run time and
   report them; never quote a snapshot from this page.** A count baked into a
   skill goes stale silently and has twice been the reason a gate reported
   `no verdict possible` on an anchor that actually cleared. The desk ladder
   stands; G1's threshold carries the consequence explicitly, capping at Gate D
   only when a class is genuinely unusable on the file in front of it.

   **Why the rungs stopped being named after journals**. The
   previous labels were `top-3`, `strong-field`, `field`, and
   `note-or-replication`. Those are the names of real outcomes, and using
   them implied the ladder had been checked against real outcomes. It has
   not. **There is no held-out evidence connecting any rung to an editorial
   result** — that is the durable half and it is why the rename stands. The
   half recorded here as "the calibration set is 62 papers, all top-3" is
   wrong: it is 43 accepted / 17 stalled / 2 uncertain,
   and the operative gap is that **0 of the stalled entries are finance
   papers**, so the set has no below-the-top evidence *for this field* rather
   than none at all. Naming a rung `field` still asserted a measurement the
   stage cannot make; `moderate` says what it is, which is where three model
   editors landed.

   **Reach is judged, not calibrated, and every artifact must say so.**
   Anchoring it to real outcomes belongs to `calibrate-rubric` and has not
   been done. Never report a reach without that qualifier. Renaming the
   rungs removed a false implication; it did not add evidence, and it is
   not a substitute for calibrating them.

## Step 1.5: the contribution judge

Invoke `idea-novelty` on every card the desk did not kill, **after the desk and
before the debate**. Full spec in that skill; what belongs here is why it sits in
this sequence and what this skill owes it.

**What step 1 cannot do.** Step 1.1 is an *occupancy* check and is deliberately
facts-only, because `novelty_facts.md` enters the debate briefing pack and a
judgment there anchors all four roles. It can retire a card only on an occupied
margin with no open adjacent one. On a themed run it killed **0 of
12**, the funnel graveyarded **0 of 8** on contribution grounds, and a *pilot
count* was terminal while a contribution judgment was not. The funnel could
retire a design for its sample size and not for being pointless.

**Why here and not somewhere cheaper.** The debate cost **40 of 61 subagents** on
that run and is the only layer whose cost is linear in surviving cards. A judge
at one agent per survivor that removes three of twelve pays for itself in debate
agents never spent. Before the pilot is wrong — a contribution table written
before the counts exist cannot say whether a live cell is reachable. A fourth
desk editor is wrong — the desk returns `panel_reach`, labelled *judged, not
calibrated* everywhere it appears, and folding a **source-checkable** judgment
into the one ladder this stage admits it cannot verify hides the better signal
inside the worse.

**What this skill owes it.** The judge is a fresh subagent on `model_strong` that
sees no `quarantine/` content — the desk verdicts included, so its judgment is
not anchored on the reach rung it will be reported beside. Its own output is
judgment-bearing, goes to `quarantine/novelty_verdict.md`, and **never enters a
briefing pack**; factual corrections land in `handoff/novelty_facts.md` under the
same rule step 3 already follows.

**Its verdicts and their routing.** `PROCEED` into the debate unchanged.
`REFRAME` writes a required framing note into `handoff/idea_card.md` and the card
proceeds — it does **not** enter the revision clinic, so it never spends that
one-re-entry-ever budget; a reframe changing data scope or source is routed as a
new card crediting the parent, per the standing rule that a source swap is a
different idea. `CONTRIBUTION-NULL` is the graveyard, is the only irreversible
verdict, and **requires a second independent confirmer** plus a quoted verified
claim from the occupying paper. It is in scope for step 3 under **defect class
7**, with a layer-matched control drawn from the novelty-cleared cards.

**The one finding from its first trial that changes how step 1.1 should be
read**. It was recorded
here that two of the four menu items had a directly-occupying refereed paper
"that nothing in the run surfaced", and that a theme-scoped occupancy check was
the cause. **Both papers had been surfaced** — by step 1.1's own searches, verified, and
filed as `handoff/novelty_facts.md` **"Closest work" item 1** a full day
*before* the retrofit that reported them missing. Both were heavily-cited
papers in top field journals. One entry stated in bold that the effect
completes at a resolution finer than its card's best case, so the card could
not have detected anything that paper had not already shown. Paths and
timestamps are in the project's evidence notes.

**So step 1.1's defect is not what it retrieves, it is what it hands over.**
Four debate roles per card, three desk editors, an audit and three G1 judges
each read those entries and none moved the paper from *related* to *occupying*.
Two consequences, both binding on step 1:

- **Every "Closest work" entry carries the design-relevant comparison against
  what the card proposes** — same quantity? at what resolution, population,
  frequency? — stated as **facts**, never as a verdict, since this file enters
  the briefing pack and must stay judgment-free. An entry that summarises a
  paper without saying how it lines up against the card's own parameters is the
  state a whole funnel has been in, and it fails validation.
- The **explicit** `occupies` / `adjacent` / `context` call belongs to step 1.5,
  which is a judgment layer and quarantined. Step 1 lays the comparison out;
  step 1.5 rules on it.

The mechanism-scoped search rule still holds — nothing shows a theme-scoped scan
is sufficient in general — but it is a search rule on its own merits and no
longer the fix for this defect.

## Step 2: the debate (clean room)

Briefing pack per idea: `handoff/idea_card.md` (score-free by F2
construction) + `novelty_facts.md`, plus — in anchored mode —
`handoff/data_profile_extract.md` from F-1. Nothing else: no F2 scores,
no desk verdicts, no state file, no other idea's debate. The pack never
carries a `data_availability.md`: that memo is the feasibility
assessor's own position, written during the debate, so it cannot also
be an input to round one. **Nor does it carry `novelty_verdict.md`**: the
contribution judge's verdict is a judgment on the same grounds the advocate and
skeptic are about to argue, and handing it to them decides the argument. The
`REFRAME` framing note *does* travel, because it lives on the card and is the
card's own framing, not a verdict on it.

Four roles, each a fresh subagent on `model_strong`:

- **Advocate** — strongest honest case; protocol: the advocate side of
  peer-review's contribution panel (workspace `peer-review`, read in
  place).
- **Skeptic** — SKEPTIC disposition from
  `peer-review/references/referee-dispositions.md`, ex-ante mode:
  attacks the planned contribution's fragility, not estimated results;
  cites the briefing pack or a logged search, never memory.
- **Methods referee** — CREDIBILITY disposition, ex-ante mode: can any
  credible design answer this at achievable power.
- **Feasibility assessor** — data availability: named sources with
  their access route, expected coverage, variation, measurement. Writes
  `data_availability.md` as its position; every claim cites a source,
  logged search, or number.
  Anchored mode: the assessor holds read-only query access to the held
  data and the F-1 profile extract in its pack, under one binding rule
  — **an objection a query can settle must be settled by a query, not
  asserted.** "The identifier may be unstable" is not a position; the
  vintage-to-vintage switch count is. Its probes obey the peek firewall
  (no relation between two substantive variables) and append to
  `peek_log` like any other query. This is the change that makes the
  pilot gate reachable: across six real debates in the validation runs
  the assessor voted REVISE five times and KILL once and never EXPLORE,
  so under the original unanimous-EXPLORE gate that one role decided
  every outcome. Under the current no-KILL gate its REVISE votes no
  longer block a pilot, and what changes here is that its objections
  resolve to numbers rather than arguments.

Rounds: round 1 positions are written blind and in parallel; rebuttals
unlock only when all four are filed. Adaptive depth: one round by
default; rounds 2-3 run only while verdicts disagree or change; cap 3.
Verdicts: EXPLORE / REVISE / KILL.

Routing is **measure before repair**. Read the verdicts, then classify what the REVISE and KILL
objections actually rest on, because the classification decides the route.

- **No KILL: pilot** (invoke `idea-pilot`). Zero KILL votes is the whole
  gate; EXPLORE votes are not required. Four REVISE and no KILL runs a
  pilot. Rationale in `idea-pilot`'s gate history: REVISE is what an
  adversarial role returns when it has found something worth naming, and
  what it names is usually countable.
- **Any KILL, objections are contribution-type: graveyard.** Contribution
  objections dominate execution objections. If any role's record contains
  a strawman-displacement or additive-contribution finding, the card is a
  contribution failure and is retired even when other roles' REVISE votes
  rest on fixable execution problems. Polish does not create a margin.
- **Any KILL, objections are execution or counting only: fallback triage**
  (below), which may route to the revision clinic when a role named a
  concrete design fix.

### The clinic is downstream of the pilot, not parallel to it

A card never enters the revision clinic on debate verdicts alone. The
clinic runs only on a card whose **pilot returned `infeasible`**, or on a
card triaged there with no pilot available. One rework by a fresh agent
(never the advocate) from the record's named findings; the reworked card
re-enters step 1 in full. One re-entry per idea, ever.

Why this ordering, from one run: the single viable card carried
three REVISE votes, and all three rested on countable questions (how many
event series carried a complete price partition, how many observation days
survived synchronisation). Routed to the clinic, those questions were
answered by assumption; the rework conceded scope on each one, and three
fresh editors then rejected the narrowed paper unanimously at high
confidence. Routed to the pilot, the same questions cost a handful of
queries and the answer either clears the card or kills it on a number.

A rewrite can only narrow. Narrowing is what the desk rejects. So the
cheap measurement runs first, and the expensive rewrite runs only when
measurement says the card is genuinely infeasible as posed.

Artifacts: full transcript, rebuttals, verdict table by round to
`quarantine/debate_record.md`; refined idea card and
`data_availability.md` to `handoff/`.

Machine-readable verdict block (required, at the end of
`debate_record.md`): a fenced ```verdicts block holding the FINAL round
only, one `role: EXPLORE|REVISE|KILL` line per role plus `rounds: N`.
Downstream gates (idea-pilot's entry gate, the run driver) read this
block, never the prose — free-text parsing misfires on phrases like
"REVISE (from EXPLORE)". Example:

    ```verdicts
    final_round: 2
    advocate: REVISE
    skeptic: REVISE
    methods_referee: REVISE
    feasibility_assessor: KILL
    ```

### Any number carrying a KILL is re-derived first

**Before the verdict block is written, every number a KILL vote rests on is
independently re-derived, and the re-derivation is recorded beside it.**

The measured evidence points both ways. Eleven figures in one run were
independently confirmed and held; the two that were never confirmed are the two
that failed. On the advance side the same asymmetry ran four for four: every
overturned menu item rested on a number computed once. `idea-pilot` now derives
its own terminal counts twice; this rule extends the same discipline to numbers
a *role* introduces during the debate — an assessor's coverage count, a methods
referee's cluster count, a skeptic's overlap figure.

Re-derivation is by a **different path to the same quantity**, run by the driver
against the registered slice, not by asking the role to check its own work. The
verdict block gains one line per re-derived number:

    ```verdicts
    final_round: 2
    ...
    rederived: usable_meetings 13 (assessor) / 13 (driver, by meeting id) — agree
    ```

A disagreement **blocks the KILL**: the card returns to the round with both
numbers on the table. A role that introduces a number and cannot say what would
re-derive it has stated a hunch, and the Material Gap rule already covers hunches.

## Step 3: decision audit (audits the panel, not the idea)

Every layer above this one can kill. Nothing above this one checks
whether a kill was *right*. That asymmetry matters more than it looks.
A wrong survival is caught later by the desk screen, the panel, the
pilot, or the S8 referees, but **a wrong kill is invisible forever**:
nobody reads the paper that was never written. The audit counters
measure the kill *rate*; they cannot tell a correct rate from a biased
one.

So one fresh agent per terminal decision on `model_strong`, never a role
that voted on it, reviews the record. It judges the reasoning, not the
idea.

**It audits advances too, not only kills** (renamed from "kill audit"
after the first live trial). The asymmetry argument above is
correct and is why kills must be audited. It is not a reason to leave
advances unaudited, and the trial showed why: on one record the
auditors upheld 4 of 5 kills and rerouted 1, overturning none — while
flagging **2 of 3 advances**, one of them with three defects. The single
most valuable finding of that trial was that a card was advanced on a
load-bearing premise seven of ten voices asserted and the eighth had
falsified on disk, carried forward unreconciled, and then routed to a
feasibility pilot to settle a defect three roles had located in the
estimand. No kill-only audit would ever have found it.

**In scope:** graveyard entries from the novelty audit (occupied margin),
from a unanimous desk reject, **from a confirmed `CONTRIBUTION-NULL` at step
1.5**, and from fallback triage (contribution failure, method-blocked); **and
every advance** — cards that cleared the debate gate, cleared a pilot, or reached
the menu. **Out of scope:**
blocked and access-blocked. Those are factual claims about the world with
an automatic recheck trigger already; they are not judgments and do not
need one reviewed.

**On the themed path, the pilot's terminal verdicts are also in scope** —
`unmeasured` and `access-blocked`, and also any
`construction-open` whose alternative construction the pilot declared and the
card then ignored (before the first themed run; verdict names
updated with `idea-pilot`'s taxonomy). The scope list above was written
for the swarm path, where the pilot runs last and screens a handful of cards
that have already survived every other layer. On the themed path the pilot
runs **first, on every variant**, which makes it the layer that kills the
most — and the one layer whose kills nothing reviews.

**What now reviews the pilot, and what still does not** (closing
the postmortem's item 5 with its limits stated rather than claimed away). Three
checks now sit on the layer: `idea-pilot` derives every terminal count twice by
independent expressions; the harness re-executes each reported count's literal
expression and fails on a mismatch; and this audit covers the layer's terminal
verdicts in both directions with a layer-matched control. What none of them
covers is the **design judgment inside the count** — whether the quantity the
pilot chose to measure is the quantity the design needs. Defect 6 reaches part
of that and the reachability block reaches more, but a pilot that measures the
wrong thing correctly, twice, still passes every check here. That is a known
gap, not a solved one, and it belongs in the postmortem of any run that leans on
a pilot number.

The objection to auditing it is that a count is a fact, not a judgment, and
that is why blocked sits out of scope. The count is a fact. **The
definitions behind the count are not.** Which event window, which partition
rule, what threshold makes an observation usable — each is a choice, each
changes the number, and choosing wrongly is exactly what produced the
8-to-10x error in one run: the assessor counted days on which *any*
partition cell was quoted for a design that needed *every* cell. That error
was caught by a second script only because someone thought to write one.

So a pilot-infeasible verdict is audited against defect 6 below, and the
layer-matched control is a **pilot-cleared** card. A `feasible` verdict
whose definitions are too loose is the same defect pointing the other way,
and the control is what makes it findable.

**The auditor gets literature search access**, and must use it for any
LITERATURE_ERROR check. In the trial the one occupancy kill was upheld
because its auditor retrieved the occupying paper unprompted and found the
occupation *broader* than the record claimed. A defect class that can only
be checked against sources cannot be left to whether an agent thinks to go
and look.

The auditor reads the idea card, `novelty_facts.md`, the desk verdicts,
**the novelty verdict**, the full debate record, and — where one exists — the
pilot report **and the pilot script that produced it**, and looks for seven
specific defects:

1. **Literature error**. The occupying paper does not say what the kill
   record claims it says. Checkable against `paper_set` or one logged
   search.
2. **Missed remedy**. A standard instrument, identification strategy,
   or setting swap that the record never considered. Naming it is
   required; "there might be an instrument" is not a finding.
3. **Category error**. Killed for contribution when the record actually
   describes an execution problem (which routes to the clinic, not the
   graveyard), or the reverse.
4. **Role capture**. One role's verdict decided the outcome, readable
   straight off the verdict block. The validation runs already hit this
   once: the feasibility assessor voted REVISE five times and KILL once
   and never EXPLORE across six debates, so a single role was deciding
   every pilot gate. That was found by hand. This is what finds the next
   one.
5. **Unverified premise**. The kill rests on a claim carrying
   `[MATERIAL GAP: unverified citation]`.
6. **Counting definition**. The pilot's
   event window, partition rule, or usability threshold does not match what
   the design requires — too loose, so the sample is overstated, or too
   tight, so a workable design was killed on a number that answered a
   different question. Finding it requires **quoting the pilot script's own
   definition** and naming what the design needs instead; "the window seems
   short" is not a finding. This defect is checkable against code rather
   than against a record, which makes it the most verifiable of the seven and
   the only one an auditor can settle outright.
   The report carries a ```count block per number, with the
   literal `expression` that produced it, and a ```reachability block on every
   negative verdict. Read those first — they turn this defect from a
   reconstruction into a comparison, and they add two new forms of it: a
   **stated-versus-computed mismatch** (the prose defines one unit, the
   expression computes another — both confirmed arithmetic defects so far
   were this), and a **declined quantity that was reachable** (the reachability
   block's `why_it_fails` does not survive one logged check).
7. **Contribution error**. The novelty
   verdict misreads the occupying paper's claim; asserts a theory rung a logged
   search contradicts, or an `untested` rung with no failed queries recorded; or
   returns a `CONTRIBUTION-NULL` whose outcome table **missed a live cell** — the
   commonest form being a cell the auditor can name and the judge did not
   consider, typically the reversed sign. It fires the other way on an advance
   too: a `PROCEED` whose table marks a cell live that the design's own
   pre-registration excludes. Finding it requires **quoting the verdict's own
   text** and naming the source that contradicts it. The auditor's
   literature-search access is mandatory here, as for class 1.

Verdicts: **UPHELD** / **OVERTURN** / **REROUTE** (the kill was right,
the destination was wrong: graveyard when it should be blocked registry
or clinic).

Discipline, so the audit does not become a second opinion generator:

- An overturn must quote the specific record text it disputes and name
  which of the seven defects applies. An overturn on "the idea seems
  interesting" is not a finding, and neither is a re-argument of the
  merits the panel already weighed.
- **A finding that proposes a setting swap to unheld data is labelled
  `requires_data_beyond_held_extract` and routed as a new idea, not
  counted as a defect in the audited decision**. The
  fallback triage below already says a source swap is a different idea and
  re-enters as one; the audit must obey the same rule. In the trial this
  label cut the honest defect count from 4 to 2, and without it the audit
  inflates its own rate with proposals the pipeline forbids acting on.
- An overturned idea re-enters step 1 in full. It does **not** consume
  the revision clinic's one-re-entry-ever budget: that budget exists to
  stop an idea being iterated against the judge, and an audit correction
  is the judge being wrong, not the idea changing. One audit overturn
  per idea, ever.
- The auditor's output is judgment-bearing and goes to
  `quarantine/decision_audit.md`. When a finding is *factual* (defect 1 or
  5), the correction lands in `novelty_facts.md`, which is a facts file,
  so a re-entering idea carries the corrected fact and none of the
  argument.

**Controls are layer-matched.** Every audited
decision needs a counterpart that went through the *same layer* and came
out the other way, under a symmetric brief: *was this terminal decision
soundly reasoned?*, with the same seven defects and the same requirement to
quote the record.

The old rule drew two survivors **by position in the F2 ranking** (highest
and median). The trial showed why that fails. In a run where debate depth
is rationed, F2 rank selects cards that were never debated: their record
is a card plus three desk verdicts, 2.9 KB against 6-8 KB for every
audited kill. The auditor of one said so unprompted — it could not verify
the decision because the scores it would have needed were not in the
record. A control that went through a different process, or no process,
cannot test whether an auditor is willing to find a defect in a decision
that went the other way, which is the only thing a control is for.

So draw each control from the same layer as the decisions it controls: a
debated survivor against debate kills, a card that cleared the occupancy
screen against an occupancy kill, **a pilot-cleared card against pilot
kills**, **a novelty-cleared card against a confirmed `CONTRIBUTION-NULL`**,
and so on. In the trial the one layer-matched control, added
beyond the old spec, was the one that found the most.

A defect found in an advance is recorded and routed to the panel, not
acted on: a survivor still has the pilot and every downstream gate ahead
of it, so nothing needs undoing here.

### A correction is a contested second column, never a replacement number

**This rule already existed in substance as record-don't-act, above. It was
overridden once, and that override is the single largest defect a run
produced** — so it is now stated as its own rule with its own artifact.

The an earlier run driver found four counting defects in the pilot layer and added a
correction pass (Step 6.5) to repair them. The decision audit then found **the
correction layer was the defective one**: an auditor reproduced all six original
pilot samples exactly and overturned four of six advances, every defect in the
correction, and **all four in the direction that flatters the design** — 97
where the truth was 73 or 89, 33 where it was 25, 841 where the correction's own
stated requirement gives 54. Four for four in one direction is not noise. The
auditor's verdict on the override — *motive sound, execution not* — is correct
and is adopted: the thing record-don't-act protects is **who is left to argue**,
and a terminal card has no next layer.

So when any layer finds a number wrong:

- The original number **stays** and keeps its provenance. The correction is
  written **beside** it as a second column, attributed to the layer that
  produced it, and marked `unreviewed` until something other than its own author
  has checked it.
- Both numbers travel together to every downstream reader, including the menu.
  `comparative_final.md` shows `certified / disputed` side by side, never a
  single repaired figure.
- A correction that will carry a terminal verdict obeys the second-derivation
  rule like any other terminal number, and its re-derivation is run by someone
  other than the correction's author.
- **Correcting the correction immediately before presenting the menu is the
  same override a second time** — it hides the run's most important result
  behind clean-looking numbers. The author sees the defect and the number
  together, which is what one run did at G1 and is the one part of that sequence
  that was right.

A run whose menu shows no disputed column has either found no defects or
suppressed them, and the counters below make which one visible.

This is not a blind test and should not be described as one. The record
states its own verdict, so the auditor always knows whether it is
reading a kill or an advance. What the control measures is narrower but
still worth having: whether this auditor is willing to find a defect in
a decision that went the other way. A run where it never is tells you to
discount the overturn rate, not to trust it.

## Step 4: the G1 verdict (always runs; the slate is however many clear the bar)

A fresh three-judge panel on `model_strong` reads all candidates'
`handoff/` packets side by side — nothing from any `quarantine/` — and
returns **a verdict per card against a declared threshold**. Output:
`ideas_dir/comparative_final.md`.

**G1 is a two-sided gate**, replacing an earlier feasibility menu and, before
that, a single-winner floor. It refuses cards below the bar and it promotes and improves
cards at or near it. Both halves are first-class, and **the number of cards it
passes is not fixed**: zero is a legitimate complete result and so is six.

> **From:** a feasibility-ranked menu of 3-5, always populated.
> **To:** a verdict per card on a declared ladder, with the slate being
> however many clear the threshold — none, one, or many — and a named route
> for every card that does not.

**Why this is not a return to the earlier mistake.** That change was made
because the stage was being asked "is this a top-3 paper" and answering
confidently with nothing behind the confidence. The fix then was to stop
asking. The fix now is to ask a question the stage can answer: **not whether
the paper would place, but whether the design clears the structural gates
top-3 papers clear.** Gate clearance is a claim about the card and its named
sources. Placement is a prediction about an editor, and nothing in this
pipeline may assert one.

**What is kept from that change, unchanged.** The feasibility envelope is the
one output of this stage that survives a referee. *15 meetings with 60 joint
hours* is a fact; *24 full-partition days across 2 non-independent series* is a
fact; in one run those two facts decided the outcome. Feasibility therefore
becomes **Gate F, hard** (below) rather than an annotation — it can refuse a
card outright. What it stops being is the *ranking key* among cards that all
clear the bar, because among those the question is contribution, not counts.

**And the premise that justified deleting the threshold was wrong**. The record said
`references/top_journal_calibration.json` is "62 papers, all top-3, no held-out
evidence for any lower rung". It is **43 accepted / 17 stalled / 2 uncertain**,
the accepted class is **27 JF/JFE/RFS plus 16 top accounting**, and the stalled
class carries failure-mode tags. There is a contrast class. What survives of
that reasoning is the narrower and better point kept above: no entry links a
rung to an editorial outcome.

### The ladder

Reused **verbatim** from `<skills_root>/finance-idea-screening/SKILL.md` — its
six scored dimensions, its hierarchical gates A-E, its archetype parity against
the calibration set, and its rule-based novelty-confidence cap. Nothing new is
invented here, and a divergence between the two ladders is a defect in this
file.

| Verdict | Condition |
|---|---|
| `top-generalist-candidate` | gates A-E clear, novelty confidence ≥ Medium, **and Gate F** |
| `strong-field-candidate` | all six dimensions ≥ 3, total ≥ 18, one or more gates failed |
| `revise` | total 15-20 with a clear path on the weak dimensions, or one gate failed with a fixable cause |
| `kill` | Importance < 3, contribution is mostly setting variation, the bridge cannot distinguish mechanisms, more than three essential hurdles, total ≤ 14, or any dimension = 1 |

**Gate F — feasibility, and it is hard.** A card the held data cannot carry
does not clear the threshold **at any score**: the pilot verdict must be
`feasible` or `construction-open`, and the computed usable sample must meet the
run's declared `usable_min`. An idea that would be excellent on data nobody has
is not an available idea, and no contribution score buys past that.

**Per gate, say whether it cleared on a checkable or a judged basis.** Gate A
(a displacement target named against a source) and Gate D (parity against named
calibration papers) are checkable — a referee can go and look. Gates B, C and E
are judgment. Gate F is computed. A verdict that does not carry this split is a
validation failure, because it is the split that keeps a rung from drifting back
into the thing `panel_reach` was renamed for.

### The threshold

`g1_threshold` in `pipeline-config.md`, default `top-generalist-candidate`.
This is the bar the author set: **it lives up to the top-3 finance journals,
and it does not move with the topic.** The gates never reference topic; Gate D
adapts the *comparison set* to the card's mechanism and identification style,
which changes what the card is measured against and not where the bar sits.

A project deliberately aiming lower may set `g1_threshold:
strong-field-candidate`, and the run's artifacts then say so on every page. A
missing key means `top-generalist-candidate`.

### The fallthrough tier

`g1_fallthrough` in `pipeline-config.md`, default `strong-field-candidate`.
Set it to `none` to restore the earlier behaviour, where an empty slate
ends the run.

**This is not a lower bar and it is not a refill.** The threshold does not
move; no card's verdict changes; nothing is promoted into the slate to reach a
count. What the key does is decide **whether the stage stops when the slate is
empty, or goes on to show the author what it found anyway.**

The reason it exists: an empty slate is a complete and honest result, but
*ending there* throws away a run's worth of adjudicated cards at the exact
moment the author most needs to read them. The author's decision is that a
good-enough card with strong novelty and a feasible design is worth reviewing
by hand, and that the judgment of whether to spend six months on it is theirs
and not the ladder's.

**The trap this must not fall into**, and the reason the rules below are
binding rather than stylistic: the deleted menu guaranteed it "always returns
items", which made *the theme was a bad bet* unsayable. Two tiers reported as
one tier is that menu wearing a new name. So:

1. The **top-tier count is stated first, on its own line, including when it is
   zero**, before any fallthrough card is shown.
2. The fallthrough tier is **labelled as itself** — `did not clear
   <g1_threshold>` — on the tier and on every card in it.
3. The two tiers are **never merged, never renumbered into one ranking, and
   never summed into a single count**.
4. No fallthrough card is described as having cleared the bar, as a slate
   item, or as a pick-ready design. It is material for author review.
5. The DECLINE diagnosis still runs and is still reported, because *why* the
   top tier is empty is the finding, and the fallthrough tier does not answer
   it.

### The slate is every card at or above the threshold

No range, no floor, no padding, no fallback to a lower band. Report the count
in every case, and report the full verdict distribution beside it.

- **Zero** is a complete result and not a shortfall. It routes to the
  slate-level DECLINE triage below, and the diagnosis is reported whatever
  happens next. The old guarantee that the menu "always returns items" is
  deleted: it made *the theme was a bad bet* unsayable, which is a real
  finding and the one the funnel most needs to be able to report.
  **What follows a zero depends on `g1_fallthrough`**: with
  it set (the default), the stage states the zero, reports the DECLINE
  diagnosis, and then presents the fallthrough tier for author review under
  the five binding rules above — the run reaches **CHECKPOINT**, not ARCHIVED.
  With `g1_fallthrough: none`, or when the fallthrough tier is **also empty**,
  the run ends **ARCHIVED** as before. ARCHIVED on an empty top tier alone is
  no longer automatic; ARCHIVED on two empty tiers still is.
- **One** is the ordinary case.
- **Many** is also complete. All of them are presented, ordered by gates
  cleared with feasibility reported per card; the author picks one to run and
  **the rest go to the bench at their verdict**, not as runners-up. A benched
  `top-generalist-candidate` re-enters at G1 without re-earning its verdict,
  subject to the staleness rules below.

### The promote-and-improve half

Every `strong-field-candidate` is presented at G1 with three things, and a card
missing any of them fails validation:

- **the gate that capped it** — A, B, C, D, E or F, named;
- **the cheapest action that would clear that gate**, stated as something
  checkable;
- **whether that action is in scope for the revision clinic**, or whether it is
  a scope or source swap, which under the standing rule is a different idea and
  re-enters as one.

**Rework is author-triggered, never automatic**.
The clinic's budget is one rework ever per idea, and spending it on every near
miss would exhaust it on the cards that needed it least. G1's job is to make
the route visible; choosing to walk it is the author's.

`revise` cards route to the clinic under the existing one-rework rule. `kill`
cards go to the graveyard with the kill audit, unchanged.

**Panel composition.** The three judges run on **three
distinct dispositions** drawn from
`peer-review/references/referee-dispositions.md`, the same source the
debate roles use. Never one shared brief. In one run identical briefs
produced **33 of 33** agreement across panels, while giving three desk
editors different dispositions on the same eleven cards dropped unanimity
to **4 of 11**. A panel on one brief is manufacturing confidence, and its
agreement is not evidence.

**Who is scored.** Every card that reached this step, whatever its band. The
highest-band-available ladder is deleted with the menu: a band decided which
cards were *shown*, and the ladder now decides which cards *pass*, which is a
different question and the one G1 was always asking.

**Ordering, among cards that clear the threshold**, is by gates cleared, with
the checkable gates (A, D, F) breaking ties ahead of the judged ones. Read the
F-1 profile's counts and every pilot report first, because Gate F is computed
from them and it refuses before any ordering happens.

Each slate item carries, and none of these is optional:

- **the verdict**, and **per gate, cleared or capped, checkable or judged**;

- **usable sample, computed** — the pilot's count, not an estimate, and not
  the feasibility assessor's figure unless a pilot confirmed it. On
  in one run the assessor reported "97 and 120 combo-days of support" for a
  design whose real support was **12 and 12**, because it counted days where
  *any* partition cell was quoted and the design needed *every* cell. The
  number that goes here is the one a script produced;
- **binding constraint, named** — the specific thing that caps the sample.
  In one run this turned out to be an auxiliary series the design depended on
  rather than the primary source everyone was watching, which nobody expected;
- **cheapest action that would relax it**, stated as something checkable;
- **`panel_reach`**, median of the three editors, labelled *advisory* and
  *judged, not calibrated*;
- **the step 1.5 novelty verdict** — verdict, theory status, displacement label,
  and live contribution cells out of three — **reported beside reach and marked
  as the checkable one**. Reach is a model's guess at an editorial outcome with
  no held-out evidence behind any rung; the novelty verdict is a claim about
  named sources that a referee can go and check. Presenting them as two flavours
  of the same judgment misrepresents both;
- **surviving objections**, each with the role that raised it, unreconciled;
- its **`data_request` block** from the pilot report,
  verbatim and unedited, `status: none` included. The slate is where the author
  decides what to spend six months on, and *what data would have to be found
  first* is part of that decision rather than a footnote to it. The same block
  travels with every fallthrough card, where an acquisition is frequently the
  cheapest action that would clear the capping gate.

**The verdict changes what G1 is shown, never what the stage claims.** A
`strong-field-candidate` is reported as one, with the gate that capped it, and
is not on the slate. If nothing cleared the threshold the output says
`no card cleared <g1_threshold>` with the full verdict distribution and the
DECLINE diagnosis, and presents no card as passing — and then, if
`g1_fallthrough` is set, shows the fallthrough tier **below that line and
labelled as not having cleared it**. The line is not softened because a
fallthrough tier follows it; the tier is shown because the author asked to
read what the run found, not because anything cleared. **Presenting a card as
having cleared a bar it did not clear is the one failure this step must never
produce** — and padding a thin slate to reach a count is that failure, which is
why the count is gone.

Nothing here may state or imply a predicted journal placement. A rung asserts
gate clearance; the calibration set documents what accepted and stalled papers
look like and validates no link between any rung and an editorial outcome. Any
artifact saying a card "would reach" a journal is a validation failure, and
that rule is the earlier one, kept in the form that was actually right.

Cards not on the menu keep their lineage directories on the bench,
unchanged. Refill precedence for a further cycle is unchanged: bench,
unblocked registry entries, clinic output, fresh generation.

**Bench staleness now covers occupancy as well as feasibility**. A benched card past the staleness window already re-runs its
feasibility check before re-entering G1, on the grounds that the data may have
moved. The literature moves too, and in the direction that matters: a paper
published since the run can close the card's question outright, which is a
harder kill than any sample-size change. A stale bench entry therefore re-runs
**both** its feasibility check and step 1.5's mechanism-scoped occupancy query
before it is presented again.

## Step 4b: the research proposal (one per presented card)

**Every card presented at G1 gets a 1-2 page research proposal.** Four cards
presented means four proposals. It is written to
`<ideas_dir>/<card>/handoff/research_proposal.md` and travels with the slate, and
with the fallthrough tier on the same terms.

Why a prose proposal when the card already carries a verdict: the verdict says
which gates a design cleared, and that is a machine's answer to a machine's
question. The author picks what to spend six months on, and that decision is made
against a *readable argument* — a question, its setting, what is already known,
what data would answer it, and who would care. A rung cannot carry that. This is
also the artifact a supervisor, a co-author, or a programme reads, and none of
them will read a gate table.

### It is a rendering, not a generation

**Binding, and the whole reason this step is safe to add.** The proposal writes
no new fact. Every number, citation, quantity and claim in it is already in a
`handoff/` artifact, and the step's job is to say it in prose. A proposal that
introduces a fact absent from the artifacts is a Material Gap violation and fails
validation, exactly as a claim-ledger entry with no results key does.

| Proposal section | Where its content already exists |
|---|---|
| Working title | the card's question, compressed |
| Background | the F0 landscape brief's area framing, plus the card's setting and its named **discipline** |
| Research questions | the card's question and sub-questions; the *what is new* answer comes from step 1.5's displacement verification and the `occupies`/`adjacent`/`context` calls |
| Literature review | `handoff/novelty_facts.md` "Closest work" entries and `paper_set`, tiered by citation rank |
| Data and methodology | the pilot report: computed usable sample, binding constraint, coverage, measure checks, the ```data_request block, and the card's identification strategy |
| Implications | step 1.5's **outcome-conditional contribution table** — what the paper says under the predicted sign, a null, and a reversal |
| References | verified `.bib` entries only, drawn from `paper_set` |

The implications mapping is the one to get right. Step 1.5 already asks what the
finding would *mean* under each possible result, which is the same question
"who benefits" asks from the other end. Render all three cells: a proposal whose
implications hold only if the result comes out one way is a proposal that has not
thought about the null.

### Length and register

**800-1,200 words**, which sets to one or two pages. This is a ceiling that
binds: the guidance treats concision as evidence of the author's grasp, so a
proposal that runs long has failed a criterion rather than merely been verbose.
The literature review in particular is **cohesive and focused, not
comprehensive** — it is a proposal.

Prose follows the workspace writing norms and the banned-words list, and runs the
same pass `draft-paper` runs. Six failure modes the review section must avoid,
named because they are the ones proposals actually hit: no reference literature
for the broad area, no seminal papers, no awareness of recent work, repetition,
over-reliance on non-academic sources, and citing a paper without showing its
relevance.

### The tier label travels into the proposal

A proposal for a **fallthrough** card opens with one line stating that the card
did not clear `g1_threshold`, naming the gate that capped it and the cheapest
action that would clear it. This is not a disclaimer bolted on; a polished
two-page proposal is precisely the artifact that could launder a capped card into
looking like a cleared one, and the label is what stops it. A fallthrough
proposal without that line is a validation failure.

Nothing in a proposal states or implies a predicted journal placement, on the
same rule that governs every other G1 artifact.

### Validation

- One `research_proposal.md` per presented card, slate and fallthrough alike, and
  none for a card that is presented in neither.
- **All seven sections present, in order**: working title, background, research
  questions, literature review, data and proposed methodology, implications,
  references. A missing section fails; an empty one fails.
- **Background names a discipline.** The setting is the topic *and* the
  discipline, and a background that names only the topic has skipped half of it.
- **The research-questions section answers what is new**, against named prior
  work rather than by assertion.
- **Every citation resolves to a verified `paper_set` entry** and passes
  `verify-citations`. An unverified reference in a proposal is the same defect as
  an unverified citation in a draft.
- **Every number traces to the pilot report or the profile**, by the same rule
  the claim ledger applies to the manuscript.
- Word count within 800-1,200.
- A fallthrough proposal carries its did-not-clear line.
- No placement language; no directional expectation about what the result will
  be, which would breach the pilot firewall the funnel spent the whole stage
  maintaining.

## Fallback triage (by failure type, from the record)

- Data failure: blocked registry (`ideas_dir/blocked_registry.md`)
  with the missing ingredient named; rechecked every run. Named
  setting/proxy swap in the assessor's report: revision clinic
  instead.
- Access failure (anchored mode): the data exists in house but licence,
  consent, or redistribution terms forbid this use. Blocked registry
  with the missing ingredient recorded as permission, and the licence
  clause quoted from the manifest. Kept distinct from a data failure
  because the recheck trigger is a legal or contractual change, not a
  new data release. Never reroute the idea to a public proxy here — the
  proxy is a different idea and re-enters as one.
- Contribution failure: graveyard. Exception: a named open adjacent
  margin becomes a new card crediting the parent, routed to the
  clinic.
- Execution failure: clinic only on the methods referee's named
  design fix; otherwise method-blocked or graveyard per the report.

**Access failure is no longer anchored-mode-only**. A licence wall is a licence wall whether
or not the project holds other data, and its recheck trigger differs from every
other negative route. Any run can return it. The registry records **both the
missing ingredient and the access route**, because a registry that records only
the ingredient cannot tell a new data release from a new licence, and those are
the two different events that would unblock it.

**A `construction-open` pilot verdict is not a failure and does not triage
here.** The alternative construction the pilot named becomes a required design
note on the card and the card proceeds. An `infeasible-unchecked` does not
triage either — it returns to the pilot to finish its reachability check.

## The slate-level triage: when nothing is good enough

Everything above triages **one card**. Nothing triaged **the slate**, and the
menu's old guarantee — that it always returned 3-5 items from whatever band
existed — made that gap easy to miss: there was always something to present, so
there was never a defined action for *the author reads the menu and declines
all of it*.

**The gate reaches this route by itself.** A slate where no
card clears `g1_threshold` routes here without waiting for the author to
decline, because an empty slate is now a thing the stage can say. The author's
own DECLINE of a non-empty slate still routes here too, and the diagnosis is the
same either way.

DECLINE is that action. Its route is chosen by **why** the slate failed, read
from the run's own counters rather than from hope — the same discipline as the
per-card triage above, one level up:

| Diagnosis | Read from | Route |
|---|---|---|
| **Calibration-blocked** — cards were capped by **Gate D not clearing for want of in-field analogs**, not by anything about the cards. Check this **first**: it is the only diagnosis where the slate is empty and the ideas may be fine | the Gate D line on each verdict, and `calibration_file`'s per-class in-field counts | **Rebuild the calibration set** (`calibrate-rubric`). Do **not** re-theme, do not re-generate, do not send anything to the clinic. Report the slate as `no verdict possible` rather than `nothing cleared` |
| **Contribution-thin** — most cards `REFRAME` or `CONTRIBUTION-NULL`, ≤1 live contribution cell across the slate, displacement labels mostly `additive`/`unverifiable`, few or no `verified` | step 1.5 counters and the run-level displacement line | **Re-theme. Do not re-generate.** |
| **Feasibility-thin** — most cards terminal-negative or conditional on the *same* binding constraint: the same field, the same window, the same missing quantity | the pilot verdict table's binding-constraint column | **Blocked registry with one named ingredient and its route**, plus a data-acquisition question carried to the author |
| **Execution-thin** — the methods referee is the modal killer, and its objections name different defects per card rather than one shared one | the debate verdict table and the role-capture counter | **Revision clinic**, one rework each, cycle cap unchanged |

**`no verdict possible` is not `nothing cleared`, and conflating them is the
expensive mistake here**. An empty slate says one of two very
different things: *these cards do not clear the bar*, or *this run cannot tell
whether they do*. The first is a finding about the ideas and routes to a new
theme or the clinic. The second is a finding about the anchor and routes to
`calibrate-rubric`. Re-theming on a calibration gap throws away a slate that was
never judged, which is the most expensive available response to the cheapest
available problem. The Gate D line on each verdict is what separates them, which
is why every verdict carries a per-gate cleared/capped split.

Three of these need their reasoning stated, because all three are easy to get
backwards.

**Contribution-thin routes to a new theme, not a new cycle.** The instinct is to
generate again inside the same theme, and it is wrong for exactly the reason the
per-card rule already gives: polish does not create a margin. If a slate's
cards are individually well-identified and collectively say nothing, the theme
is the thing that failed, and a fresh cycle inside it will find the best
available version of a bet that was not worth making. A new theme is a **new
run**; the graveyard's mechanism signatures carry forward as a blocklist so the
next run does not re-derive what this one retired.

**Feasibility-thin turns on whether the constraint is shared.** If every card
dies on the same missing quantity, that is one data problem and it has one
answer — name the ingredient, name the route, ask the author whether to buy it.
If each card dies on a *different* constraint, it is not a data problem at all;
it is a design problem wearing one, and it routes to the clinic. The pilot's
binding-constraint column is what separates them, which is why that column is
required rather than advisory.

DECLINE is recorded with `gate-log` like any other gate decision. **Whether the
run ends there depends on `g1_fallthrough`**: the diagnosis
is always reported, but with a fallthrough tier available the stage presents it
and stops at **CHECKPOINT** for the author, who may then decline in full. Only
an author DECLINE, an empty fallthrough tier, or `g1_fallthrough: none` ends the
run **ARCHIVED** — the documented-reject stop state the driver already defines
— not PARKED. A parked run implies something is owed; a declined slate is a
finished piece of work with an honest negative result, and the distinction
matters to the next session reading STATE.

## Gate G1

Human mode: present **the slate — every card at or above `g1_threshold`, which
may be none** — with each card's verdict and per-gate split, its counts and
binding constraint, the debate records, every pilot report, and **F0's
trajectory block** as one checkpoint. Present beside it the
`strong-field-candidate` cards with the gate that capped each and the cheapest
action that would clear it, so the author sees what could be promoted as well as
what passed. **The author picks**, or declines, or commissions a rework; record
in the decisions log.

**An empty slate is a report, not a failure of the stage.** It says which cards
were scored, where each landed, and which DECLINE route the counters point to.
The old menu could not say *nothing here clears the bar* and that silence was
the thing being fixed.

**On an empty slate with `g1_fallthrough` set**, the checkpoint has three parts
in this order, and the order is binding because it is what keeps the first part
from being read as the third:

1. `no card cleared <g1_threshold>` — the count, stated on its own, with the
   full verdict distribution.
2. The DECLINE diagnosis and the route its counters point to.
3. **Under a heading naming the tier** (`did not clear <g1_threshold> —
   presented for author review`): each fallthrough card with its verdict, the
   gate that capped it, whether that gate cleared on a checkable or a judged
   basis, the cheapest action that would clear it, its computed usable sample,
   its binding constraint, its `data_request` block, and its unreconciled
   objections.

**Every presented card arrives with its research proposal** (step 4b), slate and
fallthrough alike. The gate table is what the pipeline checked; the proposal is
what the author reads to decide. Present them together — a verdict without the
argument behind it asks the author to ratify a machine's judgment rather than
make their own.

The author's decision at that checkpoint is one of: commission rework on a named
card, take a card forward **on the record that it did not clear the bar** (which
the G1 acceptance record must then state in its own words), ask for a data
acquisition from the `data_request` list, re-theme, or decline in full and end
ARCHIVED. The stage recommends; it does not choose, and it never presents option
two as though the card had passed.

**The pick is not the handoff.** One run ended with four menu
items each carrying a stated requirement that had to be discharged before its
pre-registration could be written, and nothing said who discharged them or what
recorded that it happened. So the author's pick is followed by one artifact,
written by the driver, before any later stage runs:

`ideas/<card>/handoff/g1_acceptance.md`, carrying

- the card picked, and the date;
- **every surviving objection** with the role that raised it and its
  disposition — `discharged` (with what discharged it), `accepted as a
  limitation` (which then belongs in the paper), or `deferred to S4` (which
  binds the pre-registration);
- **every audit dispute** on that card and how it was resolved, including any
  contested second column still open;
- the step 1.5 `REFRAME` framing note where one exists;
- the retrospective-disclosure line the peek ledger requires.

**S2 refuses to run without it.** That is the same shape as the
pre-registration commit gate, one stage earlier, and for the same reason: a
decision that exists only in conversation is a decision the next session cannot
audit.

At the same moment the novelty verdict's **facts** — the literature strand, the
theory rung with its returned source, the displacement label — move into
`handoff/novelty_facts.md`, under the existing rule that factual findings live
in the facts file and arguments stay in quarantine. The verdict stays
quarantined from *agents*; the author has now read it, and S2's positioning memo
should start from a named strand rather than a cold search. That is a saving,
not only hygiene.

The trajectory block is context, not a ranking input, and it is presented
beside the menu rather than folded into it. The menu is ordered by what the
data can carry, which is checkable; where a literature is heading is not,
and it is the author's to weigh against a six-month commitment. Its rising
half reaches the author here and nowhere upstream.

**Autonomous mode always PARKs at G1**. It
records the menu, the counts, and the binding constraints so a later human
session starts from candidates rather than from nothing, and it advances
nothing.

The reasoning is not caution, it is what a menu *is*. The previous rule
compared a single winner's tier against a `min_tier` floor; a menu has no
single winner, and reach is no longer the ranking key precisely because it
is uncalibrated. There is no honest machine rule left to advance on:
picking the top menu item would restore the discarded verdict under a new
name, and gating on reach would gate on the judgment the rename just
stopped the stage from asserting. Choosing among feasible designs is the
author's call, which is what a menu was built to hand over.

`min_tier` is therefore removed from `pipeline-config.md`. **Consequence,
stated plainly: there is no longer a fully autonomous S1 to S2 handoff.**
That is the intended cost of refusing to gate on an uncalibrated judgment,
and it is a real cost — an unattended run now stops at the end of
idealization every time.

## Audit counters

Append to `ideas_dir/comparative_final.md`: **the step 1.5 counters** (verdict,
theory-status, displacement-label and contribution-cell distributions; kills
confirmed versus reversed by the confirmer, reported separately; debate agents
saved; and **the novelty-versus-feasibility rank correlation across the menu** —
a run where the two orderings coincide is a run where the layer added nothing to
G1, and that must be visible rather than inferred); the `panel_reach` distribution
across the slate (how many at each of the five rungs, and each menu item's
median reach), pilot-versus-clinic routing counts, debate kill rate,
pilot-contradicts-debate rate, audit overturn rate (by layer and by defect
type), **defects on kills versus defects on advances**, control-flag rate,
per-layer funnel counts, **per-layer subagent counts with a total**, **the per-layer cost table from
`<tools_dir>/run_cost.py`**, plus
two integrity counters: how many numbers carry a **disputed second column**, and
how many terminal numbers show a **second derivation** and whether the two agreed.
These tune next run's depth by measurement.

**Report cost beside the subagent count, and never subagent count alone**. A
subagent count is close to uncorrelated with spend. Measured on a full run, with
per-agent cost given as a multiple of the cheapest layer:

| Layer | Agents | Share of run cost | Per agent, relative |
|---|---|---|---|
| Decision audit | 7 | 16% | **56x** |
| Debate roles | **40** | 12% | **8x** |
| G1 judges | 4 | 5% | 32x |
| Desk editors | 3 | 2% | 18x |
| Generators (cheapest model) | 10 | 0.4% | **1x** |

The debate is **62% of the agent count and 12% of the cost**; cost per agent
spans 56x across the funnel; and the driver's own thread, which appears in no
agent count at all, was **63% of the run's total**. A counter that treats every
agent as 1 cannot ration anything, and a budget key set from it would have fired
on the cheapest layer in the funnel. Both tables are recorded: the count says how
many isolated judgments were bought, which is the clean-room question, and the
cost says what they cost, which is the budget question. They are different
questions and that run answered only one of them.

Also append, once per run, one `(f2_score, terminal_rank)` row per card
that carried an F2 score, to the persistent cross-run record (decision
). A single run yields ~11 such rows and a powered read on
ρ = 0.4 needs ~47, so this question is only ever answered by accumulation.
Each row carries its **brief regime**, because changing a panel's briefs
changes the outcome variable and rows from different regimes are not
comparable.

Read the audit rates together, and read them across runs, not within one:

- A rising overturn rate says the panel is killing on reasoning that
  does not survive review; tighten the layer the overturns concentrate
  in rather than the audit.
- An overturn rate that sits at zero for several runs says either the
  panel is clean or the auditor is rubber-stamping, and the control-flag
  rate is what separates those two. On one trial the rates were
  0 of 5 kills overturned against 2 of 3 advances flagged, which is what
  "not rubber-stamping" looks like when it is real.
- Repeated role capture on the same role is a defect in that role's
  brief, not in the ideas it killed.
- Defects concentrating on **advances** rather than kills mean the funnel's
  problem is what it lets through, not what it stops — a different repair
  from tightening any killing layer.

## Validation

Done when: every card entering F3 has a terminal status (graveyard,
blocked, access-blocked, clinic, pilot-cleared, benched, or on the menu);
every verdict table shows per-agent-per-round entries; every in-scope
terminal decision carries an audit verdict, every finding quotes the
record text it disputes and names its defect, and the layer-matched
controls were audited; no downstream-facing file under any `handoff/`
quotes `quarantine/` content, `decision_audit.md` included; in anchored
mode every query the assessor ran appears in `peek_log` and no feasibility
position rests on an unqueried assertion a query could have settled; the
counters block is present; lab-notebook entry written.

every desk verdict
carries one of the five rungs and the card's median reach is recorded; no
card entered the revision clinic without either a terminal negative pilot
verdict (`unmeasured` or `access-blocked`) or a triage route with no pilot
available. An `infeasible-unchecked` never routes anywhere: it sends the pilot
back to finish its reachability check.

- **No KILL verdict was written without its numbers re-derived**, and every
  re-derivation appears in the verdict block with both figures.
- **No corrected number replaced its original anywhere.** `grep` the menu and
  the handoff packets: every corrected figure appears beside its certified
  figure, attributed, and marked `unreviewed` until independently checked.
- **The cost table is present** alongside the subagent table, and the postmortem
  states where the two rank the layers differently.

For the rename, the menu, the audit, and calibration:

- **`calibration_file` is present and under six months old**, checked
  before the first desk editor ran. This is the gate that both paths now
  share; it used to live only in `idea-scoring`.

- **No journal name appears as a `panel_reach` rung anywhere**, and no reach is
  reported without the *judged, not calibrated* qualifier. Grep the run's
  artifacts for `top-3`, `field-tier`, and `note-or-replication` used as a
  **reach** rung: any hit is a validation failure.
  **Scope, narrowed deliberately.** The G1 ladder's `top-generalist-candidate` and
  `strong-field-candidate` are not reach rungs and are not covered: they name
  which structural gates a card cleared, which is a claim about the card and its
  named sources, where a reach rung named an editorial outcome nobody had
  evidence for. The distinction is the whole basis of the G1 rebuild, and
  collapsing the two would either ban the ladder or re-license the reach
  rungs.
- **Every card that reached step 4 carries a verdict** on the four-rung ladder,
  with a per-gate cleared/capped line and each gate marked **checkable** or
  **judged**. A card scored without the split fails validation.
- **The slate is exactly the cards at or above `g1_threshold`**, and the count
  is reported. An empty slate with its DECLINE diagnosis is a valid, complete
  output. **A slate padded to a count, or refilled from a lower band, is a
  validation failure** — that is the old menu's guarantee and it is what made
  "nothing clears the bar" unsayable.
- **The fallthrough tier, when one is presented, is a separate labelled tier**. Four checks, each a validation failure on its own:
  1. The top-tier count appears **before** the first fallthrough card and is
     stated even when it is zero. A report whose first card is a fallthrough
     card fails.
  2. The tier carries a heading naming what it did **not** clear, and every
     card in it repeats that label. An unlabelled fallthrough card is
     indistinguishable from a slate item, which is exactly the old menu.
  3. The two tiers are not merged, not renumbered into one ranking, and not
     summed. A single count covering both fails.
  4. No fallthrough card is described with `cleared`, `on the slate`, `passed`,
     or a synonym. Grep the G1 artifacts for those against the fallthrough
     card ids; any hit fails.
  A fallthrough tier presented when the slate is **non-empty** also fails: the
  tier exists for the empty case, and showing it beside a real slate is
  padding by another route.
- **Every `strong-field-candidate` carries the gate that capped it, the
  cheapest action that would clear it, and whether that action is in the
  clinic's scope.** A capped verdict with no route is the promote-half missing.
- **Every presented card carries a `handoff/research_proposal.md`** — slate and
  fallthrough alike, one per card, 800-1,200 words, all seven sections present
  and in order, every citation verified against `paper_set`, every number traced
  to the pilot report or the profile, and a fallthrough proposal carrying its
  did-not-clear line. A proposal asserting a fact absent from the card's
  `handoff/` artifacts is a Material Gap violation.
- **Every slate item and every fallthrough card carries its `data_request`
  block**, copied unedited from the pilot report, and the run
  emits `<ideas_dir>/data_requests.md` aggregating them. A slate item with no
  block fails; a block that appears at G1 but in no pilot report fails as an
  authored request (Material Gap rule).
- **Every slate item carries a computed usable sample**, traceable to a
  registered script, plus a named binding constraint, a cheapest relaxing
  action, an advisory reach, and an unreconciled objection list. An item
  whose sample is an assessor's estimate rather than a script's count fails
  validation — that substitution was an 8-to-10x error in one run.
- **No artifact states or implies a predicted journal placement.** A rung
  asserts gate clearance only. Grep for "would reach", "would place",
  "top-3 paper" as a prediction: any hit is a validation failure.
- If the slate fell through to the debated set, the output says `no viable
  candidate; best of a killed slate` and describes no item as viable.

- **Every pilot verdict carries an audit verdict** when `theme` is set,
  infeasible and feasible alike, and each pilot-kill audit quotes the
  script's own window, partition rule, and usability threshold. A themed run
  whose audit skipped the pilot layer has left its largest killing layer
  unreviewed.
- **The run log carries a per-layer subagent count** (F0, F1-T, pilot, desk,
  debate, audit, comparative final) and a total. This replaces the flat
  12-15 target, which was written before the audit's scope grew to advances
  and cannot be met or missed informatively. A count is a measurement; a
  stale cap is not.
- **No panel ran on a single shared brief.** The three comparative judges
  carry three distinct dispositions, recorded by name.
- Autonomous runs **PARKed** at G1 and advanced nothing; `min_tier` does
  not appear in the config.

- **Every card the desk did not kill carries a `novelty_verdict.md`** with four
  blocks and a parseable ```novelty block; `idea-novelty`'s own validation list
  governs its contents.
- **No `CONTRIBUTION-NULL` without a second independent confirmer**, and none
  resting on a TITLE-ONLY citation or on an `untested` rung. Every confirmed one
  carries a decision-audit verdict under defect class 7, and the layer-matched
  control (a novelty-cleared card) was audited.
- **`grep -rn "novelty_verdict" <ideas_dir>/*/handoff/` returns nothing**, and no
  debate briefing pack contained one. A run where the judge's verdict reached the
  debate has decided the argument it was meant to inform.
- **Every menu item reports its novelty verdict beside its reach**, with the
  checkable-versus-judged distinction stated. A menu carrying reach alone fails
  validation.
- The counters carry the **novelty-versus-feasibility rank correlation**.
