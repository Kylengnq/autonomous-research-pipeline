---
name: idea-pilot
description: "Small-sample feasibility pilot: on the themed path it screens every variant before any debate; on the swarm path it runs on any card whose debate ended with no KILL vote. Verifies the data are actually obtainable (registered download script or extract query on a slice), counts coverage and treatment variation, sanity-checks the key measure, and produces power/MDE inputs for pre-registration. Reasons over the quantity the design needs rather than the field it named, so a negative verdict must first show one alternative construction it considered and why that fails — verdicts are feasible / conditional / construction-open / unmeasured / access-blocked, plus infeasible-unchecked when no alternative was considered, which is never terminal. The run's usability threshold is one declared constant printed in every report; every reported count carries the literal expression that produced it and is re-executed by the harness; every count carrying a terminal verdict or a menu number is derived twice by independent expressions and a disagreement blocks the verdict. Firewalled from the headline effect: never estimates it; any unavoidable sight of it triggers a mandatory disclosure flag for pre-register."
---

# Idea Pilot (F3)

Feasibility test, not a preview of the result. The pilot answers "can
this design be run", never "does it work" — the second question is
S6's, behind a committed pre-registration.

Read `pipeline-config.md` first: `ideas_dir`, `registry_file`,
`scripts_dirs`, `python`, `gate_mode`, `data_access`, `data_mode` (plus
`data_manifest`, `data_profile`, and `peek_log` when `data_mode:
anchored`). Harness survival rules bind
(absolute paths, single-threaded rate-limited APIs, checkpoint files;
`playbooks/error-escalation.md`).


## When to use

Driven by `run-pipeline` inside S1b: on the themed path before the debate, on
the swarm path after the debate gate. The author may name it directly to retest
feasibility after a data source changes.

Run it only on cards that have cleared the cheaper layers. It executes code
against real sources and is the most expensive thing in the funnel per card,
which is why the sequencing puts it behind the screens that kill for free.

## Entry gate (machine)

**Two authorized entries.** Which one applies is decided by the path, not
by the card.

### Entry A — `themed-prepilot` (themed path)

When `pipeline-config.md` sets `theme`, the pilot runs on **every variant**
from `idea-variants`, before any debate. There is no verdict block to read
and none is required: the pilot is a universal screen here, not a reward.

This is the inversion the themed path is built on. When the theme is
fixed, the question is not *which idea* but *which version of this idea
can the data carry*, and that is a counting question. It is cheap — the
observed pilots have each been one script and under a minute — and
it is the layer that produced the highest-quality facts in the entire
funnel: it killed one card on 24 usable days and corrected the F3
feasibility assessor's own figure, which had counted days where *any*
partition cell was quoted when the design needed *every* cell, and was
8-to-10x too optimistic as a result.

### Entry B — post-debate (swarm path)

Refuse to run unless the idea's `quarantine/debate_record.md` carries a
machine-readable ```verdicts block whose FINAL round contains **no KILL
vote from any role**.

That is the whole gate. REVISE neither authorizes nor blocks: a card with
four REVISE votes and no KILL runs a pilot, because REVISE is what an
adversarial role returns when it has found something worth naming, and
what it has named is usually a question the pilot can answer for the price
of a few queries.

### A feasible verdict is not evidence about identification

**Hard rule after the first decision audit.** A pilot
answers whether the data exist in the shape the design needs. It says
nothing about whether the design identifies anything, and no layer may
read it as though it did.

A decision audit has found this exact substitution. Three of four roles
located a card's fatal defect in the **estimand** — the design's estimator
recovered a different quantity than the question asked for, because it
assumed an independence the setting does not have — and the card was then
routed to a *feasibility pilot*, which was commissioned to settle a count
the record had already answered adversely while the identification defect
went unaddressed. Measure-before-repair fixed the clinic ordering, correctly.
It does not help when the defect is not countable in the first place.

So on the themed path, where every variant is piloted up front, a
`feasible` verdict advances a card to the debate and **nothing more**. The
debate is where identification is attacked, it runs after the pilot, and a
pilot report in its briefing pack is a statement about sample size that
carries no weight on whether the comparison is credible.

Read the fenced block, not the prose — free-text matching misfires on
phrases like "REVISE (from EXPLORE)". A missing block, fewer than four
roles, or any KILL fails the gate: name the roles that voted KILL and
what each called fatal, then stop. (If a debate record predates this
convention and has no block, treat it as failing the gate and route back
to the debate to emit one.)

**Gate history, kept because the sequence is the argument.** Unanimous
EXPLORE (original) never fired across four runs and twelve ideas. It was
replaced by no-KILL-plus-majority-EXPLORE, which a
counterfactual on the same day showed would also have fired zero times and
which was never trialled live. It became no-KILL alone. What that trial
established is that the binding constraint was never KILL votes: the one
viable card finished with zero KILL, one EXPLORE and
three REVISE, and every one of those three REVISE votes rested on a
countable question about how many event series carried a complete price
partition. Requiring EXPLORE votes asks adversarial roles to stop being
adversarial. Requiring no KILL asks only that nobody found something fatal,
which is what unanimity was actually protecting.

**Current setting:** the gate is no longer one rule but two
entries, because the themed path removed the question the gate was
answering. When every variant is piloted, there is nothing to authorize —
the gate's whole job was rationing an expensive layer, and the layer turned
out to be the cheapest one in the funnel. The no-KILL gate survives
unchanged on the swarm path, where the debate still runs first.

The pilot is now the cheapest way to settle a REVISE on the swarm path,
and the first thing that happens to an idea on the themed one. It was
never a reward for surviving a debate.

## The usability threshold is a declared constant

**One threshold per run, declared in `pipeline-config.md` as
`usable_min`, carried into every report by `pilot_lib.write_report`.**

One run carried three different thresholds inside a single layer — `>= 10`,
`>= 30`, `>= 100` — and printed none of them. One card cleared at exactly 10;
another died at 29 against a bar it did not know about. `pilot_lib`'s own docstring says the
report exists so the usability threshold can be audited, and the threshold is
the one thing it never carried into the report.

Rules:

- The threshold is **one number for the run**, set before the first pilot runs
  and never varied per card. A card that needs a different bar is making a
  design argument, and that argument belongs in the report's binding-constraint
  line, not in a silently different comparison.
- Every report prints it: the value, and the unit it counts (traders, cells,
  meetings, market × meeting pairs — see the definition rule below).
- A report with no threshold line, or a script whose comparison constant
  differs from `usable_min`, is a **validation failure**, not an omission.
- Changing it mid-run is a gate decision, logged with `gate-log`, and every
  earlier verdict is re-derived against the new value or the run reports two
  thresholds and says which cards were judged under which.

## Stating a definition and computing it are separate acts

Both confirmed arithmetic defects found so far were **a count computed at one
unit and labelled at another**, with the report's prose accurate about intent.
In one case the pilot script computed a variable and never used it in any
reported number. The report was auditable on its definitions in exactly the sense that
made the defect invisible: the definition was stated and nothing checked that it
was the one exercised.

So every reported count carries a machine-readable definition block, and the
harness checks it:

    ```count
    name: usable_sample
    unit: <unit> × <period>
    filter: >= 10 observations in both windows
    expression: df.groupby(["<unit>","<period>"]).size.ge(10).sum
    value: 136
    ```

`expression` is the **literal source line** that produced `value`, copied from
the registered script, not a paraphrase. `pilot_lib` re-executes it against the
same slice and fails the report if the result differs from `value`, and greps
the script for symbols computed and never used in any reported expression
(`first_seen` would have failed this). A count whose expression cannot be
isolated to one line reports `expression: [MATERIAL GAP: not isolable]` and is
**barred from carrying a terminal verdict** — it may inform, it may not kill.

## Any number carrying a terminal verdict is derived twice

The pilot is the layer that decides the most and the layer nothing checks: one
script, once. A decision audit has reproduced all six original pilot samples
exactly and still overturned four of six advances — every defect in the
*correction* layer that ran once, unreviewed, on top of it.

Rule: **a count that will carry `unmeasured`, `access-blocked`, or a menu
number is computed by two independent expressions before the verdict block is
written**, and both go in the report. Independent means a different grouping
path to the same quantity — count the pairs and count the units and multiply
through — not the same expression run twice. Agreement is one line in the
report; **disagreement is a finding**, blocks the verdict, and is reported with
both numbers rather than resolved by picking one.

This is cheap. The pilots are driver-run scripts on held data; a second
derivation is a second `groupby`, and it is the difference between the eleven
an earlier run figures that were confirmed and the two that were not.

## What the pilot does

1. Data slice: write and register (script registry, per the
   `script-registry` skill) a download script for a small slice of
   the named source by its named access route — enough to prove
   access, format, and join keys. Where the route is `licensed`,
   `purchasable`, or `restricted`, the pilot proves the route works
   (credentials resolve, the subscription covers the years, the
   application is granted) before it proves anything about the data;
   an unproven route is an `access-blocked` verdict, not a footnote.
   Checkpointed; absolute paths.
   Anchored mode: instead of a download, register the **extract query**
   that builds the design's sample from the held data, and execute the
   expansion map's joins at the design's full scope rather than the
   probe's slice — a key that matched on 50k rows can still fail on the
   population. The query is registered like any script and its run
   appends to `peek_log`. Because F-1 already counted coverage and
   variation, the pilot here confirms a design at real scale rather
   than making first contact; a gap between the profile's numbers and
   the pilot's is itself a finding and goes in the report.
2. Coverage counts: units, periods, treated/control counts against
   the design in `handoff/data_availability.md`. A coverage collapse
   is a finding, not a failure of the skill.
3. Variation check: does the treatment/exposure actually vary in the
   slice (counts by cell, not effect estimates).
4. Measure sanity: the key measure computes, has plausible range and
   nonzero variance; no correlation of measure with outcome is
   computed.
5. Power inputs for S4: N, cluster counts, outcome variance,
   baseline rates — the ingredients of the pre-registration's MDE
   block, so an underpowered design dies at the freeze, not at G5.

## The firewall (hard rule)

The pilot never estimates the headline effect: no regression,
difference, or correlation of the design's outcome on its treatment,
in any form, on any subsample. If a viability check unavoidably
reveals the headline's direction or magnitude (e.g. a join exposes an
obvious pattern), write a `DISCLOSURE REQUIRED` flag into the pilot
report stating exactly what was seen; the `pre-register` skill must
carry it as a retrospective element and declare pilot-sample handling
(excluded from, or explicitly included in, the confirmatory sample).
An undisclosed sight is the outcome-conditioning failure the Phase 3
review caught — treat it as fatal to the pilot's validity.

## Output (two zones)

- `quarantine/pilot_raw/`: raw slice, full logs, anything with
  outcome values in it.
- `handoff/pilot_report.md`: feasibility section only — coverage
  counts, variation table, measure checks, power inputs, verdict, and
  any DISCLOSURE REQUIRED flag. No directional language about the
  headline relationship anywhere in this file.

## Verdicts, and the reachability check that gates the negative ones

**Reason over the quantity, not the ingredient.** In a head-to-head benchmark,
three cards declared a market-microstructure quantity unreachable because the
held extract lacked the one field the obvious construction wants — and filed it
as a data purchase. **A human measured the same quantity from a different
relation already present in the held data**, at no cost, and built a top-ranked
idea on it. That is **an instrument miss wearing a data decline's clothes**, and
it is general: a pipeline that reasons over ingredients (fields, tables,
endpoints) declines quantities that have more than one construction. Spread,
surprise, exposure, attention, liquidity and sentiment all have several.

So before any negative verdict the pilot writes a **reachability block**:

    ```reachability
    quantity: <what the design needs measured, in its own terms>
    ingredient_absent: <the field or feed the obvious construction wants>
    alternative_considered: <a second construction reaching the same quantity
                             from what IS held>
    why_it_fails: <or: it does not fail — verdict is construction-open>
    ```

`quantity` names **what the design needs measured**, in the design's own terms,
never a field name. `alternative_considered` names one construction that reaches
that quantity from what *is* held. A negative verdict with no alternative
considered returns **`infeasible-unchecked`**, which is **not terminal, is not
counted in any kill rate, and cannot enter the graveyard** — it is a statement
that the pilot did not finish.

| Verdict | Meaning | Route |
|---|---|---|
| `feasible` | the design runs at the declared threshold on held data | debate (themed: with the pilot report in the pack) |
| `conditional` | feasible under a stated proxy or sample change | returns to the debate for a one-round re-check; **never self-approves the change** |
| `construction-open` | the named ingredient is absent and the *quantity* is reachable another way | **not terminal.** The alternative construction is written into the card as a required design note and the card proceeds |
| `unmeasured` | nobody records the quantity, by any construction | graveyard/blocked; recheck trigger is a new data release |
| `access-blocked` | it exists and this project cannot get it — licence, price, application, embargo | blocked registry, `access` class; recheck trigger is a **contractual or legal** change, never a data release |
| `infeasible-unchecked` | no alternative construction was considered | validation failure; re-run the reachability check |

**`access-blocked` is no longer anchored-mode-only**.
It was written as a class of anchored mode because that is where it was first
met, but a licence wall is a licence wall whether or not the project holds other
data, and it has a different recheck trigger from every other negative verdict.
Any run can return it.

A card blocked on access is never quietly rerouted to a public proxy: the proxy
is a different idea and re-enters as one.

### The supplementary-data protocol

When the honest answer is *we need an outside source*, the pilot does not
speculate about it. Each candidate source gets, before it can be recommended:

- a named **access route** — held / public / licensed / purchasable /
  restricted;
- a named **join key**;
- a **verified join probe** reporting a real match rate on a real slice, not an
  expectation — this is F-1's expansion map machinery, reused rather than
  rebuilt;
- a **cost and time** estimate for obtaining it.

The author's G4 decision is then made against a probe rather than a hunch. If no
route resolves inside the run's budget, the card enters the blocked registry
with **both the ingredient and the route recorded** — today only the ingredient
is, and the two have different recheck triggers, so a registry that records one
cannot tell a new data release from a new licence.

### The `data_request` block

The protocol above fires when a card is **failing** for want of data. That left
a hole the author named directly: they intend to go and find data the workflow
asks for, and until now a data need could only surface as a kill verdict, or
inside the slate-level feasibility-thin route, which is reachable only when the
whole slate is declined. **A card that is alive but would be materially better
on data nobody has yet had no way to say so.**

So **every** pilot report carries a `data_request` block, whatever the verdict,
including `feasible`:

    ```data_request
    status: none | would-strengthen | required
    quantity: <what the design needs measured, in the design's own terms>
    why_it_matters: <what the paper can claim with it that it cannot without>
    candidates:
      - source: <name>
        route: held | public | licensed | purchasable | restricted
        join_key: <named key, or n/a>
        probe: <verified match rate on a real slice, or "unprobed: <reason>">
        cost_time: <estimate>
    fallback: <the construction the card uses if nothing is acquired>
    ```

Four rules, all blocking:

1. **`quantity` names what is measured, never a field or a table.** Same rule as
   the reachability block and for the same reason: a request phrased as an
   ingredient invites a shopping trip for the wrong thing, which is the instrument
   miss an earlier run benchmark measured.
2. **`status: none` is a real and common answer.** A block that requests
   something on every card is a wish list, and a wish list is not read. Ask only
   where the answer changes what the paper can claim.
3. **`required` does not by itself kill the card.** A `required` request on a
   card whose pilot returned `construction-open` means the fallback construction
   carries the design and the acquisition would improve it. Only the pilot verdict
   kills, and it does so under its own rules.
4. **`fallback` is mandatory even at `required`.** A request with no fallback is
   an admission the card is a data purchase in disguise, and it routes to the
   blocked registry with its route recorded rather than sitting on the slate.

Unprobed candidates are allowed and must say so. A probe costs a query and the
run may not have one to spend on a source nobody has agreed to buy; what is not
allowed is an unprobed candidate presented as though its match rate were known.

The blocks are aggregated by the driver into `<ideas_dir>/data_requests.md`, one
section per card, ordered by `status` then by the card's G1 verdict, so the
author has a single list to act on rather than a hunt through lineage
directories. That file is a **G1 output and travels with the slate** — including
with the fallthrough tier, where a capped card's cheapest clearing action is
often exactly one acquisition on this list.

## Validation

Done when: the download script (anchored mode: the extract query) is
registered with declared outputs on disk; the report's every number
traces to slice files; in anchored mode every query run appears in
`peek_log`; the report
contains no outcome-on-treatment comparison and no directional
language (grep for the design's outcome and treatment terms
co-occurring in a sentence with sign words); the verdict is one of the
six in the table above; lab-notebook entry written.

- **Threshold**: `usable_min` is set in `pipeline-config.md`, printed in every
  report with the unit it counts, and equals the comparison constant in every
  pilot script. `grep -L usable_min <ideas_dir>/*/handoff/pilot_report.md`
  returns nothing.
- **Definitions**: every reported count carries a ```count block whose
  `expression` is a literal source line; `pilot_lib` re-executes each and fails
  on any mismatch with `value`; every symbol a script computes appears in some
  reported expression or the script is flagged for dead computation.
- **Second derivation**: every count carrying a terminal verdict or a menu
  number shows two independent expressions and their agreement. A disagreement
  is reported as a finding and blocks the verdict.
- **Reachability**: every `unmeasured` and `access-blocked` verdict carries a
  ```reachability block naming the quantity (not the ingredient) and one
  alternative construction with why it fails. Any negative verdict lacking one
  is reported as `infeasible-unchecked` and appears in no kill count. Every
  supplementary source recommended carries a route, a key, a **verified** probe
  with a real match rate, and a cost/time estimate.
- **Data request**: every pilot report carries a
  ```data_request block, `status: none` included — `grep -L data_request
  <ideas_dir>/*/handoff/pilot_report.md` returns nothing. Every block at
  `would-strengthen` or `required` names a `quantity` in design terms (a field
  or table name there is a validation failure), at least one candidate with a
  route, and a `fallback`. Every candidate carries either a verified probe with
  a real match rate or an explicit `unprobed:` reason; a bare expected match
  rate fails. A `required` block with no `fallback` routes the card to the
  blocked registry rather than the slate.

the entry used (`themed-prepilot` or post-debate) is
recorded in the report; on the themed path **every** variant has a pilot
report, and a variant with none is a validation failure rather than an
omission; and no pilot report contains a claim about identification,
credibility, or what the design would show — grep for identification
vocabulary is part of the same pass that greps for directional language.
A pilot that has opined on identification has exceeded its warrant, and
the layer downstream will read it as settled.
