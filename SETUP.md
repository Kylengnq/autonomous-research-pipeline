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

The hooks only register when the project is the session's own directory. Launch
from the project folder, not from this one, or nothing is recorded and nothing
errors.

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
