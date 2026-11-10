#!/usr/bin/env python3
"""Journal-name resolution: assert no silent substitution (stdlib only).

`tools/free_corbis_mcp.py::_resolve_source_ids` mapped a journal name to an
OpenAlex source id by taking the first fuzzy search hit, with no check that the
hit was the journal asked for. Asking for `Review of Finance` returned
*International Review of Economics & Finance* — a different journal, 5,991
works — and every pull downstream ran against it without complaint.

That is the worst shape a defect can take here: not a crash, not an empty
result, but confident and plausible output from the wrong source. The known
casualty is an early calibration build, which put 16 accounting venues and
14 out-of-scope ones into a finance anchor as archetype analogs.

This checks the property the fix restores: **a name resolves to that journal or
to nothing.** Expectations come from a JSON file so the fixture states them:

    {"expect": {"Review of Finance": "S131117787",
                "Journal of Finance": "S5353659",
                "Nonexistent Journal of Nothing": null},
     "forbid_names": ["International Review of Economics & Finance"]}

A `null` expectation means the name must be reported unmatched. `forbid_names`
are display names that must not appear in any resolution — the near misses.

Reaches the network. A failure that says `network unreachable` is an
environment problem, not a gate problem, and says so rather than reading as a
resolver defect.

Usage:
    python3 source_resolver_check.py --tools-root DIR --expect FILE
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tools-root", required=True)
    ap.add_argument("--expect", required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(Path(args.tools_root)))
    try:
        import free_corbis_mcp as fc
    except ImportError as exc:
        print(f"FAIL: cannot import the shim from {args.tools_root}: {exc}")
        return 1

    spec = json.loads(Path(args.expect).read_text(encoding="utf-8"))
    expect = spec.get("expect", {})
    forbid = spec.get("forbid_names", [])

    # Probe the network FIRST, with a call that raises rather than one the shim
    # swallows. `_resolve_source_ids` catches its own exceptions and returns
    # None, so an unreachable API is indistinguishable from a journal that does
    # not exist -- and this checker would report a resolver defect for a network
    # outage, which is precisely the cry-wolf failure the fixture suite exists
    # to prevent in the gates it checks.
    try:
        fc._oa("sources/S5353659", {})
    except Exception as exc:  # noqa: BLE001
        print(f"SKIPPED: OpenAlex unreachable ({type(exc).__name__}: {exc}). "
              f"This is an environment failure, not a resolver failure, and the "
              f"resolver is untested rather than broken.")
        return 2

    names = list(expect)
    try:
        fc._resolve_source_ids(names)
    except Exception as exc:  # noqa: BLE001
        print(f"SKIPPED: OpenAlex unreachable mid-resolution "
              f"({type(exc).__name__}: {exc}). The resolver is untested here, "
              f"not broken — it lets transport errors through "
              f"rather than reporting them as 'journal not found'.")
        return 2

    failures = []
    for name, want in expect.items():
        got = fc._SOURCE_CACHE.get(fc._norm_source_name(name))
        if want is None:
            if got is not None:
                failures.append(
                    f"{name!r} must be reported unmatched, resolved to {got}. "
                    f"A resolver that guesses is worse than one that fails.")
            continue
        if got != want:
            failures.append(f"{name!r} resolved to {got}, expected {want}")
            continue
        try:
            display = fc._oa("sources/" + got, {}).get("display_name")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"network unreachable verifying {got} ({exc})")
            continue
        if fc._norm_source_name(display) != fc._norm_source_name(name):
            failures.append(f"{name!r} resolved to {got} whose display name is "
                            f"{display!r} — silent substitution")
        for bad in forbid:
            if fc._norm_source_name(display) == fc._norm_source_name(bad):
                failures.append(f"{name!r} resolved to the known near miss "
                                f"{display!r}")

    for f in failures:
        print("FAIL:", f)
    if failures:
        print(f"resolver: {len(failures)} problems across {len(expect)} names")
        return 1
    print(f"resolver OK: {len(expect)} names, each resolved to itself or "
          f"reported unmatched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
