# Skill specs: how to write the P1 batch

Date:. Status: proposal for review, then the work order for Phase 2.
Companion: `workflow/pipeline-design.md`, the stage map the skills serve.

Each P1 skill below gets: a verdict on the reference implementation (all
eleven the predecessor workflow references read in full; Sant'Anna's `review-paper` read for
the new twelfth), the changes our version makes, and a writing spec
(description draft, structure, gates, bundled files, size target, eval
scenarios). References: the predecessor workflow's skills read in place, and a
library of public research-skill repositories audited as study material. See
`NOTICE.md` for which repositories and what was taken from them, which was
nothing.

## How we write skills (conventions)

The workspace `references/skill-authoring-guide.md` governs: progressive
disclosure (description does discovery, body is the procedure, detail in
one-level-deep files), third-person descriptions with trigger terms, bodies
well under 500 lines, degrees of freedom matched to fragility, verification
artifact plus lab-notebook entry, validation gates, eval-first authoring.
The the predecessor workflow references average 61 lines; ours target 40 to 90.

Project deltas on top of the guide:

1. **Config over hardcoded paths.** Every skill starts by reading
   `pipeline-config.md` in the paper project's root (created by the first
   skill that needs it): paths for STATE.md, lab notebook, decisions log,
   results dir, reviews dir, paper dir, plus the field profile
   (finance / economics / econometrics) and the model policy. Skills refer
   to config keys, never literal paths. This fixes both the predecessor workflow's baked-in
   `submission/` layout and the hardcoded-path defect in the crawled repos.
2. ** replaces gate-log.** A skill that ends at a human
   gate closes with: record date, gate, options considered, choice, one-line
   rationale in the decisions log. No separate skill, no submission exhibit.
3. **Review-type skills** (`peer-review`, `edmans-audit`) set
   `disable-model-invocation: true` and write only to the reviews dir.
   **Session-close skills** (`handoff`, `commit-session`) also set
   `disable-model-invocation: true`: the close is the last stage of every
   working session and only the author activates it. The agent may suggest
   closing when the session's work is done; it never runs the pair on its
   own.
4. **Escalation by reference.** Skills cite the escalation ladder
   (`playbooks/error-escalation.md`, written with this batch) instead of
   restating it: bounded retry, flagged Material Gap, human gate.
5. **Bundled validators are stdlib-only Python** living in
   `skills/<name>/scripts/`, promoted together with the skill.
6. **Evals before body.** Each spec below fixes 2 eval scenarios; write the
   skill to pass them, then trial on a real research task.
7. **No the venue routing.** References to `/log-conversation`,
   `/contribution-report`, `/gate-log`, the venue appendices, and
   `submission/` paths do not carry over.

Build order within the batch: `pipeline-config` conventions land with
`resume`/`handoff` (S0 first), then machine-gate skills
(`verify-citations`, `pre-register`, `script-registry`, `run-analysis`,
`claim-ledger`), then `robustness-suite`, `draft-paper`, `edmans-audit`,
`peer-review`.

---

## S0. resume

Reference: the predecessor workflow `resume` (45 lines). Verdict: sound design, minor cruft.
The five-line brief, canonical-file discipline, in-flight sentinel check,
and the conflict rule (surface STATE-vs-notebook disagreement, never pick
silently) all carry over. Cruft: fallback logic for the predecessor workflow's legacy state
docs (HANDOFF.md, NEXT_SESSION.md) that our projects never had.

Changes: drop the legacy fallback (missing STATE.md just proposes running
handoff); add a staleness check (warn when STATE.md is older than the last
commit touching the project, with the commit summary shown); read paths
from config.

Spec:
- description: "Starts a session by reading the canonical state file and
  lab-notebook tail, checks in-flight jobs and state staleness, and
  produces a 5-line brief: status, live findings, in-flight work, next
  action, blockers. Run first in any continuation session."
- Structure: purpose, When to use, Workflow (4 steps), Outputs (brief only,
  read-only), Validation.
- Gates: none (read-only). Size: ~40 lines. Freedom: medium.
- Evals: (1) STATE.md older than last commit: brief must flag staleness and
  name the commit. (2) STATE.md names a sentinel that has not landed: brief
  reports the job as still running, not done.

## S0. handoff

Reference: the predecessor workflow `handoff` (51 lines). Verdict: the seven-block STATE.md
schema (date/status, question, live findings with numbers, in flight, next
action, blockers, pointers) is the core asset; keep verbatim. The
overwrite-don't-append rule and the "numbers trace to a results JSON, not
memory" validation carry over. Cruft: legacy-doc folding step.

Changes: drop legacy folding; require the next action to be written as a
runnable instruction (a command or a skill invocation plus its argument,
not "continue the analysis"); paths from config.

Spec:
- description: "Ends a session by regenerating the canonical state file
  from the lab notebook, git, and the session's artifacts: status,
  findings with numbers, in-flight jobs with sentinels, a runnable next
  action, blockers. Author-activated: the closing stage of every session,
  followed by commit-session."
- Frontmatter: `disable-model-invocation: true` (author activates the
  close; the agent only suggests it).
- Structure: purpose, When to use, The seven blocks, Workflow (4 steps),
  Outputs, Validation.
- Gates: STATE.md under 40 lines; every number traces to an artifact; every
  in-flight job has a sentinel path. Size: ~45 lines. Freedom: medium.
- Evals: (1) session produced a new estimate: STATE.md must carry the
  number and the results-file path. (2) a background crawl is mid-run:
  STATE.md must record orchestrator and sentinel so resume can poll it.

## S0. commit-session

Reference: the predecessor workflow `commit-session` (49 lines). Verdict: mostly generic git
discipline; the trailer convention is the only load-bearing part. Cruft:
justification tied to the venue contribution report.

Changes: keep one-commit-per-session, the Co-Authored-By trailer for
AI-driven work, milestone tags, and the credential/data-blob scan; recast
the rationale as plain provenance (git is the audit trail); drop the
contribution-report coupling.

Spec:
- description: "Commits the session's work with a structured message and a
  Co-Authored-By: Claude trailer, and tags milestones, so project history
  and AI attribution live in git. Author-activated, once per session,
  after handoff: the final step of the session-close stage."
- Frontmatter: `disable-model-invocation: true`.
- Structure: purpose, When to use, Convention, Workflow (5 steps),
  Outputs, Validation. Size: ~35 lines. Freedom: low (exact trailer, exact
  ordering after handoff).
- Evals: (1) diff contains an API key: skill must refuse and name the file.
  (2) work on the default branch: skill must branch first.

## S2/S7. verify-citations

Reference: the predecessor workflow `verify-citations` (64 lines). Verdict: right procedure,
weakest writing in the set. It predates the house template (no
Outputs/Validation sections), and its closing "next steps" route to the venue
skills. The status taxonomy (OK / PARTIAL / MISMATCH / UNVERIFIED /
MISSING), the field-comparison table, the batch-of-5 rate-limit rule, and
the "NEVER fill from memory" rule are all keepers.

Changes: rewrite to the house template; add the identifier-hijack check
from the fabrication taxonomy in the survey (resolve each DOI and confirm
it lands on the cited title, catching real-DOI-wrong-paper fabrications);
make it a blocking gate at two points per the design (S2: entries enter the
bib; S7: before draft-paper reports done), with MISMATCH or MISSING
failing the gate and UNVERIFIED barred from drafts via
`[MATERIAL GAP: unverified citation]`; drop the venue next-steps.

Spec:
- description: "Audits citations: every cite key resolves to a BibTeX
  entry, every entry is verified field-by-field against literature search,
  and every DOI resolves to the cited paper. Blocking gate at literature
  stage and again before a draft is done; unverified entries are barred
  from drafts."
- Structure: purpose, When to use (the two gate points), Workflow (detect
  files, extract keys, verify in batches of 5, classify, DOI check,
  report), Outputs (audit report file), Validation.
- Gates: exit status by classification; the two invocation points. Size:
  ~70 lines. Freedom: low (exact classification and table format).
- Evals: (1) a bib entry whose DOI resolves to a different paper: must
  classify MISMATCH, not OK. (2) search returns no journal field: must
  print NOT FOUND IN SEARCH, never fill from memory.

## S4. pre-register

Reference: the predecessor workflow `pre-register` (59 lines). Verdict: the strongest
reference in the set. The seven-block freeze (hypotheses, primary spec,
sample, decision rule, null statement, pre-specified robustness,
exploratory label), the re-freeze-by-dated-block rule, and the
refuse-if-blank validation all carry over unchanged.

Changes: path from config (freeze lives in the paper project, committed);
gate decision goes to; add an optional Power/MDE block
(reference: Sant'Anna `power-analysis`): expected effect size, minimum
detectable effect at the planned sample, and the underpowered-by-design
warning at the freeze rather than at G5; cite the escalation playbook for
post-freeze deviations.

Spec:
- description: "Freezes the empirical specification before any estimate
  runs: hypotheses, primary spec, sample, decision rule, the null
  statement, pre-specified robustness, and an optional power/MDE block,
  committed so git timestamps the freeze. Design gate G3; run-analysis
  refuses to run without it."
- Structure: purpose, When to use, The freeze blocks (7 + power), Workflow
  (5 steps ending in commit), Outputs, Validation. Size: ~65 lines.
  Freedom: low.
- Evals: (1) null statement left as placeholder: skill refuses to present
  for approval. (2) design pivot after freeze: new dated block appended,
  old freeze untouched in file and history.

## S5. script-registry

Reference: the predecessor workflow `script-registry` (43 lines) plus `code-sweep`. Verdict:
right idea, split across two skills and dependent on the predecessor workflow's
`script_registry.py`. The curation warning (the extractor cannot see paths
built from config constants; fill load-bearing entries by hand) is an
honest, keepable limitation note.

Changes: merge build and audit into one skill with two modes (build:
scan and write the manifest; audit: manifest vs disk, failing on
unregistered scripts, missing or stale outputs, absent docstrings); write
our own stdlib `registry.py` bundled with the skill; emit a
replication-README section from the manifest; paths from config.

Spec:
- description: "Builds and audits the replication manifest: per script its
  purpose, inputs, outputs, and packages; audit mode fails on unregistered
  scripts, missing or stale outputs, and missing docstrings. Run during
  data construction, at milestones, and before submission."
- Structure: purpose, When to use, Workflow (build mode, curate, audit
  mode), Outputs (registry JSON + readable table + README section),
  Validation. Bundled: `scripts/registry.py` (stdlib). Size: ~55 lines +
  script. Freedom: low (exact commands).
- Evals: (1) a script writes an output the manifest does not declare:
  audit exits nonzero naming it. (2) output file older than its script:
  flagged stale.

## S6. run-analysis

Reference: the predecessor workflow `run-analysis` (61 lines). Verdict: strong. The MVE
framing ("a regression you cannot first make lie on purpose is a
regression you cannot trust when it tells the truth"), synthetic-first
workflow, library verification, keyed results JSON, and the numerical
hygiene bullets (booleans cast before matmul, pinv on singular X'X,
Accelerate warning suppression) all carry over; the hygiene notes encode
real debugging cost.

Changes: add step 0, the freeze check: refuse to run if the committed
pre-registration is missing or the spec deviates from it without a dated
amendment (the predecessor workflow stated this ordering only in CLAUDE.md; ours enforces it
inside the skill); escalate on library disagreement beyond tolerance (stop
the stage, ladder step 3) instead of warning; paths from config.

Spec:
- description: "Runs an empirical estimation (event study, DiD, IV/2SLS,
  cross-section) behind two machine gates: a committed pre-registration
  and a synthetic-first check that recovers a planted effect and matches a
  reference library. Writes keyed results JSON and figures that
  draft-paper splices."
- Structure: purpose, When to use, Principles (synthetic-first, library
  verification, pre-trends, numerical hygiene), Workflow (0 freeze check,
  then 6 steps), Outputs, Validation. Size: ~70 lines. Freedom: low for
  the gates, medium for estimator internals.
- Evals: (1) no committed preregistration.md: skill stops at step 0 and
  names the missing gate. (2) hand-rolled DiD disagrees with the reference
  library beyond tolerance on the toy case: stage stops, disagreement
  reported, no real-data run.

## S6. robustness-suite

Reference: the predecessor workflow `robustness-suite` (72 lines). Verdict: strong. The
six-check gauntlet, the three-verdict scheme (robust / confounded with the
confound named / underpowered with the bound), the "headline is what
passes the most checks, not the largest t-stat" rule, and the optional
adversarial break attempt (adversary as erratic genius: every proposed
break is a lead confirmed by re-estimation, not a verdict) carry over.

Changes: generalize the confound check from the AI-project specifics
(COVID years, tech composition) to "name the era, composition, and
exposure confounds for this setting," keeping COVID as the worked example;
verdicts feed G5 with the decision recorded in; paths
from config.

Spec:
- description: "Runs a finding through a fixed gauntlet before it enters
  the paper: pre-trends and placebos, setting-specific confounds,
  equivalence/MDE bounds for nulls, alternative codings, subsample
  uniformity, selection-vs-causation, plus an optional adversarial break
  attempt. Verdict per finding: robust, confounded, or underpowered."
- Structure: purpose, When to use, The checklist (6), Workflow, Adversarial
  break attempt, Outputs, Validation. Size: ~75 lines. Freedom: medium.
- Evals: (1) a null with wide bounds: verdict must be underpowered with
  the MDE stated, not "no effect." (2) an effect that dies when the era
  confound is controlled: verdict confounded, confound named.

## S7. draft-paper

Reference: the predecessor workflow `draft-paper` (63 lines). Verdict: good skeleton. The
non-negotiable ("if a number is not in a results file, it does not go in
the paper"), programmatic booktabs tables, section delegation to
empirical-intro and hypothesis-development, banned-words pass, and the
compile gate carry over.

Changes: drop the venue appendix sync step; upgrade the exit condition from
"route to verify-citations" to a hard gate (done means: compile clean,
claim-ledger validator exit 0, citation audit clean); template path from
config; title and overclaim flagged for G6 sign-off via the decisions log.

Spec:
- description: "Assembles or updates the full LaTeX manuscript: scaffold,
  booktabs tables spliced from results JSON (numbers never retyped),
  figures, delegated intro and hypotheses, banned-words pass. Done only
  when compile is clean, the claim ledger validates, and the citation
  audit passes."
- Structure: purpose, When to use, Principles, Workflow (6 steps), Outputs,
  Validation (the triple gate). Size: ~65 lines. Freedom: medium, low for
  the gates.
- Evals: (1) a table value differs from its results JSON at the printed
  precision: skill flags it and does not report done. (2) claim ledger
  fails: skill reports which gate blocked and stops.

## S7. claim-ledger

Reference: the predecessor workflow `claim-ledger` (74 lines) plus its stdlib validator.
Verdict: the most distinctive asset in the predecessor workflow. The entry schema (numeric:
results file, dot-path key, reported value, tolerance; textual: source,
quote, locator; both: mechanism check), the quote-verification against
local files, and the load-bearing-claims scope ("the claims a referee
would challenge") all carry over.

Changes: write our own stdlib `claim_ledger.py`; add the claim-to-code
extension (the L5 upgrade, reference: Backman `review-paper-code`): for
each numeric claim, cross-reference its results file against the script
registry and fail when no registered script declares it as an output or
when the producing script postdates the results file (stale evidence);
paths from config.

Spec:
- description: "Builds and validates the claim ledger: every load-bearing
  claim maps to a results-file path, key, value, tolerance, and a
  mechanism check; textual claims carry verified quotes or locators; each
  results file must trace to a registered producing script. Validator
  exits nonzero on drift, fabricated support, or unregistered evidence."
- Structure: purpose, When to use, Entry schema (table), Workflow, Outputs,
  Validation. Bundled: `scripts/claim_ledger.py` (stdlib; validate +
  cross-ref modes). Size: ~75 lines + script. Freedom: low.
- Evals: (1) results JSON regenerated with a new value, paper not updated:
  validator exits nonzero naming the claim. (2) a claim cites a results
  file no registered script produces: cross-ref failure.

## S8. edmans-audit

Reference: the predecessor workflow `edmans-audit` (89 lines). Verdict: keep nearly whole.
The evidence ladder (statement, fact, representative data, causal proof)
with the language-must-not-exceed-rung rule, the four side dimensions
(importance, displacement, no spin, what-would-change-my-mind), and the
triaged adversarial pass carry over.

Changes: strip the venue references; output to the reviews dir; runs after the
peer-review loop and before G6 (the design's ordering); flagged rewrites
route back to draft-paper; the G6 decision lands in.

Spec:
- description: "Audits inference quality and spin after review, before
  sign-off: each load-bearing claim placed on the evidence ladder
  (statement, fact, representative data, causal proof) with language
  capped at its rung; importance, displacement, spin, and falsification
  path checked over the abstract and intro."
- Structure: purpose, When to use, The ladder, The other dimensions,
  Adversarial pass (triage discipline), Workflow, Outputs, Validation.
  `disable-model-invocation: true`. Size: ~80 lines. Freedom: medium.
- Evals: (1) an associational result phrased causally in the abstract:
  flagged with rung gap and a rewrite. (2) paper states no evidence that
  would overturn its claim: flagged as missing falsification path.

## S8. peer-review (BUILD-new, expanded scope)

Reference: Sant'Anna `review-paper` (library,
`claude-code-my-workflow/.claude/skills/review-paper/` with agents and
`journal-profiles.md`), Backman `AI-research-feedback` (advocate/skeptic
contribution panel, claim-to-code), flonat `seven-pass-review` pattern.
Verdict: do not trim; match Sant'Anna's full
mode surface and deepen rigor beyond it. This is the pipeline's flagship
skill and the largest build in the batch.

Design, in review order:

1. **Integrity pre-gate.** Before any referee spends tokens, run the
   machine gates: claim-ledger validate, script-registry audit, citation
   audit, compile check. A paper failing an integrity gate is returned as
   a desk reject with the gate report; referees never review a paper whose
   numbers do not trace.
2. **Contribution panel.** An advocate and a skeptic independently assess
   the contribution claim against the positioning memo and a live
   literature probe (Backman pattern); the editor receives both briefs.
3. **Editor desk review.** Journal-calibrated (profile file): scope fit,
   contribution threshold, mandatory novelty probe via literature search,
   desk-reject simulation with the profile's standards. Output: desk
   decision plus referee selection.
4. **Four blind referees.** Two dispositioned referees drawn from the
   six-way taxonomy (structural, credibility, measurement, policy, theory,
   skeptic) with deliberately opposed priors; a **replication referee**
   who re-derives every table and figure number from the results JSON and
   the script registry and checks run order (the claim-to-code idea
   promoted to a referee role); and an **opposition referee** (author
   addition; reference: flonat `referee2-reviewer` and
   `paper-critic` agents), a standing adversary whose brief is to find
   every flaw the paper could contain: methodology, literature use and
   coverage, findings, discussion, contribution, significance, and above
   all the coherence and logic of the whole paper as one argument. The
   opposition referee is the only role that reads the manuscript
   end-to-end as a single argument chain: does the introduction promise
   what the results deliver, do the hypotheses follow from the mechanisms,
   do the results support the discussion, does the conclusion claim more
   than the design can carry, do any two sections contradict each other.
   It is always seated (never sampled away in variance mode) and is
   expected to over-flag; the finding-verification step is its
   counterweight. Each referee report embeds the evidence-ladder check
   (language capped at its rung) and must cite a manuscript location for
   every finding. All referees run on the strong model (model policy in
   config).
5. **Finding verification.** Referees hallucinate too: every referee
   finding is triaged as a lead and confirmed against the manuscript and
   artifacts before it may enter the synthesis (the erratic-genius
   discipline, applied to our own referees). Dismissed flags are logged in
   one line each so the triage is auditable.
6. **Editorial synthesis.** Verified findings triaged fatal / addressable
   / taste; decision letter written to the profile's standards.
7. **Critic-fixer loop.** Fixes applied, re-review of changed sections;
   exit on two consecutive clean rounds, cap at five; surviving fatal
   findings escalate to the author, possibly reopening G3 or G5.

Modes (full surface): default single pipeline run; `--rr N` revise-and-
resubmit continuation (reload prior round, same referees and dispositions,
classify each prior concern Resolved / Partial / Not addressed, hard cap
at round 3); `--stress` hostile editor (all referees forced skeptic,
doubled peeves, framed to find reasons to reject); `--variance N` (N
dispositioned referees with independently sampled dispositions; the
replication and opposition referees stay seated in every draw; editor
reports a decision distribution, not a point estimate); `--light` fast
two-agent pre-submission check (contribution, identification, causal
overclaim, unsupported claims), which absorbs the P2 review-light row.

Spec:
- description: "Simulates journal peer review at full rigor: integrity
  pre-gate (ledger, registry, citations, compile), advocate/skeptic
  contribution panel, calibrated editor desk review, four blind referees
  (two opposed dispositions, a replication referee re-deriving every
  number, and a standing opposition referee attacking methodology,
  literature, findings, contribution, and whole-paper coherence and
  logic), verification of referee findings before synthesis, fatal/
  addressable/taste triage, and a bounded critic-fixer loop. Modes: R&R
  continuation, hostile-editor stress, decision-distribution variance,
  and a fast pre-submission light check."
- Structure: purpose, When to use, Pipeline (the seven steps), Modes,
  Referee dispositions (table), Escalation, Outputs, Validation.
- Bundled inside the skill at `.claude/skills/peer-review/references/` (one
  level deep): `journal-profiles.md` (tri-field:
  JF/JFE/RFS, AER/QJE/JPE/ECMA/ReStud, JoE/JAE; per journal: desk-reject
  standards, identification bar, expected robustness set, format norms,
  known peeves), `referee-dispositions.md` (six personas, the
  replication-referee protocol, and the opposition-referee protocol: the
  flaw checklist across methodology, literature, findings, discussion,
  contribution, significance, plus the coherence pass that walks the
  argument chain intro -> hypotheses -> results -> discussion ->
  conclusion hunting for gaps and contradictions),
  `review-protocol.md` (finding-verification triage rules,
  R&R ledger format, decision-letter template).
- Frontmatter: `disable-model-invocation: true`. Size: ~170 lines plus 3
  reference files. Freedom: low for pipeline shape, gates, and loop
  bounds; high for referee prose.
- Evals: (1) planted flaw (a table number off from its results JSON): the
  integrity pre-gate or the replication referee catches it; it reaches
  the synthesis as fatal. (2) planted uncontrolled confound: at least one
  dispositioned referee finds it; triage confirms it against the
  manuscript. (3) a referee report seeded with a fabricated finding (a
  claim the manuscript never makes): finding verification dismisses it
  and logs the dismissal; it never reaches the decision letter. (4) two
  clean rounds: loop terminates with a decision letter in the reviews
  dir; analysis files untouched throughout. (5) planted coherence break
  (a conclusion claiming a mechanism the results section never tests, or
  an intro promising an analysis that does not appear): the opposition
  referee flags it, verification confirms it, and it reaches the
  synthesis at least as addressable.

---

## Author decisions (all resolved, see

1. `pipeline-config.md` is markdown: one file with a key-value block at the
   paper project's root.
2. Peer-review ships at full scope, deepened: the whole Sant'Anna mode
   surface (R&R, stress, variance, light) plus our extensions (integrity
   pre-gate, contribution panel, replication referee, finding
   verification, evidence-ladder embedding). The P2 review-light row is
   absorbed as its `--light` mode.
3. Handoff and commit-session stay separate skills and form the
   session-close stage, author-activated (`disable-model-invocation: true`
   on both); the agent suggests the close but never triggers it.

## Driver. run-pipeline (BUILD-new)

Reference: none; written from scratch against the 5-10-prompt goal (see
notes/decisions.md). The stage skills exist and self-enforce;
the missing piece is the conductor that chains them, so every stage
transition and session open currently costs a prompt.

Design calls:
- Conductor, not worker: invokes stage skills, routes outputs, enforces
  stop states; performs no stage work, resolves no gate itself, restates
  no stage rule.
- Human mode batches to checkpoints (default bundles G1+G2, G4 folded
  into G5 unless a real data call arises, G6 with the decision letter);
  target is a full run in at most 6 author inputs.
- Autonomous mode never prompts: gates resolve per gate-modes.md until
  DONE / PARKED / ARCHIVED.
- Four exclusive stop states: CHECKPOINT, PARKED, ARCHIVED, DONE.
- Stage cursor line in STATE.md (written via handoff) so continuation
  sessions re-enter mid-run; sentinel discipline per error-escalation.md.
- Append-only run log `output/pipeline_run.md` with a numbered prompt
  ledger: the measurement instrument for the prompt-budget goal and the
  gated-vs-autonomous comparison.
- Interim skill mapping: S1 uses workspace research-idea-generator +
  finance-idea-screening, S3 uses hypothesis-development, until the P2
  pipeline-native versions exist; the run log notes the substitution.

Spec:
- Structure: purpose, When to use, Stage sequence (cursor table), Gate
  handling, Stop states, Long work and session breaks, Run log and
  prompt ledger, Validation.
- Gates: enforces all of them, owns none. Size: ~115 lines. Freedom: low
  (the driver must be predictable; judgment lives in the stage skills).
- Evals:
  (1) Human mode, fresh project: driver runs S0-S2 and stops at one
      G1+G2 CHECKPOINT; it never resolves the gate itself.
  (2) Autonomous mode, calibration set missing: S1 blocks top-tier
      verdicts, the G1 rule finds no survivor, run ends PARKED with the
      gap named in STATE.
  (3) Continuation: cursor at S5 with an unlanded sentinel: driver
      reports the job still running and does not restart the crawl.
  (4) Uncommitted prereg at S6: run-analysis's freeze check stops the
      stage; the driver ends at the ladder, never routes around.
  (5) Prompt ledger: every author input in a simulated gated run appears
      numbered in pipeline_run.md; gate inputs and continuation inputs
      are distinguished.

## Funnel skills: idea-swarm, idea-scoring, idea-debate, idea-pilot

Design source: pipeline-design.md S1 (F1-F2) and S1b (F3), the decisions (debate stage, clean room, investment principle,
funnel, fallback triage). Drafted in the incubator `skills/`;
untrialed; promotion waits on the idealization-stage trial.

Spec (idea-swarm, F1 + F0 literature landscape, landscape):
- Structure: purpose, F0 literature-landscape pre-step (one scan ->
  landscape_brief.md: blocklist/menu/archetypes/threats, anti-anchoring
  rule, seeds paper_set/search_log), grid (lens x subfield, 12-15
  cells), swarm rules (isolated generators, constraint digest carrying
  the F0 blocklist/menu, card schema), dedup with logged merges, funnel
  floor, output, validation. ~95 lines.
- Gates: funnel floor (raw >= 100, one retry, logged shortfall).
- Freedom: high on idea content, low on schema and isolation.
- Evals:
  (1) Pool of 104 raw / 81 distinct: counts block reconciles, every
      merge logged, no card carries any score or rank.
  (2) Two cells return nothing: retry pass hits only those cells; a
      remaining shortfall appears in pool file and notebook.
  (3) Graveyard from a prior cycle says all deaths were data: every
      generator's digest carries the named-free-source constraint, and
      no graveyard question reappears in the pool.
  (4) F0 landscape: landscape_brief.md has all four
      blocks, every claim cites a logged search, and the brief is a
      displacement-menu/blocklist not a gap list; the F1 digest carries
      the blocklist, and no card re-generates an occupied-margin
      question named in the blocklist; scan papers appear in paper_set.

Spec (idea-scoring, F2):
- Structure: purpose, hard calibration dependency, two-scorer
  protocol, four-dimension rubric, search-free rule with UNAUDITED
  header, median-of-three on band disagreement, cut rule (20-25,
  largest gap, tie handling), two-zone output (lineage dirs score-free
  in handoff), validation. ~80 lines.
- Gates: calibration present and fresh (blocking); cut within 20-25.
- Evals:
  (1) Calibration file missing: skill stops before any scoring; PARK
      in autonomous mode.
  (2) Composites 14 vs 17 for one idea: third scorer seated, median
      taken, all three sheets kept.
  (3) Survivor lineage dirs: handoff/idea_card.md contains no digit
      score, no rank, no scorer prose; sheets live only under
      ideas/scoring/.

Spec (idea-debate, F3, flagship):
- Structure: cheapest-first kill layers (novelty audit -> graveyard on
  occupied margin; three-editor desk sim -> graveyard on unanimous
  reject), clean-room debate (briefing pack = score-free card +
  novelty facts; blind round 1; adaptive depth cap 3; verdict table),
  pilot dispatch on no KILL (pilot before clinic), comparative final
  (fresh judges, handoff-only, always names one winner), fallback triage,
  G1 per gate mode,
  audit counters, validation. ~135 lines.
  `disable-model-invocation: true`.
- Reuse: SKEPTIC and CREDIBILITY dispositions and the contribution
  panel from workspace peer-review, ex-ante mode; desk sim from
  workspace finance-idea-screening, read in place.
- Gates: panel reach (median `none` kills, else survives carrying its
  reach, always labelled judged-not-calibrated; a journal name used as a
  rung is a validation failure); pilot authorization (themed path: every
  variant, up front; swarm path: no KILL from any role — and a `feasible`
  verdict is never evidence about identification); feasibility menu (the
  comparative final returns 3-5 candidates with computed samples and named
  binding constraints; a shortfall report with no menu is a validation
  failure); quarantine wall (validation greps handoff for quarantine
  references).
- Evals:
  (1) Idea whose margin is occupied (named paper): dies at the novelty
      audit; no debate tokens spent; graveyard entry names the paper.
  (2) Verdict table 4x EXPLORE round 1: debate ends in one round;
      pilot invoked; no round 2 text exists.
  (3) Verdicts split 2 EXPLORE / 2 KILL at cap: fallback triage runs;
      routing matches the failure type stated in the record.
  (4) Only one pilot-cleared survivor: no winner declared; shortfall
      report names the refill precedence; bar unchanged.
  (5) Contamination probe: a planted quarantine quote in a draft
      handoff file fails validation.
  (6) Deepened novelty audit: novelty_facts.md
      carries a positioning/threat list and cites only verified papers
      (an unverifiable cite is marked [MATERIAL GAP], never asserted);
      the papers it finds are appended to paper_set and its queries to
      search_log, so S2 inherits them.

Spec (idea-pilot, F3):
- Structure: entry gate (recorded 4x EXPLORE, refuse otherwise), five
  checks (registered slice script, coverage, variation, measure
  sanity, power inputs), headline firewall with DISCLOSURE REQUIRED
  flag, two-zone output, three verdicts, validation. ~85 lines.
  `disable-model-invocation: true`.
- Gates: entry (no KILL from any role); firewall (no outcome-on-treatment
  comparison anywhere; grep check in validation); conditional verdict
  returns to debate, never self-approves.
- Evals:
  (1) Debate record shows 3 EXPLORE + 1 REVISE: pilot refuses, names
      the precondition.
  (2) Slice reveals an obvious headline pattern during a join check:
      report carries DISCLOSURE REQUIRED with exact wording of what
      was seen; handoff report still contains no directional language.
  (3) Coverage 12 treated units vs design's assumed 200: verdict
      infeasible, named ingredient "treated-unit coverage", routed as
      data failure to the blocked registry.

## Anchored mode: data-profile plus F0-F3 amendments

Design source: pipeline-design.md S1 (F-1 layer, anchored-mode rules
through F0/F1/F2), S1b (feasibility query access, access-failure
triage), S5 (private spine), the three decisions, and the
gate-table rows for profile freshness, anchor existence, and the peek
ledger. Scope: one new skill plus amendments to four existing ones.
`data_mode: open` behaviour is unchanged everywhere, which is what
keeps the existing trials valid.

Spec (data-profile, F-1):
- Structure: purpose, entry conditions (anchored mode, manifest
  completeness, read-only access), six recorded blocks (inventory,
  identifier map with vintage stability, variation inventory with
  cluster counts, measurement quality, expansion map with verified
  probes, publication facts), peek firewall and ledger,
  blocked-registry recheck, two-zone output with the `field_index`
  contract, freshness gate, validation. ~130 lines.
- Reuse: `script-registry` for every probe script; the two-zone
  handoff/quarantine split from `idea-pilot`; the DISCLOSURE REQUIRED
  convention from the pilot firewall.
- Gates: profile freshness (blocks F1); peek-ledger completeness
  (every registered query logged); handoff carries no statistic
  relating two substantive variables.
- Freedom: high on how a source is introspected, none on the firewall,
  the ledger, or the `field_index` contract.
- Evals:
  (1) Happy path on a small held database: profile counts reconcile
      against the source, `field_index` is complete and sorted, every
      number traces to a registered script's output.
  (2) A probe computes a mean outcome by treatment group: the firewall
      check fails the run and names the offending query; no partial
      profile is published to handoff.
  (3) Manifest with no licence or no refresh cadence: the run stops
      before touching the source and names the missing field.
  (4) Blocked-registry recheck: an entry whose missing ingredient is a
      stable servicer id is marked unblocked with the supplying field
      named; an entry the data does not supply stays blocked, and both
      outcomes are reported.
  (5) An expansion candidate with no probe: recorded as candidate, not
      verified; a downstream card citing it is marked unverified rather
      than treated as a fact.

Amendments (idea-swarm, F0/F1):
- F0 takes the profile extract as a second input; anti-anchoring rule
  extends to it (capability menu, never a regression list).
- Grid reserves >= 1/4 of cells unanchored; those generators receive no
  part of the data capability digest.
- Card schema in anchored mode: `data_anchor`, `data_extension`,
  `data_class`, `public_counterfactual` replace `data_hunch`
  (unanchored cards keep it).
- New gate: anchor existence, checked against `field_index`.
- Evals:
  (6) A card names `loans.servicer_tenure`, absent from the profile:
      the card is downgraded to unanchored, the missing field is
      logged with the card id, and it is never scored as anchored.
  (7) Profile older than the manifest's cadence: F1 refuses to launch
      any generator and names the stale profile.
  (8) Reserved cells: at 12 cells, at least 3 are unanchored, their
      cards carry no `data_anchor`, and the class mix appears in the
      counts block.

Amendments (idea-scoring, F2):
- Rubric dimension 3 becomes data leverage in anchored mode; header
  changes to name what was verified; scorers still run no queries; an
  unverified extension caps at 3; the cut reports its class mix.
- Evals:
  (9) A scorer's sheet quotes a query it ran: the sheet is regenerated
      and the scorer re-seated, exactly as for a cited-paper violation.
  (10) The cut is entirely anchored while a quarter of the pool was
      unanchored: the run log records the class mix as a finding; the
      cut itself is not overridden, since the bar is the score.

Amendments (idea-debate, F3, and idea-pilot):
- Briefing pack gains the profile extract and never carries a
  data-availability memo; feasibility assessor gets read-only query
  access under the settle-by-query rule; access failure joins the
  triage routes; the pilot's first check becomes the registered
  extract query plus full-scope expansion joins.
- Evals:
  (11) The assessor votes REVISE on "the identifier may be unstable"
       with no query behind it: validation fails the position and
       returns it for the query the profile can answer.
  (12) An idea whose licence forbids the use: routed access-blocked
       with the licence clause quoted, not to the graveyard and not
       silently swapped to a public proxy.
  (13) A join that matched at 87% on the probe slice matches at 41% at
       full scope: the pilot records the gap against the profile's
       number and the verdict follows the full-scope figure.

## Memory and budget: adjudication graph, resolution dedup, rubric ratchet, complexity budget

Design source:, the reading note for
the graph-engineering synthesis PDF (read-only external reference, source
caveat in the note). Evidence source: findings A, B, C and D from a full-scale
trial run, recorded in that run's own documentation and not shipped here. Scope: one new store with read and write points in three
existing skills, one rewritten section, one new skill, one config block.

Build order is A2, then A1, then A4, then A3. A1 keys on mechanism
signatures that A2's resolution step produces, so building A1 first would
bake the current dedup's misses into the memory the whole funnel then
trusts. This ordering is a hard dependency, not a preference.

A5 sits outside that chain and after all of it: it is the
instrument that would let A1 through A4 be judged rather than argued about,
and it is built on top of a fixture suite that already exists.

Spec (A2, entity-resolution dedup, rewrites `idea-swarm` `## Dedup`):
- Problem: the trial's lexical Jaccard found roughly zero duplicate pairs
  where a hand read found 40-plus cards in 7 clusters (trial finding A). The
  skill text
  already says "cluster on question, mechanism, and setting similarity";
  the implementation did not deliver it.
- Structure: two stages. Stage 1 is cheap blocking (lexical or embedding
  prefilter) that narrows candidates only, never decides a merge. Stage 2
  is model arbitration on `model_default` over the surviving candidate
  groups, returning cluster assignments with a one-line rationale and a
  confidence per merge. Two stages rather than one call because a pool of
  100-120 cards is roughly 6,000-7,000 pairs; blocking is what makes
  arbitration affordable.
- Merge record becomes additive and reversible. Today: `kept <id> <-
  merged <ids>`. New fields per merge: the merged ids as aliases on the
  kept card, the arbitration rationale, the confidence, and the run id.
  A bad merge is then undone from the record without rebuilding the pool.
- Emits `RESOLVED_TO` edges and a `mechanism_signature` per distinct card.
  These are A1's input, which is why A2 is built first.
- Adoption gate (blocking, and the reason this spec is landable): score
  the new pass against a hand-built ground truth: 7 clusters over a 102-card
  full-scale pool, built once by reading the pool and not shipped here. Metrics from the source's §VII.B: pairwise
  precision, pairwise recall, false-merge rate, missed-merge rate, and
  compression ratio (raw surface forms over canonical entities). Replace
  the lexical implementation only when the new pass matches or beats the
  hand pass.
- The binding metric is **false-merge rate, not compression**. The source
  warns that compression alone rewards over-merging. Our stake is sharper
  than its example: merging two genuinely distinct ideas kills one of them
  silently and forever, which is the same asymmetry that justified the
  kill audit on. A wrong survival meets the desk screen, the
  panel, the pilot, and the S8 referees; a wrong merge meets nothing.
  A compression ratio that improves while false-merge rate rises is a
  failed run, not a tradeoff.
- Freedom: high on the blocking method and the arbitration prompt, none on
  the merge record fields, the adoption gate, or which metric binds.
- Gates: adoption gate above; the existing funnel floor and the
  distinct/raw ratio flag are unchanged.
- Evals:
  (1) Ground-truth replay: the new pass over the 102-card pool recovers
      the 7 hand clusters at or above the hand pass on pairwise precision
      and recall, with false-merge rate reported, not omitted.
  (2) Two cards sharing a mechanism but differing in setting and unit of
      observation: not merged, and the arbitration rationale names the
      setting difference as the reason.
  (3) A merge is later disputed: the kept card's aliases, rationale,
      confidence, and run id are sufficient to reconstruct and reverse it
      without regenerating the pool.
  (4) Compression improves while false-merge rate rises: the run reports
      the regression and the change is not adopted.

Spec (A1, adjudication graph, `ideas_dir/adjudication_graph.json`):
- Problem: the full-scale F1 grid independently regenerated the
  servicer-capacity mechanism (9 cards) and the lender-belief mechanism
  (8 cards), both already adjudicated and killed earlier in the same
  session: 17 of 102 raw cards, roughly 17% of the pool (trial findings B and
  C). The F0
  blocklist carries literature-occupied margins only. Nothing carries
  "this project already debated this to death."
- Why a typed store rather than the flat `adjudicated_mechanisms.md` the
  demo documentation proposed: a flat list answers "was this mechanism
  killed?" and not "was it killed for a reason a different setting would
  fix?" The second question is one the fallback triage and the blocked
  registry already ask in prose, and answering it is a traversal from idea
  to verdict to missing ingredient.
- Nodes (five, narrowed from the source's nine to what the funnel has):
  `Mechanism`, `Idea`, `Verdict`, `Paper`, `MissingIngredient`.
- Edges (seven): `ABOUT` (idea to mechanism), `KILLED_BY` (idea to
  verdict), `OCCUPIED_BY` (mechanism to paper, written by the novelty
  audit), `BLOCKED_ON` (idea to ingredient), `DERIVED_FROM` (clinic rework
  a card to its revision, and graveyard parent to credited new card), `RESOLVED_TO`
  (dedup merges, from A2), `SUPERSEDES` (kill-audit overturn).
- Four invariants, narrowed from the source's Appendix:
  1. every verdict cites a record path or is marked inference;
  2. every node carries the run that created it;
  3. every verdict names its kill layer (novelty audit, desk simulation,
     debate, or pilot);
  4. every superseded node stays addressable: an overturn adds a
     `SUPERSEDES` edge and never deletes.
  Invariant 4 is already the kill audit's discipline in prose. The graph
  is where it becomes checkable.
- A `Mechanism` node stores its member card ids, not only the signature.
  This is the mitigation for the one §VIII.C condition A1 does not clear
  outright: a false merge from A2 propagates into the graph, and storing
  members keeps an overturned merge traceable rather than baked in.
- Read points: F0 (steers generation), the F2 to F3 handoff screen
  (finding C: catches a recurring mechanism before F2 scoring tokens
  rather than after F3 audit tokens), the blocked-registry recheck, and
  bench refill. The last two exist today as prose procedures and become
  queries. Query shapes taken from the source's §III.C vocabulary:
  children, leaves, lineage.
- Write points: `idea-debate` terminal states, kill-audit overturns,
  `idea-swarm` dedup merges.
- Anti-anchoring rule (binding): the graph enters generation as
  **constraint digest lines, never as raw verdicts**, the same rule that
  already governs the F0 landscape brief and the anchored-mode data
  capability digest. A generator that sees prior judgments anchors on
  them, which is the Lens 6 failure in new clothes.
- Freedom: none on node and edge types, the invariants, or the
  anti-anchoring rule; high on query implementation and file layout.
- New gate: **adjudication screen** (machine, F2 to F3). A survivor whose
  mechanism signature matches a terminal entry routes to the graveyard
  citing the matching node, without spending audit tokens.
- Evals:
  (1) A terminal graveyard entry from cycle 1: cycle 2's constraint digest
      carries it as a constraint, the raw pool contains no card on that
      mechanism, and the digest quotes no verdict text.
  (2) An F2 survivor matching a killed mechanism: the adjudication screen
      routes it to the graveyard citing the node id, and no novelty audit
      or desk simulation tokens are spent on it.
  (3) An idea blocked on a missing dataset that later becomes available:
      the `BLOCKED_ON` traversal returns it for F3 re-entry under the
      existing unblocking rule, and the recheck is a query rather than a
      markdown read.
  (4) A kill audit overturns a kill: a `SUPERSEDES` edge is added, the
      original verdict node is still addressable and still cites its
      record path, and nothing was deleted.
  (5) Invariant probe: a verdict node written without a record path fails
      validation and is not published.
  (6) A merge A2 made is later reversed: the mechanism node's member card
      ids identify every affected idea, and the graph is repaired without
      a rebuild.

Spec (A3, rubric ratchet, new skill, BUILD-new, P2):
- Problem: we hold a gold set (`references/top_journal_calibration.json`,
  roughly 40 top-3 acceptances and 40 stalled analogs, with
  `mechanism_index` and `identification_style_index`) and audit counters,
  and we improve the F2 rubric by hand-read postmortem.
- Structure, in the source's §VII.A shape and its `program.md` control-spec
  style: read the current rubric and score history, propose **one**
  motivated change, re-score the calibration set, compute the metric, keep
  or revert, commit, record. Declared up front: mutable files (the F2
  rubric text only), protected files (the calibration set, the gate table,
  every other skill), the metric and its direction, the experiment budget,
  the revert rule, and the escalation policy.
- Metric: **calibration-set discrimination**, whether the rubric ranks real
  acceptances above stalled analogs, on a **held-out split**. Ratchet on
  one half, report on the other.
- Three scope limits, ours rather than the source's:
  1. Never kill rate, pool size, or cycle time. The source's §IX.B says a
     ratchet improves the metric it can see; every one of those three
     improves when a rubric becomes less discriminating, which is the
     failure this skill would otherwise industrialize. already carries the argument in the kill-audit entry.
  2. Held-out split, because the source's §IX.B names overfitting the
     evaluation set as the second failure, and a rubric tuned to
     convergence on the full set is exactly that.
  3. **F2 rubric only in this build.** F3 role briefs stay out until the
     audit counters have cross-run data. `.claude/skills/idea-debate/SKILL.md`
     says those rates are read across runs and not within one, and there
     has been one full-scale run.
- Prerequisite to check at build time: whether the calibration
  file suffices, or `calibrate-rubric` (P2, still deferred per STATE) must
  run first. The six-month staleness rule puts the file's expiry six months out, so it is current, but a ratchet is a heavier consumer of it
  than a single scoring run.
- Freedom: high on how a change is proposed, none on the metric, the
  split, the one-change rule, or the mutable-file list.
- Gates: calibration present and fresh (blocking, as for `idea-scoring`);
  one change per iteration; experiment budget from A4.
- Evals:
  (1) A proposed change improves training-half discrimination and degrades
      held-out: reverted, and the attempt is recorded rather than dropped.
  (2) A change that raises throughput and leaves discrimination flat: not
      an improvement, reverted, no exception for cost savings.
  (3) An iteration edits anything outside the rubric text: refused before
      scoring, naming the protected file.
  (4) Budget exhausted mid-run: returns the best rubric version so far,
      the completed iterations, and the reason for stopping, per A4.

Spec (A5, menu partition and menu-blind cells, BUILT into
`idea-swarm`; the one item in this batch that is code-free and therefore
landed rather than specced):
- Problem, from re-reading the pool rather than from the
  source PDF: the F1 constraint digest gave all 12 cells the same three
  open-margin targets, and those three targets are the pool's three
  largest semantic clusters, one cluster per menu item (L-1 fiscal
  channel 11 cards, K-1 servicing/forbearance 9, G-3 lender belief 8;
  28 of 102 raw, 27%). Of the 38 cards in all seven clusters, the menu
  explains 28, roughly three quarters of the duplicate generation. The
  remaining four clusters are small and genuinely independent.
- What this rules out: agent-to-agent leakage (subagents have no channel
  and the clean-room walls held), lens overlap (the clusters cut across
  lenses), and framing (`landscape_brief.md` carried the anti-anchoring
  rule verbatim and the collapse happened anyway). The anti-anchoring
  rule governs what the menu is called; the pull comes from cardinality
  and sharing, which the rule never addressed.
- Structure: F0 aims for one displacement target per steered cell rather
  than a short list for everyone. F1 reserves at least a quarter of cells
  menu-blind (blocklist only, no target), gives every other cell exactly
  one target, and never gives one target to two cells. A menu shorter
  than the steered-cell count converts the surplus cells to menu-blind
  instead of doubling up. Digests become per cell and are written out
  and kept, which is what makes the assignment auditable. The blocklist
  is not partitioned: negative steering, measured working in the same run
  (0 of 21 occupied-margin hits), and splitting it would let one cell
  re-generate what another was told to avoid.
- Interaction with anchored mode: the menu-blind reservation and the
  unanchored reservation are independent draws over the same grid, not
  the same cells renamed. Collapsing them would produce one fully blind
  group and leave every other cell steered on both dimensions at once.
- Concentration flag: the distinct/raw ratio is retained and is not
  sufficient. It scored 0.70 and passed on this run. Added: top-cluster
  share, top-three share, flag above 0.20 on the latter, and per flagged
  cluster the cell spread and whether the mechanism matches a menu
  target. Those fields separate menu pull from a single generator
  repeating itself from genuine independent convergence, which need
  different responses and only the last of which is a finding.
- Freedom: high on how targets are phrased and assigned to cells, none on
  the reserved share, the one-target rule, the no-sharing rule, or the
  shortfall-converts-to-blind rule.
- Expected effect, stated as a prediction to be checked rather than a
  claim: most of the 31 merged-away cards become distinct, so a
  comparable run should land near 90 distinct rather than 71 from the
  same 102 generations. Untested. It is not measurable at scale until
  A2 lands, since the 71 came from reading all 102 cards by hand and
  lexical dedup found one pair.
- Evals:
  (1) 12 cells, 9-target menu: 3 cells menu-blind with no target in
      their digest, 9 steered with one target each, no target repeated,
      and the assignment record reconciles with the grid.
  (2) 12 cells, 3-target menu: 3 steered and 9 menu-blind, with the menu
      shortfall logged; no two cells share a target.
  (3) One shared digest handed to every generator: validation fails,
      naming the missing per-cell digests.
  (4) Replay of the pool through the concentration fields:
      top-three share computes to 0.27, the flag fires, and each of the
      three clusters is recorded as spanning many cells and matching a
      menu target (that is, diagnosed as menu pull, not convergence).
  (5) A cluster whose members all come from one cell: recorded as a
      generator repeating itself, not as menu pull, and the menu
      assignment is not blamed for it.

Spec (A4, complexity budget, `pipeline-config` block plus error-ladder
rung). **Rewritten against measured cost; the original keys are
kept below as a record of what the measurement refuted.**
- Problem: no stage declares a limit anywhere, and finding D ("protect F3's
  budget, cut F1's before cutting F3's rounds or role count") is advice
  with no mechanism behind it.
- **What the original spec proposed, and why it does not work.** The keys were
  `max_subagents`, `max_concurrent`, `max_tokens_per_stage`, `max_wall_clock`,
  `max_retries`, `min_evidence_to_finalize`, with per-stage defaults tight on
  F1/F2 and generous on F3. That was written on with no cost
  measurement available, and the first measurement refutes its central choice.
  an earlier run, read from the session transcripts with `tools/run_cost.py`:

  | Layer | Agents | Share of run cost | Per agent, relative |
  |---|---|---|---|
  | Decision audit | 7 | 16% | **56x** |
  | Debate roles | **40** | 12% | **8x** |
  | G1 judges | 4 | 5% | 32x |
  | Desk editors | 3 | 2% | 18x |
  | Generators | 10 | 0.4% | **1x** |
  | **Driver's own thread** | **0** | **63%** | — |

  Three consequences. **(a)** Cost per agent spans 56×, so a key that counts
  agents cannot ration anything — `max_subagents: 32` would have fired at the
  debate, the cheapest-per-agent layer in the funnel. **(b)** The largest single
  line item, the driver's own thread, appears in no agent count at all and no
  proposed key bounded it. **(c)** The binding resource is not agents or wall
  clock but **context volume re-read**: cache reads are 61% of project spend,
  cache writes 25%, output 17%, fresh input 1%. `max_tokens_per_stage` was
  directionally right and was the one key with no way to observe it; that is
  what the tool now supplies.
- **Revised config block**: `max_cost_per_stage` (cost-equivalent, read from
  `tools/run_cost.py`), `driver_context_ceiling` (soft — triggers a handoff and
  a fresh session at the next layer boundary, not a stop), `max_wall_clock`,
  `max_retries`, `min_evidence_to_finalize`. `max_concurrent` survives only as a
  harness-survival setting, not a budget one. `max_subagents` is **retired as a
  budget key** and kept as a *reported counter*, because the count still answers
  the clean-room question — how many isolated judgments were bought — which is a
  different question from what they cost.
- **The reported statistic is cost per SUCCESS, not cost per run**. Every figure in the table above
  is a numerator. Cost per agent, cost per layer and cost per run all say what
  a layer *spent*; none of them says whether the spend bought anything, and a
  keep-or-cut decision needs the ratio. The measured instance is already on the
  table: `idea-novelty` saves four debate roles per kill and costs more
  than that, which reads as a verdict and is not one, because "per kill" has no
  denominator saying how many of those kills were right. Three statistics,
  matching the source: mean cost per run, cost per successful run, and the
  **incremental cost per additional success** of running an arm against not
  running it. `tools/run_cost.py --outcomes` computes all three; the template is
  `tools/outcomes.template.json`.
  Two rules bind, and they are what keep this from being a rationalization with
  a decimal point. **The success definition is declared per layer, in writing,
  with the date it was fixed, and the tool prints a Material Gap instead of a
  ratio when it is absent** — the same discipline
  applied when it fixed ρ < 0.2 before computing anything. **The incremental
  statistic compares two arms of the same work, not two layers**: the source's
  own warning is that adding context to an already-capable arm raised its cost
  per additional success by roughly a factor of two, which is invisible unless both
  arms answer the same question.
  What the statistic cannot do, stated because it will be reached for anyway:
  the source's task success is binary, immediate, and deterministic, and no
  funnel layer's is. A cost-per-success figure for a judgment layer is an
  estimate resting on an outcome coding, and it inherits every limit records about terminal-outcome samples of
  eleven.
- Per-stage defaults still encode finding D (tight on F1/F2, generous on F3),
  and the observed baseline is now per-layer cost rather than wall clock. Note
  what the numbers say about finding D itself: cutting F1 saves well under 1% of
  a run and cutting the debate saves 12%, so "cut F1's before F3's" is right about
  *quality* and nearly irrelevant to *budget*. The layer worth rationing is
  whichever one the pilot and desk let through, because the debate is the only
  layer linear in surviving cards.
- **Fourth rung on the error ladder** (`pipeline-design.md` §5): budget
  exhaustion. The ladder covers bounded retry, flagged degradation, and
  human escalation, and has no path for running out. The rule, adopted in
  substance from the source's §VIII.B: return the best current artifact,
  the completed work, the unresolved issues, and the reason for stopping.
  Never present partial completion as a finished result. This is the
  Material Gap rule pointed at budgets.
- Freedom: high on the default values, none on the exhaustion behaviour.
- Gates: none new. A budget is a declaration and a stopping rule, not a
  gate; making it a gate would put it in the path of every stage for no
  added integrity.
- Evals ( with the keys):
  (1) F1 hits `max_cost_per_stage` mid-grid: the run stops, reports which
      cells generated and which did not, and the pool records the shortfall
      the way the funnel floor already requires. Note this eval is now nearly
      unreachable in practice and that is the finding — ten haiku generators
      cost under 1% of a run, so any cost cap that F1 can hit is a cap set wrong.
  (2) A stage completes inside budget: no behavioural change of any kind
      versus today.
  (3) A run exhausts `max_wall_clock` during F3 debates: the completed
      debates are returned with their verdicts, the incomplete ones are
      named as incomplete, and no comparative final is declared from a
      partial slate.
  (4) The driver's context passes `driver_context_ceiling` mid-layer: it runs
      `handoff`, the layer resumes in a fresh session from the stage cursor,
      and **no stage output changes** — this is a soft trigger, so a run that
      splits and a run that does not must produce identical artifacts.
  (5) Replay of an earlier run through the cost keys: `tools/run_cost.py`
      reproduces the 63% driver / 37% subagent split across 65 agents, and a
      `max_subagents: 32` cap is shown to fire at the debate, one of the
      cheapest layers per agent, while leaving the driver's 63% untouched. This is the
      eval that retired the key, and it is kept so the next person to propose
      counting agents has to answer it.
  (6) `--outcomes` with a layer that declares successes and no `success_is`
      line: the row prints a Material Gap and no ratio, and the run does not
      fail. A missing definition is a gap in the record, not a broken tool.
  (7) `--outcomes` absent: byte-identical output to the version before the
      flag existed. Verified by reconstructing the pre-edit file
      and diffing both reports over all 16 sessions of this project.

Spec (A5, off-line layer eval harness, NOT BUILT):

- **Problem.** Every harness change this project has made was justified from a
  single live run, and the project has already proved to itself that a single
  live run cannot justify one.: a run yields
  about eleven terminal outcomes, detecting ρ = 0.4 needs about 47, the
  permutation null band at n = 11 runs to ±0.61, and "waiting for a bigger one
  is not a plan." an earlier run's own record says the same thing from the other side —
  eight rules written from an earlier run's transcript, none of them run. Two settings
  of the pilot gate were retired on the grounds that they "would each have
  fired zero times on the four runs to date," which is an honest observation and
  not a measurement.
- **The alternative, from.** Stop measuring harness
  changes on live runs. Freeze a task set with reference outputs, hold the model
  fixed, vary one dimension of the harness, repeat each cell k times, and score
  deterministically. The source crossed 21 tasks × 3 environments × 2 prompt
  conditions × 3 agency conditions × 5 repetitions = 1,890 runs at roughly
  a fifth of a dollar each, an order of magnitude below one full pipeline run.
  The instrument is affordable; what it
  costs is task authorship, and that cost is paid once.
- **What can be scored this way, and nothing else.** The boundary is a
  **checkable output**, not "is this a judgment layer" — the two are different
  lines and at least one layer sits between them.
  Eligible today: the counting gate's ```count re-execution, the reachability
  block's schema, the novelty verdict's parseable block, citation verification,
  claim-ledger validation, the script-registry audit, the quarantine check, and
  the manual-first estimand check.
  **Also eligible: `idea-novelty`'s counter A1, occupancy adjudication.** The
  input is a card plus a supplied paper set, the output is an
  `occupies` / `adjacent` / `context` call per work with a quoted claim, and the
  answer key is fixable in advance — take published papers and write cards whose
  designs they occupy. supplies two
  seed items, and they are better seeds than they first looked, because the task
  they define is **adjudication against a held set** rather than retrieval. This
  is the layer's core rule and no live run can power a test of it.
  Ineligible, on the source's own scoping ("open-ended empirical research falls
  outside this scope"): F1 generation quality, F2 rank validity, desk-reject
  tiers, debate verdicts, `panel_reach`, and the G1 ladder's judged gates
  (B, C, E). Those keep the route `f2-validity` already prescribes — accumulate
  `(score, terminal_rank)` pairs across runs until a powered read exists. **A5
  must not be sold as a way to measure the judgment layers.** It is a way to
  stop spending live runs on the layers that never needed one, so the live runs
  are free to accumulate outcomes for the layers that do.
- **`eval/task_registry.json`.** Per task: an id, the layer under test, the
  input artifacts, the reference output, a per-quantity tolerance, and a
  scoring rule. The registry is frozen; the same inputs run under every
  condition and every repetition, so a difference between cells is a fact about
  the condition. Seeds for any generated input live in the registry, next to
  the reference they produced.
- **Design.** One dimension varied per experiment (a config key, a prompt
  block, a tool surface, a model tier), model held fixed, k = 5 repetitions per
  cell. Deterministic scorer, task fixed effects, standard errors clustered at
  the task, wild cluster bootstrap with Rademacher weights where the cluster
  count is small — the source ran 21 clusters with 9,999 replications, and this
  project will have fewer, which makes the bootstrap more necessary rather than
  less.
- **Run record.** Reuse the audit-field list the source's Appendix B already
  worked out, because it is the schema this project keeps re-deriving in
  pieces: model id, condition, declared tool surface, permission mode,
  execution limits, session id, stop reason, turn count, token categories,
  estimated cost, and pass/fail per criterion. `tools/run_cost.py` already
  reads most of it.
- **Binding rule: the decision rule is written before any number is computed**,
  as an earlier run of the f2-validity check did, and it is committed with the
  experiment rather than announced with the result. This is the one procedural
  rule the harness cannot be trusted without, because an off-line harness makes
  it cheap to run the experiment again with a different rule.
- **Report what was not covered.** Any cell skipped, any task dropped, any
  repetition that failed to produce a scored record is named in the output.
  A harness that silently covers less than it claims reads as evidence and is
  not.
- **Build order and prerequisite.** After `gate-fixtures/`, which
  is the degenerate case: k = 1, one condition, and a scorer that asks only
  whether the gate fired. That suite exists and is green, and
  A5's scorer is its scorer with a tolerance table and repetition added. Do not
  build A5 first; a scorer nobody has run against a planted failure is the
  thing this whole line of work exists to distrust.
- Freedom: high on task selection and on which dimension the first experiment
  varies. None on the pre-fixed decision rule, none on the eligibility
  boundary, none on reporting what was skipped.
- Gates: none new. A5 measures gates; making it one would put an experiment in
  the path of every run.
- Evals for A5 itself:
  (1) Two identical conditions: the estimated difference is indistinguishable
      from zero and the reported band contains it. A harness that finds an
      effect between a condition and itself is measuring its own noise.
  (2) A planted condition difference — one arm with a gate disabled — recovers
      the sign and rough magnitude, the same synthetic-first discipline S6
      already runs on estimators.
  (3) A task whose reference output is wrong: the failure surfaces as every
      condition failing that task, not as a condition effect. Task fixed
      effects are what make this readable, which is why they are in the design
      rather than optional.
  (4) k = 1: the harness refuses, or labels the result unrepeated. One draw per
      cell is the n = 1 problem A5 exists to end, wearing a harness.

---

## F3 step 1.5. idea-novelty (BUILD-new)

- Trigger: author feedback on `experiments/an earlier data project/output/action_plans.md`
  — no plan links its empirical question or its anticipated finding to a
  literature or to a theory. Verified: that file and `ideas/comparative_final.md`
  carry **zero citations between them**, and every "what would kill it" in the
  four plans is a feasibility threat.
- The gap is structural, not a writing miss. Step 1.1 is an **occupancy** check
  (*has someone done this design*) and is deliberately facts-only because
  `novelty_facts.md` enters the debate briefing pack; it can retire a card only
  on an occupied margin with no open adjacent one, and it killed **0 of 12** on
  the first themed run. Nothing downstream carried contribution authority: the
  run graveyarded **0 of 8** on contribution grounds while its incrementality
  editor was reporting that 8 of 12 cards aimed at one sentence in one working
  paper. A pilot *count* was terminal; a contribution judgment was not.
- Does: four blocks per surviving card — (1) question-to-literature link, each
  named paper's actual claim; (2) theory link and evidence status on
  `established`/`contested`/`untested`/`none`, every rung argued from a
  **returned** source, `untested` naming the observability barrier and carrying
  the queries that failed; (3) **outcome-conditional contribution table** — what
  the paper says under the predicted sign, a null, and a reversal, each cell
  naming a strand and permitted to be *conditional*; (4) displacement
  verification against the target's actual claim, returning
  `verified`/`additive`/`misread`/`unverifiable`.
- Verdicts: `PROCEED` / `REFRAME` (framing note onto the card; never the revision
  clinic, so it never spends that budget; a scope or source change re-enters as a
  new card) / `CONTRIBUTION-NULL` (graveyard).
- Placement: after the desk, before the debate, because the debate is the only
  layer **linear in surviving cards**, so slate size is the one lever on it and
  this is the **earliest authoritative** kill available. (Rationale: the original said "cheapest kill available" on the grounds that
  the debate was 40 of 61 subagents. Measured, the debate is 62% of the agent
  count and **12% of the cost**, so a kill here saves the four debate roles that
  card would have run, and this judge costs more than those four roles. The layer is bought for what it
  catches, not for what it saves.) Not before the pilot — a contribution table
  written before the
  counts exist cannot say whether a live cell is reachable. Not a fourth desk
  editor — the desk returns an uncalibrated `panel_reach` and this verdict is
  checkable against sources; folding the verifiable judgment into the
  unverifiable ladder hides the better signal inside the worse.
- Freedom: high on how the strands are drawn and how the table is argued. **None**
  on: the four blocks, the rung ladder, the quarantine boundary, the confirmer
  rule, and the mechanism-not-theme search rule.
- Gates: one new machine gate, **Novelty gate** (`workflow/pipeline-design.md`
  gate table), plus **defect class 7** in the decision audit with a
  novelty-cleared layer-matched control.
- Explicitly not built: any change to the card schema. Handing generators a theory
  list would reproduce an earlier attractor in which the occupied-margin
  blocklist became a displacement-target menu and 9 of 20 cards named one target.
  There is no partition available to break it. **Assessment is judge-side only**,
  and `idea-variants` and `idea-swarm` are deliberately untouched.
- Evals, all three drawn from the retrofit on the four live menu items
  (`experiments/an earlier data project/output/novelty_positioning.md`), which is the
  layer's first and so far only trial:
  (1) **A design that is feasible and answered.** K3-1 asks how fast prices adjust
      at the release instant, on 5-minute bars, with 60-second ticks as its best
      case. Ederington & Lee closed the question on interest-rate futures at
      10-second resolution in 1995 (*JFQA*, 306 cites) and Chordia et al. at 5ms
      in 2018 (*RFS*). The layer must return 0 live cells as written, a
      `CONTRIBUTION-NULL`, and — because one pass ran, not two — route on
      `REFRAME` under the confirmer rule rather than killing.
  (2) **A hunch that misreads its own target.** K2-2 claims to displace a paper
      that attributes gains to *makers*, using an outcome variable measured
      entirely on the *taker* side. The layer must return `misread` and quote both.
  (3) **A theory-status call that survives its own power.** K9-1 carries the set's
      only fully `untested` prediction with a named barrier the venue removes
      (persistence without delegated capital flows), and its displacement target
      already reports weak persistence on 2.4M users against this design's 180
      traders. The layer must return `untested`, `additive`, and cells marked
      *live but not at this sample* — not a clean `PROCEED` on the strength of the
      theory link alone.
