---
name: claim-ledger
description: "Builds and validates the claim ledger: every load-bearing claim maps to a results-file path, key, value, tolerance, and a mechanism check; textual claims carry verified quotes or locators; each results file must trace to a registered producing script. Also emits prose numbers as generated LaTeX macros so they cannot be retyped or drift. Validator exits nonzero on drift, fabricated support, or unregistered evidence."
---

# Claim Ledger

Make every load-bearing claim traceable and falsifiable against its own
evidence. Targets three failure modes: claim drift (a printed number whose
source changed), fabricated support (a quote its source does not contain),
and unregistered evidence (a results file no known script produces).

Scope is load-bearing claims: the abstract, the introduction's headline
magnitudes, and every number in a table or figure. The claims a referee
would challenge, not every sentence.

Two controls, not one. Validation *detects* a number that no longer matches
its source. Macro emission *prevents* it: a prose number quoted through a
generated macro has no second copy to drift. Prefer prevention for every
number quoted in prose; validation still covers tables, textual claims, and
anything a macro cannot express.

## When to use

- During writing (S7), as tables and the abstract are drafted.
- After any results refresh, to confirm no printed number drifted.
- As part of the peer-review integrity pre-gate.

## Entry schema

`claim_ledger` (path from `pipeline-config.md`) is a JSON list. A claim is
numeric (traces to a results file), textual (attributed to a source), or
both. Every claim needs a `mechanism_check`.

| Field | Meaning |
|---|---|
| `id` | short id, e.g. `C1` |
| `claim` | the sentence as it appears in the paper |
| `location` | where it appears: `abstract`, `sec:results`, `tab:main` |
| numeric: `results_file` | path to the results JSON backing the number |
| numeric: `results_key` | dot-path into the JSON, e.g. `did.full.beta` or `event.0.coef` |
| numeric: `reported_value` | the number printed in the paper (`null` = existence check only) |
| numeric: `tolerance` | absolute tolerance for the match (default exact at printed precision) |
| textual: `source` | a local file path or a citation / arXiv id |
| textual: `quote` | the exact supporting span |
| textual: `page` / `section` | locator when no quote is available |
| `mechanism_check` | one line: does the evidence imply this mechanism, or only the correlation? |
| macro: `macro` | LaTeX macro name, letters only (`BetaMain`). Its presence makes the claim generated |
| macro: `precision` | decimals to round to (default: inferred from `reported_value`, else 3) |
| macro: `scale` | multiplier applied before rounding, e.g. `100` for a fraction shown as a percent |
| macro: `unit` | siunitx unit *macro* including the backslash (`\percent`); omit for a bare number |

A claim carrying `macro` sets `reported_value` to `null`. The macro is the
single source; `values.lock.json` records what the paper last printed.

## Generated values

Numbers quoted in prose are emitted as macros and referenced by name, so the
manuscript holds no numeric literal:

```latex
Treated firms raise disclosure by \BetaMain{} relative to controls.
```

```
<python> <skill_dir>/scripts/claim_macros.py emit <claim_ledger> \
        --out <values_tex> --lock <results_dir>/values.lock.json
<python> <skill_dir>/scripts/claim_macros.py accept <claim_ledger> \
        --out <values_tex> --lock <results_dir>/values.lock.json
<python> <skill_dir>/scripts/claim_macros.py check <claim_ledger> \
        --tex <main_tex> --values <values_tex> --generated <build_dir>/tab_*.tex
```

`emit` pulls each value from the results file the claim names, writes
`values_tex`, and reports every macro that moved from the accepted baseline.
**That diff is the alarm that replaces drift detection**: with generated
values the paper can no longer be wrong about its own results, but a number
that moved is still news. `--fail-on-change` turns the diff into a gate
(`make check`, and before submission).

`emit` never writes the lock. `accept` is the only command that does, and it
is a person's decision after reading the diff: a build step that accepted
the numbers it had just changed would leave the gate nothing to catch. The
lock is source, not a build artefact. It lives beside the ledger (the
default), belongs in version control, and must survive `make clean`.

`check` fails on: a macro defined but never used (a claim that quietly left
the paper), a macro-backed value also typed as a literal in the prose, and a
macro claim that kept a `reported_value`. Generated table files are exempt
from the literal scan; literals shorter than three characters are skipped as
too collision-prone to flag.

Whole regression tables stay generated `.tex` files that `main.tex` inputs,
not per-cell macros. Macros are for prose numbers, where retyping does the
damage.

## Workflow

1. Read `pipeline-config.md` for `claim_ledger`, `registry_file`,
   `results_dir`, `values_tex`, `main_tex`, `python`. `<skill_dir>` below is
   this skill's own folder (the directory containing this SKILL.md).
2. As each table or abstract claim is written, add its entry. Give a `macro`
   to every claim whose number is quoted in prose; leave table-cell claims
   without one.
3. Validate:
   `<python> <skill_dir>/scripts/claim_ledger.py validate <claim_ledger>`
   It checks: results file exists, key resolves, value matches within
   tolerance, mechanism check non-empty; for textual claims with a local
   source and a quote, that the quote appears in the source
   (whitespace-normalized). External-source citations are confirmed
   separately by `verify-citations`.
4. Cross-reference against the script registry:
   `<python> <skill_dir>/scripts/claim_ledger.py cross-ref <claim_ledger> --registry <registry_file>`
   It fails when a `results_file` is not declared as an output by any
   registered script, or when the producing script is newer than the
   results file (stale evidence: the code changed after the number was
   produced).
5. Emit and check the macros. Read the moved-macro report, then `accept` it:
   a headline magnitude that moved is a result to understand, not a diff to
   wave through. In `gate_mode: autonomous`, acceptance follows the
   pre-specified rule and the moved values go in the `auto-mode` log entry
   verbatim.
6. For each flagged claim: fix the number (drift), supply the missing
   source, rebuild the stale result, or rewrite the claim to what the
   mechanism supports. A claim that cannot be backed does not go in the
   paper.
7. Record the pass (any claims downgraded to suggestive) in
   `lab_notebook`; record any macro that moved, with its old and new value.

## Outputs

- Validated `claim_ledger`.
- `values_tex` (generated) and the accepted-values lock file (source,
  committed).
- Validator, cross-ref, emit, and check exit codes (the gates).
- A dated `lab_notebook` entry.

## Validation

- Every table and figure number and every abstract/intro magnitude has an
  entry.
- No entry ships with an empty `mechanism_check`.
- Every number quoted in prose carries a `macro`; none carries both a
  `macro` and a `reported_value`.
- All four commands exit 0 before `draft-paper` reports the draft done.
