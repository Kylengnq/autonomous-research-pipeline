#!/usr/bin/env python3
"""Data request gate: every pilot report says what data it would want (stdlib only).

Until then a data need could surface only as a kill verdict
(`unmeasured`, `access-blocked`) or inside the slate-level feasibility-thin
route, which is reachable only when the whole slate is declined. So a card that
was alive but would be materially better on data nobody held **had no way to
say so**, and the author who intends to go and find that data had nothing to
act on.

The block, on every pilot report whatever the verdict:

    ```data_request
    status: none | would-strengthen | required
    quantity: effective half-spread at the release instant
    why_it_matters: separates the liquidity channel from the information channel
    candidates:
      - source: TAQ millisecond quotes
        route: purchasable
        join_key: ticker x date
        probe: unprobed: no licence to sample against
        cost_time: ~$1.5k, 2 weeks procurement
    fallback: YES/NO no-arbitrage bound from paired contract prices
    ```

Four rules, all blocking:

  quantity   -- names what is measured, in the design's own terms. A field or
                table name is a validation failure: a request phrased as an
                ingredient sends the author shopping for the wrong thing, which
                is the instrument miss an earlier run benchmark measured (three
                cards declined spread as a data purchase while the human
                measured the same quantity with no order book at all).
  candidates -- at least one, each with a route, and each with either a
                verified probe carrying a real match rate or an explicit
                `unprobed:` reason. A bare expected match rate is a hunch
                wearing a measurement's clothes.
  fallback   -- mandatory even at `required`. A request with no fallback is a
                data purchase in disguise and routes to the blocked registry
                rather than sitting on the slate.
  status     -- `none` is a real and common answer. A run that requests
                something on every card has produced a wish list, and a wish
                list is not read.

Usage:
    python3 data_request_check.py --report FILE
"""

import argparse
import re
import sys
from pathlib import Path

STATUSES = {"none", "would-strengthen", "required"}
ROUTES = {"held", "public", "licensed", "purchasable", "restricted"}
# A quantity phrased as an ingredient. These are schema words, not measurements.
INGREDIENT_HINTS = [
    r"\btable\b", r"\bcolumn\b", r"\bfield\b", r"\bschema\b", r"\bendpoint\b",
    r"\.csv\b", r"\.parquet\b", r"\bdataset\b",
]
# A match rate stated without a probe behind it.
UNBACKED_RATE = re.compile(
    r"\b(?:expect(?:ed)?|estimat(?:e|ed)|should\s+be|about|approx\w*|~)\s*"
    r"\d{1,3}\s*%", re.IGNORECASE)


def blocks(text, tag):
    return re.findall(r"```" + tag + r"\s*\n(.*?)```", text, re.DOTALL)


def parse_block(body):
    """Parse the flat keys and the `candidates:` list."""
    flat, candidates, cur, in_list = {}, [], None, False
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            in_list = True
            cur = {}
            candidates.append(cur)
            stripped = stripped[2:].strip()
            if not stripped:
                continue
        indented = line[:1] in (" ", "\t")
        key, sep, value = stripped.partition(":")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if key == "candidates":
            in_list = True
            continue
        if in_list and indented and cur is not None:
            cur[key] = value
        else:
            in_list = False
            flat[key] = value
    return flat, candidates


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

    found = blocks(text, "data_request")
    if len(found) != 1:
        print(f"FAIL: expected exactly one ```data_request block, found "
              f"{len(found)}. Every pilot report carries one, `status: none` "
              f"included — a card that is alive but data-hungry must be able to "
              f"say so.")
        return 1

    flat, candidates = parse_block(found[0])
    status = flat.get("status")
    if status not in STATUSES:
        failures.append(f"status {status!r} must be one of "
                        f"{', '.join(sorted(STATUSES))}")

    if status == "none":
        for key in ("quantity", "candidates", "fallback"):
            if flat.get(key) or (key == "candidates" and candidates):
                failures.append(f"status is `none` but `{key}` is populated; "
                                f"say nothing or say what you need, not both")
    elif status in {"would-strengthen", "required"}:
        quantity = flat.get("quantity", "")
        if not quantity:
            failures.append("no `quantity`. Name what the design needs "
                            "measured, in its own terms.")
        else:
            for pat in INGREDIENT_HINTS:
                if re.search(pat, quantity, re.IGNORECASE):
                    failures.append(
                        f"`quantity` reads as an ingredient, not a measurement: "
                        f"{quantity!r} matches {pat!r}. A request phrased as a "
                        f"field or table sends the author shopping for the wrong "
                        f"thing — spread, surprise, exposure, attention, "
                        f"liquidity and sentiment all have several constructions.")
                    break
        if not flat.get("why_it_matters"):
            failures.append("no `why_it_matters`: state what the paper can "
                            "claim with it that it cannot without")
        if not candidates:
            failures.append("no candidate sources. A request with no candidate "
                            "is a wish, not an acquisition the author can act on.")
        for i, c in enumerate(candidates, 1):
            tag = c.get("source") or f"candidate {i}"
            if not c.get("source"):
                failures.append(f"{tag}: no `source` named")
            route = c.get("route")
            if route not in ROUTES:
                failures.append(f"{tag}: route {route!r} must be one of "
                                f"{', '.join(sorted(ROUTES))} — the route, not "
                                f"the price, is the feasibility question")
            probe = c.get("probe", "")
            if not probe:
                failures.append(f"{tag}: no `probe`. Give a verified match rate "
                                f"or an explicit `unprobed: <reason>`.")
            elif not probe.lower().startswith("unprobed:") and \
                    UNBACKED_RATE.search(probe):
                failures.append(
                    f"{tag}: probe {probe!r} states an expected match rate with "
                    f"no probe behind it. Either run the probe on a real slice "
                    f"or say `unprobed:` and why — an expectation presented as a "
                    f"measurement is the hunch this block exists to remove.")
            if not c.get("cost_time"):
                failures.append(f"{tag}: no `cost_time` estimate")
        if not flat.get("fallback"):
            failures.append(
                "no `fallback`, and it is mandatory even at `required`. A "
                "request with no fallback is an admission the card is a data "
                "purchase in disguise; it routes to the blocked registry with "
                "its route recorded rather than sitting on the slate.")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"data_request: {len(failures)} problems")
        return 1
    print(f"data_request OK: status {status}, {len(candidates)} candidate(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
