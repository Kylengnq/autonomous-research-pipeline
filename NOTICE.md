# Notice

This pipeline is released under the MIT License (`LICENSE`). Two things in it
are not ordinary source code and are worth stating plainly.

## Prior work this was written against, and not from

Before any skill here was written, six public repositories of research skills
were cloned and audited: what each claimed to contain against what it actually
contained, its license, its structure, and which stages of a research pipeline
it had something to teach. The audit's standing rule was that nothing would be
copied. The skills here were written from scratch, and the repositories were
read as study material.

| Repository | License |
|---|---|
| [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) | MIT |
| [flonat/claude-research](https://github.com/flonat/claude-research) | MIT |
| [AlessandroCaforio/Academic-Writing](https://github.com/AlessandroCaforio/Academic-Writing) | MIT |
| [claesbackman/AI-research-feedback](https://github.com/claesbackman/AI-research-feedback) | MIT |
| [franklee16/academic-research-skills](https://github.com/franklee16/academic-research-skills) | none stated |
| [imbad0202/academic-research-skills](https://github.com/imbad0202/academic-research-skills) | custom |

Three findings from that audit shaped what is here, and the credit belongs with
the repositories that demonstrated them. The first is that the strongest peer
review machinery treats referee disposition and journal calibration as
parameters rather than as prompt flavour, which is why `peer-review` samples
dispositions and reports a decision distribution. The second is that claim
verification appeared independently in three of the six, which was the evidence
that it is required rather than optional: `claim-ledger` exists because of it.
The third is a negative finding. Hardcoded absolute paths and sprawling
environment flags were the recurring maintainability defect across all six, and
the rule that no skill here hardcodes a path, that every path comes from
`pipeline-config.md`, is a direct response.

None of those repositories is redistributed here, in whole or in part.

## Journal standards

`references/journal-standards/` paraphrases the expectations of specific
journals, assembled from editorial statements, published submission guidance,
and a structured reading of recent articles.
`references/journal-standards/sources.md` records what each claim rests on. These are summaries of observable norms in our own words. They
are not reproduced editorial material, and they carry no endorsement from any
journal.

See `DATA.md` for the provenance of the calibration set.
