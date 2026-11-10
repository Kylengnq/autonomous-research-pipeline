---
name: code-sweep
description: "End-of-milestone audit of the code folder against the replication manifest and disk: scripts not in the registry, registry entries whose file is gone, declared outputs missing on disk, outputs older than the script that produces them (stale), scripts with no docstring, and TODO/FIXME. Run at milestones and before submission to catch reproducibility drift. Uses the script-registry skill's registry.py audit."
---

# Code Sweep

Catch the silent drift that accumulates over a long project: a script whose output was never
regenerated after the code changed, a new script nobody registered, a results file that a table cites
but that no longer exists. This is the reproducibility counterpart to `/robustness-suite`: it audits
the code-and-data package, not the findings.

## When to use

- At the end of a milestone (a finished data build, a results refresh, a draft).
- Before submission, as a final reproducibility gate.
- After a results refresh, to find tables that now cite stale or missing outputs.

## Workflow

1. Ensure the manifest is current: run `/script-registry` (its `build` step) first.
2. Run `<python> <skill_dir>/scripts/registry.py audit --registry <registry_file>
   --dirs <scripts_dirs>`, taking `python`, `registry_file` and `scripts_dirs`
   from `pipeline-config.md` and `<skill_dir>` as the `script-registry` skill's
   own directory. It reports:
   - **NEW** scripts on disk not in the registry (manifest is stale).
   - **REMOVED** registry entries whose script file is gone.
   - **MISSING OUTPUTS** declared by a script but absent on disk (a broken replication step).
   - **STALE OUTPUTS** whose file is older than the script that writes it (the output predates the
     current code, so a number in the paper may be from old code).
   - **NO DOCSTRING** scripts, and **TODO/FIXME** counts.
   It exits non-zero on real drift (new unregistered scripts or missing outputs).
3. Resolve each finding: re-run the producing script to refresh a stale/missing output, register or
   delete a stray script, add a docstring, close or document a TODO.
4. Re-run until it passes. A clean sweep means every declared output exists and is at least as new as
   its code.
5. Lab-notebook entry at submission-prep.

## Outputs

- The sweep report (stdout).
- A entry noting the clean sweep before submission.

## Validation

- Before submission, the sweep passes (no new/unregistered scripts, no missing outputs).
- Stale outputs are regenerated or explicitly justified; a paper number must not come from code older
  than the output.
- Run after `/claim-ledger`: the ledger checks numbers trace to a results JSON; the sweep checks that
  results JSON is current with its producing code.
