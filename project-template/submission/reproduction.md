# Reproduction

How to rebuild every number in the paper, and what that does and does
not cover.

## What `make verify` covers, and what it does not

`make verify` is `distclean all check`: from source alone, everything
rebuilds and every integrity gate still passes.

**Data collection sits outside the build graph by design.** So
`make verify` reproduces estimation through the PDF and **not** the
crawls. The collection scripts are registered and re-runnable, and are
listed separately below. A reader should not infer that running
`make verify` re-downloads anything.

## Data files

| Path | Bytes | sha256 (16) | Produced by |
|---|---|---|---|
| — | — | — | *no data files yet* |

## Environment

| Field | Value |
|---|---|
| Python | `.venv/bin/python` |
| Seed | `20260818` |
| Makefile | `Makefile` |
| Registry | `output/script_registry.json` |
