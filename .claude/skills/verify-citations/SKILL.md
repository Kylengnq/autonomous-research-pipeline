---
name: verify-citations
description: "Audits citations: every cite key resolves to a BibTeX entry, every entry is verified field-by-field against literature search, and every DOI resolves to the cited paper. Blocking gate at the literature stage and again before a draft is done; unverified entries are barred from drafts."
---

# Verify Citations

No unverified citation enters a draft. Fabricated citations are the
best-documented failure of AI-assisted writing, and most are compound
(a plausible entry wearing a real identifier), so this audit checks
fields and resolves identifiers; it never trusts surface plausibility.

## When to use (the two gate points)

- **S2 gate:** before new entries enter `bib_file`.
- **S7 gate:** before `draft-paper` may report the draft done.
- Also: any single entry on demand (`--key <bibkey>`).

## Workflow

1. Read `pipeline-config.md` for `main_tex`, `bib_file`, `search_log`.
2. Extract every `\cite`-family key from the `.tex` sources; read
   `bib_file` in full.
3. For each key, in batches of 5 searches (rate-limit rule in
   `<skills_root>/playbooks/error-escalation.md`):
   a. Key missing from `bib_file`: classify **MISSING**.
   b. Search the literature for `"{title}" {first author surname} {year}`;
      pull details for the best match.
   c. Compare field by field (authors, title, year, journal). If search
      returns nothing for a field, write `NOT FOUND IN SEARCH`; never fill
      a field from memory.
   d. **DOI check:** if the entry carries a DOI, resolve it and confirm it
      lands on the cited title. A DOI that resolves to a different paper is
      identifier hijacking: classify **MISMATCH** regardless of the other
      fields.
4. Classify each entry:
   - **OK**: all fields confirmed, DOI (if present) resolves correctly.
   - **PARTIAL**: authors and title confirmed; journal/volume unconfirmed.
   - **MISMATCH**: any field or the DOI contradicts search results.
   - **UNVERIFIED**: paper cannot be found by search.
   - **MISSING**: cited key with no BibTeX entry.
5. Write the audit report (counts, then one line per flagged entry) next to
   `bib_file`, and log the searches to `search_log`.

## Gate rules

- MISMATCH or MISSING fails the gate; fix before proceeding.
- UNVERIFIED entries are barred from drafts: keep the entry out of
  `bib_file`, or mark the citation site
  `[MATERIAL GAP: unverified citation <key>]` until confirmed.
- PARTIAL may proceed at S2 but must be resolved or downgraded before S7
  passes.

## Outputs

- The audit report file; updated `search_log`; a dated `lab_notebook`
  entry.

## Validation

- Every flagged entry names the failing field(s).
- No field in the report was filled from memory.
- Exit state is explicit: gate passed, or the list of blocking entries.
