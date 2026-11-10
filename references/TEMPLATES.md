# Templates Index

Quick map of scaffolds in this repo. Copy or let skills fill them in; do not
edit the originals in place.

## Paper and submission

| Template | Path | Use |
|----------|------|-----|
| LaTeX manuscript | Built by `paper-build` into `paper/main.tex` | No standalone template ships; the skill scaffolds the document |
| Submission call checklist | `submission/call_requirements.md` | Compliance map (fill during `/init-submission`) |
| Initial prompt, model config, data access | `submission/initial_prompt.md`, `model_config.md`, `data_access.md` | Populated by `init-submission` |
| Conversation index | `submission/conversations/README.md` | One transcript per AI session |

## Skill output scaffolds

| Template | Path | Produced by |
|----------|------|-------------|
| Idea menu | `.claude/skills/research-idea-generator/assets/idea-menu-template.md` | `research-idea-generator` |
| Idea card + gates | `.claude/skills/finance-idea-screening/assets/idea-card-template.md` | `finance-idea-screening` |
| Literature positioning matrix | `.claude/skills/literature-positioning-map/assets/literature-matrix-template.md` | `literature-positioning-map` |
| Reading list | `.claude/skills/literature-review/assets/reading-list-template.md` | `literature-review` |

Assets live beside the skill that produces them, under
`.claude/skills/<skill>/assets/`.

## Shared data (created by skills, not shipped empty)

| File | Role |
|------|------|
| `output/paper_set.json` | Deduplicated Corbis paper cache across skills |
| `output/search_log.md` | Transparency log of every search query |
| `references/top_journal_calibration.json` | Held-out JF/JFE/RFS anchor from `/calibrate-rubric` |
| `ideas/<date>_<slug>/` | Per-idea lineage from `/idea` |

## Discovery

Claude Code finds the skills automatically when launched from the folder holding
`.claude/skills/`. No install step and no plugin manifest.
