# Call requirements

Fill this in from the call for papers of the venue you are submitting to, before
`/init-submission` runs. Several skills read it: `init-submission` confirms it
exists and is populated, `contribution-report` and `finalize-compliance` take the
eligibility floor from it, and the final checklist is checked against it.

It is a per-project parameter on purpose. Venues differ on what they ask an
AI-assisted submission to disclose, and a pipeline that hardcoded one venue's
rules would quietly apply them to every other.

## The venue

| Field | Value |
|---|---|
| Venue | `<journal or conference>` |
| Track or session | `<if the AI-workflow disclosure rules are track-specific>` |
| Submission deadline | `<YYYY-MM-DD>` |
| Eligibility floor | `<YYYY-MM-DD, or none>` |
| Call URL | `<link>` |

The eligibility floor is the date on or after which work must have started, where
the call states one. `init-submission` refuses to record a start date before it,
because a compliance record that claims work began earlier than the rules allow
is worse than no record.

## What the call asks for

Delete the rows that do not apply and add the ones that do.

| Requirement | Satisfied by | Status |
|---|---|---|
| Disclosure that AI was used, and how | `workflow.md` | |
| Full text of AI conversations | `conversations/` | |
| Log of human time | `human_time_log.md` | |
| Human versus AI contribution shares | `contribution_report.md` | |
| Model and configuration disclosure | `model_config.md` | |
| Data access and licensing statement | `data_access.md` | |
| Code and data availability | `reproduction.md` | |
| Author limits, lead-author limits | n/a, check against the call | |

## Rules that constrain the run itself

Some calls restrict who may work on the project, how many submissions an author
may be on, or whether the work must be new. Those cannot be checked by a file, so
write them here explicitly and read them before starting:

- `<rule>`
- `<rule>`

## Final checklist

- [ ] Every row above is either satisfied or marked n/a with a reason.
- [ ] The paper's appendices match what the submission artifacts say.
- [ ] The start date on record is on or after the eligibility floor.
- [ ] Submitted by the deadline, through the route the call specifies.
