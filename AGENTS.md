# Research pipeline workspace

You are working in a self-contained research pipeline. This file governs the
whole folder. A paper project has its own `AGENTS.md` that governs its subtree.

## Read first

- `README.md` for what this is and how to start.
- `workflow/pipeline-design.md` is the canonical stage map: stages S0 to S8, the
  six human gates, and every machine gate. Do not restate its content elsewhere;
  link to it.
- `workflow/pipeline-guide.md` is the readable tour of the same thing.

## How to work here

- **When a request matches a skill, use the skill instead of improvising.** The
  skills encode rules that exist because the obvious approach fails in a specific
  way. `.claude/skills/` lists them.
- **Every path comes from `pipeline-config.md`.** No skill hardcodes a location.
  If you need a path, read the config key.
- **Search before asserting.** Never guess about novelty, prior literature, or
  whether data exists when a tool can check.
- **A machine gate is not advisory.** If a gate refuses, the stage does not
  proceed. Do not work around it, and do not weaken the check to make it pass.
- **Everything ships as a file.** A decision discussed and not written down is
  lost at the end of the session.
- **Say what is missing.** Where a fact is unverified, mark it
  `[MATERIAL GAP: ...]` rather than filling it from memory. A confident wrong
  number costs more than an admitted hole.

## The six human gates

G1 idea, G2 framing, G3 design freeze, G4 data calls, G5 what survives, G6 title
and overclaim. Between gates you run unattended. At a gate you stop, present the
artifacts, and wait. `gate_mode: autonomous` in the config pre-specifies some of
these; read `playbooks/gate-modes.md` before assuming a gate can be self-resolved.

Do not promote a card to fill a menu. A padded slate produces a weak paper, which
is the outcome the bar exists to prevent. When nothing clears, report what capped
each card and rework the funnel.

## Writing

Documentation and prose follow `references/writing-norms.md` and
`references/banned-words.md`. Plain and concrete, no promotional language, no em
dashes, no filler intensifiers. This applies to your own notes as much as to a
manuscript.

## Layout

```text
.claude/skills/     the skills that run
references/         shared inputs: calibration set, writing norms, journal standards
tools/              cost accounting, PDF rendering, literature search backend
workflow/           the stage map
gate-fixtures/      planted-failure suite for the machine gates
project-template/   copied per paper
docs/               design notes for extending the skill set
```

A paper project is a copy of `project-template/`. All of its files live inside
it. Do not scatter project files into this folder.

## Extending the pipeline

`docs/skill-specs.md` carries the per-skill writing spec: what each skill must
do, which gates it owns, and the failure it exists to prevent. Read it before
adding a skill or changing one substantially.

After changing a skill, run `python3 gate-fixtures/run_fixtures.py`. If a gate
lost a property, a fixture says which.
