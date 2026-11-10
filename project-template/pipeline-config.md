# Pipeline config

Every pipeline skill reads this file first, and no skill hardcodes a
path. Relative paths are relative to this project's root.

Set `project_name`, `theme` and `usable_min` before running S1. Full
documentation of every key, and the reason each default is what it is,
is in `../.claude/skills/pipeline-config.template.md`.

Generated from that template at build time. Edit the values here; edit
the template to change what keys exist.

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
tools_dir:        ../tools

# Ideation funnel (S1/S1b)
ideas_dir:        ideas
idea_pool:        ideas/pool.json
calibration_file: ../references/top_journal_calibration.json
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
