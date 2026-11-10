---
name: paper-build
description: "Owns the build graph from estimation to PDF: a Makefile whose prerequisites are the replication manifest, generated LaTeX macros so no number is typed into the manuscript, and `make verify` (clean rebuild plus all integrity gates) as the reproducibility test. Data collection stays outside the graph."
---

# Paper Build

Make the paper a build target rather than a document that happens to agree
with the results. Every displayed number, table, and figure descends from a
script by a declared path, so changing a sample rule and rebuilding is a
command, not an editing pass.

The reason to do this is not the referee. It is that a paper you can rebuild
is a paper you can change: the cost of a reviewer asking for one more
control is a `make`, not a hunt through the manuscript for every place the
old number appeared.

## When to use

- Setting up a paper project's build (once, at the start of S7 writing).
- Adding an estimation, table, or figure: the graph gains a rule.
- Before a milestone, submission, or any claim that results reproduce.

## Source and generated

Classify every file before touching it. This is the rule that keeps the
graph honest.

| Source (edit these) | Generated (never edit) |
|---|---|
| `data/processed/*` extracts, config | `output/*_results.json` |
| estimation and table/figure scripts | `build/*.tex` tables, `build/values.tex` |
| `main.tex` prose, `references.bib` | `build/*.pdf` figures, `build/main.pdf` |
| the claim ledger, the pre-registration | the registry's mechanical fields |

**Repair direction.** A wrong number on the page is never fixed on the page.
Trace it to the results key, then to the script that wrote it, fix there,
rebuild. An agent that edits a generated file has broken the graph, and the
next `make` silently reverts the fix. When a generated file must be touched
by hand for a real reason (a journal's table format the generator cannot
express), move the generation into the script instead, or promote the file
to source and say so in the Makefile comment.

## The graph

Copy `<skill_dir>/assets/Makefile.template` to the paper project root as
`Makefile` and fill the variables from `pipeline-config.md`
(`python`, `paper_dir`, `main_tex`, `bib_file`, `results_dir`,
`scripts_dirs`, `claim_ledger`, `registry_file`, `build_dir`, `values_tex`,
`seed`). Structure:

```
data/processed/*.csv   (source: no recipe, missing extract fails loudly)
        |
   analysis/*.py  -->  output/*_results.json
        |                    |
        |            scripts/make_tables.py  -->  build/tab_*.tex
        |            scripts/make_figures.py -->  build/fig_*.pdf
        |            claim_macros.py emit    -->  build/values.tex
        |                    |
     paper/main.tex  +  the generated files  -->  build/main.pdf
```

Rules the template encodes and a hand-written graph must keep:

- **`.DELETE_ON_ERROR:`**. A recipe that dies halfway leaves a target with a
  fresh timestamp that Make will never rebuild. Without this line a crashed
  estimation looks like a completed one.
- **Prerequisites are the truth.** Whatever a script actually reads goes in
  the prerequisite list, including `preregistration.md` for estimation
  targets, so a re-freeze forces a re-run.
- **Seeds are passed, not defaulted.** `--seed $(SEED)` on every stochastic
  recipe. A seed living inside the script is a seed nobody rebuilds against.
- **`make verify` = `distclean all check`.** The full statement: from source
  alone, everything rebuilds and every gate still passes. `distclean`, not
  `clean`: Make rebuilds only when a prerequisite is strictly newer, so with
  the results JSON left in place a script edited within the same second, or
  a fresh clone where git gave every file the checkout time, would let
  `verify` pass without re-deriving anything. Deleting the results is what
  makes the claim true.
- **The build stamps what it built.** `check` records the script/output
  pairing in the registry (content hashes, so a later audit and a fresh
  clone can both answer "was this output produced by this script?"). It
  stamps first, then audits: the artefacts were just rebuilt, so this is the
  one moment the pairing is known good, and the audit's staleness question
  is about other moments.
- **The lock is source.** `$(LOCK)` holds the last accepted values and sits
  outside `$(BUILD)` so `clean` cannot reach it. `make accept` is the only
  thing that writes it, and it is a person's call after reading the diff. A
  first `make verify` on a new project fails until `make accept` has run
  once; that is the baseline being set deliberately rather than by accident.

## The data boundary

The build graph starts at processed extracts. Collection stays outside it:
EDGAR and OpenAlex crawls run for hours, are rate-limited, are not
idempotent, and belong to `data-pipeline` with its checkpointing and
detached orchestrator. A `make` that could start a six-hour crawl is a
`make` nobody will run, which defeats the point.

So extracts are declared as source with a recipe that only reports their
absence, and `distclean` never deletes them. The extract's provenance is
carried by the script registry and the data manifest, not by Make.

## Generated values

Numbers quoted in prose are emitted as LaTeX macros from the claim ledger
and referenced by name, so the manuscript holds no numeric literal to drift:

```latex
Treated firms raise disclosure by \BetaMain{} relative to controls.
```

Mechanics, ledger fields, and the moved-number report are in the
`claim-ledger` skill. Two rules matter here: `build/values.tex` is generated
(never edited), and whole regression tables are generated as `.tex` files
that `main.tex` `\input`s, not as per-cell macros. Macros are for prose
numbers, which is where retyping does the damage.

## Workflow

1. Read `pipeline-config.md` for the keys above. `<skill_dir>` is this
   skill's own folder.
2. **Inspect before writing.** If the project already has a Makefile,
   Quarto project, or build script, extend it; do not replace it.
3. Copy and fill the template. Add one rule per estimation script, one per
   table, one per figure. Extend `RESULT_JSON`, `TABLES`, `FIGURES`.
4. Add `\usepackage{siunitx}` and `\input{build/values.tex}` to the
   manuscript preamble.
5. Sync the registry from the graph:
   `<python> <skills_root>/script-registry/scripts/registry.py build --dirs <scripts_dirs> --out <registry_file> --merge --makefile Makefile`.
   Make prerequisites become the registry's inputs and outputs, so the
   replication manifest stops being hand-curated for every script the build
   covers. Re-run it whenever the graph gains or loses a rule.
6. Run `make accept` once to set the values baseline, then `make verify` and
   fix what it reports. A first run that passes immediately usually means a
   target is missing from the graph; check that `clean` really emptied
   `build/`.
   From then on `make verify` is the loop: when it stops on a moved number,
   read the diff, decide, and `make accept`.
7. Dated `lab_notebook` entry: the graph's targets and the `make verify`
   result.

## Outputs

- `Makefile` at the paper project root.
- `build/` holding every generated artefact; nothing generated outside it,
  and nothing source inside it.
- A registry whose inputs and outputs come from the graph, carrying the
  content-hash stamps the last good build recorded.
- A `make verify` exit code, which is the reproducibility claim.

## Validation

- `make verify` exits 0 before any milestone commit or submission.
- No generated file is edited by hand; no numeric literal quoted in prose
  that `claim_macros.py check` can trace to a macro.
- Every stochastic recipe passes `--seed`.
- `distclean` leaves `data/processed/` intact.
- A missing extract fails with the collection instruction, never by starting
  a crawl.
