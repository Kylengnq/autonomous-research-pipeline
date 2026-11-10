# Referee dispositions and special-referee protocols

Used by `peer-review` step 4. Referee A and B take one disposition each,
chosen by the editor to stress the paper's weak points and deliberately
opposed to each other. The replication and opposition referees are always
seated.

## The six dispositions

| Disposition | Prior | Attacks first |
|---|---|---|
| STRUCTURAL | the paper's architecture is the risk | framing, section logic, whether the design answers the question asked, contribution placement |
| CREDIBILITY | identification is the risk | exclusion restrictions, parallel trends, treatment endogeneity, SE/clustering choices, power |
| MEASUREMENT | the variables are the risk | proxy validity, measurement error, sample construction, survivorship, winsorization choices |
| POLICY | relevance is the risk | economic magnitude, external validity, so-what for practitioners or policy, anchored comparisons |
| THEORY | the mechanism is the risk | whether hypotheses follow from a mechanism, competing channels, model-free storytelling |
| SKEPTIC | the result is the risk | fragility, specification search, publication-bias patterns, too-good-to-be-true magnitudes |

Each dispositioned referee writes a full report to the journal profile's
standards: summary, major concerns, minor concerns, and a recommendation.
Every finding cites a manuscript location (section, table, or line). The
evidence-ladder check is embedded: for each load-bearing claim touched,
state the rung the evidence reaches (statement / fact / representative
data / causal proof) and flag language above its rung.

## Replication referee protocol

Goal: every printed number is re-derivable from the project's artifacts.

1. Read the claim ledger, the script registry, and the results files.
2. For every table and figure: re-derive each number from its results
   file; confirm the value at printed precision; confirm the results file
   is a declared output of a registered script; confirm the producing
   script is not newer than the results file.
3. Check run order: the registry's input/output graph must run the
   pipeline from raw inputs to every cited results file without a missing
   step.
4. Spot-run where cheap: if a registered script is stdlib-or-declared-deps
   and runs in seconds, run it and compare.
5. Report format: a table of checked numbers (location, printed value,
   derived value, verdict) plus a list of untraceable or stale items.
   Untraceable numbers are fatal-class findings.

## Opposition referee protocol

Goal: find every flaw the paper could contain. Over-flagging is expected
and accepted; the verification step filters. Do not soften.

Flaw checklist, in order:

1. **Methodology.** Estimator choice, identification, inference, power,
   robustness coverage; anything the credibility and measurement
   dispositions would find, hunted without their politeness.
2. **Literature.** Missing closest papers, mischaracterized citations,
   contribution claims the cited literature already delivers, threat
   papers unaddressed.
3. **Findings.** Internal contradictions between tables, magnitudes
   inconsistent across sections, results whose economic size is trivial
   despite statistical significance, nulls dressed as findings.
4. **Discussion.** Interpretations the results do not license, competing
   channels ignored, limitations understated.
5. **Contribution and significance.** Would a top-journal reader care;
   what exactly is displaced; is the increment real or framing.
6. **Coherence and logic (the whole-paper pass).** Read the manuscript
   end-to-end as one argument chain: introduction promises vs results
   delivered; hypotheses vs the mechanisms argued; results vs discussion
   claims; conclusion vs what the design can carry; any two sections that
   contradict each other; any term whose meaning drifts between sections;
   any figure or table the text never uses; any claim that appears only
   in the abstract.

Report format: a numbered flaw list, each with location, the flaw in one
sentence, and why it matters. No recommendation; the opposition referee
does not vote, it hunts.
