# Data provenance

One file here is a dataset rather than code, and a reader is entitled to know
where it came from before using it to judge research ideas.

## `references/top_journal_calibration.json`

**What it is.** 141 published papers, each tagged on 22 fields, used as the
external anchor for idea scoring. Without it, scoring has nothing to calibrate
against and `idea-scoring` refuses to run rather than issue uncalibrated
verdicts. Alongside the papers it carries indexes over mechanism, field tag,
topic area, identification style and failure mode.

**Where the papers came from.** Pinned OpenAlex source identifiers, each
verified by exact journal name before any work was pulled. OpenAlex metadata is
open. Paper identifiers in the file are OpenAlex `W…` keys, so every entry can
be resolved back to its source record.

**What the fields are.** Authored one-line summaries: the paper's question, its
mechanism, what it displaces, the failure modes it avoids. These are judgments
about published work, written for this purpose. The longest value in the file is
197 characters. It contains no abstracts, no body text, no figures, and no
tables. It is commentary and metadata, not reproduced content.

**One class is a substitute, and is labelled as one.** The design called for a
"never placed" class: working papers that circulated and never landed. SSRN
carries that population and OpenAlex holds no abstracts for it, 0 of 125
sampled, so every derived field would have been underivable. The `stalled` class
is the substitute actually used: field-journal papers 24 to 48 months old with
fewer than five citations. Published, old enough to have been noticed, and not
noticed. That is a weaker construct than the one specified, and the file says so
in its own `selection_bias_summary` rather than quietly swapping one for the
other.

**Known gaps, carried in the file.** One journal is excluded because OpenAlex
splits it across two records under a former name. 27 of the top-tier entries
came from an earlier themed pull on a single topic and carry that
neighbourhood's slant. The `stalled` class is thin in one topic area against its
own per-area floor. Each of these is stated in `selection_bias_summary`, and
each entry carries a `calibration_confidence` value.

## Building your own

`calibrate-rubric` is the recipe. It pulls recent acceptances and stalled
analogs through the literature backend, tags them on the same schema, and writes
the same file. Run it if you want an anchor built for your own field, or to
refresh this one: `idea-scoring` treats a calibration set older than six months
as stale and blocks on it.

## Everything else

No other data ships here. `project-template/data/` is empty, by design. The
literature backend reads public APIs (OpenAlex, FRED) at run time and caches
nothing into the repository.
