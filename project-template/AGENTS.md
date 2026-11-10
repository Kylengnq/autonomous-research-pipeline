# <project name>

One paper, produced end to end by the S0-S8 pipeline. The folder above owns the
shared machinery (`references/`, `tools/`, `.claude/skills/`). This file governs
everything inside this project, and every file and datum for this paper lives
here.

## Before anything else

Set these in `pipeline-config.md`:

- `project_name`
- `theme`, one sentence. Present means the themed path; absent means the open
  swarm, whose deduplication is the weaker layer.
- `usable_min`, one integer and the unit it counts. Three gates read it and the
  run stops at the first deep layer without it. One value for the whole run.

Then hand control to `/run-pipeline`, which drives S0 to S8 and stops at each
human gate.

## The two rails

1. **Research** — the pipeline itself, six human gates, machine gates inside
   stages. Config: `pipeline-config.md`.
2. **Compliance** — `submission/`, plus the hooks in `.claude/`. Only needed when
   a venue asks for a record of how much of the work was AI-driven. Delete
   `submission/` and `.claude/hooks/` if yours does not.

If you are running the compliance rail, launch Claude Code **from this
directory**. The hooks register only when this project is the session's own
project directory. Started from anywhere else they never fire, nothing is
written, and no error appears: they are written to fail closed and exit 0, so an
unrecorded session looks exactly like a recorded one.

## Layout

```text
notes/          STATE.md (canonical state), decisions.md, lab_notebook.md
ideas/          the S1 funnel's cards, pool and profiles
output/         results JSON, figures, logs, the script registry
scripts/        registered data and estimation scripts
analysis/       registered analysis scripts
paper/          main.tex, references.bib
reviews/        adversarial review packets
data/           held data and its manifest. Never committed
build/          generated LaTeX values and the PDF
submission/     the compliance record, if the venue wants one
```

## Standing rules

- **Read first in every session.** `/resume` does this and
  produces a five-line brief. It is the canonical state; the lab notebook is the
  narrative.
- **Every script is registered** through `script-registry` with its purpose,
  inputs, outputs and packages. An unregistered script that produced a number in
  the paper is a reproducibility hole.
- **No number is typed into the manuscript.** Numbers reach the paper as
  generated macros through `paper-build`, so a changed estimate cannot leave a
  stale figure in the text.
- **No estimate before the pre-registration is committed.** `run-analysis`
  refuses without it, and that refusal is the point.
- **Log gate decisions** with `/gate-log` as they are made, not afterwards.
