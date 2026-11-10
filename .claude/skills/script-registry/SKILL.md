---
name: script-registry
description: "Builds and audits the replication manifest: per script its purpose, inputs, outputs, and packages; audit mode fails on unregistered scripts, missing or stale outputs, and missing docstrings. Reads inputs and outputs from the build graph when one exists, and decides staleness by content hash rather than mtime. Run during data construction, at milestones, and before submission."
---

# Script Registry

One manifest of what every pipeline script does and which files it touches,
so any output traces back to the code that produced it and the project
ships a real replication package. Three modes in one skill: build writes the
manifest, stamp records which script produced which output, audit checks it
all against disk.

## When to use

- During data construction, as scripts are added (build).
- At milestones and before submission (audit).
- At session start, and before committing work that touched a script, to
  catch an edit that was never rerun (audit).
- When a continuation session needs to know which script writes which file.

## Workflow

1. Read `pipeline-config.md` for `python`, `scripts_dirs`, `registry_file`,
   `results_dir`. `<skill_dir>` below is this skill's own folder (the
   directory containing this SKILL.md).
2. **Build:** run
   `<python> <skill_dir>/scripts/registry.py build --dirs <scripts_dirs> --out <registry_file>`.
   Per script it records: the docstring purpose, heuristically detected
   inputs, outputs, and referenced files, third-party packages, non-blank
   LOC, and TODO/FIXME count. It also writes a readable `.md` table next to
   the JSON.
3. **Curate, or let the build graph do it.** The extractor reads
   string-literal paths only; paths built from config constants or `Path`
   joins are invisible to it. Two ways to fix that, in order of preference:
   - **From the Makefile.** If the project has a build graph
     (`paper-build`), add `--makefile <path>`. Every script owned by an
     explicit rule takes its inputs from that rule's prerequisites and its
     outputs from its targets, and is marked `declared_by: makefile`. The
     graph is a dependency declaration that also executes, so it cannot
     quietly disagree with what the build does; hand curation can. Rules
     with no single owning script are skipped for curation.
   - **By hand,** for the load-bearing scripts the graph does not cover
     (data build, one-off extracts): fill in the true inputs and outputs and
     correct misclassified entries.
   The resulting JSON is the manifest.
4. **Rebuild with `--merge`.** After the first curation pass, every
   rebuild adds `--merge` (`--makefile` again, if used): entries already
   in the registry keep their curated purpose, inputs, outputs, and
   referenced files while mechanical fields (LOC, TODO count, packages)
   refresh from the scan. Makefile-declared entries are the exception:
   their inputs and outputs re-read from the graph every time, since a
   hand-edit that disagrees with the graph describes a build that does not
   happen. A script that leaves the graph is reported and falls back to
   curation. New scripts are appended as scanned; entries whose file has
   vanished are kept so the audit surfaces the retirement decision. A plain
   `build` on a curated registry clobbers the curation — never run it
   after step 3.
5. **Stamp after a good build:** run
   `<python> <skill_dir>/scripts/registry.py stamp --registry <registry_file>`.
   It records, per entry, a hash of the script's parsed code and a hash of
   each declared output. Run it when the outputs on disk were just produced
   by the scripts on disk; `make check` does this for you, right after
   `make verify`'s clean rebuild, which is the moment the pairing is known
   good. Stamping a state you did not build launders staleness rather than
   recording it.
6. **Audit:** run
   `<python> <skill_dir>/scripts/registry.py audit --registry <registry_file> --dirs <scripts_dirs>`.
   It exits nonzero on: scripts on disk missing from the registry, registry
   entries whose file is gone, declared outputs missing on disk, and stale
   outputs. It warns on missing docstrings and TODO/FIXME counts.
   **Staleness by hash, not mtime.** With stamps recorded, an output is
   stale when its producing script's code hash has changed while the output
   has not: the script was edited and never rerun. This survives a fresh
   clone, where git gives every file the checkout time and mtime ordering
   is meaningless. The hash covers the parsed tree, so comments, docstring
   wording, and reformatting do not raise a false alarm. Without stamps the
   check falls back to mtime and says so. An output that changed while its
   script did not is a warning, not a failure: an input may legitimately
   have moved, but so may someone have hand-edited a generated file.
   The audit is most useful **standalone** — at session start, or before
   committing work that edited a script without rerunning it. Inside
   `make check` the artefacts were just rebuilt, so what it earns there is
   the unregistered-script and missing-output checks.
7. On audit failure, fix the drift (register the script, rebuild the
   output, or retire the entry) and re-run until exit 0. A stale output is
   fixed by rerunning its producer, never by re-stamping.
8. The manifest feeds the paper's data-availability statement; `audit`
   also prints a replication-README section generated from the manifest.

## Outputs

- `registry_file` (JSON, committed) and its `.md` table. The stamps travel
  in it, which is what makes staleness answerable in a fresh clone.
- Audit report on stdout; exit code is the gate.
- A dated `lab_notebook` entry at milestones.

## Validation

- Every load-bearing script has a curated purpose and inputs/outputs.
- Audit exits 0 before a milestone commit or submission.
- Raw heuristic output is never treated as final; curation is a required
  step.
- Stamps are recorded only after a build that produced the outputs on disk.
- Every rebuild after the first curation pass uses `--merge`; a curated
  registry is never overwritten by a plain `build`.
