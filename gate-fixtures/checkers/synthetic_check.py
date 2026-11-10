#!/usr/bin/env python3
"""Planted-effect recovery check for the synthetic-first gate (stdlib only).

`pipeline-design.md` §4 states the synthetic-first gate as two obligations, and
`estimand_check.py` covers only the second (the hand-derived reference). This
checker covers the first: **a planted effect is recovered on synthetic data
before the estimator is pointed at real data.**

The gate exists because an estimator that is wired up wrong usually still
returns a number. Running it first on data whose true effect you chose is the
only cheap way to learn that the number means what the script says it means.

Four ways the check is passed without being performed, each of which this
catches:

1. The recovery simply fails and the stage continues anyway.
2. The only effect planted is zero. Recovering a null shows the estimator can
   return zero; it shows nothing about whether it can find an effect that is
   there, which is what the real run is asking it to do.
3. The tolerance is wide enough to admit any answer. A band as large as the
   effect cannot distinguish recovery from failure.
4. The real-data run happened first, so the synthetic pass is a formality
   written up afterwards. The gate is an ordering claim, and an ordering claim
   is checkable only against timestamps.

Input, written by the analysis scripts rather than by hand:

  synthetic_recovery.json
    {estimator, seed, planted_effect, recovered_effect, tolerance,
     synthetic_run_ts, real_run_ts}

`real_run_ts` may be null when the real run has not happened yet, which is the
normal state at the moment this gate is checked.

Usage:
    python3 synthetic_check.py --recovery FILE
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


REQUIRED = (
    "estimator",
    "seed",
    "planted_effect",
    "recovered_effect",
    "tolerance",
    "synthetic_run_ts",
)


def parse_ts(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recovery", required=True)
    args = ap.parse_args()

    path = Path(args.recovery)
    failures: list = []

    if not path.is_file():
        print(f"FAIL: {path} not found; the synthetic-first gate has no record to check")
        return 1
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {path} unreadable: {exc}")
        return 1

    for key in REQUIRED:
        if key not in rec:
            failures.append(
                f"recovery log is missing `{key}`; the gate is a claim about a "
                f"run that happened, and an incomplete log cannot support it"
            )
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1

    planted = float(rec["planted_effect"])
    recovered = float(rec["recovered_effect"])
    tol = float(rec["tolerance"])
    estimator = rec["estimator"]

    if planted == 0.0:
        failures.append(
            "the only planted effect is zero. Recovering a null shows the "
            "estimator can return zero and says nothing about whether it can "
            "find an effect that is present, which is what the real run asks of "
            "it. Plant a nonzero effect."
        )
    elif tol >= abs(planted):
        failures.append(
            f"tolerance {tol} is at least as large as the planted effect "
            f"{planted}, so the band admits zero and recovery cannot be "
            f"distinguished from failure. The tolerance has to be tight enough "
            f"for the test to be able to fail."
        )
    elif abs(recovered - planted) > tol:
        failures.append(
            f"{estimator} recovered {recovered} against a planted effect of "
            f"{planted} (tol {tol}). The estimator does not recover what was "
            f"put in, so no number it produces on real data is interpretable. "
            f"The stage stops here; this is not resolved by widening the "
            f"tolerance."
        )

    synth_ts = parse_ts(rec["synthetic_run_ts"])
    real_ts = parse_ts(rec.get("real_run_ts"))
    if synth_ts is None:
        failures.append(
            "`synthetic_run_ts` does not parse as a timestamp, so the ordering "
            "the gate asserts cannot be checked"
        )
    elif real_ts is not None and real_ts < synth_ts:
        failures.append(
            f"the real-data run at {real_ts.isoformat()} precedes the synthetic "
            f"recovery at {synth_ts.isoformat()}. Synthetic-first is an ordering "
            f"rule: a recovery written up after the real estimates were seen is "
            f"a description of the estimator, not a test of it."
        )

    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1

    print(
        f"synthetic-first OK: {estimator} recovered {recovered} against a "
        f"planted {planted} within {tol}, seed {rec['seed']}, run at "
        f"{rec['synthetic_run_ts']} before any real-data estimate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
