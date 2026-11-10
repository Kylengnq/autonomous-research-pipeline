#!/usr/bin/env python3
"""Citation verification check (stdlib only, offline).

`pipeline-design.md` §4: no unverified citation appears in any draft, at S2 and
again at S7. `verify-citations` performs the verification; this checker asserts
that the gate around it holds, against artifacts planted to fail.

It is deliberately offline. The suite already carries one network fixture
(`resolver_no_substitution`) and one is enough: a gate suite that fails when an
API rate-limits is the same defect it exists to catch, reported against the
wrong thing. What is checked here is the *bookkeeping* the online step
produces, which is where the failures actually live.

Four defects, each seen in this project's own history or in the skill's rules:

1. **DOI hijack.** The entry's DOI resolves to a different work than the entry
   describes. `verify-citations` records the resolved title; a mismatch means
   the citation points somewhere else, and the draft asserts something the cited
   paper does not say.
2. **Unverified entry in a draft.** An entry still marked unverified, or
   carrying a Material Gap, is cited in the manuscript. Unverified entries are
   barred from drafts rather than flagged in them.
3. **Dangling key.** The draft cites a key with no bibliography entry.
4. **Verified from memory.** An entry marked verified with no `source_query`
   recorded. Field-by-field verification means a search returned it; an entry
   nobody can show a query for was verified against recall, which is the one
   thing the Material Gap rule forbids.

Inputs:

  entries.json  {key: {title, doi, resolved_title, verified, source_query}}
  draft.tex     the manuscript, scanned for \\cite / \\citep / \\citet keys

Usage:
    python3 citation_check.py --entries FILE --draft FILE
"""

import argparse
import json
import re
import sys
from pathlib import Path


CITE_RE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}")
GAP_RE = re.compile(r"\[MATERIAL GAP", re.I)


def normalise(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def cited_keys(tex: str) -> list:
    keys = []
    for match in CITE_RE.finditer(tex):
        for key in match.group(1).split(","):
            key = key.strip()
            if key and key not in keys:
                keys.append(key)
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entries", required=True)
    ap.add_argument("--draft", required=True)
    args = ap.parse_args()

    entries_path, draft_path = Path(args.entries), Path(args.draft)
    if not entries_path.is_file():
        print(f"FAIL: {entries_path} not found")
        return 1
    if not draft_path.is_file():
        print(f"FAIL: {draft_path} not found")
        return 1

    try:
        entries = json.loads(entries_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {entries_path} unreadable: {exc}")
        return 1

    tex = draft_path.read_text(encoding="utf-8")
    keys = cited_keys(tex)
    failures: list = []

    if not keys:
        print("FAIL: the draft cites nothing; there is no citation gate to pass "
              "and this is more likely a broken fixture than a clean paper")
        return 1

    for key in keys:
        entry = entries.get(key)
        if entry is None:
            failures.append(
                f"`{key}` is cited in the draft and has no bibliography entry. "
                f"A dangling key compiles to a question mark and reads as a "
                f"citation."
            )
            continue

        title = entry.get("title", "")
        resolved = entry.get("resolved_title")
        verified = bool(entry.get("verified"))
        query = entry.get("source_query")

        if not verified:
            failures.append(
                f"`{key}` is cited in the draft while still unverified. "
                f"Unverified entries are barred from drafts, not flagged inside "
                f"them."
            )
            continue

        if GAP_RE.search(json.dumps(entry)):
            failures.append(
                f"`{key}` carries a MATERIAL GAP and is cited anyway; the gap is "
                f"the reason it may not enter a draft"
            )
            continue

        if not query:
            failures.append(
                f"`{key}` is marked verified with no `source_query`. "
                f"Verification means a search returned the record; an entry with "
                f"no query behind it was verified from memory."
            )
            continue

        if resolved is not None and normalise(resolved) != normalise(title):
            failures.append(
                f"DOI mismatch on `{key}`: {entry.get('doi', '[no doi]')} "
                f"resolves to {resolved!r}, the entry claims {title!r}. The "
                f"citation points at a different paper than the one the draft "
                f"is citing."
            )

    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1

    print(f"citations OK: {len(keys)} cited key(s), every one resolved to a "
          f"verified entry whose DOI matches its title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
