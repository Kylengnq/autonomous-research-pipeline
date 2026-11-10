# Skills Guide

How to use the eleven workflows in this the submission submission template. In Claude
Code, they are available as slash commands. In Codex, Cursor, and other MCP
clients, use the same workflow names and examples below as prompt templates.

## Running the skills

Claude Code discovers the skills automatically when launched from the folder
holding `.claude/skills/`. There is no install step. Type a skill's name as a
slash command (`/init-submission`, `/brainstorm <topic>`, `/idea <question>`,
and the others below). Literature search needs an MCP backend: the keyless shim
is wired in `.mcp.json`. Output templates are indexed in
[`TEMPLATES.md`](TEMPLATES.md).

## Which skill to use

### the venue submission skills

| I want to... | Skill / Command |
|---|---|
| Set up the venue submission package on day one | `/init-submission` |
| Capture a verbatim AI conversation transcript | `/log-conversation` |
| Log a block of direct human work | `/log-human-time` |
| Recompute the human-vs-AI contribution tally | `/contribution-report` |

### Calibration

| I want to... | Skill / Command |
|---|---|
| Build the top-3 journal anchor for idea screening | `/calibrate-rubric` |
| Refresh the anchor (every ~6 months) | `/calibrate-rubric` |

### Research skills

| I want to... | Skill / Command |
|---|---|
| Survey what a field knows about a topic | `/lit-review` |
| Find the closest papers to my idea and sharpen the contribution | `/lit-search` |
| Generate research ideas in a topic area | `/brainstorm` |
| Evaluate whether a specific idea is worth pursuing | `/idea` |
| Check that my citations are correct and complete | `/verify-citations` |
| Visualize trends, gaps, and methods in a literature | `/lit-landscape` |

## First-time setup

The skills depend on each other. Run them in this order on day one:

```text
1. /init-submission         # captures the initial prompt + model config under submission/
2. /calibrate-rubric        # builds the top-3 journal calibration anchor (~5-10 min, one-time)
3. /brainstorm <topic>      # or /idea <specific question> if you already have one
```

`/calibrate-rubric` is the step most people miss. Without it, `/brainstorm` and `/idea` still run, but they cap the verdict at Strong Field Candidate — they cannot certify an idea against the top-3 journal frontier.

Do not run `/init-submission` for a real project before. The the venue
call requires the investigation to begin on or after that date with the initial
AI prompt. The local call checklist is
`submission/call_requirements.md`.

## The submission workflow (run continuously)

These run throughout the project, not as a one-time setup:

```text
After every AI conversation     -> /log-conversation
After every block of human work -> /log-human-time
At submission time              -> /contribution-report
```

Pair them with the research skills, not in place of them.

## Common research workflows

**Starting from a vague topic:**
1. `/lit-review [your topic]` — understand the field
2. `/brainstorm [your topic]` — generate 10 ranked ideas with gate verdicts
3. `/idea [best candidate from brainstorm]` — screen the chosen idea rigorously

**Starting with a specific question:**
1. `/lit-search [your paper's question]` — find closest work
2. `/idea [your idea]` — score and stress-test it against the calibration set

**Visualizing a literature:**
1. `/lit-review [your topic]` — build the paper set
2. `/lit-landscape [your topic]` — generate trend and gap figures

**Polishing citations:**
1. `/verify-citations` — audit your `.bib` against Corbis

**Reading a paper:**

If your assistant supports repo-defined agents, use the paper-reader prompt:
> "Read and summarize the paper at ~/Downloads/fama_french_1993.pdf"

## Key concepts you'll see in the output

`/brainstorm` and `/idea` use terms that aren't standard finance vocabulary:

- **Displacement target.** What an idea would render wrong if it succeeds. Must be one of four concrete categories with a falsifiable counterfactual: (1) a named paper, (2) a model claim, (3) an empirical regularity, or (4) a maintained assumption / measurement convention / decision-relevant belief (this last category requires citing evidence the assumption is held and naming a specific alternative). Ideas without a concrete target cap at Strong Field Candidate.

- **Calibration set.** `references/top_journal_calibration.json`, built by `/calibrate-rubric`. ~40 recent JF/JFE/RFS acceptances and ~40 stalled SSRN analogs, each tagged with question, mechanism, identification style, and displacement target. The external anchor for tier labels.

- **Archetype parity.** For each top-tier candidate, the skill pulls 3 accepted and 2 stalled analogs from the calibration set. Below parity on all dimensions of all three accepted → tier downgrade. Can't differentiate from a stalled analog → tier downgrade.

- **Top-tier novelty audit.** Before issuing a Top Generalist Candidate, the skill fires one final fresh Corbis search scoped to the candidate's displacement target + mechanism (Phase 6.5a in `/brainstorm`, Stage 3.5a in `/idea`). A near-duplicate caps the verdict at Strong Field Candidate.

- **Novelty confidence tag (rule-based).** Every verdict carries High / Medium / Low confidence, determined by paper_set coverage, calibration mechanism match, and number of targeted searches that ran. **Low confidence automatically caps the verdict at Strong Field Candidate.** This is not LLM self-assessment — the thresholds are explicit in the skill files.

- **Three-editor desk-reject.** Before issuing a Top Generalist Candidate, the skill writes desk-reject letters from three functional editor archetypes in parallel: an identification skeptic (mandatory), an incrementality skeptic (mandatory), and a third chosen by the candidate's type (mechanism skeptic, general-interest skeptic, or execution skeptic). 2+ convincing → tier downgrade; 3 of 3 → two-tier downgrade.

- **Failure-mode benchmarking.** Stalled papers in the calibration set are tagged with up to 2 of 8 failure modes (setting variation only, unclear mechanism, weak identification, no displacement target, incremental data extension, hard-to-interpret null, insufficient external validity, execution too complex). To clear the differentiation gate, the candidate must show it has *fixed* the dominant failure mode of comparable stalled analogs — not merely avoid sharing it.

- **Lens-source discipline.** Ideas come from 11 generative lenses. ≥2 of the top 3 must come from Lens 1 (practitioner gap), Lens 3 (first principles), Lens 4 (unification), Lens 5 (policy shock), Lens 8 (mechanism decomposition), or Lens 9 (boundary conditions). Lens 10 (new data × old question) is hard-capped at Strong Field.

- **Minimum viable empirical test (MVE).** For every Top Generalist or Strong Field Candidate, `/idea` produces a 9-field block specifying the dataset (must cite `output/paper_set.json` or a `search_datasets` result — no hallucinated data), unit of observation, treatment, outcome, first-stage variation, falsification test, robustness test, what can be checked in 48 hours, and what would kill the project. Missing or free-form data → tier downgrade.

- **Wildcard slot in `/brainstorm`.** Reserved for one candidate that failed exactly one gate but has high upside if reframed. Labeled "WILDCARD — not gated, requires re-screening before promotion." Cannot be promoted to Top Generalist Candidate without re-running every gate.

- **Human override.** After Kill or Revise verdicts in `/idea`, the user can invoke a disciplined override path: name the private information, name the gate being challenged, file a falsifiable validation deadline (≤ 90 days). Auto-reverts to the model verdict if validation evidence is not filed by the deadline.

- **Hierarchical gates.** Tier labels are determined by gates passed, not by a smoothed total score. Importance ≥ 4 → Contribution ≥ 4 → Bridge ≥ 4 → displacement named → archetype parity → fresh-search novelty audit → desk-reject survival → confidence ≥ Medium. Failing any caps the verdict.

- **Three tiers.** The labels use *Candidate*, not *Go* — a screening pass, not a publishability prediction.
  - *Top Generalist Candidate* — has the structure of an idea that recent JF/JFE/RFS papers cleared. All gates cleared, confidence ≥ Medium.
  - *Strong Field Candidate* — solid idea, one or more gates failed, or Low confidence.
  - *Workshop* — feasible but narrow scope, falls below Strong Field gates.

- **Idea lineage.** Every `/idea` run writes a dated directory at `ideas/<date>_<slug>/` containing `idea_card.md`, `gate_scores.json`, and `desk_rejects.md`. This accumulates an audit trail over time — which gates kill projects, which lenses produce winners, how ideas evolved through re-screening.

## Notes

- Literature reviews produce BibTeX citations automatically via `export_citations`.
- Results are saved to `notes/` and `output/`; lab notebook entries are appended automatically.
- the venue documentation is saved under `submission/` and is the primary submission artifact.
- `submission/call_requirements.md` maps the call rules to the files the skills maintain.
- The Corbis MCP is the literature search engine; expect 15-25 Corbis calls per `/brainstorm` run, 4-8 per `/idea` run after the efficiency upgrades.
- If your client reads `CLAUDE.md` and `.claude/` directly, it routes requests automatically. Otherwise use the tables above as the manual workflow guide.
