---
name: contribution-report
description: "Regenerate submission/contribution_report.md with current line-count tallies for code, writing, and documentation, split by human and AI authorship. Run before the submission submission."
---

# Contribution Report

Regenerates the submission contribution tally. The call requires "a report on the
fraction of project lines (code, writing, and documentation) that were
contributed by humans as opposed to AI." This skill produces that report.

## When to use

- The user is preparing the final submission package.
- The user wants a checkpoint snapshot mid-project.
- The user explicitly asks for a contribution report or human-vs-AI split.

## Inputs to collect

| Input | Required? | Default |
|---|---|---|
| AI attribution method | Yes | Default: the `Co-Authored-By: Claude` commit trailer (written by `/commit-session`). Fallback: regex over `git log --format=%ae`, default `(agent|claude|gpt|codex|bot)@`. |
| Human authors | Yes | List of names/emails that count as human |
| Code globs | No | `**/*.py`, `**/*.R`, `**/*.do`, `**/*.sas`, `**/*.sql`, `**/*.ipynb` |
| Writing globs | No | `paper/*.tex`, `paper/**/*.tex` |
| Documentation globs | No | `*.md`, `notes/**/*.md`, `submission/**/*.md`, `references/**/*.md` |
| Cutoff date | No | submission date or HEAD |

## Steps

1. Confirm `submission/initial_prompt.md` exists and has a date on or after
   the venue's eligibility floor, declared in `submission/call_requirements.md`. If
not, refuse and ask the user to run `/init-submission` first.
2. For each category (code, writing, documentation), run:
   - `git log --no-merges --since=<initial_prompt date> --pretty=format:'%H %ae %ad %(trailers:key=Co-Authored-By)' --date=iso -- <globs>` to enumerate commits and their trailers.
   - `git blame --line-porcelain -- <file>` for each file matched by the globs
     to attribute every surviving line to a commit.
   - Classify each commit as AI-driven if it carries a `Co-Authored-By: Claude` trailer
     (the `/commit-session` convention); otherwise human. Fall back to the committer-email
     regex only for repos predating the trailer convention. If the repo has only one or two
     commits, attribution from git is impossible — say so explicitly and fall back to the
     conversation-log method rather than reporting a false ~100% AI or ~100% human split.
3. For writing, additionally word-count `paper/*.tex` body text (between
   `\begin{document}` and `\bibliography`). If AI authorship is recorded via
   commits, use that; otherwise ask the user to estimate the AI share by
   checking the conversation log under `submission/conversations/`.
4. Cross-check against `submission/conversations/`: if a conversation file's
   "Outputs" section lists a file path, treat lines from that conversation's
   commits as AI-authored unless explicitly flagged in **Human interventions**.
5. Populate the headline table in `submission/contribution_report.md` with the
   counts, totals, and human-share percentages.
6. Rewrite the **Method** section to reflect the actual globs, committer
   pattern, and any heuristics used.
7. Surface edge cases in the **Edge cases** section: ghost-written text the
   human typed but the AI suggested, AI-generated tables pasted verbatim, large
   mechanical refactors. Ask the user to confirm classifications it cannot
   infer.
8. Append a dated entry to summarizing the headline
   numbers.

## Outputs

- Updated `submission/contribution_report.md`.
- Entry in.

## Validation

- Refuse to run if there are uncommitted changes (`git status --porcelain` is
  non-empty); the report should reflect a committed state. Ask the user to
  commit first.
- Warn if the human share is below 5% or above 95% — either extreme is worth
  the user double-checking the committer attribution.
- Note that the absolute split alone is not a quality signal: the contribution record
  prizes "highest possible research quality per unit of human expertise and
  effort," not a minimal human share.

## Next steps to suggest

After regenerating the report, explicitly tell the user what to do next:

1. **If the report ran cleanly**: "Contribution report regenerated. Walk through the rest of the `submission/` checklist in `submission/README.md` — confirm `workflow.md`, `conversations/`, and `human_time_log.md` are all current."
2. **If edge cases were flagged**: "Some classifications were ambiguous (see the Edge cases section). Resolve them by either adjusting the committer attribution convention or by annotating the edge cases with your manual classification."
3. **Approaching submission deadline**: "Run `/verify-citations` on the final `.bib` and confirm the LaTeX appendix sections A-D match the artifacts under `submission/`. Then commit and prepare submission."
4. **Always remind**: "Log this contribution-report run with `/log-conversation` and the time reviewing the output with `/log-human-time`."
