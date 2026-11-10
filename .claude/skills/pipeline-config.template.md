# Pipeline config (template)

Copy this file to the paper project's root as `pipeline-config.md` and fill
the values. Every pipeline skill reads this file first and refers to these
keys; no skill hardcodes a path. Keys use `key: value`, one per line, inside
the block below. Relative paths are relative to the paper project's root.

```text
# Identity
project_name:     <short name>
field_profile:    finance        # finance | economics | econometrics
gate_mode:        human          # human | autonomous (see playbooks/gate-modes.md)
theme:            <one sentence, or omit>   # set = themed path; omit = open swarm

# State and logs
state_file:       notes/STATE.md
lab_notebook:     notes/lab_notebook.md
decisions_log:    notes/decisions.md
run_log:          output/pipeline_run.md
tools_dir:        <path to the shared tools/ directory>

# Ideation funnel (S1/S1b)
ideas_dir:        ideas
idea_pool:        ideas/pool.json
calibration_file: <path to top_journal_calibration.json>
g1_threshold:     top-generalist-candidate   # top-generalist-candidate | strong-field-candidate
g1_fallthrough:   strong-field-candidate     # tier shown for review when the slate is empty; none = end ARCHIVED
usable_min:       <integer> <unit>          # e.g. 200 firm-quarters; one bar for the whole run

# Held data (S1 anchored mode)
data_mode:        open          # open | anchored (missing = open)
data_access:      any           # any | free_only (missing = any)
data_manifest:    data/held_data_manifest.md
data_profile:     ideas/data_profile.json
peek_log:         ideas/peek_log.md
private_spine:    allowed       # allowed | extension_only

# Literature
paper_set:        output/paper_set.json
search_log:       output/search_log.md
bib_file:         paper/references.bib

# Design and analysis
prereg_file:      preregistration.md
results_dir:      output
registry_file:    output/script_registry.json
claim_ledger:     output/claim_ledger.json
scripts_dirs:     scripts, analysis
seed:             20260101      # frozen in prereg block 9; every stochastic step takes it

# Writing and review
paper_dir:        paper
main_tex:         paper/main.tex
reviews_dir:      reviews
writing_hub:                    # optional; a voice and phrase pack. Empty = norms only

# Build graph (paper-build)
makefile:         Makefile
build_dir:        build
values_tex:       build/values.tex
values_lock:      output/values.lock.json

# Execution
python:           .venv/bin/python

# Model policy
model_default:    <cheap/default model for mechanical stages>
model_mid:        <mid tier: F2 idea scorers; falls back to model_default>
model_strong:     <strong model: referees, debate panel, causal-inference review>

# Budget
driver_context_ceiling: 250000   # STOPPING RULE: split at next layer boundary above this
budget:
  max_wall_clock:         <minutes per stage>   # STOPPING RULE (rung 4)
  max_retries:            3
  max_subagents:          <reported counter, NOT a cap — see note below>
  max_concurrent:         <cap on workers running at once>
  max_tokens_per_stage:   <reported counter>
  min_evidence_to_finalize: <what must exist before a stage may declare done>
```

Conventions the keys imply:

- `field_profile` selects the journal calibration profile that idea
  screening and peer review use (JF/JFE/RFS; AER/QJE/JPE/ECMA/ReStud;
  JoE/JAE).
- `reviews_dir` is write-only for review skills and is never read as
  analysis input.
- `build_dir` holds every generated artefact (tables, figures,
  `values_tex`, the PDF). Nothing in it is edited by hand: a wrong number is
  fixed at the results key and the script that wrote it, then rebuilt. The
  `makefile` declares the graph that produces it and is what
  `script-registry --makefile` reads for inputs and outputs.
- `values_lock` records the last accepted values of the generated macros. It
  is source, not a build artefact: it sits outside `build_dir` so `clean`
  cannot reach it, it is committed, and only an explicit `accept` writes it.
  The gate that compares against it is what turns a moved headline number
  into a decision instead of a silent rebuild.
- `budget` declares what a run may spend before it stops. Defaults are tight
  on the breadth layers (F1 generation, F2 scoring) and generous on F3,
  because the depth layers are where a full-scale run finds
  every real problem and where debates converge fastest; economizing on
  breadth is the cheap cut and economizing on depth removes the signal.
  A budget is a declaration and a stopping rule, not a gate: it does not sit
  in the integrity path of any stage. When a stage exhausts its budget it
  returns the best current artefact, the completed work, the unresolved
  issues, and the reason it stopped, per rung 4 of the error ladder.
  Partial completion is never reported as a finished result. A stage may not
  skip a machine gate because the budget expired: it stops *before* the gate
  and records it as unrun.
- **Only two keys are stopping rules**: `driver_context_ceiling`,
  which makes the driver split at the next layer boundary, and
  `budget.max_wall_clock`, which triggers rung 4. Everything else in the block
  is a **reported counter**.
  `max_subagents` is deliberately a counter and not a cap. The first cost
  measurement retired it: it would have fired at the debate layer, which is 62%
  of the agent count and only **12%** of the cost, and it cannot see the driver's
  own thread, which was **63%** of the run at a 344K median context. Capping agents rations the cheapest thing in the funnel. How many
  *isolated* judgments a run bought is still worth knowing — that is the
  clean-room question — which is why the key survives as a counter.
- `seed` mirrors block 9 of the pre-registration. It is passed to scripts as
  an argument, never hardcoded inside them, so the build graph reproduces
  the same numbers.
- `decisions_log` is append-only: date, gate, options considered, choice,
  one-line rationale.
- `run_log` is the conductor's append-only run record: one dated line per stage
  transition, one per gate resolution, and the prompt ledger. It is the
  measurement for the fewer-than-N-prompts goal, and it is where the per-layer
  cost and subagent tables are pasted at every stop state.
- `tools_dir` locates the shared tooling (`run_cost.py` and its outcomes
  template) that lives outside any one paper project. Skills reference it by key
  rather than by a relative path, because a relative `tools/...` resolves
  against the vehicle and misses the shared directory entirely.
- `writing_hub` is the seam for a voice layer: a directory holding per-section
  vocabulary, sentence templates, a claim-strength ladder, an author voice
  profile, and whatever prose measurement comes with them. The writing skills
  (`draft-paper`, `empirical-intro`, `hypothesis-development`,
  `literature-review`) load it when the key is set and fall back to
  `references/writing-norms.md` and `references/banned-words.md` when it is
  empty. It is optional because a voice pack is author-specific and the rest of
  the pipeline does not depend on one: an empty key produces correct, plain
  prose, not broken prose. Leave it empty unless you have a pack to point at.
- `data_mode` decides which idea funnel S1 runs. `open` (the default,
  and what a missing key means) is the literature-first funnel: the
  project holds no data and every data claim is a hunch until F3.
  `anchored` is for a project that already holds data; F-1 profiles it
  before generation and the later layers read verified facts. Anchored
  mode requires `data_manifest`; the other three keys have the defaults
  shown above.
- `data_access` decides which sources an idea may rest on. `any` (the
  default) admits any source with a **named access route**: `held` (in
  `data_manifest`), `public`, `licensed` (a subscription the author can
  actually use), `purchasable`, or `restricted` (application or approval
  needed). A card that names no route fails the same way a card naming a
  field outside the profile fails — the route, not the price, is the
  feasibility question. `free_only` restores the older behaviour, where
  every source must be free and collectable by a referee; set it for a
  venue whose data-availability policy requires it.
- `data_manifest` is author-written and declares each held source: name,
  kind (`db` | `api` | `file`), access method, **the environment
  variable holding the credential, never the credential itself**,
  licence and redistribution terms, and refresh cadence. The cadence is
  what the profile-freshness gate measures against.
- `peek_log` is append-only and records every query run against held
  data during S1 and S1b (timestamp, script, fields touched, purpose).
  The pre-registration reads it to declare retrospective elements.
- `private_spine: allowed` lets held data carry a paper's headline,
  against a disclosed replication plan approved at G4;
  `extension_only` confines it to measurement and validation, leaving
  identification on sources a referee can collect.
- `theme` is the pipeline's input contract. Set it to
  one sentence naming the question area, and S1 runs the **themed path**:
  F0 narrowed to the theme, 8-12 deliberate variants of it rather than a
  swarm, a feasibility pilot on every variant up front, and debate only on
  what the data can carry. Omit it and S1 runs the open **swarm** grid,
  which searches a space instead of covering one question's design space.
  A themed run still reserves 2-3 **theme-blind** cells, because a themed
  entry cannot tell you the theme is wrong: it will find the best available
  version of a bad bet, efficiently.
- `g1_threshold` is **the bar G1 accepts at**, and it is the same bar
  whatever the topic: the four-rung ladder from `finance-idea-screening`
  (`top-generalist-candidate` / `strong-field-candidate` / `revise` /
  `kill`), with the default admitting only cards that cleared every gate a
  top-3 paper clears — including Gate F, feasibility, which refuses at any
  score a design the held data cannot carry. G1 returns **however many cards
  clear it: none, one, or many.** Set `strong-field-candidate` for a project
  deliberately aiming lower; the run's artifacts then say so on every page.
  Missing key means `top-generalist-candidate`.
  A rung asserts **gate clearance**, never a predicted journal placement, and
  an artifact implying one is a validation failure.
- `g1_fallthrough` decides **what happens when no card clears
  `g1_threshold`**. Default `strong-field-candidate`: the
  stage states the zero, reports the DECLINE diagnosis, and then presents the
  capped cards as a **separately labelled tier** for author review, stopping at
  CHECKPOINT. Set `none` to end the run ARCHIVED on an empty slate.
  **This does not move the bar and does not refill the slate.** No verdict
  changes and nothing is promoted to reach a count; the key decides only whether
  the stage stops on an empty slate or shows what it found. The tiers are never
  merged, renumbered, or summed, the top-tier count is stated first even at zero,
  and no fallthrough card may be described as cleared or on the slate — those
  four rules are what keep this from being the deleted always-returns-items
  menu. A card taken forward from the fallthrough tier carries an acceptance
  record stating that it did not clear the threshold and why the author
  proceeded.
- `usable_min` is **the pilot's usability bar: one number for the whole run**,
  with the unit it counts named beside it (traders, cells, meetings, firm
  quarters). `idea-pilot` prints it in every report and every pilot script's
  comparison constant must equal it; a report without the line, or a script
  comparing against something else, is a **validation failure**. G1's Gate F
  refuses any card whose computed usable sample falls below it, at any score.
  Set it before the first pilot runs and never vary it per card: a card that
  needs a different bar is making a design argument, and that belongs in its
  binding-constraint line. Changing it mid-run is a gate decision, logged with
  `gate-log`, after which every earlier verdict is re-derived or the run reports
  both thresholds and says which cards were judged under which. Three gates read
  this key, so leaving it unset stops the run at the first deep layer rather than
  failing quietly.
- `min_tier` is obsolete and **replaced by `g1_threshold`**. A config still
  carrying `min_tier` is stale; delete the line. Note that `panel_reach` is
  uncalibrated, and that the calibration set is not all top-3: it carries a real
  contrast class, and every skill reads its per-class counts at run time rather
  than quoting a figure from any page. See `playbooks/gate-modes.md`.
- `gate_mode` decides who resolves the six judgment gates and session
  close: `human` (the author, the default) or `autonomous` (pre-specified
  per-gate rules, `auto-mode` log entries, disclosure in the paper). The
  rules live in `playbooks/gate-modes.md` next to the skill folders. A
  missing `gate_mode` key means `human`.
- Skills that need a key that is missing or blank stop and ask rather than
  guessing (in `human` mode) or PARK the project (in `autonomous` mode);
  see `playbooks/error-escalation.md` next to the skill folders.
