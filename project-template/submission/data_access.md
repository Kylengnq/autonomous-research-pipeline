# Data Access

Every data source the project touched, with access windows. Reviewers will use
this to judge whether the AI workflow could in principle be reproduced.

State the project's source policy in one line here, because it decides what a
referee can collect: (free/public/keyless only | any source with a named access
route | held or licensed data carries the headline, with a replication plan).

## Data sources

Add a row the first time a source is touched, and keep `Last accessed` current.
A source that was considered and rejected belongs in the section below, not here.

| Source | Type | Access method | Credentials scope | First accessed | Last accessed |
|---|---|---|---|---|---|
| | | | | | |

**Credentials rule:** name the environment variable that holds a credential,
never the credential. A token pasted into this file or into a transcript is a
submission defect and must be scrubbed and rotated before the package ships.

## Data access at the initial prompt

What the project held when the initial prompt was issued. "Nothing" is the
common and expected answer, and it is the one that makes the crawl record
meaningful.

| Held at start | Detail |
|---|---|
| | |

## Sources considered and not used

Why a source was rejected is evidence about the design, and a referee who
wonders "why didn't they just use X" should find the answer here.

| Source | Why not used | Where the decision is recorded |
|---|---|---|
| | | |

## Replication plan

For every source that cannot simply be re-downloaded: what ships with the paper
(derived extract, schema, code, a synthetic twin), what cannot ship, and why.

| Source | Spine (private / hybrid / public) | What ships | What cannot, and why |
|---|---|---|---|
| | | | |
