#!/usr/bin/env python3
"""Claim-ledger validator and registry cross-referencer (stdlib, Python 3.9+).

validate:  every numeric claim's results file exists, its key resolves, the
           reported value matches within tolerance, the mechanism check is
           non-empty; textual claims carry a locator, and a quote given for
           a local source must appear in that file (whitespace-normalized).
cross-ref: every results_file is declared as an output by some script in
           the registry, and the producing script is not newer than the
           results file (stale evidence).

Exit 0 only when every claim passes.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def resolve_key(obj, dotpath):
    """Resolve 'a.b.0.c' through nested dicts/lists; raise KeyError if absent."""
    cur = obj
    for part in dotpath.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            if part not in cur:
                raise KeyError(part)
            cur = cur[part]
        else:
            raise KeyError(part)
    return cur


def norm_ws(text):
    return re.sub(r"\s+", " ", text).strip()


def check_numeric(claim, errors):
    rf = Path(claim["results_file"])
    if not rf.is_file():
        errors.append(f"results file missing: {rf}")
        return
    try:
        data = json.loads(rf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"results file unreadable: {rf} ({exc})")
        return
    try:
        value = resolve_key(data, claim["results_key"])
    except (KeyError, IndexError, ValueError):
        errors.append(f"key does not resolve: {claim['results_key']} in {rf}")
        return
    reported = claim.get("reported_value")
    if reported is None:
        return  # existence check only
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"key resolves to non-numeric {type(value).__name__}: "
                      f"{claim['results_key']}")
        return
    tol = claim.get("tolerance")
    if tol is None:
        # Default: exact at the precision the paper printed.
        dec = len(str(reported).split(".")[1]) if "." in str(reported) else 0
        tol = 0.5 * 10 ** -dec
    if abs(value - reported) > tol:
        errors.append(f"drift: reported {reported}, source has {value} "
                      f"(tol {tol}) at {claim['results_key']}")


def check_textual(claim, errors):
    if not any(claim.get(k) for k in ("quote", "page", "section")):
        errors.append("textual claim has no locator (quote/page/section)")
        return
    src = claim.get("source", "")
    quote = claim.get("quote")
    src_path = Path(src)
    if quote and src and src_path.is_file():
        text = norm_ws(src_path.read_text(encoding="utf-8", errors="replace"))
        if norm_ws(quote) not in text:
            errors.append(f"quote not found in {src} (fabricated support?)")
    # External sources (citations, arXiv ids) are confirmed by verify-citations.


def validate(args) -> int:
    ledger_path = Path(args.ledger)
    if not ledger_path.is_file():
        print(f"FAIL: ledger not found: {ledger_path}")
        return 1
    claims = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(claims, list) or not claims:
        print("FAIL: ledger is not a non-empty JSON list")
        return 1

    n_bad = 0
    for claim in claims:
        errors = []
        cid = claim.get("id", "?")
        if not claim.get("claim"):
            errors.append("empty claim text")
        if not claim.get("location"):
            errors.append("missing location")
        if not norm_ws(claim.get("mechanism_check", "")):
            errors.append("empty mechanism_check")
        is_numeric = "results_file" in claim or "results_key" in claim
        is_textual = "source" in claim
        if not is_numeric and not is_textual:
            errors.append("claim is neither numeric nor textual")
        if is_numeric:
            if "results_file" not in claim or "results_key" not in claim:
                errors.append("numeric claim needs results_file and results_key")
            else:
                check_numeric(claim, errors)
        if is_textual:
            check_textual(claim, errors)
        for e in errors:
            print(f"FAIL [{cid}]: {e}")
        n_bad += bool(errors)

    if n_bad:
        print(f"validate: {n_bad}/{len(claims)} claims failed")
        return 1
    print(f"validate OK: {len(claims)} claims backed")
    return 0


def cross_ref(args) -> int:
    claims = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    reg_path = Path(args.registry)
    if not reg_path.is_file():
        print(f"FAIL: registry not found: {reg_path}")
        return 1
    registry = json.loads(reg_path.read_text(encoding="utf-8"))

    producers = {}  # output path -> script path
    for entry in registry:
        for out in entry.get("outputs", []):
            producers[str(Path(out))] = entry["script"]

    n_bad = 0
    seen = set()
    for claim in claims:
        rf = claim.get("results_file")
        if not rf or rf in seen:
            continue
        seen.add(rf)
        key = str(Path(rf))
        script = producers.get(key)
        if script is None:
            print(f"FAIL: {rf} is not a declared output of any registered script")
            n_bad += 1
            continue
        sp, rp = Path(script), Path(rf)
        if sp.is_file() and rp.is_file() and sp.stat().st_mtime > rp.stat().st_mtime:
            print(f"FAIL: stale evidence: {script} is newer than {rf}; rerun it")
            n_bad += 1
    if n_bad:
        print(f"cross-ref: {n_bad} results files unbacked or stale")
        return 1
    print(f"cross-ref OK: {len(seen)} results files trace to registered scripts")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("ledger")
    c = sub.add_parser("cross-ref")
    c.add_argument("ledger")
    c.add_argument("--registry", required=True)
    args = ap.parse_args()
    return validate(args) if args.cmd == "validate" else cross_ref(args)


if __name__ == "__main__":
    sys.exit(main())
