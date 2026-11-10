---
name: data-pipeline
description: "Build a reproducible, free-data pipeline (SEC EDGAR, OEWS, FRED, Ken French, yfinance) with checkpointing and the detached-orchestrator pattern for multi-hour crawls. Encodes the survival rules the harness imposes: background jobs get killed, OpenAlex must run single-threaded, relative paths break in backgrounded shells. Use before any large data collection so the long pole does not become a re-derivation exercise."
---

# Data Pipeline

Stand up a data-collection pipeline that survives multi-hour runs and is reproducible from the
sources a project actually has. The discipline here is operational: a large crawl that dies at hour
14 with no checkpoint is the single most expensive mistake in this workflow, and it is entirely
avoidable.

## When to use

- A new data source needs to be pulled at scale (thousands of filings, a full universe).
- A crawl is expected to run longer than the harness will hold a foreground call.
- An existing pull needs to be parallelized or made resumable.

## Principles

- **Any source with a named access route** (the older rule barred a proprietary
  source from ever being a primary spine). Public and keyless remains the cheapest route and the
  default starting point: SEC EDGAR (universe, financials, full-text via EFTS, 10-K filings), BLS
  OEWS, FRED, Ken French Data Library, yfinance, OpenFIGI. Held, licensed, purchasable and
  restricted sources are equally admissible, and may carry the headline. What the old rule
  protected — a referee's ability to collect the data — is now bought with disclosure instead of
  prohibition: a non-public spine ships a replication plan naming what can be released (derived
  extract, aggregates, schema, code, a synthetic twin) and what cannot, with the reason, approved
  by the author at gate G4. A project that needs the strict rule back sets `data_access: free_only`
  in `pipeline-config.md`; a submission whose venue requires collectable data should.
- **Credentials live in the environment.** A licensed or restricted route names the environment
  variable holding its credential; no config file, script, log, or commit ever holds the value.
- **Checkpoint everything.** Write per-shard partial results to disk continuously and a sentinel
  file on completion. Progress must be observable from the filesystem, not from a live process.
- **Re-aggregate, do not re-crawl.** Store per-item raw hits (e.g. per-phrase counts) so a measure
  change is a re-aggregation pass, not a second multi-hour crawl.

## Survival rules (the expensive lessons, do not relearn them)

- **The harness kills `run_in_background` jobs.** For any multi-hour crawl use the
  **detached-orchestrator pattern**: launch from a normal Bash call as
  `( nohup bash scripts/<orchestrator>.sh >> logs/<job>.log 2>&1 & )` — the subshell + `nohup`
  reparents the job to launchd so it outlives the turn. Then poll a sentinel file
  (`data/raw/<job>.DONE`); there is no auto-ping, so the next session checks the sentinel.
- **Background shells start in a different cwd.** Use absolute paths and the repo `.venv/bin/python`
  in any backgrounded command; relative paths exit 127.
- **Never run two OpenAlex/Corbis jobs concurrently.** Concurrency trips rate-limiting and every job
  retries at once; one concurrent test ran 1693s for zero results. Run searches single-threaded with
  progress prints.
- **Parallelize crawls by sharding the universe, not by threading one source.** The Russell-3000
  headcount crawl went from ~15-20h single-thread to ~2-3h as 6 disjoint CIK shards, each its own
  detached process writing its own partial, merged at the end.

## Workflow

1. **Define the universe and the schema** up front: the key (e.g. CIK), the columns, the coverage
   target, and the output path (`data/raw/<name>.parquet` or `.csv`).
2. **Write the extractor** as a single-item function with a retry/backoff and a skip-if-present
   check, so a re-run resumes instead of restarting.
3. **Shard and orchestrate.** Split the universe into N disjoint shards; write a shard runner and an
   orchestrator script. For long runs, launch detached and drop a `.DONE` sentinel per shard.
4. **Poll, then merge.** Check sentinels; merge partials into the panel; record coverage (% of
   universe with non-null outcome) and known parse failures (e.g. table-based 10-K filers mis-parse).
5. **Validate and document.** Spot-check a few known firms by hand, winsorize obvious extraction
   noise, and write a short data-readiness note to `output/` plus a `notes/lab_notebook.md` entry.

## Outputs

- The pipeline scripts under `scripts/` (extractor, shard runner, orchestrator, merge).
- The assembled panel under `data/` and a coverage/caveats note under `output/`.
- Sentinels under `data/raw/` recording completion.
- A `notes/lab_notebook.md` entry.

## Validation

- Coverage and parse-failure rate reported explicitly; do not silently drop firms.
- Every source named with a public retrieval path so a reviewer can reproduce it.
- For any run launched detached, the sentinel path is recorded in the lab notebook so the next
  session knows what to poll.
