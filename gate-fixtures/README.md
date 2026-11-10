# Gate fixtures: planted failures for the machine gates

Status: **100 fixtures**, all behaving as declared, **two real defects found and
fixed** by writing them. Eight cover the G1 threshold gate and one covers
journal-name resolution, each written at the same time as the thing it checks.

The G1 fallthrough tier and the data-request block are covered by six
`g1_fallthrough_*`, seven `datareq_*`, and seven `g1accept_*` fixtures, plus two
checkers (`data_request_check.py`, `g1_acceptance_check.py`). The fallthrough set
found a defect in its own first draft, which is the point of writing them with the
rule: the clean fixture filed a `kill`-verdict card in the fallthrough tier and
the checker refused it, because the tier is bounded below by `g1_fallthrough`
and is not a home for everything that did not clear. The fixture was wrong, not
the gate.

**A second batch** closed the two gate families that had no
planted failure and were the only untested gates whose failure puts a defect
into the paper rather than into a decision: seven `synth_*` and six `cite_*`,
with checkers `synthetic_check.py` and `citation_check.py`.

`estimand_check.py` already covered the *hand-derived reference* half of the
synthetic-first gate. `synth_*` covers the other half, planted-effect recovery,
and the four ways it gets passed without being performed: the recovery simply
fails, the only planted effect is zero (recovering a null says nothing about
finding an effect that is there), the tolerance is as wide as the effect, or the
real run precedes the synthetic one — synthetic-first is an ordering claim and
is checkable only against timestamps.

`cite_*` is deliberately **offline**. It checks the bookkeeping the online
verification produces, which is where the failures live: a DOI resolving to a
different paper, an unverified entry reaching a draft, a dangling key, an entry
marked verified with no query behind it, and a MATERIAL GAP cited anyway. One
network fixture in the suite is enough.

**A third batch** added the review-rendering gate: five
`render_*` fixtures and `review_render_check.py`. The gate says every artifact
presented at a human gate is delivered as a PDF and the checkpoint names it, so
the fixtures plant the four ways an author ends up reading the wrong thing: no
packet, a packet the checkpoint never names, a checkpoint handing over Markdown
paths instead, and a packet older than a source bound into it.

The stale case is the one that will actually happen, and it needs `setup.py` to
stamp mtimes: fixtures run in a temp copy, which gives every file the copy time,
so a fixture about ordering has to set the order it asserts.

**One fixture reaches the network** (`resolver_no_substitution`, marked
`requires: network`). An unreachable OpenAlex reports as **skipped**, never as a
gate failure: a suite that cries wolf about its environment is the same defect
it exists to catch in the gates. Getting that right took two passes — the first
version read a rate-limited API as a broken resolver, because the shim was
swallowing transport errors into "journal not found". Both halves are fixed.

```bash
python3 run_fixtures.py            # all fixtures
python3 run_fixtures.py --only registry -v
python3 run_fixtures.py --skills-root /path/to/other/skills
```

**Added**, after a cold run of the published tree stopped before G1:
four `reach_*` fixtures and `reachability_check.py`. The gate they cover is
stage reachability. Seven skills carried `disable-model-invocation: true`,
including four funnel layers, so `run-pipeline` could not enter the stages its
own table names, and the harness also refuses the documented SKILL.md fallback
for those skills. Every other fixture passed throughout, which is the point: the
suite tested what gates do and nothing tested whether a stage could be called at
all. One of the four fixtures exists only because the first draft of the checker
required a hyphen in a skill name and silently skipped `handoff`.

## Why this exists

`workflow/pipeline-design.md` §4 lists twenty-odd machine gates. Every one of
them asserts that something cannot pass. Without these, nothing asserts that
the gate itself works. The failure mode is not hypothetical: a recount once
built its adjacency test on the same expression as the count it was auditing, so
it agreed with itself and compounded the error rather than catching it. A checker that shares an assumption with the artifact it checks
passes silently, and the only thing that finds it is an artifact planted to
fail.

The paper this comes from runs a seven-fixture suite against its own scorer,
on a taxonomy of wrong estimator, wrong sample, wrong inference, wrong fixed
effects, wrong output, hard-coded output, and package-default failure. The
mapping to our gates is in the table below.

## Both directions are tested

A planted defect a gate passes is a hole in the gate. A clean case a gate
fails is a gate that cries wolf, and that is the same defect wearing different
clothes: a gate whose warnings are routinely wrong stops being read. So the
suite carries clean fixtures too — 22 of 82 — including a comment-only edit
that must **not** register as stale, and a count whose two derivations agree.

This is the symmetry the decision audit already uses when it audits advances
as well as kills, for the same reason: a checker run in one direction measures
its own disposition rather than the thing it checks.

## What each fixture plants

| Fixture | Gate | Planted defect |
|---|---|---|
| `ledger_key_missing` | claim-ledger validate | result file lacks the key the claim names |
| `ledger_drift` | claim-ledger validate | paper prints a number the source no longer holds |
| `ledger_quote_fabricated` | claim-ledger validate | textual claim quotes what the source does not say |
| `ledger_mechanism_empty` | claim-ledger validate | number traces, meaning does not |
| `ledger_clean` | claim-ledger validate | — |
| `crossref_unregistered_output` | claim-ledger cross-ref | a results file no registered script declares |
| `crossref_stale_evidence` | claim-ledger cross-ref | script edited after the results it backs |
| `crossref_clean` | claim-ledger cross-ref | — |
| `macros_typed_literal` | generated values | a macro-backed number also typed in prose |
| `macros_unused` | generated values | a claim that left the paper without leaving the ledger |
| `macros_double_source` | generated values | macro claim keeps its own copy of the value |
| `macros_unaccepted_move` | generated values (emit) | the source moved and the paper would reprint it unread |
| `macros_clean` | generated values | — |
| `registry_unregistered_script` | script-registry audit | code on disk that no manifest declares |
| `registry_output_missing` | script-registry audit | declared output absent from disk |
| `registry_stale_output` | script-registry audit | script's code changed, output never rerun |
| `registry_comment_only_edit` | script-registry audit | — (a comment is not a reason to rerun an estimation) |
| `registry_no_docstring` | script-registry audit | — (an undocumented script must be reported) |
| `registry_clean` | script-registry audit | — |
| `quarantine_path_leak` | quarantine check | downstream artifact names a `quarantine/` path |
| `quarantine_quote_leak` | quarantine check | advocacy copied across the wall without naming the path |
| `quarantine_clean` | quarantine check | — |
| `count_expression_mismatch` | counting definition | count computed at one unit, labelled at another |
| `count_derivations_disagree` | counting definition | terminal count whose two derivations disagree |
| `count_same_expression_twice` | counting definition | the recount reruns the same expression |
| `count_clean` | counting definition | — |
| `estimand_package_default` | manual-first reference | a clean-running package call computes a different estimand |
| `estimand_derivations_disagree` | manual-first reference | the two hand derivations disagree |
| `estimand_clean` | manual-first reference | — |
| `g1_padded_slate` | G1 threshold | the old menu's count guarantee returning |
| `g1_gate_f_ignored` | G1 threshold | a design the data cannot carry, awarded the top rung |
| `g1_capped_no_route` | G1 threshold | a capped verdict with no cheapest action — a label, not a route |
| `g1_placement_language` | G1 threshold | a rung asserting an editorial outcome |
| `g1_missing_gate_basis` | G1 threshold | a gate cleared without saying checkable or judged |
| `g1_empty_no_diagnosis` | G1 threshold | an empty slate with no DECLINE route named |
| `g1_zero_clears_diagnosed` | G1 threshold | — |
| `g1_many_clear` | G1 threshold | — (six clear and six are presented; the old menu capped at five) |
| `resolver_no_substitution` | journal-name resolution | — (`Review of Finance` must resolve to itself or to nothing, never to *International Review of Economics & Finance*) |
| `g1_fallthrough_clean` | G1 fallthrough tier | — (empty slate, tier labelled, zero stated first) |
| `g1_fallthrough_beside_slate` | G1 fallthrough tier | tier shown next to a non-empty slate — padding by another route |
| `g1_fallthrough_zero_buried` | G1 fallthrough tier | cards precede the `no card cleared` line, so the zero reads as their footnote |
| `g1_fallthrough_described_as_cleared` | G1 fallthrough tier | a card in the tier described as clearing the bar |
| `g1_fallthrough_counts_summed` | G1 fallthrough tier | the two tiers added into one count |
| `g1_fallthrough_unlabelled` | G1 fallthrough tier | tier cards carry no `tier` key, so they read as slate items |
| `datareq_clean` | data request | — (a required request, one probed and one honestly unprobed candidate, a fallback) |
| `datareq_none_clean` | data request | — (`status: none`, nothing else populated) |
| `datareq_quantity_is_ingredient` | data request | the quantity named as a table, sending the author shopping for the wrong thing |
| `datareq_no_fallback` | data request | a `required` request with no fallback — a data purchase in disguise |
| `datareq_unbacked_probe` | data request | an expected match rate presented as a verified probe |
| `datareq_block_missing` | data request | a pilot report that cannot say it wants data |
| `datareq_none_but_populated` | data request | `status: none` beside a populated request |
| `g1accept_clean` | G1 acceptance | — (a card that cleared, taken from the slate) |
| `g1accept_fallthrough_disclosed` | G1 acceptance | — (a fallthrough card taken forward, with the author's reason recorded) |
| `g1accept_fallthrough_undisclosed` | G1 acceptance | a card that did not clear, carried forward with no reason — the tier becoming the old menu |
| `g1accept_tier_contradicts` | G1 acceptance | `cleared_threshold: yes` on a card filed in the fallthrough tier |
| `g1accept_discharged_no_evidence` | G1 acceptance | an objection discharged with nothing named as having answered it |
| `g1accept_no_objections` | G1 acceptance | an acceptance record claiming the debate raised nothing |
| `g1accept_silent_disclosure` | G1 acceptance | disclosure absent rather than `none` — silence read as a value |
| `proposal_clean` | G1 research proposal | — (seven sections in order, discipline named, novelty argued) |
| `proposal_fallthrough_labelled` | G1 research proposal | — (a fallthrough proposal carrying its did-not-clear line) |
| `proposal_fallthrough_unlabelled` | G1 research proposal | a capped card's proposal reading as though it had cleared |
| `proposal_missing_implications` | G1 research proposal | a section of the outline simply absent |
| `proposal_no_discipline` | G1 research proposal | background naming a topic but no discipline |
| `proposal_novelty_asserted` | G1 research proposal | novelty claimed rather than argued against named work |
| `proposal_title_is_abstract` | G1 research proposal | a working title written as an abstract |
| `proposal_placement_language` | G1 research proposal | a proposal predicting an editorial outcome |
| `proposal_directional` | G1 research proposal | a proposal stating what the result will be (pilot firewall) |
| `intro_clean` | Introduction formula | — (gap in ¶1, design ¶2, result ¶3, roadmap present) |
| `intro_no_gap` | Introduction formula | ¶1 motivates but never says what is missing |
| `intro_slow_to_design` | Introduction formula | what the paper does slips past ¶2 |
| `intro_citation_heavy` | Introduction formula | heavy citation before the contribution paragraphs |
| `intro_criticises_prior_work` | Introduction formula | "prior literature has failed to" |
| `intro_passive_voice` | Introduction formula | "regressions are estimated ... results are discussed" |
| `intro_has_footnote` | Introduction formula | a footnote in the introduction |
| `intro_no_roadmap_clean` | Introduction formula | — (no roadmap: the default, and correct) |
| `intro_roadmap_narrates` | Introduction formula | a surviving roadmap narrating the paper section by section |
| `ledger_complete` | Run ledger | — (a complete package passes `--final`) |
| `ledger_scaffold_refused` | Run ledger | an empty scaffold passing `--final` would make the gate inert |
| `ledger_session_without_transcript` | Run ledger | a queued session whose transcript was never written |
| `ledger_unattributed_data_file` | Run ledger | a data file no registered script produces |
| `ledger_queue_unreconciled` | Run ledger | queue rows never reconciled into the human time log |
| `ledger_missing_artifact` | Run ledger | a required submission artifact absent |

## Three gates had no implementation, and now have one

`checkers/g1_slate_check.py` covers the G1 threshold gate: its two decay-prone
properties are checked rather than described.
**Padding** — the old menu guaranteed 3-5 items from whatever band existed,
which is what made "nothing clears the bar" unsayable, so a slate count
exceeding the cards that cleared fails. **The promote half** — a
`strong-field-candidate` with no capping gate and no cheapest action is a label
rather than a route, and the positive half of the gate has quietly become an
annotation again. It also enforces Gate F's refusal, the per-gate
checkable/judged split, and the ban on predicted placements.

`checkers/quarantine_check.py` and `checkers/count_check.py` are also new. Both
gates were specified in prose — the design doc calls the quarantine wall "a
grep-level check" and `idea-pilot` says the harness re-executes every count —
and neither had anything to run. A gate nobody can run is a gate whose state
nobody knows.

`checkers/estimand_check.py` implements the manual-first reference rule
`run-analysis` took on the same day. Its fixture is the concrete case: on a
locked staggered panel with unequal cohort sizes, the uniform average over
supported cells is **1.667** and the group-size-weighted aggregate that
`aggte(type="simple")` returns is **2.333**. Neither call errors. A
package-versus-package cross-check cannot see a 40% gap that is entirely a
disagreement about the estimand, which is why the reference is now derived by
hand first and the package is the thing under test.

All three checkers are candidates for promotion to `tools/` once a live run
has used them.

## What the runs have found

**Journal resolution.** `_resolve_source_ids` in
`tools/free_corbis_mcp.py` took the first fuzzy search hit with no check that it
was the journal asked for, so `Review of Finance` resolved to *International
Review of Economics & Finance* — a different journal with 5,991 works. An early
calibration build is the known casualty: 16 accounting venues and 14
out-of-scope ones entered a finance anchor as archetype analogs. It also
swallowed transport errors into `None`, reporting "no such journal" when the
truth was "could not ask". Both fixed; `resolver_no_substitution` holds them and
goes red against the pre-fix file.

## What the first run found

`registry.py`'s no-docstring and TODO warnings sat inside the `if unstamped:`
block and read the loop variable after the loop had ended. They reported at
most one script, always the last one scanned, and only when some entry
happened to be unstamped. Fixed the same day; `registry_no_docstring` is the
fixture that holds it fixed. It fails against the pre-fix file and passes
against the current one, which is the only evidence worth having that a
fixture tests anything.

Still open, not changed here: `script-registry`'s own description says audit
"fails on ... missing docstrings" while the code warns. One of the two is
wrong and the choice is the author's.

## Verifying the suite itself

The suite has to be able to go red, or its green means nothing:

```bash
cp -R ../../../.claude/skills /tmp/weakened-skills
# disable one check in /tmp/weakened-skills/claim-ledger/scripts/claim_ledger.py
python3 run_fixtures.py --skills-root /tmp/weakened-skills
```

Disabling the drift comparison turned exactly one fixture red (`ledger_drift`,
"expected nonzero exit, got 0") and left the other 28 alone. Run this after
any change to a gate.

## Fixture format

One directory per fixture. `fixture.json` declares the gate, the defect class,
the expected exit status, and the text the report must (or must not) name;
`setup.py` is optional and runs first for fixtures that need mtimes set or a
registry stamped. Fixtures run in a temp copy, so nothing here mutates the
source tree. Placeholders `{python}`, `{skills}`, `{checkers}`, `{dir}` are
substituted into `cmd`.

## What the suite still does not cover

Stated because a suite that lists only its coverage reads as complete. The gate
table in `workflow/pipeline-design.md` §4 has roughly twenty-five entries; these
have **no planted-failure fixture**:

| Gate | Why it is still uncovered |
|---|---|
| Synthetic-first (**half covered**) | The estimand half **is** covered: `estimand_package_default` plants a clean-running call that computes a different estimand, and `estimand_derivations_disagree` plants two hand derivations that disagree. What is **not** covered is the other half of the gate — recovering a *planted effect on synthetic data* before the real run. An earlier version of this table listed the whole gate as uncovered and described the missing fixture as exactly the one that already exists; overstating a gap sends someone to build what is already there, which is the mirror of understating one |
| Citation verification | needs a planted `.bib` entry whose metadata does not match the paper it claims. **The highest-value gap now**: an unverifiable citation reaching a draft is the L6 failure, and nothing plants it |
| Rebuilds from source (`make verify`) | needs a fixture repo with a real build graph; expensive to plant, and the clean-rebuild property is partly covered by `registry_stale_output` |
| Pre-registration commit | needs a git fixture; the property (S6 refuses without a committed freeze) is a one-line check but the fixture needs a repo |
| Reachability | the `data_request` fixtures cover the adjacent block on the same report; the ```reachability block's own rules (quantity-not-ingredient, one alternative construction, `infeasible-unchecked` on absence) are checked by no fixture |
| Novelty gate (step 1.5) | `CONTRIBUTION-NULL` needs a second confirmer, a quoted verified claim, and a decision-audit verdict — three properties, none planted |
| Pilot authorization | both entries (themed pre-pilot, swarm no-KILL) unchecked |
| Decision audit | layer-matched controls, quoted disputed text, named defect class — unchecked |
| Peek ledger / pilot firewall | anchored-mode gates; unchecked, and not exercised by an `open`-mode run |
| Funnel floors, profile freshness, anchor existence, panel reach | unchecked |

**Citation verification is now the single highest-value gap**, and it is real:
nothing plants a `.bib` entry whose metadata contradicts the paper it claims. It
is the one remaining unfixtured gate that would put a defect **into the paper**
rather than into a decision. Due before S7 runs, not before the run starts.
Synthetic-first's remaining half (planted-effect recovery) is second.
