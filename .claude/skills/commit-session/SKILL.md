---
name: commit-session
description: "Commit the session's work with a structured message and a Co-Authored-By: Claude trailer, so AI-authored work is marked in version control and the contribution report is reproducible from git rather than from conversation logs. Commit once per session; optionally tag a version. Run at the end of a session, after /handoff."
---

# Commit Session

Make per-session, attributed commits so version history is real. The prior project had two commits
total, which made `/contribution-report` fall back to "everything is AI" and meant "versions" existed
only as transcripts and hand-typed `v1.x` notes. A `Co-Authored-By: Claude` trailer on each
AI-driven commit lets the contribution report key off the trailer and lets versions be tags.

## When to use

- Ending a working session (after `/handoff`).
- Reaching a milestone worth tagging (first full draft, submission candidate).

## Convention

- **One commit per session**, on a non-default branch when the work is substantial.
- Message body: the stage(s) touched and the deliverables, in the project's terse style.
- **Trailer**, always, for AI-driven work:
  `Co-Authored-By: Claude <noreply@anthropic.com>`
- A purely human-typed commit omits the trailer; that is how the contribution report tells them
  apart.
- Tag milestone snapshots (`v0.1`, `v1.0`, `submission-candidate`) so the contribution report and the
  paper can be pinned to a reproducible state.

## Workflow

1. `git status` / `git diff --stat` to review what changed. Confirm no credential or large data blob
   is being committed (respect `.gitignore`; data lives outside git where the call permits).
2. Stage the intended files.
3. Write the message: a one-line summary, then a short body listing stage + deliverables.
4. Append the `Co-Authored-By: Claude <noreply@anthropic.com>` trailer for AI-driven work.
5. Commit. If this is a milestone, `git tag` it.
6. Note the commit/tag in.

## Outputs

- A commit (optional tag) on the current branch.
- A pointer.

## Validation

- Never commit credentials or proprietary data; scan the diff first.
- Confirm the branch is not the protected default before committing substantial work; branch if so.
- The trailer is present exactly for AI-driven commits, absent for human-only ones, so
  `/contribution-report` can attribute by trailer.
