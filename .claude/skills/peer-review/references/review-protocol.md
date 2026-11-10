# Review protocol: verification, R&R ledger, decision letter

Used by `peer-review` steps 5-7 and `--rr` mode.

## Finding verification (step 5)

Every referee finding is a lead, not a verdict. Before a finding may enter
the editorial synthesis:

1. **Locate.** The cited passage, table, or number must exist at the cited
   location. A finding citing nothing is dismissed.
2. **Reproduce the objection.** For a numeric flag, recompute from the
   results file. For a logic flag, quote the two passages alleged to
   conflict. For a literature flag, run the search; the missing paper must
   exist and say what the referee claims.
3. **Check the design's answer.** If the manuscript already addresses the
   objection (a control, a robustness check, a stated scope condition),
   the finding is dismissed as answered, citing where.
4. **Log.** Confirmed findings enter the synthesis with their evidence.
   Dismissed flags get one line each in the verification log: finding,
   reason dismissed. The log ships with the decision letter so the triage
   is auditable.

False-positive discipline: demanding generality the paper never claimed,
flagging a stated limitation as a hidden flaw, or requiring evidence the
journal's bar does not require are dismissals, not findings.

## Triage classes (step 6)

- **Fatal**: invalid inference, broken identification, untraceable or
  irreproducible numbers, a contribution the literature already delivers,
  a claim below the profile's identification bar.
- **Addressable**: fixable with bounded work: a missing robustness check,
  an overclaimed sentence, a missing citation, an unclear derivation.
- **Taste**: reasonable disagreement: framing preferences, additional
  analyses beyond the bar, exposition style.

The decision letter reports all three classes; only fatal and addressable
drive the decision.

## Critic-fixer loop (step 7)

- Round = apply fixes for addressable findings, then re-review changed
  sections only (the full pipeline is not re-run unless a fix touched
  analysis).
- Exit: two consecutive rounds with no confirmed findings, or the hard cap
  of five rounds.
- A fix that touches analysis re-triggers the affected machine gates
  (claim ledger, registry audit) before the re-review round counts.
- Fatal findings are never "fixed" inside the loop by weakening the claim
  silently; a claim downgrade is presented to the author.

## R&R ledger (`--rr` mode)

One row per prior concern:

| # | Referee | Prior concern (one line) | Response location | Status |
|---|---|---|---|---|
| 1 | B | ... | p.14, tab 6 | Resolved / Partial / Not addressed |

Rules: same referees and dispositions as the prior round; a Partial or Not
addressed on a fatal-class concern is a rejection at round 3; new findings
are admitted only where the revision introduced new material.

## Decision letter template

```text
Journal: <profile>    Round: <n>    Date: <date>

Decision: <reject | major revision | minor revision | accept>

Summary of the paper (3 sentences, the editor's own words).

Assessment: contribution panel outcome, desk criteria, and how the
referee reports agree or divide.

Fatal findings: <numbered, each with location and evidence>
Addressable findings: <numbered, each with location and the fix required>
Taste (non-binding): <numbered>

What a successful revision must do: <the short list>

Attachments: referee reports (A, B, replication, opposition),
verification log, fix log (rounds so far).
```

In `--variance` mode the letter is replaced by a decision distribution:
the table of draws (disposition pair -> decision) plus the modal decision
and the findings that appeared in every draw (those are the paper's real
problems).
