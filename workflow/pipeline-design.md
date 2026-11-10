# Pipeline design: standalone research pipeline for economics, finance, and econometrics

Date:. Status: canonical stage map for this project (Phase 1).
Grounding: the design implications drawn from a survey of comparable workflows.
Skill-level specifications: `docs/skill-specs.md`.

## 1. Purpose and non-goals

This pipeline takes an empirical economics, finance, or econometrics project
from idea to a referee-ready draft, with AI doing the stage work and the
author deciding at defined gates. It is standalone: no the venue submission
tracking, no compliance logging, no time accounting. Papers produced in
the paper projects that run it are the customers.

Non-goals: theory-only papers (the theory branch exists but is secondary),
fully autonomous operation end to end (L1: autonomy pays inside stages, not
across judgment calls), and any machinery that cannot be maintained by hand
(L12).

## 2. Design principles

1. Stages end in files, not conversation (L2). A stage is done when its
   verification artifact exists and passes its check.
2. Human gates sit at judgment calls; machine gates sit at integrity checks
   (L1, L3, L4, L5, L6). A machine gate is a script or check that must pass;
   a human gate is a decision the author records.
3. The Material Gap rule holds pipeline-wide: a number, citation, quote, or
   fact not present in a project artifact is written as
   `[MATERIAL GAP: ...]`, never filled from model memory.
4. Errors climb a ladder (L8): bounded retry, then a flagged Material Gap,
   then escalation to the nearest human gate. No step silently proceeds.
5. Skills are small, plain markdown, hand-editable, with paths from project
   configuration (L12). External repos in `references/skill-library/` are
   study material; nothing is copied.
6. Model strength follows the task (L11): cheap models for mechanical
   stages, strong models for identification review and adversarial referees.

## 3. Stage map

Each stage is specified as: what the agent does alone, how it verifies its
own work, the artifact that ends the stage, the gate that opens the next
stage, and where errors escalate.

### S0. Session bookends (cross-cutting)

- Agent does: at session open, read plus the lab-notebook
  tail and produce a five-line brief (status, live findings, in-flight work,
  next action, blockers). At session close, regenerate `STATE.md` from the
  notebook, git, and the session's artifacts, then commit.
- Self-verification: the brief names a concrete next action; the regenerated
  STATE.md carries numbers, not summaries of summaries.
- Artifact: (one canonical file, L9); dated append-only
  entries in; one commit per session.
- Human gate: the close is human-activated. Handoff and commit run only
  when the author initiates them (the agent may suggest closing, never
  self-trigger); the session-close pair is the pipeline's last stage in
  every working session.
- Escalation: a session that cannot reconstruct state from STATE.md logs the
  gap in the notebook and asks the author rather than guessing.

### S1. Ideation and screening (funnel layers F-1 to F2; literature-aware, data-anchored mode, themed entry)

**The pipeline's input is a theme**. Set
`theme` in `pipeline-config.md` and S1 runs the themed path; omit it and
S1 runs the open swarm. The contract is: *give it a general question area,
get back detailed research designs the held data can carry.*

| | Themed path (default) | Swarm path (fallback) |
|---|---|---|
| F0 | narrowed to the theme: occupied, closest-three, archetypes, trajectory (saturating half only) | full brief: blocklist, target menu, archetypes, threats, trajectory |
| F1 | `idea-variants`: 8-12 versions of the theme, 2-3 theme-blind | `idea-swarm`: 100-120 cards on a lens grid |
| F2 | **does not run** | `idea-scoring` cuts to 20-25 |
| Pilot | **first**, on every variant | after the debate's no-KILL gate |
| F3 | reach sim + debate on pilot survivors only, typically 2-3 | on the whole cut |
| Cost | **unmeasured; predicted 25-37 subagents** | 23 measured (first pass) |

**On the cost row.** It
read "target 12-15 subagents" and that number cannot be met. It was written
earlier the same day the decision audit was expanded to cover advances as
well as kills, and the audit scales on terminal decisions, so auditing a
themed run's 8-12 variants costs more than auditing a swarm run's handful of
survivors. Adding the pilot layer to audit scope raised it again.

Counting the current design at ten variants: 1-2 at F0, 8-12 generators,
0-2 writing pilot scripts, 3 desk editors, 4-8 debate roles, 6-10 auditors,
3 comparative judges — **25 to 37**. Against 23 for the swarm run's first
pass, the themed path may be more expensive rather than less.

That is a prediction, not a finding, and the first themed run is what
settles it. Until then the row reports a prediction and the run reports a
**per-layer count** (`idea-debate`'s counters block), because a total says
only that the design costs too much while a per-layer table says which layer
to ration. The saving the themed path was designed to capture — spending the
deep layers on 2-3 pilot survivors instead of a 20-25 cut — is real and
should show up as small desk and debate lines; whether the generator grid
and the audit eat it is exactly what is unknown.

Why the default inverted. Across five runs the layers that decided
outcomes were F0 (what the literature occupies), F-1 and the pilots (what
the data contains), and the adversarial debate roles (what a hostile
reader finds wrong). The F1 swarm at scale and the F2 rubric decided
nothing measurable: F2's retrospective rank-versus-outcome correlation is
0.16, indistinguishable from zero at the only sample available. When the theme is given, the swarm's
machinery is spent generating 60-120 cards to find variants of something
already in hand, and then paying a rubric to get back to a dozen.

**The risk, stated because it does not go away.** A themed entry cannot
tell you the theme is wrong. The open funnel at least searches elsewhere;
the themed path optimizes within the author's premise, and if the premise
is a bad bet it will find the best available version of that bet
efficiently. The 2-3 theme-blind cells are a partial guard and not a cure,
and their fate is reported at G1 for exactly that reason.

The original three-layer funnel survives as
the swarm path: F1 builds 100-120, F2 cuts to 20-25, F3 applies the
highest standard to the survivors. Breadth is bought where ideas are
cheap; rigor is spent where the cut already concentrated quality.

Two modes. `data_mode: open` in
`pipeline-config.md` is the funnel above, unchanged: the project starts
with a field and no data, and every data claim stays a hunch until F3.
`data_mode: anchored` is for a project that already holds data — a
database, an API, a delivered extract. A verified profile of that data
is built at F-1, before any generation, and the funnel's data claims
are checkable facts from there on. A missing `data_mode` key means
`open`. Anchored mode changes what each layer knows; it does not change
the layer count, the cut sizes, or any human gate. It adds three machine
gates of its own (profile freshness, anchor existence, peek ledger) and
leaves the rest as they are.

- Agent does, F-1 (held-data profile, anchored mode only): before the landscape scan, a read-only pass over every
  source named in `data_manifest` produces `data_profile.json` and its
  readable companion — inventory (tables or endpoints, unit of
  observation, time span, coverage), identifier map (candidate join
  keys with coverage, uniqueness, and stability across vintages),
  variation inventory (which fields carry usable variation, plus the
  cluster counts S4's power block needs), measurement quality
  (missingness, masking, coarsening, restatement risk), and an
  expansion map: outside sources joinable to the held data, each with
  its access route, a named key, and a verified join probe reporting a
  real match rate rather than a hunch. This is the feasibility evidence moved to
  the front of the funnel. In three validation runs the feasibility
  assessor never voted EXPLORE, so a data objection surfacing at F3 was
  a run-ender no later layer could resolve; the same objection answered
  at F-1 costs one query.
  Peek firewall (binding): profiling never computes a relation between
  two substantive variables — no correlation, no group mean on a
  candidate outcome — and every query it runs appends to `peek_log`,
  which S4's pre-registration reads to declare retrospective elements.
  Holding the data before the question exists is the
  outcome-conditioning hazard the Phase 3 review caught; the ledger is
  what makes the disclosure checkable instead of asserted.
  Before generation spends anything, the blocked registry is rechecked
  against the profile: entries whose named missing ingredient the held
  data supplies re-enter F3 directly under the existing unblocking
  rule, so already-vetted ideas are reconsidered before new ones are
  invented.
- Agent does, F0 (literature landscape): before any
  generator launches, ONE topic-level literature scan (reusing the S2
  `literature-review` / `literature-landscape` skills in shallow mode,
  OpenAlex-primary to protect metered quota) produces
  `landscape_brief.md`: an occupied-margin blocklist, an open-margin
  displacement-target menu, recent-acceptance archetypes, and a threat-
  paper list. One scan amortized across 100+ ideas. It feeds the F1
  constraint digest so generation is aware of prior work at the front of
  the funnel, not only at F3 — the trial showed F2-top-ranked ideas
  dying in F3 for occupied margins that generation could have avoided.
  Anti-anchoring rule (binding): the brief is a displacement-target menu
  and blocklist, never a "gaps to fill" list, which would collapse
  generators into marginal literature-gap extensions (the Lens 6
  failure); diversity still comes from lens/subfield isolation. The scan
  seeds `paper_set`/`search_log` so S2 inherits it.
  Menu partition: the anti-anchoring rule
  governs what the menu is called and does not reach what a short shared
  menu does to a wide grid. The full-scale run carried the
  rule verbatim and its three menu targets became the pool's three
  largest semantic clusters, 28 of 102 cards, mapping one cluster to one
  menu item; across all seven clusters the menu accounts for roughly
  three quarters of the duplicate generation. Isolation was intact
  throughout, so the mechanism was never leakage between agents: twelve
  independent generators handed the same three targets walk to the same
  three places. F0 therefore aims for one target per steered cell, F1
  gives each steered cell exactly one and no two the same, and at least
  a quarter of cells are menu-blind. A menu shorter than the steered-cell
  count converts the surplus cells to menu-blind rather than doubling
  them up, since a thin menu is evidence the literature offers few open
  margins and the answer to that is freer generation, not more agents
  aimed at the same margins. The blocklist stays shared and unpartitioned:
  its steering is negative, the same run showed it working (0 of 21 cards
  hit an occupied margin), and splitting it would let one cell
  re-generate what another was told to avoid. In anchored mode the
  scan takes the F-1 profile as a second input and targets margins where
  a held-data capability — a key, a frequency, a population, a measure —
  is the lever. The anti-anchoring rule extends with it: the profile
  enters as a capability menu, never as a list of regressions the data
  would support.
  **Mechanism-scoped second arm.** F0 runs a second scan built from the field profile's *mechanism,
  outcome and identification* vocabulary **with the theme's nouns stripped**,
  written so that it can return work from a different asset class, venue, or
  instrument. Its hits join the occupied-margin blocklist; its queries are
  logged in their own marked block in `search_log`, because they answer a
  different question from the theme scan and mixing them makes neither
  readable.
  **The arm is OPTIONAL, not binding, and its original evidence was wrong**. It was adopted on the finding that two of the four
  cards reaching an earlier run's menu had a directly-occupying refereed paper that a
  219-paper F0 scan, six novelty searches, three desk editors, four debate
  roles, a decision audit and three G1 judges "all missed", because F0 was
  scoped to the theme. The artifacts contradict that. Both papers were
  **retrieved by step 1.1's own searches** (`N6`, `N2`), verified, and written
  into the card's `handoff/novelty_facts.md` as **"Closest work" item 1** on
  Aug 12 11:14, against the retrofit that reported them missing on Aug 13
  15:46 — Bernile, G., Hu, J. & Tang, Y. (2016, *JFE*, 179 cites) for K2-2, and
  Ederington & Lee (1993, *JF*, 1,022 cites; 1995, *JFQA*, 306) for K3-1, whose
  entry stated in bold that the adjustment completes within the first minute
  against that card's 60-second best case. Evidence with paths and timestamps: and.
  **So the defect was adjudication, not retrieval**, and it sits one layer
  along: every downstream role read those entries under the heading "Closest
  work" and none moved the paper from *related* to *occupying*. A second search
  arm re-solves a problem that was already solved.
  The arm is kept because nothing shows a theme-scoped scan is sufficient in
  general — only that it was not the binding constraint on this run — and it
  costs one scan and no subagents. It is no longer binding, no longer justified
  by that finding, and a run where it returns nothing new is a normal run.
  **The load moves to `novelty_facts.md`'s format** (below), which is where the
  measured defect actually was.
  What the arm may **not** do: its hits enter as blocklist lines, never as a
  target menu and never as a theory list. The attractor turned a
  blocklist into a target menu through a door nobody was watching, and 9 of 20
  an earlier run cards named one target as a result. Negative steering only.
- Agent does, F1 (swarm generation): a swarm of generator agents, each
  assigned one lens-by-field cell and isolated from the others
  (diversity by independence — the generation analog of the debate's
  blind round), builds a raw pool of 100-120 candidate ideas, its
  constraint digest carrying the F0 blocklist/menu. The pool is
  deduplicated by clustering on question, mechanism, and setting;
  merges are logged so the distinct count is auditable.
  In anchored mode the grid gains a data class per cell. A reserved
  quarter of the cells generate unanchored: those generators see the
  landscape brief only, never the data digest, so the funnel keeps a
  supply of ideas the held data did not suggest. The remaining cells
  see a data capability digest — distilled verified facts, never raw
  query output, mirroring how the constraint digest carries the
  blocklist without the brief's citations. Card schema in anchored mode
  replaces the unverified `data_hunch` with `data_anchor` (held tables
  and fields), `data_extension` (external source, named join key, and
  the probe supporting it, or `none`), and `data_class` (anchored,
  extended, or unanchored). Every card, in either mode, names the
  access route its data would come by. Two rules keep the data from capturing generation: every
  field an anchored or extended card names must exist in the profile
  (machine gate below), and every anchored card states in one line why
  the question matters if everyone held the data. The second rule is
  the guard against data-first framing, which the desk-reject
  simulation already kills as additive-not-novel.
- Agent does, F1 contrast pass: the grid varies designs and nothing recombines them, and the
  benchmark says that is where the misses are. **Every partial rediscovery in
  an earlier run head-to-head is the pipeline generating both halves of a human
  idea in separate cells and never posing the contrast** — one card asking
  whether pre-release price velocity predicts accuracy while two others carried
  the accuracy and volume halves separately, with no card putting activity
  against accuracy on one axis. Four of eight human ideas partially
  rediscovered, none cleanly.
  Isolation is what produces the halves, so the fix cannot be to relax it. One
  agent reads the distinct cards' **`(mechanism, outcome, identification,
  unit)` codes and nothing else** — no prose, no question text, no blocklist,
  no target menu, no theme — and returns 2-4 contrast cards, each putting two
  cards' halves on one axis and naming both parents. They enter the pool as
  ordinary cards and are piloted with the rest.
  The code-only input is binding, not stylistic: this is the one agent in the
  funnel that sees every card at once, which makes it the one place a shared
  target menu could capture the whole pool in a single step — an earlier attractor's worst case. Codes cannot carry a target. A contrast card naming a
  displacement target is a validation failure. If the pass returns nothing,
  that is a finding about the grid and goes in the counts block.
- Adjudication memory (NOT BUILT; spec in
  `docs/skill-specs.md`):
  the funnel keeps a typed store of its own terminal decisions,
  `ideas_dir/adjudication_graph.json`, with five node types (mechanism,
  idea, verdict, paper, missing ingredient) and seven edge types. F0 and
  F1 read it, F3 writes it. The evidence for adding it is direct: an earlier full-scale run regenerated two mechanisms that had already
  been debated and killed earlier in the same session, 17 of 102 raw
  cards. The F0 brief carries margins occupied by the *literature*; it
  had no way to carry margins this project had already closed itself.
  A flat blocklist was the first proposal and was rejected as too weak:
  it answers whether a mechanism was killed, and not whether it was
  killed for a reason a different setting would fix, which is the
  question the fallback triage and the blocked registry already ask.
  Four invariants bind every write: a verdict cites a record path or is
  marked inference, a node names the run that created it, a verdict names
  its kill layer, and a superseded node stays addressable (an overturn
  adds an edge, never a deletion, which is the kill audit's existing
  discipline made checkable). Anti-anchoring rule, binding and identical
  to F0's: the store enters generation as constraint digest lines, never
  as raw verdicts, because a generator that sees prior judgments anchors
  on them. Sequencing: the store keys on the mechanism signatures the
  dedup step produces, so it is built after dedup is fixed, never before.
- Agent does, F1 dedup (NOT BUILT; the shipped
  `idea-swarm` still clusters lexically): clustering is a
  resolution task, not a string-similarity task. Cheap blocking narrows
  candidates, then a model arbitrates the clusters and returns a
  rationale and a confidence per merge; the kept card retains the merged
  ids as aliases, so a merge is reversible from the record. The trial's
  lexical implementation found roughly zero of the seven clusters a hand
  read found in the same 102-card pool, and at 100-plus cards the pool
  quality this layer exists to produce depends on it. The binding metric
  is false-merge rate rather than compression: a compression ratio can be
  improved by over-merging, and a wrong merge kills one of two distinct
  ideas with nothing downstream to catch it, the same asymmetry that
  justified the kill audit.
- Agent does, F2 (calibrated scoring): every distinct idea is scored
  against the held-out calibration set on a fixed rubric (archetype
  match, displacement plausibility, data plausibility, desk-reject
  risk) by two independent scorers; disagreement beyond one band seats
  a third. The cut keeps 20-25. F2 is deliberately search-free: the
  full novelty audit belongs to F3, so F2 scores are labeled unaudited
  and are never quoted as verdicts (Material Gap rule).
  In anchored mode the third dimension changes from data plausibility
  to data leverage: does the held data supply identifying variation the
  literature lacks, and is the extension join verified. The scorers
  stay search-free — they read the card's verified anchor fields rather
  than querying anything — but the dimension stops being a guess about
  whether a source exists, which is the one thing anchored mode already
  knows. The cut stays a single ranking of 20-25; the cut report shows
  the class mix so capture by the held data is visible rather than
  silent.
- Self-verification: swarm assignments cover the whole lens-by-field
  grid; dedup merges are logged; both scoring sheets are kept; funnel
  counts (raw, distinct, cut) are recorded for the audit counters. The
  menu assignment is recorded per cell and the reserved menu-blind share
  is checked, so a run that quietly reshared the menu is visible after
  the fact. Concentration is reported beside the distinct/raw ratio: top-cluster and top-three share, with a flag above
  0.20 on the latter, plus each flagged cluster's cell spread and whether
  its mechanism matches a menu target. The ratio alone was not enough,
  having scored 0.70 and passed on the run whose top three clusters took
  27% of the pool: it counts what survives merging and cannot see how the
  merged cards were distributed. The three diagnoses the extra fields
  separate (menu pull, one generator repeating itself, genuine
  independent convergence) call for different responses and only the
  third is a finding rather than a defect. In
  anchored mode the counts carry the class mix at every layer, and each
  downgraded card (a named field absent from the profile) is logged
  with the field that was missing.
- Artifact: idea pool file with dedup log, scoring sheets, the F2 cut
  list, and a lineage directory for each surviving idea. Anchored mode
  adds `data_profile.json` with its readable companion, the expansion
  map's probe results, and the append-only `peek_log`.
- Gate: none here. The F2 cut advances to S1b (F3); G1 sits after S1b
  so the author picks from fully vetted, comparatively ranked ideas.
- Escalation: calibration set missing or stale (older than six months)
  blocks F2 scoring; a raw pool short of 100 gets one more swarm pass,
  then proceeds with the shortfall logged, never silently. In anchored
  mode a missing profile, or one older than the manifest's stated
  refresh cadence, blocks F1 until it is regenerated: generating
  against a stale schema reintroduces the hunch the mode exists to
  remove.
- Model policy (L11): F1 on the cheap model (breadth, not judgment);
  F2 scorers on the mid tier; F3 on the strong model.

### S1b. Multi-round debate, refinement, and pilot (funnel layer F3)

The funnel's last layer, run at the highest standard the pipeline owns:
every idea in the F2 cut (20-25) gets the full selection toolkit —
novelty audit with logged searches, three-editor desk-reject
simulation, positioning threat scan, the four-role debate, a
feasibility pilot on any card with no KILL vote, and the comparative final.
Only comparatively ranked survivors reach G1. This stage absorbs the
"data inventory + S1 feasibility screen" item from the approved
improvement order. Sequencing inside F3 is cheapest-first so weak
ideas exit before the expensive machinery: novelty audit and
desk-reject simulation first (both can kill on their own — an occupied
margin or a unanimous desk reject retires the idea to the graveyard
without a debate), then the debate, then pilots, then the final.

- Novelty audit is a positioning pass: it starts
  from the F0 landscape brief's threat list rather than a cold search,
  positions the idea against the closest strands (reusing S2's
  `literature-positioning-map` ex-ante), and runs `verify-citations` on
  every paper it names so `novelty_facts.md` carries only verified
  references (the Palmon-Sun-Tang Material Gap the gated arm hit is
  caught here). Papers and queries accumulate into `paper_set`/
  `search_log`, so S2's literature review inherits the idealization
  stage's work instead of restarting — literature awareness now bookends
  the funnel (F0 landscape in, F3 positioning out) rather than appearing
  only mid-F3.
- **Contribution judge, F3 step 1.5 (`idea-novelty`).** The
  novelty audit above is an *occupancy* check — *has someone done this design* —
  and is deliberately facts-only, because `novelty_facts.md` enters the debate
  briefing pack. It answers nothing about what the finding would **mean**. On the
  first themed run it killed 0 of 12 while the funnel graveyarded 0 of 8 on
  contribution grounds and a *pilot count* was terminal; the funnel could retire
  a design for its sample size and not for being pointless. Step 1.5 closes that,
  after the desk and before the debate, on four blocks per card: the literature
  strand the question joins; the **theoretical prediction** it bears on, on an
  `established`/`contested`/`untested`/`none` ladder where `untested` names the
  observability barrier and carries the searches that failed; an
  **outcome-conditional contribution table** stating what the paper says under
  the predicted sign, a null and a reversal, where no live cell is a terminal
  `CONTRIBUTION-NULL`; and verification of the card's generator-asserted
  displacement hunch against the target's actual claim. Verdicts
  `PROCEED`/`REFRAME`/`CONTRIBUTION-NULL`; the kill is the only irreversible one
  and needs a second confirmer, a quoted verified claim, and a decision-audit
  verdict under defect class 7.
  **The layer's real finding is adjudication, and it is what step 1.1's output
  format now carries**. The rule recorded here was that
  the layer searches the card's *mechanism* rather than the run's *theme*,
  because two of the four items on the first themed menu had a directly-occupying
  refereed paper that the whole funnel missed. **Both papers had in fact been
  retrieved** by step 1.1's own searches and filed as `novelty_facts.md`
  "Closest work" item 1 a day before the retrofit said otherwise. What no layer did was
  **adjudicate** them: four debate roles per card, three desk editors, an audit
  and three G1 judges each read an entry stating the occupying finding in bold,
  and none moved the paper from *related* to *occupying*.
  So step 1.1's `novelty_facts.md` changes format: **every "Closest work" entry
  carries the design-relevant comparison against what the card proposes** —
  same quantity? at what resolution, population, frequency? — stated as facts,
  never as a verdict, because that file enters the debate briefing pack and must
  stay judgment-free. For K3-1 the entry reads "measures adjustment at 10-second
  resolution and finds it complete within the first minute; this card's best
  case is 60-second resolution." No reader files that as related work. Step 1.5
  then returns an explicit `occupies` / `adjacent` / `context` call per entry,
  quoting the claim on any `occupies`, and its counters report **new work found
  and held work adjudicated as two numbers**, because collapsing them is how an
  adjudication defect got written up as a retrieval one. The mechanism-scoped
  search survives as a search rule on its own merits and no longer as the fix
  for this defect.
  Placement is driven by **linearity, not by price** (rationale once cost was measured). The debate was 40 of 61 subagents on that
  run, and the original argument read that as "the expensive layer, so a kill
  before it is the cheapest kill available". The first measurement refutes the
  second half: the debate is 62% of the agent count and **12% of the cost**, so a
  card killed here saves the four debate roles that card would have run, and this
  judge costs more than those four roles. What survives is the real argument — the debate is the
  **only layer linear in surviving cards**, so slate size is the one lever on
  it, and this is the **earliest authoritative** kill available rather than the
  cheapest. It is not a fourth desk editor, because the desk returns an
  uncalibrated `panel_reach` and this verdict is **checkable against sources** —
  folding the verifiable judgment into the unverifiable ladder hides the better
  signal inside the worse. **The card schema does not change**: handing
  generators a theory list would reproduce an earlier attractor, where a
  blocklist became a target menu and 9 of 20 cards named one target. Assessment
  is judge-side only.
- Agent does: convene four fixed roles per idea — an advocate
  (steelmans the contribution and the displacement claim), a skeptic
  (attacks novelty, mechanism, and identification), a feasibility
  assessor (data availability: named sources with their access route,
  expected coverage, sample size, treatment variation, measurement
  quality), and a methods
  referee (can any credible design answer this question at achievable
  power). In anchored mode the feasibility assessor holds read-only
  query access to the held data, and the profile extract sits in its
  briefing pack, under one rule: an objection a query can settle must
  be settled by a query, not asserted. Its probes obey the peek
  firewall and append to `peek_log`. This is what makes the pilot gate
  reachable. Across six real debates the assessor voted REVISE five
  times and KILL once, never EXPLORE; since the pilot requires
  unanimous EXPLORE, that one role determined the outcome regardless of
  the other three. The gate is unchanged — what changes is that a
  feasibility objection now resolves to a number instead of an
  argument. Rounds run: blind opening positions, written rebuttals,
  revised positions. Depth is adaptive: one round by
  default; rounds two and three run only while verdicts disagree or are
  still changing; cap three. Adaptive depth is what makes debating the
  full F2 cut affordable: most ideas settle in one round, and the
  tokens saved fund the comparative final below. Verdicts per agent:
  EXPLORE, REVISE, or KILL. A REVISE consensus sends the idea back for one rework and one
  re-entry, at most once. Majority KILL, or no convergence at the cap,
  retires the idea to the graveyard with its debate record.
- Pilot (no KILL from any role; author decision, second
  revision, replacing unanimous EXPLORE and then
  no-KILL-plus-majority-EXPLORE): a small-sample feasibility test, not a
  preview of the result. It verifies the data are actually obtainable
  (a registered script downloads a slice), counts coverage and treatment
  variation, sanity-checks the key measure, and produces the empirical
  inputs the S4 power/MDE block needs (N, cluster counts, outcome
  variance). Firewall, learned from the Phase 3 trial: the pilot never
  estimates the headline effect. If a viability check unavoidably
  reveals the headline direction or magnitude, the S4 pre-registration
  must disclose that as a retrospective element and declare how the
  pilot sample is handled (excluded from, or explicitly included in, the
  confirmatory sample). Pilot verdicts (**taxonomy**):
  `feasible`; `conditional` (feasible only under a stated proxy or sample
  change, which returns to the debate for a one-round check);
  `construction-open` (the named ingredient is absent and the *quantity* is
  reachable another way — not terminal, the alternative becomes a required
  design note and the card proceeds); `unmeasured` (nobody records the
  quantity, by any construction — recheck trigger is a new data release);
  `access-blocked` (it exists and this project cannot get it — recheck trigger
  is a legal or contractual change, and no longer anchored-mode-only); and
  `infeasible-unchecked`, which is what a negative verdict returns when no
  alternative construction was considered and is never terminal.
  The split exists because the pipeline reasoned over **ingredients** — fields,
  tables, endpoints — and must reason over **quantities**, which usually have
  more than one construction. The benchmark measured the cost: three cards
  declared spread and depth unreachable because the extract carries executed
  price and not the quote stack, while the human measured the same quantity
  with no order book at all, from the YES/NO no-arbitrage relation. That is an
  instrument miss wearing a data decline's clothes, and spread, surprise,
  exposure, attention, liquidity and sentiment are all constructible more than
  one way.
- Kill audit: every layer in S1b can kill, and until now
  nothing checked whether a kill was right. The asymmetry is the reason
  to add one: a wrong survival is caught downstream by the desk screen,
  the panel, the pilot, or the S8 referees, but a wrong kill is
  invisible forever, and the audit counters measure the kill rate
  without being able to tell a correct rate from a biased one. One fresh
  agent per killed idea, never a role that voted, reviews the record for
  five defects (literature error, missed remedy, category error, role
  capture, unverified premise) and returns UPHELD, OVERTURN, or REROUTE.
  Scope is judgments only: blocked and access-blocked are factual claims
  with an automatic recheck trigger and are not audited. An overturn
  re-enters step 1 without consuming the revision clinic's
  one-re-entry-ever budget, since that budget exists to stop an idea
  being iterated against the judge and this is the judge being wrong;
  capped at one overturn per idea. Two survivors are audited as controls
  under a symmetric brief, because an auditor that overturns kills and
  never questions an advance is running one direction and its overturn
  rate is then its own disposition rather than a measurement of the
  panel. The control is not blind (the record states its verdict) and is
  not described as one; a defect found in an advance is recorded and
  routed to the panel rather than acted on, since a survivor still has
  the pilot and every downstream gate ahead of it. Source: the review-the-evaluation step in
  `alejandroll10/idea-evaluation-pipeline`, narrowed from every
  judgment to the irreversible ones.
- Adjudication writes and the F2-to-F3 screen (NOT
  BUILT): every
  idea reaching a terminal state here (graveyard, blocked, access-blocked,
  clinic-exhausted) writes its verdict, kill layer, and record path to
  the adjudication store described in S1, and every kill-audit overturn
  writes a superseding edge beside the verdict it disputes rather than
  replacing it. At the F2-to-F3 handoff a machine screen checks each
  survivor's mechanism signature against the store's terminal entries and
  routes a match to the graveyard citing the matching node. The screen
  sits before the novelty audit deliberately: the trial caught two
  recurrences by hand only after F2 scoring had been spent on them, and
  the whole value of the check is that it is the cheapest layer in F3.
- Comparative final: pilot-cleared candidates do not reach
  G1 on solo verdicts. The panel reconvenes once with all survivors'
  `handoff/` packets side by side and answers a comparative question —
  which of these papers most deserves to be written, which displaces
  more, which is likeliest to survive S8 — producing a head-to-head
  ranking with stated reasons. Rationale: the costly failure is not a
  bad pilot but a full run spent on the second-best idea; selection is
  a comparison, not a threshold. The final reads `handoff/` packets
  only, so cross-idea contamination stays out of the clean room's
  per-idea walls.
- **Research proposal per presented card**: the verdict says
  which gates a design cleared, which is a machine's answer to a machine's
  question. The author picks what to spend six months on, and that decision is
  made against a readable argument. So every card presented at G1 also carries a
  **1-2 page research proposal** on the seven-section outline in
  `references/research-proposal-outline.md`. It is written as a rendering of the
  card's verified `handoff/` artifacts and never as new generation, which is what
  makes it safe to add to a stage otherwise built to keep speculation out: the
  background comes from the F0 brief and the card's setting, the literature
  review from `novelty_facts.md` and `paper_set`, the methodology from the pilot
  report's computed sample and binding constraint, and the implications from step
  1.5's outcome-conditional table, whose three cells are the same question *who
  benefits* asks from the other end. Fallthrough proposals carry the
  did-not-clear line.
- **G1 is a two-sided threshold gate** (author decision, replacing in turn a
  feasibility menu, a best-available floor, and before those a selection bar).
  The stage both **refuses**
  cards below a declared bar and **promotes and improves** cards at or near it,
  and **the number it passes is not fixed**: zero is a legitimate complete
  result and so is six.
  The ladder is reused verbatim from the promoted `finance-idea-screening`
  skill — six scored dimensions, hierarchical gates A-E, archetype parity
  against the calibration set, a rule-based novelty-confidence cap — giving
  `top-generalist-candidate` / `strong-field-candidate` / `revise` / `kill`.
  **Gate F, feasibility, is added and is hard**: a pilot verdict outside
  `feasible`/`construction-open`, or a computed usable sample below
  `usable_min`, refuses the card at any score. An idea that would be excellent
  on data nobody has is not an available idea, and this is where the
  feasibility insight is kept — as a refusal rather than as the ranking key.
  **The threshold is `g1_threshold` in `pipeline-config.md`, default
  `top-generalist-candidate`: the top-3 bar, and the same bar whatever the
  topic.** The gates never reference topic; Gate D adapts the comparison set to
  the card's mechanism and identification style, which changes what a card is
  measured against and not where the bar sits.
  **The slate is exactly the cards at or above the threshold, and the count is
  reported.** No range, no padding, no fallback to a lower band. Zero routes to
  the slate-level DECLINE triage — the old menu's
  guarantee that it "always returns items" made *the theme was a bad bet*
  unsayable, which is the finding the funnel most needs to be able to report.
  **What follows a zero is set by `g1_fallthrough`** (default `strong-field-candidate`). With it set, the stage states
  the zero, reports the DECLINE diagnosis, and then presents a **separately
  labelled fallthrough tier** for author review, ending at CHECKPOINT rather
  than ARCHIVED. The threshold does not move and no verdict changes: the key
  decides whether the stage *stops* on an empty slate or *shows what it found*.
  Five rules keep it from becoming the deleted menu — the top-tier count is
  stated first and on its own even at zero; the tier is labelled by what it did
  not clear and every card repeats the label; the tiers are never merged,
  renumbered, or summed; no fallthrough card is described as having cleared
  anything; and the DECLINE diagnosis is reported regardless, because *why* the
  top tier is empty is the finding and the fallthrough tier does not answer it.
  ARCHIVED now requires an author DECLINE, an empty fallthrough tier, or
  `g1_fallthrough: none`.
  Many is equally complete: all are presented, the author picks one, the rest
  bench **at their verdict** rather than as runners-up.
  **The promote half is structural, not an annotation.** Every
  `strong-field-candidate` is presented with the gate that capped it, the
  cheapest action that would clear it, and whether that action is in the
  revision clinic's scope. Rework is **author-triggered** in both gate modes:
  the clinic's budget is one per idea and spending it on every near miss would
  exhaust it on the cards that needed it least.
  **Per gate, the verdict says whether it cleared on a checkable or a judged
  basis** — Gate A (displacement target against a source) and Gate D (parity
  against named calibration papers) are checkable, B/C/E are judgment, F is
  computed. A rung asserts **gate clearance and never a predicted placement**;
  an artifact implying one is a validation failure. That is's rule
  kept in the form that was right, and it is what keeps the restored threshold
  from being the discarded verdict under a new name.
  A fresh generation cycle is still available and still capped at two per
  project slot, at the author's option.
- Bench: runners-up keep their lineage directories —
  debate record, pilot, handoff packet — as a warm bench. A downstream
  kill (a killer paper at S2, a failed G3 pivot, a fatal S8 finding)
  re-enters at G1 with the bench, not at S1 from scratch: turning back
  costs one gate decision, not a restart. Bench entries expire with
  the calibration-set staleness rule (six months); a stale benched
  idea re-runs its feasibility check before re-entering G1.
- Fallback triage: when F3 leaves the slate short — no
  comparative winner, or the winner later fails downstream — the way
  out depends on why the idea failed, read from F3's own record, never
  from hope:
  1. Data failure (no obtainable source on any named route, coverage
     collapse, an `unmeasured` pilot verdict): blocked, not dead. The idea
     enters the blocked registry
     with its missing ingredient named (dataset, access, sample
     length) **and the access route recorded beside it** — a registry holding
     only the ingredient cannot tell a new data release from a new licence,
     and those are the two different events that would unblock it; every new
     run rechecks the registry before swarming, and
     an unblocked idea re-enters F3 directly. If the feasibility
     assessor named a viable setting or proxy swap, the idea goes to
     the revision clinic instead. A `construction-open` verdict is not a data
     failure and does not triage here — the named alternative construction
     becomes a required design note and the card proceeds.
  2. Contribution failure (occupied margin, weak displacement,
     unanimous desk reject): kill and explore. Upgrading a
     contribution-weak idea is the sunk-cost trap — polish does not
     create a margin. Sole exception: the novelty audit or the skeptic
     named a specific adjacent margin that is open; that becomes a new
     idea card routed to the revision clinic, crediting its graveyard
     parent.
  3. Execution failure (no credible identification, hopeless MDE):
     revise only if the methods referee named a concrete design fix
     (different instrument, outcome, or sample). Otherwise blocked
     registry (method-blocked) or graveyard, per the report.
  4. Access failure (anchored mode): the data exists
     in house but licence, consent, or redistribution terms forbid this
     use. Blocked registry with the missing ingredient recorded as
     permission, kept distinct from a data failure because its recheck
     trigger is a legal or contractual change, not a new data release.
     An idea blocked on access is never quietly rerouted to a public
     proxy; the proxy is a different idea and re-enters as one.
  Revision clinic: a failed idea earns at most one rework, written by
  a fresh agent from the record's named findings — never the advocate,
  who is invested — and the reworked card re-enters the full F3
  gauntlet: no shortcut past the audit, the panel, or the pilot, so
  revision can never become the bar-lowering path. Revised ideas fill
  their cycle's slate; they do not extend it.
  Directed exploration: when a cycle's kills cluster on one failure
  type, the next swarm inherits that as a generation constraint (all
  deaths by data means F1 prompts require a named access route), so
  exploration learns from the graveyard instead of resampling it.
  Precedence when refilling the slate: bench first (already
  pilot-cleared), then unblocked registry entries, then revision-
  clinic output, then a fresh swarm cycle. The cycle cap holds at every
  step. Note what the threshold did and did not change here: refilling means bringing *more cards* to be scored, never
  relaxing the bar for the cards already scored. A killed card is still
  killed and a `strong-field-candidate` is still below the threshold; the
  refill precedence decides what else gets a verdict, not who passes. The
  old menu's job — stopping the stage from returning nothing — is gone on
  purpose: returning nothing is now a reportable result.
- **Calibration-blocked, checked before any other slate diagnosis**. An empty slate says one of two very different things: *these
  cards do not clear the bar*, or *this run could not tell*. Gate D
  (archetype parity) is the calibrated gate, and it does not clear when the
  calibration set has fewer than 8 in-field entries in the `top3_finance` or
  `strong_field` class — the verdict then caps at `strong-field-candidate`
  with the reason named, exactly as a missing calibration file caps it. A
  slate empty for that reason is reported as **`no verdict possible`**, not
  `nothing cleared`, and routes to `calibrate-rubric` rather than to a new
  theme. Re-theming on a calibration gap discards a slate that was never
  judged, which is the most expensive response to the cheapest problem.
  **As of the v2026-08 rebuild this gate clears** for `field_profile:
  finance`: **55** in-field `top3_finance`, **31** in-field `strong_field`,
  **20** in-field `stalled`, against a floor of 8 — so a card can be awarded
  `top-generalist-candidate` again. The v2026-06r1 state recorded here (27 /
  0 / 0) was the contaminated build, whose named cause was a resolver that
  took the first fuzzy hit and returned *International Review of Economics &
  Finance* for *Review of Finance*; the build now pins verified source ids and
  resolves nothing by name. Counts read from
  `references/top_journal_calibration.json` (v2026-08, 141 papers, built); its `selection_bias_summary` carries the class definitions and
  the standing shortfall (2 household `stalled` entries against a per-area
  floor of 4).
- Slate-level triage — the DECLINE route: the four
  classes above triage **one card**, and nothing triaged **the slate**. The
  menu's own guarantee hid the gap — it always returns items, so there was
  never a defined action for *the author reads the menu and declines all of
  it*. DECLINE is that action, and like the per-card triage its route is read
  from the run's own counters:
  **contribution-thin** (most cards `REFRAME` or `CONTRIBUTION-NULL`, ≤1 live
  contribution cell across the slate, few or no `verified` displacement labels)
  routes to a **new theme, not a new cycle** — if the cards are individually
  sound and collectively say nothing, the theme is what failed, and generating
  again inside it finds the best available version of a bet not worth making;
  the graveyard's mechanism signatures carry forward as a blocklist.
  **Feasibility-thin** (most cards terminal-negative or conditional on the
  *same* binding constraint) routes to the blocked registry with one named
  ingredient **and its access route**, plus a data-acquisition question for the
  author; if the constraint differs per card it is a design problem wearing a
  data problem's clothes and routes to the clinic instead — the pilot's
  binding-constraint column is what separates the two, which is why that column
  is required rather than advisory.
  **Execution-thin** (the methods referee is the modal killer, on different
  defects per card) routes to the clinic, one rework each, cycle cap unchanged.
  DECLINE is logged with `gate-log` and the run ends **ARCHIVED**, not PARKED:
  a declined slate is finished work with a negative result, and PARKED would
  tell the next session something is still owed. Note the distinction an earlier fallthrough introduces: **running the DECLINE triage is not the
  same act as the author declining.** An empty slate always runs the triage and
  reports its route; only an author DECLINE, an empty fallthrough tier, or
  `g1_fallthrough: none` ends the run.
- Self-verification: every feasibility claim in the debate cites a
  source, a logged search, or a pilot number, never memory (Material Gap
  rule); the debate record shows each agent's verdict in each round, so
  the pilot gate's single condition (no KILL from any role) is
  checkable rather than asserted, as is the desk tier each editor
  returned and the median the card carries. The record also carries three
  audit counters — debate kill rate, screen-versus-debate disagreement
  rate, pilot-contradicts-debate rate — so S1b's depth is grown or cut
  by measurement after each run, not by taste.
- Artifact: per-idea `debate_record.md` (positions, rebuttals, verdicts
  by round), `data_availability.md`, and `pilot_report.md` in the idea's
  lineage directory; pilot scripts registered in the script registry.
- Human gate G1 (idea, relocated here): the author is shown **the slate —
  every card at or above `g1_threshold`, which may be none** — with each
  card's verdict and per-gate split, its counts and binding constraint, the
  debate records and pilot reports, and beside it every
  `strong-field-candidate` with the gate that capped it and the cheapest
  action that would clear it. The author picks, declines, or commissions a
  rework. Recorded in. **On an empty slate with
  `g1_fallthrough` set** the checkpoint carries three parts in order — the zero,
  the DECLINE diagnosis, then the labelled fallthrough tier — and the author may
  additionally take a fallthrough card forward, in which case the G1 acceptance
  record must state that it did not clear the threshold and why the author
  proceeded anyway. Autonomous mode rule
  (`playbooks/gate-modes.md`): 0 clearing the threshold → DECLINE triage, then
  PARK if a fallthrough tier exists (taking a card that did not clear the bar is
  a judgment no rule may make) and end ARCHIVED if it does not; 1 → advance it;
  more than 1 → PARK, because choosing among
  designs that all clear the bar is a judgment about what is worth six
  months. On a downstream kill, re-enter with the bench and walk the
  fallback precedence; a benched `top-generalist-candidate` re-enters at its
  verdict, subject to the staleness rules.
- Machine gate (pilot authorization): the pilot refuses to run without a
  a recorded verdict block with no KILL and a majority of EXPLORE; S4's
  pre-registration must reference the
  pilot report and state the pilot-sample handling.
- Escalation: a pilot that contradicts the debate's feasibility premise
  (coverage collapse, dead variation, broken measure) reopens the debate
  with the pilot numbers attached rather than proceeding on the original
  premise.
- Model policy: all four debate roles run on the strong model (L11);
  this is judgment-call territory, the exact place autonomy is spent
  deliberately.
- Component reuse: the panel is seated from S8's review
  machinery run in ex-ante mode — skeptic and methods referee take the
  SKEPTIC and CREDIBILITY dispositions from peer-review's taxonomy,
  the advocate follows its contribution-panel protocol, and the
  claims-are-leads verification discipline and bounded-round
  convergence carry over. The S8 skill itself is not invoked at S1b:
  its integrity pre-gate, replication referee, and opposition walk
  presuppose a manuscript with traceable numbers, which an idea card
  does not have. Details in `docs/skill-specs.md`, S1b.
- Isolation, the clean-room rule: ideation and debate run
  in an isolated environment so their advocacy, speculation, and labels
  cannot contaminate later stages. This mirrors, at the front end, the
  L7 rule segregating `reviews/` from analysis inputs at the back end.
  Three walls:
  1. Role isolation. Each debate role runs in a fresh agent context
     given only a briefing pack: the idea card stripped of F2 scores
     and desk-reject verdicts (judgments anchor), plus the F3
     novelty-audit fact sheet (verified search findings are evidence,
     not advocacy, and the skeptic needs them), plus — in anchored mode
     — the F-1 profile's handoff extract. The pack carries no
     data-availability memo: that memo is the feasibility assessor's
     own position, written during the debate, so it cannot also be an
     input to round one. Debaters
     never see the main session, STATE.md, or other candidates'
     debates; round-one positions are written blind and in parallel,
     and rebuttals open only after all positions are filed. Blindness
     to screening labels keeps the debate an independent second filter
     rather than a confirmation of the screen; screen-versus-debate
     disagreement is recorded in the debate record as signal, not
     reconciled away.
  2. Artifact quarantine. Each idea's lineage directory splits into
     `quarantine/` (full debate transcript, rebuttals, speculative
     magnitudes or directional expectations, raw pilot outputs) and
     `handoff/` (the refined idea card as the debate's sanitized
     distillate, `data_availability.md`, and the pilot report's
     feasibility section: coverage counts, variation, measure checks,
     MDE inputs — no directional language). Stages S2 through S7 read
     only `handoff/`. S8 referees may read `quarantine/`: they audit,
     they do not build.
  3. State hygiene. STATE.md, lab-notebook, and run-log entries about
     S1b carry verdicts and artifact pointers only, never the debate's
     substantive expectations, because S0 reads state into every later
     session and would otherwise re-import the contamination.
  Machine gate (quarantine check): at S4 entry and again inside S7's
  gate stack, a grep-level check confirms no downstream artifact
  (hypotheses, preregistration, manuscript) references a `quarantine/`
  path or quotes the debate transcript; a hit fails the stage like a
  claim-ledger failure. The quarantine binds agent contexts and
  artifacts, not the author: G1 presents the full debate record to the
  author by design.

### S2. Literature and positioning

- Agent does: run searches through Corbis/OpenAlex, merge results into the
  canonical deduplicated paper set, tier papers by relative citation rank
  (top 10 percent foundational, next 30 percent established, rest emerging),
  write the positioning memo (closest papers, exact differences), and build
  the bibliography.
- Self-verification: every search is logged with query and parameters; every
  bibliography entry is checked against search metadata. No citation enters
  any draft unverified (L6, machine gate).
- Artifact: `paper_set.json`, `search_log.md`, positioning memo, verified
  `.bib` entries.
- Human gate G2 (framing): the author approves the positioning and the
  threat list (which existing papers could kill this one).
- Escalation: unverifiable citation metadata is flagged
  `[MATERIAL GAP: journal unconfirmed]` and excluded from drafts until
  confirmed; it is never silently included.
- Phase 2+ option: a local RAG corpus over the paper set's PDFs for
  page-level claim grounding (Caforio pattern), added only when the plain
  search-and-verify loop proves insufficient.

### S3. Hypotheses

- Agent does: turn the economic mechanisms into numbered, directional,
  falsifiable hypotheses argued from 2 to 4 supporting papers each; decide
  whether a formal model earns its place (structural parameters, a
  quantitative bound, or a model-implied identifying restriction) or prose
  hypotheses suffice.
- Self-verification: each hypothesis cites papers present in
  `paper_set.json`; the formal-model decision is stated with its reason.
- Artifact: hypothesis-development section draft.
- Human gate: folded into G3 (the author signs hypotheses and specification
  together at the design freeze).
- Escalation: a mechanism with no literature support is flagged as
  speculative rather than dressed with weak citations.

### S4. Research design and pre-registration

- Agent does: write the pre-registration: hypotheses, primary specification
  (units, treatment, outcome, controls, fixed effects, clustering), the null
  statement (what will be reported if the result is flat), and which
  alternative specifications are exploratory.
- Self-verification: the specification is complete enough that S6 can run
  without further design decisions.
- Artifact: `preregistration.md`, author-approved and committed to git so the
  hash timestamps the freeze (L3, machine gate: S6 refuses to run without a
  committed pre-registration).
- Human gate G3 (design freeze): the author approves, pivots, or kills.
  Design pivots later add a new dated block; the original freeze is never
  overwritten.
- Escalation: any post-freeze deviation in S6 must reference a dated
  amendment or stop.

### S5. Data construction

- Agent does: build the data pipeline from the sources the design names,
  each with its access route recorded — held, public (SEC EDGAR, FRED,
  Ken French, OEWS, Yahoo Finance), licensed, purchasable, or restricted
  — with checkpointing for long crawls, register every script in the
  script registry (purpose, inputs, outputs, packages), and produce a
  coverage report.
- Self-verification: the registry audit passes (no unregistered scripts, no
  missing or stale outputs, L10); crawls resume from checkpoints rather than
  restarting; harness survival rules hold (absolute paths, single-threaded
  rate-limited APIs, L13).
- Artifact: `script_registry.json`, checkpointed datasets, coverage report.
- Source policy (extended the same day):
  the pipeline has no free-data requirement. `data_access: any` admits
  any source with a named access route — held, public, licensed,
  purchasable, or restricted — and held or licensed data may carry the
  headline, overriding the workspace `data-pipeline` rule that no
  proprietary source becomes a primary spine. What the old rule
  protected was referee collectability, and that is now bought with
  disclosure rather than prohibition: every idea carries a spine tag
  (private, hybrid, or public) and a replication plan naming what ships
  — derived extract, schema, code, a synthetic twin — and what cannot,
  with the reason. Two switches restore the conservative behaviour where
  a venue demands it: `data_access: free_only` bars non-free sources
  outright, and `private_spine: extension_only` lets held data sharpen
  measurement or validate but never carry identification.
  What the change does not relax: a source still has to be obtainable.
  The route is the feasibility question, not the price, and a card that
  names no route is treated exactly like a card naming a field that does
  not exist.
- Human gate G4 (data calls): the author approves proxy and source
  choices, and in anchored mode the spine tag and replication plan.
- Escalation: structural breaks, coverage collapses, or proxy failures go to
  the author with options, not silent workarounds (the 2504.09736 pattern).

### S6. Estimation and robustness

- Agent does: implement the pre-registered estimator, pass the
  synthetic-first gate (recover a planted effect on synthetic data, then
  reproduce a hand-derived reference for the estimand before any estimation
  package is trusted, L4, machine gate), run on real data, write results to
  keyed JSON, then run the robustness checklist: pre-trends and placebos,
  confound controls, alternative treatments and outcomes, subsample
  uniformity, and equivalence or minimum-detectable-effect bounds for any
  null result.
- Self-verification: synthetic recovery log; per-finding robustness verdict
  (robust, confounded, or underpowered); a null without equivalence bounds
  cannot be labeled precise.
- Artifact: results JSON files, synthetic-recovery log, per-finding
  robustness verdicts.
- Human gate G5 (survival): the author decides what survives and at what
  evidence bar.
- Escalation: estimator-library disagreement beyond tolerance stops the
  stage; it is never averaged away.

### S7. Writing (data-chained)

- Agent does: assemble the LaTeX manuscript with tables and prose numbers
  generated from results JSON (numbers are never typed), draft the
  introduction to the punchline-first spine, run the banned-words and
  AI-tell pass, build the claim ledger linking every load-bearing claim to
  its results path with tolerance and a mechanism check, and verify all
  citations.
- The chain: the paper is a build target, not a
  document that agrees with the results. A Makefile declares the path from
  extracts through estimation to the PDF, prose numbers are emitted as
  LaTeX macros from the claim ledger, and `make verify` (clean rebuild plus
  every integrity gate) is the reproducibility claim. Source and generated
  files are classified, and a wrong number is repaired at the results key
  and its producing script, never on the page. This closes the L5 upgrade
  path below: the ledger detects drift, the macros make it unrepresentable.
- Self-verification: four machine gates: rebuilds from source (`make
  verify`), claim-ledger validator and macro check exit 0 (L5), citation
  verification passes (L6), LaTeX compiles clean.
- Artifact: manuscript, `Makefile`, `claim_ledger.json` (validated),
  `values.tex` and its lock file, verified bibliography.
- Human gate: none here; the author's writing decisions surface at G6 after
  review. The one judgment the build surfaces is a moved headline number:
  the emit diff reports it, and accepting it is a decision, not a rebuild.
- Escalation: a claim whose number cannot be traced to a results file is
  removed or flagged, not defended.
- Staleness by content, not timestamp: the registry records a
  hash of each script's parsed code and of each declared output at the
  moment a good build produced them, so "was this output produced by this
  script?" stays answerable in a fresh clone, where git gives every file the
  checkout time and mtime ordering means nothing. The parsed tree is what is
  hashed, so a comment or a reformat is not an alarm. `make verify` runs
  `distclean` for the same reason: Make rebuilds only on a strictly newer
  prerequisite, so leaving the results in place would let the rebuild claim
  pass without re-deriving anything.
- Phase 2+ upgrade path: claim-to-code run-order checks (L5).

### S8. Adversarial review (new relative to the predecessor workflow; full-rigor scope)

- Agent does: run the simulated editorial pipeline (L7) at full scope: an integrity pre-gate (claim ledger,
  script registry, citations, compile) that desk-returns any paper whose
  numbers do not trace before referees spend tokens; an advocate-versus-
  skeptic panel on the contribution claim; a journal-calibrated editor
  desk review with a mandatory novelty probe; four blind referees: two
  with opposed dispositions drawn from an explicit taxonomy (structural,
  credibility, measurement, policy, theory, skeptic), a replication
  referee who re-derives every table and figure number from the results
  JSON and the script registry, and a standing opposition referee briefed
  to attack everything (methodology, literature, findings, discussion,
  contribution, significance) and to walk the whole paper as one argument
  chain hunting for incoherence and broken logic; verification of every
  referee finding
  against the manuscript and artifacts before synthesis (referee findings
  are leads, not verdicts); an editorial synthesis triaging verified
  findings as fatal, addressable, or taste; and a critic-fixer loop that
  exits after two consecutive clean rounds, capped at five. Modes: R&R
  continuation (concerns classified resolved / partial / not addressed,
  cap at round 3), hostile-editor stress test, decision-distribution
  variance mode (N sampled referees), and a fast two-agent light check.
  The inference-quality audit (Edmans evidence ladder) is embedded in
  every referee report and runs standalone before G6.
- Self-verification: every referee finding cites a manuscript location and
  survives verification; dismissed flags are logged so the triage is
  auditable; fixes re-enter the loop rather than being taken on faith.
- Artifact: review reports, verification log, and decision letter in
  `reviews/` (segregated from analysis inputs, L7), fix log, final audit.
- Human gate G6 (title and overclaim): the author signs off on the title,
  abstract, and claim strength; decides whether the paper is ready.
- Escalation: a fatal finding that survives the fix loop goes to the author
  with the referee report, possibly reopening G3 or G5.
- Review skills run only when explicitly invoked (never self-triggered);
  all referees run on the strong model per the config model policy (L11).
- Calibration profiles by field (L14): JF/JFE/RFS for finance,
  AER/QJE/JPE/ECMA/ReStud for economics, JoE/JAE for econometrics. The
  referee taxonomy is shared; the journal profile sets desk-reject
  standards, expected identification rigor, and format norms.

### Theory branch (optional)

When S3 decides a formal model earns its place: a proof skill writes the
model and propositions with single-pass rigor, and a separate
exposition pass improves readability without touching the mathematics. The
branch re-enters the main pipeline at S4.

## 4. Gate table

| Gate | Type | Where | What must hold |
|------|------|-------|----------------|
| Session close | Human | end of every session | author activates handoff + commit; never self-triggered |
| G1 idea | Human | after S1b | author is shown the slate (every card at or above `g1_threshold`, possibly none) plus every capped card with its gate and cheapest fix; picks, declines, or commissions a rework; decision logged |
| G2 framing | Human | after S2 | author approves positioning and threat list |
| G3 design freeze | Human | after S4 | author signs pre-registration |
| G4 data calls | Human | after S5 | author approves proxies and sources |
| G5 survival | Human | after S6 | author sets the evidence bar |
| G6 title/overclaim | Human | after S8 | author signs title, abstract, claim strength |
| Funnel floors | Machine | inside S1 | raw pool >= 100 (one swarm retry, then logged shortfall); F2 cut within 20-25 |
| Profile freshness | Machine | inside S1, anchored | F1 refuses to run without a profile newer than the manifest's refresh cadence |
| Anchor existence | Machine | inside S1, anchored | every field an anchored or extended card names exists in `data_profile.json`; a card naming an absent field is downgraded to unanchored and logged, never scored as anchored |
| Panel reach | Machine | inside S1b | every desk verdict carries one of five `panel_reach` rungs (`very-high`, `high`, `moderate`, `low`, `none`); the card's median reach kills only when it is `none`. Reach is model judgment, not a calibrated outcome, and no artifact may report it without that qualifier. Renamed from journal-tier labels, because a rung named an editorial outcome nobody had checked. **Premise**: the stated ground was "the calibration set is 62 papers, all top-3", which was wrong twice over. Under v2026-06r1 the file was 43 accepted / 17 stalled / 2 uncertain; under the **v2026-08 rebuild it is 141 papers, in-field finance 55 `top3_finance` / 31 `strong_field` / 20 `stalled`**. The rule stands on the ground that survives both builds: **no entry links a rung to an editorial outcome**, so reach is uncalibrated whatever the contrast classes hold. The v2026-06r1 corollary that the finance contrast classes were empty is **superseded** — they are populated now, which is what lets Gate D clear, and it still does not calibrate `panel_reach`. **Scope**: any journal name used as a *reach* rung is a validation failure; the G1 ladder's `top-generalist-candidate` / `strong-field-candidate` are not reach rungs and are not covered, because they assert gate clearance rather than placement |
| Novelty gate | Machine | inside S1b (step 1.5) | every card the desk did not kill carries a `novelty_verdict.md` with four blocks and a parseable ```novelty block whose `contribution_cells` matches its table; every theory rung names a **returned** source and every `untested` rung carries the queries that failed; at least one **mechanism-scoped** query per card is in `search_log`, written without the theme's nouns. **A `CONTRIBUTION-NULL` requires a second independent confirmer**, may not rest on a TITLE-ONLY citation or on an `untested` rung, must quote the occupying paper's verified claim, and carries a decision-audit verdict under defect class 7 with a novelty-cleared control. The verdict is quarantined: any occurrence under a `handoff/` path, or in a debate briefing pack, is a validation failure. Every menu item reports it beside `panel_reach` and marks it as **the checkable one** — reach is a guess at an editorial outcome with no held-out evidence, this is a claim about named sources. Counters carry the novelty-versus-feasibility rank correlation, because a run where the two orderings coincide is a run where the layer added nothing to G1. Added |
| Adjudication screen (SPECCED, NOT BUILT) | Machine | S1 to S1b | every F2 survivor's mechanism signature is checked against the adjudication store's terminal entries; a match routes to the graveyard citing the matching node, before any audit or desk-simulation tokens are spent. No skill implements this yet: the spec is in `docs/skill-specs.md` and the marker is dropped when `idea-scoring`'s validation list carries the check |
| Pilot authorization | Machine | inside S1 (themed) or S1b (swarm) | **Two entries**. Themed path: `themed-prepilot` runs the pilot on **every variant** before any debate — there is nothing to authorize, because the gate's job was rationing a layer that turned out to be the cheapest in the funnel. Swarm path: unchanged, a recorded verdict block with **no KILL vote from any role**, EXPLORE not required (second revision; the two earlier settings would each have fired zero times on the four runs to date). Both entries: a `feasible` verdict is **never** evidence about identification, and a pilot report that opines on credibility fails validation |
| Decision audit | Machine | inside S1b | every judgment-based terminal decision carries an audit verdict — **kills and advances alike**; findings quote the disputed record text and name a defect; **layer-matched** controls were audited; a finding proposing a setting swap to unheld data is labelled `requires_data_beyond_held_extract` and routed as a new idea rather than counted as a defect. Trialled for the first time: 4 of 5 kills upheld, 1 rerouted, 0 overturned, against 2 of 3 advances flagged. The old F2-rank control rule drew never-debated cards and was replaced |
| G1 threshold | Machine | inside S1b | every surviving card carries a verdict on the `finance-idea-screening` ladder (`top-generalist-candidate` / `strong-field-candidate` / `revise` / `kill`) with a **per-gate cleared/capped line marked checkable or judged**, and the slate is **exactly the cards at or above `g1_threshold`** (default `top-generalist-candidate`) — none, one, or many, count always reported. **Gate F, feasibility, refuses at any score**: pilot verdict outside `feasible`/`construction-open`, or a computed usable sample below `usable_min`. Every slate item still carries a **computed** usable sample traceable to a registered script (never an assessor's estimate — that substitution was an 8-to-10x error on), a named binding constraint, the cheapest relaxing action, an advisory `panel_reach` labelled *judged, not calibrated*, and its unreconciled objections. Every `strong-field-candidate` carries the gate that capped it and the cheapest action that would clear it. **A slate padded to a count, or refilled from a lower band, is a validation failure**, and so is any artifact implying a predicted journal placement — a rung asserts gate clearance only. **Fallthrough tier**: on an empty slate, `g1_fallthrough` (default `strong-field-candidate`, `none` disables) presents the capped cards for author review instead of ending the run. The threshold does not move and no verdict changes. Four checks, each a failure: the top-tier count appears before the first fallthrough card and is stated at zero; the tier and every card in it are labelled by what they did **not** clear; the tiers are never merged, renumbered, or summed; and no fallthrough card is described as cleared, on the slate, or passed. A fallthrough tier presented beside a **non-empty** slate is padding by another route and fails. A fallthrough card carried forward needs a `g1_acceptance.md` stating it did not clear the bar and why the author proceeded. Autonomous mode: 0 clearing → DECLINE triage, then PARK if a fallthrough tier exists, ARCHIVED if not; 1 → advance; more than 1 → PARK. Author decision, replacing the feasibility menu of |
| G1 acceptance | Machine | G1 to S2 | the picked card carries `handoff/g1_acceptance.md`: every surviving objection with its disposition (discharged / accepted as a limitation / deferred to S4), every audit dispute and its resolution, the step 1.5 `REFRAME` note, and the retrospective-disclosure line. **S2 refuses to run without it** — same logic as the pre-registration commit gate, one stage earlier: a decision that lives only in conversation cannot be audited by the next session. The novelty verdict's *facts* move to `novelty_facts.md` at the same moment; the verdict itself stays quarantined. Added |
| Reachability | Machine | inside S1/S1b (pilot) | no negative pilot verdict is terminal without a ```reachability block naming the **quantity** the design needs (never a field name) and one alternative construction with why it fails. A verdict lacking one is `infeasible-unchecked`, is counted in no kill rate, and cannot enter the graveyard. The verdict set is `feasible` / `conditional` / `construction-open` / `unmeasured` / `access-blocked`, with `access-blocked` generalized out of anchored mode because a licence wall has a different recheck trigger from a data gap. Every supplementary source recommended carries a route, a key, a **verified** join probe with a real match rate, and a cost/time estimate. Added after the benchmark found three cards declining spread and depth as a data purchase while the human measured the same quantity with no order book |
| Data request | Machine | inside S1/S1b (pilot), reported at G1 | every pilot report carries a ```data_request block, `status: none` included; a block at `would-strengthen` or `required` names the **quantity** in the design's own terms (a field or table name is a validation failure), at least one candidate source with a route, and a `fallback`; every candidate carries a **verified** probe with a real match rate or an explicit `unprobed:` reason, never a bare expectation; a `required` block with no fallback routes the card to the blocked registry rather than the slate. The driver aggregates the blocks into `<ideas_dir>/data_requests.md` and authors none of them. Added after the author's decision to acquire data the funnel asks for: until then a data need could surface only as a kill verdict or inside the slate-level feasibility-thin route, so a card that was alive but would be materially better on data nobody held had no way to say so |
| Research proposal | Machine | inside S1b (step 4b), presented at G1 | every card presented at G1 — slate **and** fallthrough tier, one per card — carries `handoff/research_proposal.md`: **800-1,200 words**, the seven sections of `references/research-proposal-outline.md` present and in order (working title, background, research questions, literature review, data and proposed methodology, implications, references), no section empty, the background naming a **discipline** and not only a topic, the research-questions section answering *what is new* against named prior work rather than asserting it, and at least two reference entries. The proposal is a **rendering of the card's verified `handoff/` artifacts, never new generation**: a fact absent from those artifacts is a Material Gap violation, every citation resolves to a verified `paper_set` entry, and every number traces to the pilot report or the profile. A **fallthrough** proposal states on its face that the card did not clear `g1_threshold`, names the capping gate and the cheapest clearing action — a polished two-page proposal is exactly the artifact that could launder a capped card into looking like a cleared one. No placement language and no directional expectation about the result, which would breach the pilot firewall. Added |
| Counting definition | Machine | inside S1/S1b (pilot) | one `usable_min` per run, declared in config and printed in every report with the unit it counts; every reported count carries a ```count block whose `expression` is the literal source line, re-executed by the harness and failed on mismatch; every count carrying a terminal verdict or a menu number is derived twice by independent expressions, and a disagreement blocks the verdict rather than being resolved by picking one. Added: both of an earlier run's confirmed arithmetic defects were a count computed at one unit and labelled at another, with the prose accurate about intent |
| Pilot firewall | Machine | S1b to S4 | prereg references the pilot report and declares pilot-sample handling |
| Peek ledger | Machine | S1 to S4, anchored | every query run against held data appears in `peek_log`; the prereg reads the ledger and declares its retrospective elements |
| Quarantine check | Machine | S4 entry and inside S7 | no downstream artifact references `quarantine/` or quotes the debate transcript |
| Pre-registration commit | Machine | S4 to S6 | S6 refuses to run without committed freeze |
| Synthetic-first | Machine | inside S6 | planted effect recovered; the estimand's `meta.reference` derived by hand twice, by independent routes, agreeing to floating-point tolerance, before any estimation package is run; the package call then tested against that reference, with any disagreement resolved by naming the differing convention (aggregation weights, instrument set, df rule) and never by preferring the package. Revised: the old rule read "library match", which cannot see a package that computes a different estimand without erroring — the failure the w35588 reading note records at |
| Estimand weighting | Machine | S4 to S6 | a multi-period, staggered, or event-time design carries an aggregation-weighting **formula** in prereg block 2; a package name is not a formula. Unfrozen, the estimand is chosen after the freeze by whichever package call S6 reaches for. Added |
| Claim ledger | Machine | inside S7 | validator exits 0 |
| Generated values | Machine | inside S7 | macro emit and check exit 0: no prose number typed, no macro-backed literal, no unused macro |
| Rebuilds from source | Machine | inside S7, before milestones | `make verify` exits 0: clean rebuild plus every integrity gate |
| Citation verification | Machine | S2 and S7 | no unverified citation in any draft |
| Compile clean | Machine | inside S7 | LaTeX builds without errors |
| Run ledger | Machine | milestones and before submission | `run-ledger` reconciles the session queue against the transcripts on disk and reports both directions (a queued session with no transcript, and a transcript in no queue row, are different defects); reports runtime as **wall clock and gap-capped active time both**, because wall clock across an overnight session is not a measure of effort; reports **tokens by type as the primary figure** with the list-rate dollar equivalent beside it and **always carrying its not-an-invoice label**, since Claude Code plans bill against usage limits; inventories every data file with size, sha256 and its registered producing script, excluding the pipeline's own bookkeeping files named in config; and renders a reproduction document stating plainly that **`make verify` covers estimation through the PDF and not the crawls**, which sit outside the build graph by design. Default mode reports and refuses nothing so it is usable mid-run; `--final` is the gate and exits nonzero on any artifact absent, stale or unreconciled. It authors no fact. Added |
| Review convergence | Machine | inside S8 | two clean rounds or cap; fatal findings escalate |
| Review rendering | Machine | every human gate | every artifact presented at a gate is delivered as a **PDF**, rendered by `<tools_dir>/review_pdf.py` into one packet per gate, and the checkpoint names the PDF path. Markdown remains the machine-readable source the skills read and the ledger traces; it is not what the author is asked to read. Four failures: a checkpoint naming a `.md` path, a packet older than any source bound into it, a fact in the packet that is in no source file (the driver renders and never authors), and a failed render worked around by handing over Markdown instead of reported. The manuscript is already a PDF by S7 and is not re-rendered. Added (author decision): a gate document is read once, carefully, by someone deciding something and often away from the terminal, and a slate's tables rendered as pipes in a terminal lose the structure the document was written to carry |

**An approved gate advances the run.** Once the author decides, the decision is
logged, applied as an input to the next stage, and the run continues without a
further prompt: G1 into S2, G2 into S3, G3 into S5, G4 into S6, G5 into S7, G6
into DONE. A human approval settles a judgment call; it never waives a machine
gate, so a stage whose integrity check refuses stays refused and is reported as
unrun. `run-pipeline` carries the per-gate detail of what each decision
constrains.

Human gates are recorded in with date, options
considered, choice, and a one-line rationale, naming the review packet the
decision was taken from.

Gate modes: `gate_mode` in `pipeline-config.md` selects
who resolves the human gates. `human` is the table above. `autonomous`
replaces the author with pre-specified per-gate rules (rule-or-park, never
guess), logged `auto-mode`, with mandatory disclosure in the paper. The
rules live in `playbooks/gate-modes.md` next to the workspace skill
folders; machine gates are identical in both modes. Standing arms:
`experiments/pipeline-gated/` and `experiments/pipeline-autonomous/`.

## 5. Error escalation

The ladder, applied at every stage (L8):

1. Bounded retry: transient failures (rate limits, timeouts, compile errors)
   retry with backoff, at most three attempts.
2. Flagged degradation: if retry fails, the step writes a
   `[MATERIAL GAP: ...]` marker or a checkpoint describing exactly what is
   missing, and continues only if the gap is non-blocking.
3. Human escalation: blocking gaps, judgment calls (structural breaks, proxy
   failures, estimator disagreement, fatal referee findings), and any
   post-freeze deviation go to the nearest human gate with options laid out.
4. Budget exhaustion (**the two stopping-rule keys were** — `driver_context_ceiling` and `budget.max_wall_clock`
   are read by `run-pipeline` and defined in `playbooks/error-escalation.md`;
   every other `budget` key remains a reported counter): when a stage
   spends its declared
   budget before finishing, it returns the best current artifact, the work
   that completed, the issues left unresolved, and the reason it stopped.
   Partial completion is never presented as a finished result. This rung is
   distinct from the three above because nothing failed: retry covers
   transient errors, degradation covers missing material, and escalation
   covers judgment, while running out of budget is a normal outcome that
   previously had no defined behaviour. It is the Material Gap rule pointed
   at budgets.

Every run declares a budget (****,
**stopping rules**): maximum cost per stage, a soft
driver-context ceiling, maximum wall clock, maximum retries, and the minimum
evidence required to finalize. Two of these bind — the context ceiling and the
wall clock — and the rest report.
The keys live in `pipeline-config.md`; per-stage defaults are tight on F1 and
F2 and generous on F3, which is where an earlier run found every real
problem and where convergence was fastest. A budget is a declaration and a
stopping rule, not a gate.

**The keys counted subagents, and the first measurement refuted
that choice.** Read from the session transcripts with `tools/run_cost.py`,
an earlier run cost $150 of which the **driver's own thread was 63%** — a line
item that appears in no agent count and that no proposed key bounded. Cost per
agent spans **56×** across the funnel, from a generator on the cheapest model to
a batched auditor, so `max_subagents: 32` would have fired at the debate, which
is 62% of the agent count and 12% of the cost. The binding resource is
**context volume re-read**, not agents: cache reads are 61% of project spend
against 17% for output. `max_subagents` is retired as a budget key and kept as
a reported counter — how many isolated judgments a run bought is the clean-room
question, and it is a different question from what they cost. Detail and the
per-layer table: `docs/skill-specs.md` spec A4.

**How a harness change gets judged**. Everything in this
document was decided from single live runs, and the project has established
that a single live run cannot decide most of it: a run yields about eleven
terminal outcomes against the ~47 a powered read needs. Two instruments answer the two halves of
that. The gates are tested against deliberately planted failures —
`gate-fixtures/`, 58 fixtures, both directions, two real defects found
and fixed on the days their fixtures were added — so a gate's state is known
rather than assumed. The layers
with a checkable output are measured off-line against a frozen task set with
repetitions, rather than on live runs (spec A5 in `docs/skill-specs.md`,
SPECCED, NOT BUILT). Neither reaches the judgment layers, and A5 says so in
writing: F1 generation, F2 rank, desk tiers, debate verdicts and `panel_reach`
stay on the accumulate-outcomes-across-runs route, which is the reason to stop
spending live runs on everything else. Reading note:.

Harness survival rules (L13), binding on every skill and script: absolute
paths in backgrounded commands; single-threaded access to OpenAlex and other
rate-limited APIs; checkpoint files for anything longer than a session turn;
progress prints so partial work is visible; every skill runnable by reading
its SKILL.md when slash registration fails.

## 6. What changed from the predecessor workflow

| | Detail |
|---|---|
| Dropped | the venue compliance rail: submission package, human time log, contribution report, conversation auto-logging hooks, eligibility checks, finalize-compliance. Gate logging shrinks from a submission exhibit to a entry. |
| Added | Data-anchored funnel mode with the F-1 held-data profile, the peek ledger, and the private-spine disclosure rule; S1b multi-round debate, refinement, and gated pilot; S8 adversarial review as a stage of its own (editor plus opposed referees, critic-fixer loop, advocate/skeptic contribution pass, decision-distribution option); the explicit error-escalation ladder; model-escalation policy; segregated `reviews/`; explicit-invocation-only review skills. |
| Kept | Pre-registration hard gate, synthetic-first gate, claim ledger and validator, script registry and drift audit, paper set and search log, citation tiering, Material Gap rule, session bookends and single STATE.md, lab notebook, banned-words discipline. |

## 7. Domain specificity

The harness is field-agnostic; economics, finance, and econometrics enter
through data and norms (L14): calibration sets built from recent JF/JFE/RFS,
AER/QJE/JPE/ECMA/ReStud, and JoE/JAE acceptances plus stalled working
papers; displacement-target gating at S1; the Edmans evidence ladder at S8;
equivalence bounds for nulls at S6 (a null is precise only if its interval
rules out an economically meaningful effect); the free-data tooling
(FRED, SEC EDGAR, Ken French, OEWS) that covers the public route at S5; and Corbis/OpenAlex search at S2. Swapping
these inputs retargets the pipeline to another empirical field without
touching the stage map.

Held data is an input class, not a field. Anchored mode
reads whatever the project owns through `data_manifest` and profiles it
with the same read-only introspection whether it is a mortgage panel, an
administrative register, or a vendor API. What is field-specific is the
displacement question the data is pointed at, which stays with
`field_profile`.

## 8. State and memory

One canonical state file, regenerated at every session
close and read at every open (L9). is the
append-only audit trail, one dated entry per skill output.
is the append-only record of gate decisions and design choices. Nothing else
holds state; any document that starts accumulating state gets folded into
these three or deleted.

## 9. Roadmap

The skills are written from the specs in
`docs/skill-specs.md`, starting with the session bookends and the
highest-priority stage skills, each a single hand-editable SKILL.md that
takes paths from project configuration. Phase 3 trials the pipeline on a
real research task, logs the run, and
promotes skills that prove out to the workspace `.claude/` per the promotion
rule in `AGENTS.md`.
