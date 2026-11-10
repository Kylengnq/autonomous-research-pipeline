#!/usr/bin/env python3
"""G1 threshold gate: the slate rules, made executable (stdlib only).

G1 is a two-sided threshold gate (`idea-debate` step 4). It
refuses cards below a declared bar and hands every near miss the gate that
capped it plus the cheapest action that would clear it, and the slate is
however many cards clear the bar -- none, one, or many.

Two of those properties are exactly the kind that decay silently, which is why
they are checked rather than described:

  padding      -- the old menu guaranteed 3-5 items from whatever band existed,
                  which made "nothing clears the bar" unsayable. A slate whose
                  count exceeds the cards that actually cleared is that
                  guarantee coming back.
  the promote  -- a `strong-field-candidate` with no capping gate and no
      half      cheapest action is a label, not a route, and the positive half
                  of the gate has quietly become an annotation again.

Also enforced: Gate F (feasibility) refuses at any score; a top rung requires
every gate cleared; each gate is marked checkable / judged / computed; and no
artifact asserts a predicted journal placement, which is the placement rule
kept in the form that was right.

The fallthrough tier is the same decay risk one step along.
On an empty slate the stage may present the capped cards for author review
rather than ending the run, and two tiers reported as one tier is the deleted
always-returns-items menu wearing a new name. So: the tier only exists when the
slate is empty, every card in it is labelled, the counts are never summed, the
zero is stated before the first fallthrough card, and no fallthrough card is
described as having cleared anything.

Block format, mirroring the project's ```novelty and ```count conventions:

    ```g1_slate
    threshold: top-generalist-candidate
    scored: 4
    slate: 0
    diagnosis: calibration-blocked
    ```

    ```g1
    card: K2-2
    verdict: strong-field-candidate
    gate_a: capped | checkable
    gate_b: cleared | judged
    gate_c: cleared | judged
    gate_d: capped | checkable
    gate_e: cleared | judged
    gate_f: cleared | computed
    capped_by: A
    cheapest_action: verify the hunch against the target's actual claim
    clinic_scope: yes
    ```

Usage:
    python3 g1_slate_check.py --report FILE
"""

import argparse
import re
import sys
from pathlib import Path

LADDER = ["kill", "revise", "strong-field-candidate", "top-generalist-candidate"]
GATES = ["gate_a", "gate_b", "gate_c", "gate_d", "gate_e", "gate_f"]
BASIS = {"checkable", "judged", "computed"}
# A rung asserts gate clearance. These assert an editorial outcome.
PLACEMENT = [r"would reach", r"would place", r"will be accepted",
             r"is a top-3 paper", r"publishable in"]
# Words that assert a fallthrough card cleared the bar it did not clear.
CLEARED_WORDS = [r"cleared the threshold", r"on the slate", r"passed the bar",
                 r"clears the bar", r"is a slate item"]


def blocks(text, tag):
    return re.findall(r"```" + tag + r"\s*\n(.*?)```", text, re.DOTALL)


def blocks_with_pos(text, tag):
    """Same as blocks(), but keeps each block's start offset.

    Ordering is load-bearing for the fallthrough tier: the top-tier count has
    to appear before the first fallthrough card, or a reader meets the cards
    first and the zero reads as a footnote to them instead of the headline.
    """
    return [(m.start(), m.group(1))
            for m in re.finditer(r"```" + tag + r"\s*\n(.*?)```", text, re.DOTALL)]


def parse(body):
    out = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def check_card(card, failures):
    label = card.get("card", "?")
    verdict = card.get("verdict")
    if verdict not in LADDER:
        failures.append(f"{label}: verdict {verdict!r} is not on the ladder "
                        f"({', '.join(LADDER)})")
        return None
    capped = []
    for g in GATES:
        raw = card.get(g)
        if raw is None:
            failures.append(f"{label}: missing {g}")
            continue
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) != 2 or parts[0] not in {"cleared", "capped"} \
                or parts[1] not in BASIS:
            failures.append(f"{label}: {g} must read "
                            f"`cleared|capped | checkable/judged/computed`, "
                            f"got {raw!r}. The basis split is what keeps a rung "
                            f"from drifting back into an uncalibrated claim.")
            continue
        if parts[0] == "capped":
            capped.append(g[-1].upper())

    if verdict == "top-generalist-candidate" and capped:
        failures.append(f"{label}: top rung awarded with gate(s) "
                        f"{', '.join(capped)} capped")
    if "F" in capped and verdict == "top-generalist-candidate":
        failures.append(f"{label}: Gate F refuses at any score; a design the "
                        f"held data cannot carry is not an available idea")
    if verdict == "strong-field-candidate":
        if not card.get("capped_by"):
            failures.append(f"{label}: capped verdict with no `capped_by` gate")
        if not card.get("cheapest_action"):
            failures.append(f"{label}: capped verdict with no `cheapest_action` "
                            f"— that is a label, not a route, and the "
                            f"promote-and-improve half is missing")
        if not card.get("clinic_scope"):
            failures.append(f"{label}: capped verdict does not say whether the "
                            f"action is in the revision clinic's scope")
    return verdict


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    path = Path(args.report)
    if not path.is_file():
        print(f"FAIL: report not found: {path}")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []

    heads = blocks(text, "g1_slate")
    if len(heads) != 1:
        print(f"FAIL: expected exactly one ```g1_slate block, found {len(heads)}")
        return 1
    head = parse(heads[0])
    threshold = head.get("threshold")
    if threshold not in LADDER:
        failures.append(f"slate: threshold {threshold!r} is not on the ladder")
        threshold = None

    raw_cards = blocks_with_pos(text, "g1")
    cards = [parse(b) for _, b in raw_cards]
    positions = [pos for pos, _ in raw_cards]
    if not cards:
        failures.append("no ```g1 card blocks; every card that reached step 4 "
                        "carries a verdict")
    verdicts = [check_card(c, failures) for c in cards]

    # --- fallthrough tier ---
    fallthrough = head.get("fallthrough")
    # `tier` is optional. Absent means the card was scored and is presented in
    # neither tier -- which is exactly what a killed card is. Only the two
    # presented tiers are named.
    tiers = [c.get("tier", "") for c in cards]
    for c, t in zip(cards, tiers):
        if t and t not in {"slate", "fallthrough"}:
            failures.append(f"{c.get('card','?')}: tier {t!r} must be `slate`, "
                            f"`fallthrough`, or absent")
    ft_idx = [i for i, t in enumerate(tiers) if t == "fallthrough"]

    if threshold:
        bar = LADDER.index(threshold)
        cleared = [v for v in verdicts if v and LADDER.index(v) >= bar]
        stated = head.get("slate")
        if stated is None or not stated.isdigit():
            failures.append("slate: block has no numeric `slate` count")
        elif int(stated) != len(cleared):
            failures.append(
                f"slate: block states {stated} but {len(cleared)} card(s) reach "
                f"{threshold}. A slate padded to a count, or refilled from a "
                f"lower band, is the old menu's guarantee returning — it is what "
                f"made 'nothing clears the bar' unsayable.")
        scored = head.get("scored")
        if scored is not None and scored.isdigit() and int(scored) != len(cards):
            failures.append(f"slate: `scored` says {scored}, {len(cards)} card "
                            f"blocks present")
        if not cleared and not head.get("diagnosis"):
            failures.append("slate: empty slate with no `diagnosis`. An empty "
                            "slate is a complete result and has to say which "
                            "DECLINE route it points to — `calibration-blocked` "
                            "is not the same finding as `contribution-thin`.")
        if cleared and head.get("diagnosis"):
            failures.append(f"slate: {len(cleared)} card(s) cleared and a "
                            f"DECLINE `diagnosis` is set; those are exclusive")

        # --- the five fallthrough rules ---
        if ft_idx:
            if cleared:
                failures.append(
                    f"fallthrough: {len(ft_idx)} fallthrough card(s) presented "
                    f"beside a NON-EMPTY slate of {len(cleared)}. The tier "
                    f"exists for the empty case; showing it next to a real "
                    f"slate is padding by another route.")
            if not fallthrough or fallthrough == "none":
                failures.append(
                    "fallthrough: cards are in the tier but the slate block "
                    "declares no `fallthrough` threshold (or declares `none`)")
            elif fallthrough not in LADDER:
                failures.append(f"fallthrough: {fallthrough!r} is not on the ladder")
            else:
                fbar = LADDER.index(fallthrough)
                for i in ft_idx:
                    v, label = verdicts[i], cards[i].get("card", "?")
                    if not v:
                        continue
                    if LADDER.index(v) >= bar:
                        failures.append(
                            f"{label}: verdict {v} reaches {threshold} but is "
                            f"filed in the fallthrough tier; it belongs on the "
                            f"slate")
                    elif LADDER.index(v) < fbar:
                        failures.append(
                            f"{label}: verdict {v} is below the declared "
                            f"fallthrough bar {fallthrough}; the tier is not a "
                            f"home for everything that did not clear")
                    if not cards[i].get("capped_by"):
                        failures.append(f"{label}: fallthrough card with no "
                                        f"`capped_by` gate")
                    if not cards[i].get("cheapest_action"):
                        failures.append(f"{label}: fallthrough card with no "
                                        f"`cheapest_action`")

            # the zero must be stated before the first fallthrough card
            first_ft = min(positions[i] for i in ft_idx)
            zero_stated = None
            for m in re.finditer(r"no card cleared", text, re.IGNORECASE):
                zero_stated = m.start() if zero_stated is None else zero_stated
            if zero_stated is None:
                failures.append(
                    "fallthrough: report never states `no card cleared "
                    "<threshold>`. The top-tier count is the headline and the "
                    "tier is the appendix, not the other way round.")
            elif zero_stated > first_ft:
                failures.append(
                    "fallthrough: the first fallthrough card appears BEFORE "
                    "the `no card cleared` line. A reader meets the cards first "
                    "and the zero reads as a footnote to them.")

            # no fallthrough card described as having cleared
            for pat in CLEARED_WORDS:
                for m in re.finditer(pat, text, re.IGNORECASE):
                    if m.start() > first_ft:
                        line = text[:m.start()].count("\n") + 1
                        failures.append(
                            f"{path}:{line}: {m.group(0)!r} appears in the "
                            f"fallthrough tier. No card there cleared anything; "
                            f"describing one as though it had is the deleted "
                            f"always-returns-items menu.")

            # counts are never summed
            for m in re.finditer(r"(?:total|combined)\s+(?:slate|candidates?)",
                                 text, re.IGNORECASE):
                line = text[:m.start()].count("\n") + 1
                failures.append(f"{path}:{line}: {m.group(0)!r} sums the two "
                                f"tiers into one count")
        elif fallthrough and fallthrough != "none" and not cleared:
            failures.append(
                f"fallthrough: slate is empty and `fallthrough: {fallthrough}` "
                f"is declared, but no card is filed in the tier. Either the "
                f"tier is genuinely empty (say so with `fallthrough: none` and "
                f"end ARCHIVED) or the cards are missing.")

    for pat in PLACEMENT:
        for m in re.finditer(pat, text, re.IGNORECASE):
            line = text[:m.start()].count("\n") + 1
            failures.append(f"{path}:{line}: predicted placement ({m.group(0)!r}). "
                            f"A rung asserts gate clearance; nothing here has "
                            f"evidence linking a rung to an editorial outcome.")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"g1: {len(failures)} problems across {len(cards)} cards")
        return 1
    tier_note = f", fallthrough tier of {len(ft_idx)}" if ft_idx else ""
    print(f"g1 OK: {len(cards)} cards scored, slate of {head.get('slate')} at "
          f"threshold {threshold}{tier_note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
