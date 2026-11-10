#!/usr/bin/env python3
"""Manual-first reference check for an estimand (stdlib only).

`run-analysis` requires that the estimand be derived by
hand twice, by independent routes, before any estimation package is trusted,
and that the package call then be tested against that reference. The failure
this catches is the one a package-versus-package cross-check cannot see: a
call that computes a *different estimand* and returns cleanly.

The canonical instance is aggregation weighting. Averaging cohort-time
treatment effects with group-size weights and averaging them uniformly are
two different estimands; every staggered-DiD package picks one by default,
neither errors, and the choice is invisible in the output.

Inputs, both written by the analysis scripts rather than by hand:

  reference.json  {formula, expression_a, value_a, expression_b, value_b,
                   tolerance}
  package.json    {call, value, convention}

Exit 0 only when the two hand derivations agree, they were reached by
different expressions, and the package call reproduces them.

Usage:
    python3 estimand_check.py --reference FILE --package FILE
"""

import argparse
import json
import sys
from pathlib import Path


def load(path: Path, failures: list):
    if not path.is_file():
        failures.append(f"{path} not found")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{path} unreadable: {exc}")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--package", required=True)
    args = ap.parse_args()

    failures: list = []
    ref = load(Path(args.reference), failures)
    pkg = load(Path(args.package), failures)
    if ref is None or pkg is None:
        for f in failures:
            print("FAIL:", f)
        return 1

    for key in ("formula", "expression_a", "value_a", "expression_b", "value_b"):
        if key not in ref:
            failures.append(f"reference is missing `{key}`; the estimand is a "
                            f"mathematical object and both derivations are "
                            f"recorded, not just the number")
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1

    tol = float(ref.get("tolerance", 1e-8))
    a, b = float(ref["value_a"]), float(ref["value_b"])

    if ref["expression_a"].strip() == ref["expression_b"].strip():
        failures.append("the two derivations are the same expression run twice; "
                        "that agrees with itself by construction")
    if abs(a - b) > tol:
        failures.append(f"the two hand derivations disagree: {a} vs {b} "
                        f"(tol {tol}). The reference is blocked; no package call "
                        f"is tested until they agree.")
    else:
        value = float(pkg.get("value", "nan"))
        if abs(value - a) > tol:
            failures.append(
                f"package call {pkg.get('call', '?')!r} returns {value} against a "
                f"hand-derived reference of {a} (tol {tol}). Formula: "
                f"{ref['formula']}. Differing convention: "
                f"{pkg.get('convention', '[MATERIAL GAP: convention not named]')}. "
                f"The package is the thing under test; this is not resolved by "
                f"preferring its number.")

    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1
    print(f"estimand OK: two independent derivations agree at {a}, and "
          f"{pkg.get('call', 'the package call')} reproduces it within {tol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
