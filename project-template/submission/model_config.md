# Model Configuration

Every model, agent, and tool the project used. Reviewers use this to judge how
much of the workflow was AI-driven, so the stage table below is the part that
carries weight.

Keep this current as the project runs. A configuration written once at kickoff
and never revised will misstate the work, because model choices change mid-project.

## Primary models

| Model ID | Role | Version / date | Reasoning / temperature | Context window |
|---|---|---|---|---|
| | | | | |

If the model changed mid-project, add a row per model and say when and why the
change happened. A single pinned row that was not true throughout is a
misstatement, not a simplification.

## Agents and roles

| Agent | Responsibility | Backing model |
|---|---|---|
| | | |

## AI role by stage

The call asks that AI play a systematic role across multiple stages, not only
modular tasks. Cover every stage the project reached; write "not reached" rather
than deleting a row.

| Stage | Models / agents used | AI responsibilities | Human controls or review |
|---|---|---|---|
| idea | | | |
| literature | | | |
| design | | | |
| data | | | |
| analysis | | | |
| robustness | | | |
| writing | | | |
| revision | | | |
| submission-prep | | | |

## MCP servers and tools

| MCP server | URL / endpoint | Tools used |
|---|---|---|
| | | |

## Skills and slash commands

| Skill | Purpose | Dates used | Conversation links |
|---|---|---|---|
| | | | |

## Autonomy

Any stretch the workflow ran without human intervention: what decided, what was
pre-specified, and what the human would otherwise have decided.

| Started | Ended | Agent / model | Ceiling | Artifacts | Transcript |
|---|---|---|---|---|---|
| | | | | | |

## Settings and budgets

- (rate limits, concurrency rules, anything that shaped how the work ran)
- (spend ceilings or stopping rules, and whether they fired)

## Reproducibility notes

- **Interpreter**: `Python 3.12.13`, in the project virtualenv at `.venv/`, which is what
  the `python:` key in `pipeline-config.md` resolves to. Every registered
  script, the pilot library, the gate fixtures and `make verify` run through it.
  `.venv/` itself is gitignored; the pins below are committed.
- **Rebuild the environment**:

  ```bash
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  ```

  `requirements.txt` names the direct dependencies; `requirements.lock.txt` is
  the full `pip freeze` taken when the environment was built. Reproduce
  exactly from the lock file, not from `requirements.txt`.
- **Direct dependencies as pinned**:

```text
  pandas==3.0.5
  numpy==2.5.2
  scipy==1.18.0
  statsmodels==0.14.6
  linearmodels==7.0
  matplotlib==3.11.1
  requests==2.34.2
  yfinance==1.6.0
  pyarrow==25.0.1
```

- **Random seed**: `seed: 20260818`, frozen in `pipeline-config.md` and read by
  every script that draws. It is set in one place so a rerun is a rerun rather
  than a new draw.
- **Caching**: literature search results land in `output/paper_set.json` and
  `output/search_log.md`, and data crawls checkpoint to `data/`, so a rebuild of
  the analysis does not re-hit external APIs. Note the boundary that
  `submission/reproduction.md` states: `make verify` covers estimation through
  the PDF, and **not** the crawls, which sit outside the build graph by design.
