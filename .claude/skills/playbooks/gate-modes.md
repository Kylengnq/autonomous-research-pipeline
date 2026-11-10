# Gate modes playbook

Every pipeline skill that touches a gate reads `gate_mode` from the paper
project's `pipeline-config.md` and follows this playbook. Two modes exist;
the gates themselves never disappear, only who decides them changes.

`<skills_root>` in skill files means the directory containing all the
pipeline skill folders and this `playbooks/` directory.

## The two modes

- **`gate_mode: human`** (default). The current protocol: the six judgment
  gates (G1 idea, G2 framing, G3 design freeze, G4 data calls, G5 survival,
  G6 title/overclaim) and session close are author decisions, recorded in
  `decisions_log`. Skills present options and stop; nothing proceeds past a
  gate without the author. Once the author decides, the decision is logged and
  the run continues into the next stage with that decision applied as an input,
  without a further prompt. Waiting is for the absence of an answer, not for a
  second confirmation of one.
- **`gate_mode: autonomous`**. No human request at any point. Each gate is
  decided by the pre-specified rule below, logged in `decisions_log` with
  the marker `auto-mode` in place of the author. Machine gates (freeze
  commit, synthetic-first, claim ledger, citation verification, compile,
  review convergence) are identical in both modes: they were never human.

The core principle of autonomous mode: **rule-or-stop, never guess.** Where
a rule below covers the decision, apply it and log it. Where no rule
covers it, the pipeline does not improvise a judgment call: it writes a
`[MATERIAL GAP: ...]` marker, sets the project status to PARKED in
`state_file`, and stops the stage. A parked project is the autonomous
analog of "ask the author"; it is never silently resumed with a guess.

## Per-gate autonomous rules

- **G1 (idea). Count the cards clearing `g1_threshold`, then apply the rule**
  (author decision, replacing an earlier always-PARK rule). S1b scores
  every surviving card on the four-rung ladder and returns the slate — every
  card at or above `g1_threshold`, default `top-generalist-candidate`.

  | Cards clearing the threshold | Autonomous action |
  |---|---|
  | **0, because Gate D could not clear** | **PARK, do not ARCHIVE.** The slate is `no verdict possible`, not `nothing cleared` — the calibration set has fewer than 8 in-field entries in a class the top rung depends on, so the cards were never judged. Log the per-class in-field counts and the rebuild as the next action. Archiving here would discard an unjudged slate on a fixable anchor problem. |
  | **0, on the merits, `g1_fallthrough: none`** | Run the slate-level DECLINE triage on the counters, log the route it names, and end the run **ARCHIVED** — finished work with a negative result, not PARKED. Nothing is owed to the next session. |
  | **0, on the merits, with a non-empty fallthrough tier** | **PARK, do not ARCHIVE and do not advance**. Run the DECLINE triage and log its route, then record the labelled fallthrough tier — each card with its capping gate, checkable-or-judged basis, cheapest clearing action, usable sample, binding constraint, and `data_request` block. Taking forward a card that did not clear the bar is exactly the judgment autonomous mode may not make, so the run stops and the author decides. Merging the tiers, or advancing the top fallthrough card because it is the best available, is the always-returns-items menu re-entering through the rule table. |
  | **0, on the merits, fallthrough tier also empty** | **ARCHIVED**, as above. Two empty tiers is a complete negative result. |
  | **1** | **Advance it.** Write `g1_acceptance.md`, log `auto-mode`, proceed to S2. |
  | **more than 1** | **PARK.** Record the slate, every verdict, and every capped card's gate and cheapest action. Choosing among designs that all clear the bar is a judgment about what is worth six months, and no rule here covers it. |

  Never rework a `strong-field-candidate` in autonomous mode. Rework is
  author-triggered in both modes, and the clinic's budget is one per idea; an
  unattended run that spent it would take the option away from the author it
  parked for.

  **Why a rule exists again.** An earlier removal of this rule was right about
  its target and wrong about its premise. Right: `panel_reach` is judged, not
  calibrated, and gating on it would gate on a judgment the stage had just
  stopped asserting. Wrong: the stated ground was that the calibration file was
  all top-3 acceptances with no held-out evidence for any lower rung. It is not:
  it carries an accepted class, a stalled class with failure-mode tags, and a
  small uncertain class. There is a contrast class. Read the file's own counts
  rather than any figure quoted on a page.

  What the ladder gates on is **not** reach. It is gate clearance — whether the
  card cleared the structural gates that top-3 papers clear, each gate marked
  checkable or judged. That is a claim about the card and its named sources. No
  rung here asserts a placement, and any artifact implying one is a validation
  failure, which is that earlier rule kept in the form that was right.

  `min_tier` is replaced by `g1_threshold` in `pipeline-config.md`; a config
  carrying `min_tier` is stale. **Consequence: a fully autonomous S1 to S2
  handoff exists again, on exactly one path — a slate of one.** A run that
  produces several good candidates still stops for the author, and a run that
  produces none now ends by itself instead of waiting to be told it failed.

  Rules that still apply when a *human* resumes from the PARK and a
  downstream stage later kills the chosen idea: re-enter here with the
  bench and walk the fallback precedence (pipeline-design.md S1b fallback
  triage) — bench, then unblocked blocked-registry entries, then
  revision-clinic output, then a fresh generation cycle if the cycle cap
  allows. Never promote a graveyard idea, and never advance an idea whose
  pilot verdict is `conditional` without the debate's one-round re-check
  on the stated condition.
- **G2 (framing).** Auto-approve only if the positioning names a specific
  displacement target and a non-empty threat list. Otherwise one bounded
  revision of the positioning, then PARK.
- **G3 (design freeze).** Auto-approve only if every pre-register refusal
  rule passes: no blank block, MDE at or below the equivalence bound, no
  realized-sample reference for past events, retrospective label where
  required. A refusal triggers at most one redesign loop (sample, bound,
  or design may change; refusal rules may not be weakened). Second
  failure: PARK. The freeze is still committed so git timestamps it.
- **G4 (data calls).** The prereg's block 3 must list a ranked set of
  acceptable sources, each with a passed liveness probe at freeze time.
  On source failure mid-run, take the next ranked source via a dated
  amendment (amendment-not-overwrite, as in human mode). List exhausted:
  PARK. A source never on the ranked list is never adopted autonomously.
- **G5 (survival).** Adopt the robustness-suite verdicts mechanically: the
  headline is the finding that passes the most checks; `confounded` and
  `underpowered` findings never headline and are reported under their
  verdict labels. If nothing survives, the paper is written as the
  pre-registered null statement. No verdict is re-litigated in prose.
- **G6 (title / overclaim).** Adopt the edmans-audit wording: the title
  and abstract must pass the audit with zero rung violations, and
  claim strength is capped at the audit's assessed rung. A fatal
  peer-review finding that survives the fix loop makes the manuscript a
  documented reject: it is archived with its decision letter, not spun.
- **Session close.** `handoff` runs automatically at the end of every
  autonomous session, followed by a git commit with the standard trailer.
  The author-activation rule is a human-mode rule.

## Escalation ladder in autonomous mode

Rungs 1 and 2 of `error-escalation.md` (bounded retry, flagged
degradation) are unchanged. Rung 3 ("human escalation") becomes
**rule-or-park**: apply the matching per-gate rule above; no matching
rule means PARK with the gap written where the decision would have gone.

## Disclosure

Autonomous mode is disclosed, not hidden, in the same spirit as the
retrospective-registration label:

- Every auto-mode gate entry in `decisions_log` carries the `auto-mode`
  marker and names the rule applied.
- `draft-paper` carries an "Autonomous mode: gate decisions made by
  pre-specified rule, no human review" statement into the paper's title
  footnote or introduction, alongside any retrospective-registration
  label.
- `resume` states the project's gate mode in its opening brief.

A reader may never mistake an autonomous paper for a human-gated one.
