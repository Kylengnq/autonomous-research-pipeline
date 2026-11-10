---
name: data-profile
description: "Funnel layer F-1 (anchored mode): profiles the data a project already holds — a database, an API, a delivered extract — before any idea is generated. Read-only introspection produces an inventory, an identifier map with join-key stability, a variation inventory carrying the cluster counts S4's power block needs, a measurement-quality report, and an expansion map whose external joins are verified by a real probe rather than assumed. Enforces the peek firewall and writes the peek ledger, so the pre-registration can declare exactly what was seen before the question existed. Runs before idea-swarm's F0 scan; blocks F1 when stale."
---

# Data Profile (F-1)

The feasibility layer, moved to the front of the funnel. In `data_mode:
anchored` the project already holds data, so what used to be argued at
F3 — does a usable source exist, does the key join, is there variation —
is answerable by query before a single idea is generated. Facts only:
this skill describes what is in the data and never what the data
implies.

Read `pipeline-config.md` first: `data_mode`, `data_manifest`,
`data_profile`, `peek_log`, `private_spine`, `ideas_dir`,
`registry_file`, `scripts_dirs`, `python`, `gate_mode`. Harness survival
rules bind (absolute paths, checkpoints, single-threaded rate-limited
APIs; `playbooks/error-escalation.md`).

Reference scripts live in this skill's own `scripts/` folder:
`profile_source.py` (source-agnostic profiler) and `load_delimited.py`
(stage a delivered CSV into SQLite as TEXT, blanks as NULL, so
profiling sees the extract as delivered). A project symlinks them into
its `scripts_dirs` so the registry audit can see them; they are shared,
not copied, because a per-project copy drifts.

## Entry conditions

- `data_mode: anchored`. In `open` mode this skill does not run and F0
  is the funnel's first layer.
- `data_manifest` exists and declares, per source: name, kind (`db` |
  `api` | `file`), access method, the **environment variable holding
  the credential — never the credential itself**, licence and
  redistribution terms, and refresh cadence. A manifest missing the
  licence or the cadence blocks the run: the first sets what may be
  published, the second sets when this profile goes stale.
  Optional keys that make the checks sharper, each worth filling:
  `candidate_outcomes` and `candidate_treatments` (the firewall cannot
  be mechanical without them), `expected_members` and `universe_field`
  (a coverage gap is invisible without a declared membership — a count
  alone tells you something is missing but never what), `coded_fields`
  (so a coded column carrying free text is caught), `unit_hint`, and
  `prior_table` for the vintage-stability check.
- Access is read-only. Use a read-only role or connection where the
  source offers one, and never issue DDL or DML. A profile run that
  could modify the source is a defect, not a convenience.

## What the profile records

Every script is registered through the `script-registry` skill (purpose,
inputs, outputs, packages), so the profile is reproducible rather than
recalled. Large tables are sampled with the sample size and seed
recorded; counts that come from a sample are labeled as such.

1. **Inventory** — per source: tables or endpoints, row counts, unit of
   observation, time field, time span and frequency, and the entity or
   geographic coverage. Per field: type, missing rate, distinct count.
2. **Identifier map** — candidate join keys with coverage, uniqueness,
   and **stability across vintages**: the same key checked in at least
   two extracts or snapshots, reporting how many entities change or
   lose an id between them. Instability is the failure that killed
   a design once, and it is invisible in a single snapshot.
3. **Variation inventory** — which fields carry usable cross-sectional
   and time variation: level counts, cluster counts, within-unit
   switches, and the span over which they occur. These are the power
   inputs `pre-register` needs, computed once at F-1 instead of at the
   pilot.
4. **Measurement quality** — each finding tied to the field it affects,
   in plain terms, because ideas will be built on it. The checks a real
   delivered extract made necessary: missingness; masking or
   coarsening; top-coding; **mixed types** (a column where only some
   values parse as numbers); **malformed and implausible dates** (a
   column that mostly parses can still carry typo years, which string
   min/max hide); **zero mass** (a numeric field with a spike at exactly
   zero, which may be a sentinel for unknown rather than a measured
   zero); **duplicate units** (the candidate unit key is not unique);
   **vocabulary sprawl** (a declared coded field carrying free text);
   and **unexpected members** (values outside the declared universe,
   which matter as much as absent ones — a differently spelled member
   reads as both).

   Type classification is counted over the whole column, never a head
   sample. A delivered extract is usually ordered by something, so its
   first rows are systematically unrepresentative.

   Never let the database decide a type question silently. SQLite casts
   non-numeric text to 0, so a naive zero-mass or top-coding test on a
   mixed column reports a spike that does not exist; guard every numeric
   comparison with a shape test first.
5. **Expansion map** — external sources that can be joined to the held
   data. Each entry names the external source, the join key, and a
   **verified probe**: a registered script that performs the join on a
   small slice and reports a real match rate, the rows probed, and what
   fails to match. An entry with no probe is recorded as a candidate,
   never as verified, and downstream layers may not treat it as a fact.
   This is what keeps expansion from being the same unverified hunch
   one layer out.
6. **Publication facts** — from the manifest: what may be redistributed
   (a derived extract, aggregates, schema, code), what may not, and the
   licence clause behind each. G4 approves a spine tag and replication
   plan from this block.

## The peek firewall (hard rule)

Profiling describes the data; it never relates one substantive variable
to another. No correlation, no regression, no group mean or rate broken
out by a candidate treatment, no cross-tabulation of a candidate
outcome against anything but time or coverage. Univariate summaries and
join diagnostics are the whole permitted vocabulary.

If a viability check unavoidably reveals a relationship — a join
exposing an obvious pattern, a coverage table that doubles as a
treatment-outcome cross-tab — write a `DISCLOSURE REQUIRED` entry in the
ledger stating exactly what was seen, and carry it forward: the
`pre-register` skill must record it as a retrospective element and
declare how the affected sample is handled.

**Peek ledger.** Every query run against held data during S1 and S1b
appends one line to `peek_log`: timestamp, registered script, source,
tables and fields touched, purpose, and rows returned. The ledger is
append-only and is never rewritten to look cleaner. Its point is
narrow and important — the author owned this data before the question
existed, so the only honest defence against outcome-conditioning is a
record of what was looked at and when.

## Blocked-registry recheck

Before F0 runs, read `ideas_dir/blocked_registry.md` and check each
entry's named missing ingredient against the profile's inventory,
identifier map, and expansion map. Entries the held data supplies are
marked unblocked with the supplying field named, and re-enter F3
directly under the existing unblocking rule. Report the recheck result
even when nothing unblocks: already-vetted ideas are the cheapest
candidates in the project, and they are reconsidered before new ones are
invented.

## Output (two zones)

- `data_profile` (JSON, the machine-readable profile) plus
  `data_profile.md` beside it for reading. The JSON carries per source:
  `tables`, `identifiers`, `variation`, `quality`; and at the top level
  `expansion`, `publication`, `generated`, `manifest_hash`, and
  `field_index` — a flat array of fully qualified `source.table.field`
  names. The anchor-existence gate at F1 reads `field_index`, so it is
  required, sorted, and complete.
- `handoff/data_profile_extract.md` — the facts F0, F1, F2, and the
  debate's briefing pack may see: capabilities, keys, coverage,
  variation, quality caveats, verified joins. No query output that
  relates two substantive variables reaches this file.

  **Every capability line carries its counts.** A
  capability stated without a population size is not a capability, it is
  an invitation to design against an imagined sample. Each line reports,
  from the inventory and the variation inventory that already compute
  them: **N units, N periods, N clusters, and the coverage window**, plus
  the match rate for a capability that depends on a join. Where a count
  comes from a sample it is labeled, per the sampling rule above.

  Why this is a required field rather than a style note: a funnel branch
  has spent four idea cards and a full four-role debate on a data subset
  that turned out to hold **12 units across 2 periods**. The profile knew
  that number. The extract did not carry it, so nothing downstream could
  see it until a pilot counted rows. One line would have prevented the
  whole branch.

  Counts are the *only* addition here. The distilled-not-raw rule is
  unchanged, and a count that would relate two substantive variables (a
  cell count broken out by a candidate treatment against a candidate
  outcome) is a peek-firewall violation and stays in `quarantine/`.
- `quarantine/` — raw query output, full logs, anything carrying values
  that could reveal a relationship, plus every `DISCLOSURE REQUIRED`
  entry.
- Append to `peek_log`; lab-notebook entry with the date, sources
  profiled, counts, unblocked registry entries, and any disclosure flag.

## Freshness (machine gate)

The profile carries `generated` and the manifest's `refresh_cadence`. F1
refuses to run against a profile older than that cadence: generating
ideas against a stale schema reintroduces exactly the hunch this layer
exists to remove. Regeneration is a re-run of the registered scripts,
not a hand edit.

## Validation

Done when: every source in the manifest appears in the profile or its
absence is logged with the reason; every count traces to a registered
script's output on disk; `field_index` is present, sorted, and matches
the per-table field lists; every expansion entry is either probe-verified
with a match rate or explicitly labeled a candidate; no file under any
`handoff/` contains a statistic relating two substantive variables (grep
the design's candidate outcome and treatment terms co-occurring in one
sentence); `peek_log` has one line per query the registered scripts
issued; the blocked-registry recheck is reported; lab-notebook entry
written.

**Every capability line in
`handoff/data_profile_extract.md` carries N units, N periods, N clusters
and a coverage window**, each traceable to a registered script, and a
join-dependent capability carries its match rate. A capability line
without counts is a validation failure, not a stylistic one.
