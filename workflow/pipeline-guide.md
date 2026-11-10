# The Pipeline in One Page

Date:. Companion: `pipeline-infographic.svg` (one-page visual).
Full detail: `pipeline-design.md`.

**What it is.** A standalone pipeline that takes an empirical economics,
finance, or econometrics project from nothing to a referee-ready draft.
AI agents do the stage work; the author decides at defined gates. One
driver skill chains everything, so a full run needs at most **6 author
inputs** in human mode — or **zero** in autonomous mode, where
pre-specified rules resolve each gate and any uncovered call parks the
project rather than guessing.

**The idea funnel (stages S1–S1b).** The pipeline's input is a **theme**:
set `theme` in `pipeline-config.md` and it returns detailed research
designs the held data can carry. Omit it and the open swarm runs instead,
searching a topic space rather than covering one question's design space.
Both paths rest on the principle that a wrong idea discovered late costs a
full run, so heavy investment up front is cheap by comparison:

- **F-1 — held-data profile** (anchored mode only, `data_mode:
  anchored`). When the project already owns data — a database, an API,
  a delivered extract — a read-only pass profiles it before anything is
  generated: inventory, identifier map with key stability, variation
  and cluster counts, measurement quality, and an expansion map whose
  external joins are verified by a real probe. Every query it runs goes
  in a peek ledger, and it never computes a relation between two
  substantive variables, so the pre-registration can declare exactly
  what was seen before the question existed. In `data_mode: open`, the
  default, this layer does not run and the funnel is the three layers
  below.
- **F1-T — variants** (themed path, the default). 8–12 mutually isolated
  generators produce **versions of the theme**, each varying it along
  mechanism, outcome variable, identification strategy, or unit of
  observation and naming what it holds fixed — 1–2 cards per cell, not
  8–10, because a themed cell asked for ten returns ten rewordings of one
  design. 2–3 cells are **theme-blind**, the only structural guard against
  the theme itself being a bad bet, and their fate is reported at G1 rather
  than discarded. **Every variant is then piloted before any debate**: when
  the theme is fixed the question is not which idea but which version the
  data can carry, and that is a counting question. No scoring layer runs.
- **F1 — swarm** (no-theme fallback). 12–15 mutually isolated generator
  agents (one per lens-by-field cell, cheap model) build a pool of 100–120
  ideas, deduplicated with logged merges. In anchored mode a reserved
  quarter of the cells never see the data, so the pool keeps ideas the held
  data did not suggest; the rest carry verified anchor fields, and a card
  naming a field the profile does not contain is downgraded rather than
  scored.
- **F2 — scoring** (swarm path only). Two independent scorers per idea
  (mid model) rate archetype match, displacement, data plausibility, and
  desk-reject risk against a held-out calibration set; the pool is cut to
  20–25. Search-free; scores are labeled unaudited. It has **never been
  shown to predict anything** — retrospective rank-vs-outcome correlation
  0.16 — and was kept only because that check was underpowered by
  construction (n=11, null band ±0.61). Treat it as a cheap concentrator,
  never a verdict, and never ration downstream depth by its rank.
- **F0 — landscape scan**, before any generation. Five blocks: what is
  occupied, open margins to displace, recent-acceptance archetypes, the
  closest threat papers, and a **trajectory** read of where the literature
  is going. Trajectory splits by sign, because this pipeline has twice
  measured that positive steering handed to many cells becomes an
  attractor: the **saturating** half (crowding margins, methods now table
  stakes) is shared with every generator, while the **rising** half never
  is — it is partitioned one-per-cell on the swarm path, withheld from
  generators entirely on the themed path, and delivered instead to the desk
  editors as a currency check and to the author at G1.
- **F3 — full rigor**, spent on pilot survivors (themed: typically 2–3) or
  the whole cut (swarm). Cheapest-first: novelty audit with logged
  searches, a three-editor desk simulation that returns a **`panel_reach`
  estimate** rather than a pass/fail (`very-high`, `high`, `moderate`,
  `low`, `none`; only a median of `none` kills). The rungs stopped being
  named after journals, because no evidence connects a rung to
  an editorial outcome, so a rung called `field` asserted a measurement the
  stage cannot make. (The reason first recorded — "the calibration set is 62
  papers, all top-3" — was wrong; it is 43 accepted / 17 stalled / 2 uncertain,
  and the real gap is that **0 stalled entries are finance papers**. Corrected.) Then a four-role clean-room debate — advocate, skeptic, methods
  referee, feasibility assessor — blind first round, adaptive depth. In
  anchored mode the feasibility assessor can query the held data, so an
  objection that a query settles is settled by one rather than argued.
  **Any card with no KILL vote earns a small-sample feasibility pilot**,
  firewalled from ever estimating the headline effect, and the pilot runs
  *before* the revision clinic: a rewrite can only narrow, so the cheap
  measurement settles the countable objections first. A decision audit
  reviews every terminal decision — **kills and advances alike** — for
  literature error, missed remedy, category error, role capture, or an
  unverified premise. A wrong survival is caught downstream and a wrong
  kill never is, which is why kills must be audited; the first live trial
  then found 4 of 5 kills sound and **2 of 3 advances defective**, which is
  why advances are audited too.
  A comparative final always runs and returns a **feasibility menu of 3-5
  candidates**, ordered by what the held data can carry. Each item carries
  its computed usable sample, its named binding constraint, the cheapest
  action that would relax it, an advisory `panel_reach` labelled *judged,
  not calibrated*, and its unreconciled objections. Cards off the menu stay
  warm on a bench so any downstream kill re-enters here, not at zero.
  **Autonomous mode always PARKs at G1**: a menu has no single winner and
  reach is uncalibrated, so there is no honest machine rule left — choosing
  among feasible designs is the author's call. Failures
  route by type: data-blocked ideas wait in a registry for new data,
  contribution-dead ideas go to the graveyard, execution problems get
  one revision only when a referee named the fix.

**The paper pipeline (S2–S8).** Literature and positioning (G2) →
hypotheses → pre-registration, committed to git before any estimate runs
(G3) → data construction with a script registry (G4) → estimation that
must first recover a planted effect on synthetic data, then robustness
(G5) → writing as a build target: tables and prose numbers generated from
results JSON, a claim ledger tracing every number, verified citations, and
`make verify` rebuilding the paper from source → adversarial review by a
simulated editor and four blind referees with a bounded fix loop → title
and overclaim sign-off (G6).

**Skills and agents.** 19 pipeline skills (11 promoted and proven, 8 in
trial: the driver, session commit, the four funnel skills, the held-data
profile, and the build graph), plus 2 shared playbooks (gate modes, error
escalation) and one config file all skills read paths from. A full run
instantiates roughly **450–500 agents across ~22 distinct roles** —
about 90% are cheap funnel scorers and generators; the strong model is
reserved for debate panels and referees, where judgment lives.

**What keeps it honest.** Two gate systems: **6 human gates** (idea,
framing, design freeze, data calls, what survives, title/overclaim) and
**15 machine gates**, 18 in anchored mode (a 16th, the adjudication
screen, is specced but not yet built) — funnel floors, panel reach, pilot
authorization and firewall, the decision audit, the feasibility menu, the
quarantine check, the
pre-registration commit, synthetic-first recovery, the claim-ledger
validator, the generated-values check, a clean rebuild from source,
citation verification, clean compile, review convergence,
and in anchored mode profile freshness, anchor existence, and the peek
ledger. There is no free-data requirement: any source is admissible if
the idea names how it would be obtained — held, public, licensed,
purchasable, or restricted — and held or licensed data may carry a
paper's headline, but only against a replication plan the author
approves at G4. The route, not the price, is the feasibility question.
`data_access: free_only` restores the strict rule for a venue that
requires referee-collectable data. A clean-room rule
isolates the funnel: debaters see sanitized briefing packs only, and
later stages may read each idea's `handoff/` files but never its
`quarantine/` (transcripts, speculation, raw pilot output). Anything not
present in a project artifact is written as `[MATERIAL GAP]`, never
filled from model memory. Sessions bookend with a canonical state file,
so any session can resume mid-run from its stage cursor.
