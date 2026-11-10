#!/usr/bin/env python3
"""G1 acceptance gate: the pick is not the handoff (stdlib only).

S2 refuses to run
without `handoff/g1_acceptance.md` — the same logic as the pre-registration
commit gate, one stage earlier: a decision that lives only in conversation
cannot be audited by the next session. an earlier run ended with four menu items each
carrying a stated requirement that had to be discharged before its
pre-registration could be written, and nothing recorded who discharged them.

Required blocks:

    ```g1_acceptance
    card: K3-1
    cleared_threshold: yes | no
    threshold: top-generalist-candidate
    tier: slate | fallthrough
    reason_for_proceeding: <required when cleared_threshold is `no`>
    retrospective_disclosure: <the pilot-sample handling line, or `none`>
    reframe_note: <step 1.5's REFRAME note, or `none`>
    ```

    ```objection
    raised_by: skeptic
    text: the displacement target is asserted, not verified
    disposition: discharged | limitation | deferred-to-s4
    evidence: output/novelty_facts.md, closest-work item 1
    ```

The disclosure rule is the one this gate exists for. A card may
now be carried forward from the **fallthrough tier** — it did not clear the bar
and the author took it anyway — and that fact has to travel with the card into
S2-S8 and into the paper's limitations. An acceptance record that omits it is
the one way the fallthrough tier could quietly become the deleted
always-returns-items menu.

Usage:
    python3 g1_acceptance_check.py --record FILE
"""

import argparse
import re
import sys
from pathlib import Path

DISPOSITIONS = {"discharged", "limitation", "deferred-to-s4"}
LADDER = ["kill", "revise", "strong-field-candidate", "top-generalist-candidate"]


def blocks(text, tag):
    return re.findall(r"```" + tag + r"\s*\n(.*?)```", text, re.DOTALL)


def parse(body):
    out = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--record", required=True)
    args = ap.parse_args()

    path = Path(args.record)
    if not path.is_file():
        print(f"FAIL: no g1_acceptance record at {path}. S2 refuses to run "
              f"without it: a decision that lives only in conversation cannot "
              f"be audited by the next session.")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []

    heads = blocks(text, "g1_acceptance")
    if len(heads) != 1:
        print(f"FAIL: expected exactly one ```g1_acceptance block, found "
              f"{len(heads)}")
        return 1
    head = parse(heads[0])

    if not head.get("card"):
        failures.append("no `card` named")
    cleared = (head.get("cleared_threshold") or "").lower()
    if cleared not in {"yes", "no"}:
        failures.append(f"`cleared_threshold` must be yes or no, got "
                        f"{head.get('cleared_threshold')!r}")
    threshold = head.get("threshold")
    if threshold not in LADDER:
        failures.append(f"`threshold` {threshold!r} is not on the ladder")
    tier = (head.get("tier") or "").lower()
    if tier not in {"slate", "fallthrough"}:
        failures.append(f"`tier` must be slate or fallthrough, got {tier!r}")

    # The rule: a card taken from the fallthrough tier must say so.
    if cleared == "no":
        if tier != "fallthrough":
            failures.append(
                "`cleared_threshold: no` but `tier` is not `fallthrough`; a "
                "card that did not clear the bar was not on the slate")
        if not head.get("reason_for_proceeding"):
            failures.append(
                "card did not clear the threshold and no "
                "`reason_for_proceeding` is recorded. The author's reason has "
                "to travel with the card into S2-S8 and into the paper's "
                "limitations — an acceptance record that omits it is how the "
                "fallthrough tier becomes the deleted always-returns-items menu.")
    if cleared == "yes" and tier == "fallthrough":
        failures.append("`tier: fallthrough` with `cleared_threshold: yes`; a "
                        "card in the tier did not clear by definition")

    for key in ("retrospective_disclosure", "reframe_note"):
        if not head.get(key):
            failures.append(f"no `{key}`. `none` is a valid value and silence "
                            f"is not — the gate cannot tell an absent "
                            f"disclosure from an unwritten one.")

    objections = [parse(b) for b in blocks(text, "objection")]
    if not objections:
        failures.append("no ```objection blocks. Every surviving objection "
                        "carries a disposition; a record with none is a claim "
                        "that the debate raised nothing, which no run has done.")
    for i, o in enumerate(objections, 1):
        tag = o.get("raised_by") or f"objection {i}"
        if not o.get("text"):
            failures.append(f"{tag}: no `text`")
        disp = (o.get("disposition") or "").lower()
        if disp not in DISPOSITIONS:
            failures.append(f"{tag}: disposition {disp!r} must be one of "
                            f"{', '.join(sorted(DISPOSITIONS))}")
        if disp == "discharged" and not o.get("evidence"):
            failures.append(f"{tag}: discharged with no `evidence`. Discharging "
                            f"an objection is a claim that something answered "
                            f"it, and the something has to be nameable.")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"g1_acceptance: {len(failures)} problems")
        return 1
    print(f"g1_acceptance OK: {head.get('card')} from the {tier} tier, "
          f"{len(objections)} objection(s) dispositioned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
