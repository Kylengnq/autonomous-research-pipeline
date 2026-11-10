# Skill-authoring guide

How to construct skills for this repo so the agent discovers and uses them reliably. It merges
Anthropic's official skill-authoring best practices with the agent-skills research literature (see
`output/literature_review_claude_code_research.md`) and this repo's own conventions. Read this before
adding or editing a skill; the finance-domain norms a research skill must enforce live in
[finance-research-practice.md](finance-research-practice.md).

## The model: progressive disclosure

A skill is a directory with a `SKILL.md`. Only the frontmatter `name` + `description` are preloaded
into the agent's context; the body is read when the skill is triggered, and bundled files are read
only when referenced. So:

- The **description does the discovery work** (it competes with 20+ other skills' descriptions).
- The **body is the procedure** and must earn every token.
- **Bundled reference files / scripts cost nothing until read** — push detail out of the body into
  one-level-deep files.

This is the "harness" construct the literature treats as the primary lever for agent effectiveness
(De Macedo 2026 on what makes a harness; Xin et al. 2026 on environment engineering): the skill is a
unit of the harness, and its quality, not the model's, sets the ceiling.

## Frontmatter rules

```yaml
---
name: <lowercase-hyphen, <=64 chars, no "anthropic"/"claude", no XML>
description: "<third person. What it does + WHEN to use it, with key trigger terms. <=1024 chars>"
---
```

- **Name:** gerund or noun-phrase, specific. Good: `pre-register`, `claim-ledger`, `robustness-suite`.
  Avoid `helper`, `utils`, `tools`.
- **Description (the single most important field):** always third person ("Builds...", not "I can
  help..."). State *what* and *when*, and pack in the words a user would actually say so the agent
  triggers it. Compare the repo's skills: each description names the artifact it writes and the stage
  it belongs to. A vague description is the top cause of a skill never firing.

## Body rules

- **Keep it under ~500 lines.** Past that, split into one-level-deep reference files linked from
  SKILL.md (never nest references two deep; the agent may only partially read nested files).
- **Assume the model is smart.** Cut explanations of things Claude already knows (what a 10-K is,
  what clustering is). Add only what is specific to *this* repo or task. Every paragraph must justify
  its tokens.
- **One consistent term per concept.** Pick "results JSON" or "results file", not both.
- **No time-sensitive text** ("before August..."); put superseded approaches in an "old patterns"
  aside.
- **Forward slashes** in all paths; reference the repo `.venv/bin/python` for scripts.

## Degrees of freedom: match specificity to fragility

| Freedom | Use when | Form |
|---|---|---|
| High | many valid approaches, context-dependent | prose steps (e.g. `lit-review` synthesis) |
| Medium | a preferred pattern with variation | a template / parameterized script (e.g. `draft-paper` table generation) |
| Low | fragile, must-be-exact, high-stakes | "run exactly this command" (e.g. `claim-ledger` validation; `data-pipeline` detached-orchestrator) |

A finance estimation that must not be silently re-specified is low-freedom; a positioning memo is
high-freedom. The 2026 evidence is that agents systematically under-comply with scaffolds (Ding et
al. 2026, OctoBench), so for the steps that matter, be explicit and gate them, do not trust default
compliance.

## House conventions (what makes a skill an *the venue-harness* skill)

These are this repo's additions on top of the generic best practices. A research skill should:

1. **Leave a verification artifact.** Every deliverable skill writes something inspectable (results
   JSON, search log, a verdict, a ledger). This is the literature's central anti-"claim drift" move
   (Wang et al. 2026): trust is externalized into artifacts, not inferred from prose.
2. **Gate before adoption (skills as hypotheses).** A skill that produces a measure or a finding
   carries a validation gate it must pass before its output is used — the pattern in
   `text-measure-builder` (correlation/monotonicity/time-profile) and `robustness-suite`. Treat a
   skill's output as a hypothesis to be checked, not a fact (Wu et al. 2026, Bayesian-Agent; Liu et
   al. 2026, SkillsVote).
3. **Run a feedback loop for quality-critical output.** Validator -> fix -> repeat, with an explicit
   "only proceed when it passes" (e.g. `claim_ledger.py validate` exiting 0 before `draft-paper` is
   done; the compile gate). Surface a plan-validate-execute step for batch or destructive operations.
4. **Log to the shared state.** Append to `notes/lab_notebook.md` (one dated entry per deliverable)
   and, for literature work, `output/search_log.md`; merge into `output/paper_set.json`, never
   overwrite.
5. **Name its human gate, if any.** If the stage involves an author decision (idea, framing, design,
   data, survival, title), route it to `/gate-log`. The gate is both the reliability lever and the
   the venue "human labor" exhibit (Zhu et al. 2026).

## Utility scripts (when a skill bundles code)

- **Solve, don't punt:** handle the error in the script, don't fail and let the agent improvise.
- **No voodoo constants:** justify every threshold in a comment (a cosine cutoff, a winsorize bound).
- **Make execution intent explicit:** "run `scripts/x.py`" (execute) vs "see `scripts/x.py` for the
  algorithm" (read). Prefer execution; it is more reliable and token-cheap.
- **List dependencies** and use the repo `.venv`. Stdlib-only where possible (the `claim_ledger.py`
  validator is stdlib).

## Build evals first, then iterate with Claude

Anthropic's strongest recommendation: write the evaluation before the skill. Run the task *without* a
skill, note where the agent fails, write 2-3 concrete scenarios that capture those gaps, then write
the minimum instructions that pass them. Iterate by using the skill on a real task ("Claude B"),
watching where it strays, and refining. Test across the models you'll run (Haiku needs more guidance
than Opus). This is the empirical answer to the literature's finding that implementation, not
ideation, is the binding constraint (Zhu et al. 2025): a skill is only as good as the gaps it
demonstrably closes.

## SKILL.md template (house style)

```markdown
---
name: <lowercase-hyphen>
description: "<third person: what + when, with trigger terms>"
---

# <Title>

<1-3 sentence purpose: what it produces and the failure it prevents.>

## When to use
- <trigger>
- <trigger>

## Principles            (optional; the non-obvious rules)
- <...>

## Workflow              (numbered steps; checklist for complex ones)
1. <...>

## Outputs
- <the verification artifact(s) + lab-notebook entry>

## Validation
- <the gate(s) that must pass; "do not proceed until ...">
```

## Authoring checklist

- [ ] Description is third person, specific, and says what + when with trigger terms.
- [ ] Body under ~500 lines; detail in one-level-deep files.
- [ ] No content the model already knows; consistent terminology; no time-sensitive text.
- [ ] Degrees of freedom matched to fragility; fragile steps are explicit and gated.
- [ ] Leaves a verification artifact and a lab-notebook entry.
- [ ] Has a validation gate / feedback loop for quality-critical output.
- [ ] Routes any author decision to `/gate-log`.
- [ ] Scripts: solve-don't-punt, no magic constants, forward slashes, `.venv`, deps listed.
- [ ] At least one concrete eval scenario in mind; tested on a real task.
- [ ] Registered in `CLAUDE.md` (routing table + pipeline ordering if applicable).

## When NOT to add a skill

If the task is a one-off, or the agent already does it well without guidance, do not add a skill —
context is a public good and every description competes for discovery. Add a skill only when you have
seen the agent repeatedly need the same context or repeatedly fail the same way.
