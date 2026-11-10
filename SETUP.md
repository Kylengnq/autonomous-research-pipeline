# Setup

Everything here is stdlib Python plus a small analysis stack. Nothing needs an
API key to start.

## Requirements

- **Python 3.11 or newer.** The skills' own scripts are standard library only.
  A paper project needs an analysis environment; `project-template/requirements.txt`
  pins it.
- **Claude Code**, launched from this folder so `.claude/skills/` is discovered.
- **LaTeX** (`xelatex` or `pdflatex`) only if you build a manuscript. The pipeline
  runs to G1 without it.
- Network access for literature search. Everything else runs offline.

## 1. Verify the gates work

```bash
python3 gate-fixtures/run_fixtures.py
```

Expected: `100/100 fixtures behaved as declared`. This is the acceptance test for
the whole bundle. It resolves the skills directory by walking up from itself, so
it works wherever you put this folder.

If a fixture fails, the gate it names is not working on this machine. Fix that
before running a real pipeline: a gate that does not fire is worse than no gate,
because the run reports clean.

One fixture reaches a public API and reports `SKIPPED` when offline, which is not
a failure.

## 2. Literature search

Several skills refuse to run without a search backend: novelty checking,
citation verification, the literature review, and the calibration builder.

`.mcp.json` wires a keyless backend over public sources:

```json
{"mcpServers": {"corbis": {"command": "python3", "args": ["tools/free_corbis_mcp.py"]}}}
```

Claude Code reads that on start when launched from this folder. Confirm it loaded
by asking for a literature search and checking that results carry titles, years
and citation counts.

The backend resolves journal names against a public catalogue. It is written to
let transport errors surface rather than report them as "journal not found",
because the two are different and the second is a silent wrong answer.

## 3. A paper project

```bash
cp -r project-template my-paper
cd my-paper
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Then open `pipeline-config.md` and set, at minimum:

- `project_name`
- `theme`, one sentence. Set it for the themed path; omit it for the open swarm,
  whose deduplication is weaker.
- `usable_min`, one integer and the unit it counts, for example `200 firm-quarters`.
  Three gates read this and the run stops at the first deep layer without it.
  Fix one value for the whole run.
- `field_profile` and `gate_mode`.
- The three model tiers: `model_default`, `model_mid`, `model_strong`. They ship
  as placeholders, and they are not optional. The funnel runs its bulk work on
  `model_default` and reserves `model_strong` for adjudication and review, which
  is most of why a full run is affordable. Leave them unset and a skill has no
  model to delegate to.
- `budget.max_wall_clock`, if you want the run to stop on its own. It and
  `driver_context_ceiling` are the only two budget keys that are stopping rules;
  every other key in that block is a counter that reports and does not halt.
  There is no spend cap, so set the wall clock before an unattended run.

Worth knowing before the first run: `g1_threshold` and `g1_fallthrough` decide
whether a funnel that clears nothing ends PARKED or ARCHIVED. The defaults are
deliberate and most first runs clear nothing, which is the bar working rather
than a fault.

Paths in that file are relative to the project. `tools_dir` and `calibration_file`
point back up at this bundle, so keep the project inside it or set absolute paths.

## 4. The submission rail, if you need it

`project-template/submission/` and the three hooks in `project-template/.claude/`
record how much of the work was AI-driven: transcripts, subagent exports, human
time, gate decisions. Use it when a venue asks for that record; delete the
directory when it does not.

Two things to set first:

- **The eligibility floor.** `ELIGIBILITY_FLOOR` appears in all three hooks in
  `.claude/hooks/` and defaults to admitting everything. If your venue requires
  work to begin after a date, set it identically in all three.
- **`submission/call_requirements.md`** ships blank. Fill it from your venue's
  call before `/init-submission` runs; several skills read it.
  Replace it with your own; the compliance skills read the floor and deadline from it.

**Known limitation: you cannot have both the skills and the hooks in one
session.** The hooks register only when the project folder is the session's own
directory. The skills and the search backend load only from this bundle's root,
because that is where `.claude/skills/` lives and where `.mcp.json` resolves its
relative path. Those are different directories, so:

- Launch from the bundle root and you get all 41 skills and the search backend.
  The hooks never register, so nothing is recorded, and nothing errors.
- Launch from the project folder and the hooks record correctly. You lose the
  skills and the backend, which several skills refuse to run without.

The hooks themselves handle either case: `resolve_project_dir` finds the
project from its own path rather than trusting `CLAUDE_PROJECT_DIR`. The
constraint is Claude Code's hook registration, which is per session root.

Until this is resolved, run the pipeline from the bundle root and maintain the
contribution record deliberately: `/log-conversation` and `/log-human-time` write
the same files the hooks would, and `/finalize-compliance` reconciles them. The
record is then as complete, and you are the one keeping it current rather than
the hooks. Do not assume a silent hook is a working one.

## Troubleshooting

**Skills not found.** Claude Code must be launched from the folder containing
`.claude/skills/`. Check with `/help` that the skills are listed.

**A skill asks for `top_journal_calibration.json`.** It ships at
`references/top_journal_calibration.json`. If a project cannot find it, its
`calibration_file` key points somewhere else.

**The top tier is never awarded at G1.** That is often correct. It is also what
happens if the calibration file is missing, so check the file resolves before
concluding the ideas were weak.

**A fixture fails after you edit a skill.** That is the suite doing its job. The
fixture names the gate and the property that broke.
