#!/usr/bin/env python3
"""Introduction gate: the paragraph formula's checkable rules (stdlib only).

Most of what makes an introduction good is judgment and cannot be checked. Some
of it is mechanical, decays silently, and is exactly what a tired author gets
wrong at 2am. This checks only the mechanical part, and deliberately says so:
passing this is necessary and nowhere near sufficient.

What is checked, and why each one earns its place:

  gap        -- the single most-omitted sentence. A reader who reaches the
                design without knowing what is missing does not know why the
                paper exists.
  pacing     -- the design belongs in paragraph 2 and the result in paragraph 3.
                "Taking too long to get to what the paper does" is the most
                common structural failure in submitted intros.
  citations  -- heavy early citation makes the field look crowded and works
                against the author's own contribution, at the exact moment the
                reader is deciding whether to continue.
  criticism  -- "prior literature has failed to" costs goodwill and focus, and
                is trivially detectable.
  voice      -- passive and third-person throughout blunts the paper. Economics
                expects first person.
  footnotes  -- they slow the reader down where the paper can least afford it.
  roadmap    -- absence is correct and unflagged; what is flagged is a roadmap
                that survives and then narrates the paper section by section.

Not checked, because a regex cannot: whether the contribution is real, whether
the implications follow, whether the extensions are well chosen.

Usage:
    python3 intro_check.py --intro FILE [--max-footnotes 0]
"""

import argparse
import re
import sys
from pathlib import Path

GAP = [r"\bremains? (?:unknown|unclear|unanswered)\b", r"\blittle is known\b",
       r"\bhas (?:not|never) been\b", r"\bno (?:study|paper|work) has\b",
       r"\bwe (?:do not|don't) (?:yet )?know\b", r"\bis missing\b",
       r"\bunresolved\b", r"\bevidence (?:is|remains) (?:scarce|limited|thin)\b",
       r"\bhard to (?:get|obtain|come by)\b", r"\bhas been difficult\b",
       r"\bwhat is missing\b", r"\bgap\b"]
DOES = [r"\bwe (?:estimate|exploit|use|study|examine|test|measure|document|show|compare)\b",
        r"\bthis paper (?:estimates|exploits|uses|studies|examines|tests|measures|documents|shows)\b",
        r"\bwe draw on\b", r"\bour (?:design|identification|strategy|instrument)\b"]
FINDS = [r"\bwe find\b", r"\bwe show\b", r"\bwe document\b", r"\bwe estimate that\b",
         r"\bour (?:estimates?|results?|findings?) (?:show|imply|indicate|suggest)\b",
         r"\bthe (?:estimated|point) (?:effect|elasticity|coefficient)\b"]
CRITICISM = [r"\bfailed to\b", r"\bfails? to (?:account|address|consider)\b",
             r"\bof little value\b", r"\bneglects?\b", r"\bignores?\b",
             r"\bflawed\b", r"\bmisguided\b", r"\bsuffers? from\b"]
PASSIVE = [r"\b(?:regressions?|results?|estimates?|specifications?|models?|robustness checks?)\s+"
           r"(?:are|is|were|was)\s+(?:estimated|discussed|presented|reported|conducted|performed)\b",
           r"\bit is (?:shown|found|argued|demonstrated)\b",
           r"\bare (?:then )?(?:estimated|discussed|presented|reported)\b"]
FIRST_PERSON = [r"\bwe\b", r"\bour\b", r"\bI\b", r"\bmy\b"]
ROADMAP = [r"rest of the paper", r"remainder of the paper", r"paper proceeds as follows",
           r"structured as follows", r"organized as follows", r"organised as follows"]


def paragraphs(text):
    body = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    body = re.sub(r"^\\section\*?\{[^}]*\}\s*$", "", body, flags=re.MULTILINE)
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def hits(pats, s):
    return sum(1 for p in pats if re.search(p, s, re.IGNORECASE))


def first_para_matching(paras, pats):
    for i, p in enumerate(paras, 1):
        if hits(pats, p):
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--intro", required=True)
    ap.add_argument("--max-footnotes", type=int, default=0)
    args = ap.parse_args()

    path = Path(args.intro)
    if not path.is_file():
        print(f"FAIL: no introduction at {path}")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    paras = paragraphs(text)
    failures = []

    if len(paras) < 4:
        failures.append(f"only {len(paras)} paragraphs; the formula needs at "
                        f"least motivation, does, finds, and a roadmap")

    # --- 1. the knowledge gap, in paragraph 1 ---
    if paras and not hits(GAP, paras[0]):
        failures.append(
            "paragraph 1 never says what is missing from current knowledge. "
            "This is the most-omitted sentence in a draft introduction and the "
            "reason a reader reaches the design without knowing why the paper "
            "exists.")

    # --- 2. paragraph 1 length ---
    if paras and len(paras[0].split()) > 280:
        failures.append(f"paragraph 1 runs {len(paras[0].split())} words, past "
                        f"the half-page budget. Do not cheat the formula by "
                        f"making paragraphs long.")

    # --- 3. pacing: does by 2, finds by 3 ---
    p_does = first_para_matching(paras, DOES)
    p_finds = first_para_matching(paras, FINDS)
    if p_does is None:
        failures.append("no paragraph states what the paper does")
    elif p_does > 2:
        failures.append(f"what the paper does first appears in paragraph "
                        f"{p_does}; it belongs in paragraph 2. Taking too long "
                        f"to get there is the most common structural failure.")
    if p_finds is None:
        failures.append("no paragraph states what the paper finds")
    elif p_finds > 4:
        failures.append(f"the findings first appear in paragraph {p_finds}; the "
                        f"result belongs in paragraph 3")
    if p_does is not None and p_finds is not None and p_finds < p_does:
        failures.append("findings appear before the design")

    # --- 4. citation density before the contribution paragraphs ---
    early = " ".join(paras[:3])
    cites = len(re.findall(r"\([A-Z][A-Za-z'\-]+(?: (?:et al\.?|and [A-Z][A-Za-z'\-]+))?,? \d{4}[a-z]?\)", early))
    cites += len(re.findall(r"\\cite[tp]?\{", early))
    if cites > 3:
        failures.append(f"{cites} citations in the first three paragraphs. Heavy "
                        f"early citation makes the field look crowded and works "
                        f"against your own contribution; one motivational cite "
                        f"is enough, and the rest belong in the contribution "
                        f"paragraphs.")

    # --- 5. criticism of prior work ---
    for pat in CRITICISM:
        for m in re.finditer(pat, text, re.IGNORECASE):
            line = text[:m.start()].count("\n") + 1
            failures.append(f"{path}:{line}: criticism of prior work "
                            f"({m.group(0)!r}). Highlight your accomplishments "
                            f"rather than others' shortcomings — 'we build on', "
                            f"'we extend', 'our findings complement'.")

    # --- 6. voice ---
    for pat in PASSIVE:
        for m in re.finditer(pat, text, re.IGNORECASE):
            line = text[:m.start()].count("\n") + 1
            failures.append(f"{path}:{line}: passive voice ({m.group(0)!r}); "
                            f"economics expects first person and active voice")
    if not any(re.search(p, text) for p in FIRST_PERSON):
        failures.append("no first-person voice anywhere; a third-person "
                        "introduction throughout diminishes the paper's impact")

    # --- 7. footnotes ---
    fn = len(re.findall(r"\\footnote\{", text)) + len(re.findall(r"(?<!\w)\[\^\w+\]", text))
    if fn > args.max_footnotes:
        failures.append(f"{fn} footnote(s); aim for zero in an introduction. Ask "
                        f"of each whether it can be deleted, promoted into the "
                        f"text, or moved to another section.")

    # --- 8. roadmap: absent by default, and short if present ---
    # Absence is correct and is NOT flagged. The rule this enforces is the
    # opposite one: a roadmap that survives should be two sentences, because a
    # section-by-section narration of the paper is what the reader skips.
    for i, para in enumerate(paras, 1):
        if any(re.search(pat, para, re.IGNORECASE) for pat in ROADMAP):
            sentences = [x for x in re.split(r"(?<=[.!?])\s+", para.strip()) if x]
            if len(sentences) > 2:
                failures.append(
                    f"paragraph {i} is a roadmap running {len(sentences)} "
                    f"sentences. The default is to omit the roadmap entirely; "
                    f"if one is kept for a venue that expects it, cap it at two "
                    f"sentences and never narrate section by section.")
            break

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"intro: {len(failures)} problems across {len(paras)} paragraphs")
        return 1
    print(f"intro OK: {len(paras)} paragraphs, does@{p_does}, finds@{p_finds}, "
          f"{cites} early cites, {fn} footnotes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
