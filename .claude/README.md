# Skills

The skills every project in this folder runs. Claude Code discovers them
automatically when launched from the folder above this one.

`pipeline-config.template.md` is copied into a project as `pipeline-config.md`
and filled in. `playbooks/` holds two operational documents the skills reference:
`error-escalation.md` (what a stage does when something fails) and
`gate-modes.md` (which gates may be resolved without a human, and which may not).

Keep these under version control. A mid-run skill edit needs to be recoverable,
and a rule changed without a diff to read is how a pipeline quietly stops doing
what its documentation says.

These are the only copies. `../docs/skill-specs.md` describes what each one must
do and why, but it does not run.
