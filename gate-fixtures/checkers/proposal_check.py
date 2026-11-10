#!/usr/bin/env python3
"""G1 research proposal gate: the seven-section outline, made executable.

Every card presented at G1 -- slate and fallthrough alike -- carries a 1-2 page
research proposal (`idea-debate` step 4b). The proposal is a **rendering** of the
card's verified handoff artifacts, never new generation, which is what makes it
safe to add to a stage otherwise built to keep speculation out.

Four properties decay silently and are therefore checked rather than described:

  sections   -- the outline is not decorative. A proposal missing its literature
                review or its implications is a description of an idea, not a
                proposal, and the omission is invisible in prose that reads well.
  discipline -- the setting is the topic AND the discipline. Different
                disciplines read the same problem into different questions, so a
                background naming only the topic has skipped half the section.
  novelty    -- "in what way is your question new?" is the evaluator's question.
                A proposal that asserts novelty rather than arguing it against
                named prior work has answered nothing.
  the label  -- a polished two-page proposal is precisely the artifact that could
                launder a capped card into looking like a cleared one, so a
                fallthrough proposal must say on its face that it did not clear.

Usage:
    python3 proposal_check.py --proposal FILE [--tier slate|fallthrough]
"""

import argparse
import re
import sys
from pathlib import Path

# In order. The proposal must present them in this sequence.
SECTIONS = [
    ("title",        r"working title"),
    ("background",   r"background"),
    ("questions",    r"research question"),
    ("literature",   r"literature review"),
    ("method",       r"data and (?:proposed )?methodology|data and method"),
    ("implications", r"implications"),
    ("references",   r"references|bibliography"),
]
WORD_MIN, WORD_MAX = 800, 1200
DISCIPLINE = r"\b(finance|financial economics|economics|econometrics|accounting|" \
             r"strategy|organisational behaviour|organizational behaviour|" \
             r"real estate|marketing)\b"
NOVELTY = r"\b(unlike|in contrast to|whereas|differs from|has not been|" \
          r"no (?:paper|study|work) (?:has|yet)|closest work|neither of these|" \
          r"what is new|extends?|displaces?)\b"
# A rung asserts gate clearance, never an editorial outcome.
PLACEMENT = [r"would reach", r"would place", r"will be accepted",
             r"is a top-3 paper", r"publishable in", r"would be published in"]
# The pilot firewall: a proposal states what it will test, never what it will find.
DIRECTIONAL = [r"we (?:expect|anticipate) to find", r"the results will show",
               r"this will demonstrate that", r"we will confirm"]


def headings(text):
    """Ordered (level, text) for every markdown heading and bold-only line."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            out.append(m.group(2))
            continue
        m = re.match(r"^\*\*(.+?)\*\*:?\s*$", line.strip())
        if m:
            out.append(m.group(1))
    return out


def body_words(text):
    stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    stripped = re.sub(r"^#{1,6}\s+.*$", "", stripped, flags=re.MULTILINE)
    return len(stripped.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--proposal", required=True)
    ap.add_argument("--tier", choices=["slate", "fallthrough"], default="slate")
    args = ap.parse_args()

    path = Path(args.proposal)
    if not path.is_file():
        print(f"FAIL: no proposal at {path}. Every card presented at G1 carries "
              f"one — four presented cards means four proposals.")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    heads = headings(text)
    failures = []

    # --- sections present and in order ---
    found_at = {}
    for key, pat in SECTIONS:
        for i, h in enumerate(heads):
            if re.search(pat, h, re.IGNORECASE):
                found_at[key] = i
                break
    for key, _ in SECTIONS:
        if key not in found_at:
            failures.append(f"missing section: {key}. The outline is not "
                            f"decorative — a proposal without it is a "
                            f"description of an idea, not a proposal.")
    present = [k for k, _ in SECTIONS if k in found_at]
    order = [found_at[k] for k in present]
    if order != sorted(order):
        failures.append(f"sections out of order: {', '.join(present)}")

    # --- no empty section ---
    for i, key in enumerate(present):
        start = found_at[key]
        end = found_at[present[i + 1]] if i + 1 < len(present) else None
        seg_heads = heads[start:end] if end else heads[start:]
        # crude: locate the heading in the raw text and measure to the next one
        h_text = heads[start]
        idx = text.find(h_text)
        nxt = text.find(heads[end], idx) if end is not None and end < len(heads) else len(text)
        body = text[idx + len(h_text):nxt]
        n_body = len(body.split())
        if key == "title":
            # A title is one line by definition, so the body-prose floor does not
            # apply to it. What does apply is the opposite bound: the guidance
            # asks for concise and descriptive, and a title running past a clause
            # or two has stopped being a title.
            if n_body == 0:
                failures.append("working title section is empty")
            elif n_body > 25:
                failures.append(f"working title runs {n_body} words; a title is "
                                f"concise and descriptive, not an abstract")
        elif n_body < 12:
            failures.append(f"section {key!r} is present but effectively empty")

    # --- length ---
    n = body_words(text)
    if n < WORD_MIN:
        failures.append(f"{n} words, below the {WORD_MIN} floor")
    elif n > WORD_MAX:
        failures.append(f"{n} words, over the {WORD_MAX} ceiling. Concision is "
                        f"a criterion here, not a preference: running long fails "
                        f"the requirement rather than merely padding it.")

    # --- background names a discipline ---
    if "background" in found_at:
        idx = text.find(heads[found_at["background"]])
        nxt = text.find(heads[found_at["questions"]], idx) if "questions" in found_at else len(text)
        if not re.search(DISCIPLINE, text[idx:nxt], re.IGNORECASE):
            failures.append("background names no discipline. The setting is the "
                            "topic AND the discipline; naming only the topic "
                            "skips half the section.")

    # --- questions argue novelty ---
    if "questions" in found_at:
        idx = text.find(heads[found_at["questions"]])
        nxt = text.find(heads[found_at["literature"]], idx) if "literature" in found_at else len(text)
        if not re.search(NOVELTY, text[idx:nxt], re.IGNORECASE):
            failures.append("the research-questions section never answers what "
                            "is new. Novelty is argued against named prior work, "
                            "not asserted.")

    # --- references non-empty ---
    if "references" in found_at:
        idx = text.find(heads[found_at["references"]])
        tail = text[idx + len(heads[found_at["references"]]):]
        if len(re.findall(r"\(\d{4}[a-z]?\)|\b\d{4}\b", tail)) < 2:
            failures.append("references section lists fewer than two entries")

    # --- the tier label ---
    if args.tier == "fallthrough":
        if not re.search(r"did not clear|does not clear", text, re.IGNORECASE):
            failures.append(
                "fallthrough proposal does not state that the card did not clear "
                "the threshold. A polished proposal is exactly the artifact that "
                "could launder a capped card into looking like a cleared one.")

    for pat in PLACEMENT:
        for m in re.finditer(pat, text, re.IGNORECASE):
            failures.append(f"predicted placement ({m.group(0)!r}); a proposal "
                            f"asserts gate clearance, never an editorial outcome")
    for pat in DIRECTIONAL:
        for m in re.finditer(pat, text, re.IGNORECASE):
            failures.append(f"directional expectation ({m.group(0)!r}); the "
                            f"proposal states what will be tested, never what "
                            f"will be found — that is the pilot firewall")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"proposal: {len(failures)} problems")
        return 1
    print(f"proposal OK: 7 sections in order, {n} words, tier {args.tier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
