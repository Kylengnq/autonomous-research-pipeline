#!/usr/bin/env python3
"""Per-layer cost accounting for a pipeline run, read from Claude Code transcripts.

WHY THIS EXISTS

The pipeline's original cost instrument was a per-layer subagent count. Measured
against a full run, that count is close to uncorrelated with spend. Per-agent
cost below is a multiple of the cheapest layer:

    Decision audit         7 agents   16% of run    56x per agent
    Debate roles          40 agents   12% of run     8x per agent
    G1 judges              4 agents    5% of run    32x per agent
    Desk editors           3 agents    2% of run    18x per agent
    Generators            10 agents  0.4% of run     1x per agent
    ---------------------------------------------------------
    Driver's own thread    0 agents   63% of run    not counted

The debate was 62% of the agent count and 12% of the cost; cost per agent spans
56x across the funnel; and the largest single line item appears in no agent
count at all. A budget key set from subagent count would have fired on the
cheapest layer in the funnel and never touched the most expensive one.

WHAT IT MEASURES

Cost here is dominated by re-reading context, not by producing text. Across the
whole project to date: cache reads 61%, cache writes 25%, output 17%, fresh
input 1%. That is why the driver dominates -- its context ran a 344K median and
786K maximum, and every turn re-reads all of it before doing anything.

THE ONE TRAP

Streaming writes several usage records per assistant message. Summing them
naively overstates by roughly 3x. This script deduplicates by message id, which
is the difference between $150 and $450 for the same run. If a port of this
tool reports figures ~3x high, that is the bug.

CAVEAT ON THE DOLLAR FIGURES

Prices are Anthropic first-party list rates. Claude Code plans bill against
usage limits rather than per token, so these are cost-EQUIVALENTS, useful for
comparing layers against each other -- which is the question the pipeline
actually has. They are not an invoice.

USAGE

    python3 tools/run_cost.py                        # every session in this project
    python3 tools/run_cost.py --session 08db2de2     # one session, per-layer breakdown
    python3 tools/run_cost.py --     # sessions from a date onward
    python3 tools/run_cost.py --project <slug>       # a different project directory
    python3 tools/run_cost.py --json                 # machine-readable, for the counters block
    python3 tools/run_cost.py --outcomes outcomes.json   # add cost per SUCCESS

COST PER SUCCESS

Cost per run says what a layer spent; it cannot say whether the spend bought
anything. `--outcomes` adds the two statistics that can: cost per successful
run, and the incremental cost per ADDITIONAL success of running an arm against
not running it. The tool reads the numerator from the transcripts and refuses
to invent the denominator -- successes are declared by the author, per layer,
with a one-line definition and the date it was fixed:

    {
      "declared_on": "<YYYY-MM-DD, dated before any cost was read>",
      "layers": {
        "novelty judge": {"runs": 2, "successes": 1,
                          "success_is": "kill later upheld by the decision audit"}
      },
      "comparisons": [
        {"name": "novelty judge on/off",
         "with":    {"layers": ["novelty judge", "debate roles"],
                     "runs": 12, "successes": 4},
         "without": {"layers": ["debate roles"], "runs": 12, "successes": 3}}
      ]
    }

A layer with no `success_is` prints a Material Gap rather than a ratio. The
declared date is printed beside every figure and nothing here can verify it
came first, which is the whole reason it is printed.

No pip dependencies -- pure Python standard library.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

PROJECTS = os.path.expanduser("~/.claude/projects")

# (input, output, cache_write_5m, cache_read) $ per million tokens.
# Cache write is 1.25x input at the default 5-minute TTL; cache read is 0.1x.
PRICES = {
    "opus":   (5.0, 25.0, 6.25, 0.50),
    "fable":  (10.0, 50.0, 12.50, 1.00),
    "mythos": (10.0, 50.0, 12.50, 1.00),
    "sonnet": (3.0, 15.0, 3.75, 0.30),
    "haiku":  (1.0, 5.0, 1.25, 0.10),
}

# description substring -> funnel layer. First match wins, so order matters.
#
# "audit" is tested FIRST because an auditor's description always names the
# layer it audits -- "Audit the desk kill" is a decision-audit agent, not a
# desk editor, and matching on "desk" first silently moved it, and its cost, into
# the wrong layer. Any layer that reviews another layer has to win the tie.
LAYERS = [
    ("audit", "decision audit"),
    ("generator", "F1 generators"),
    ("rebuttal", "debate roles"),
    ("advocate", "debate roles"),
    ("skeptic", "debate roles"),
    ("methods", "debate roles"),
    ("assessor", "debate roles"),
    ("editor", "desk editors"),
    ("desk", "desk editors"),
    ("novelty", "novelty judge"),
    ("contribution", "novelty judge"),
    ("judge", "G1 judges"),
    ("benchmark", "benchmark"),
    ("contrast", "contrast pass"),
    ("clinic", "revision clinic"),
]


def family(model: str | None) -> str:
    m = (model or "").lower()
    for key in PRICES:
        if key in m:
            return key
    return "opus"


def layer_of(description: str) -> str:
    d = (description or "").lower()
    for needle, name in LAYERS:
        if needle in d:
            return name
    return "other"


def read_usage(path: str) -> tuple[collections.Counter, float, list[int], str]:
    """Return (token counter, cost, per-request context sizes, dominant model).

    Deduplicates by assistant message id -- see THE ONE TRAP above.
    """
    seen: dict[str, dict] = {}
    fam: dict[str, str] = {}
    models: collections.Counter = collections.Counter()
    for line in open(path, errors="replace"):
        try:
            obj = json.loads(line)
        except (ValueError, TypeError):
            continue
        msg = obj.get("message")
        if not isinstance(msg, dict):
            continue
        usage = msg.get("usage")
        if not usage:
            continue
        mid = msg.get("id") or f"anon{len(seen)}"
        seen[mid] = usage
        fam[mid] = family(msg.get("model"))
        models[msg.get("model")] += 1

    counts: collections.Counter = collections.Counter()
    cost = 0.0
    contexts: list[int] = []
    for mid, usage in seen.items():
        p_in, p_out, p_cw, p_cr = PRICES[fam[mid]]
        tin = usage.get("input_tokens", 0)
        tout = usage.get("output_tokens", 0)
        tcw = usage.get("cache_creation_input_tokens", 0)
        tcr = usage.get("cache_read_input_tokens", 0)
        counts["input"] += tin
        counts["output"] += tout
        counts["cache_write"] += tcw
        counts["cache_read"] += tcr
        counts["requests"] += 1
        cost += (tin * p_in + tout * p_out + tcw * p_cw + tcr * p_cr) / 1e6
        contexts.append(tin + tcw + tcr)
    dominant = models.most_common(1)[0][0] if models else "unknown"
    return counts, cost, sorted(contexts), dominant


def percentile(values: list[int], q: float) -> int:
    if not values:
        return 0
    return values[min(len(values) - 1, int(len(values) * q))]


def analyse_session(jsonl: str) -> dict:
    sid = os.path.basename(jsonl)[:-6]
    main_counts, main_cost, contexts, model = read_usage(jsonl)

    layers: dict[str, dict] = {}
    subdir = jsonl[:-6] + "/subagents"
    for meta_path in sorted(glob.glob(subdir + "/*.meta.json")):
        transcript = meta_path.replace(".meta.json", ".jsonl")
        if not os.path.exists(transcript):
            continue
        try:
            meta = json.load(open(meta_path))
        except (ValueError, OSError):
            continue
        counts, cost, _, _ = read_usage(transcript)
        name = layer_of(meta.get("description", ""))
        row = layers.setdefault(
            name, {"agents": 0, "cost": 0.0, "counts": collections.Counter()}
        )
        row["agents"] += 1
        row["cost"] += cost
        row["counts"] += counts

    sub_cost = sum(r["cost"] for r in layers.values())
    sub_agents = sum(r["agents"] for r in layers.values())
    return {
        "session": sid,
        "model": model,
        "driver": {
            "requests": main_counts["requests"],
            "cost": round(main_cost, 2),
            "context_median": percentile(contexts, 0.5),
            "context_p90": percentile(contexts, 0.9),
            "context_max": contexts[-1] if contexts else 0,
            "cost_per_request": round(main_cost / main_counts["requests"], 3)
            if main_counts["requests"] else 0.0,
            **{k: main_counts[k] for k in
               ("input", "output", "cache_write", "cache_read")},
        },
        "subagents": {
            "agents": sub_agents,
            "cost": round(sub_cost, 2),
            "layers": {
                name: {
                    "agents": r["agents"],
                    "cost": round(r["cost"], 2),
                    "cost_per_agent": round(r["cost"] / r["agents"], 2),
                    "cache_read": r["counts"]["cache_read"],
                    "output": r["counts"]["output"],
                }
                for name, r in sorted(
                    layers.items(), key=lambda kv: -kv[1]["cost"]
                )
            },
        },
        "total": round(main_cost + sub_cost, 2),
    }


def print_report(results: list[dict]) -> None:
    grand_driver = sum(r["driver"]["cost"] for r in results)
    grand_sub = sum(r["subagents"]["cost"] for r in results)
    grand = grand_driver + grand_sub

    print(f"{'session':10} {'requests':>8} {'driver $':>10} {'agents':>7} "
          f"{'subagent $':>11} {'total $':>9}  ctx med/max")
    for r in results:
        d, s = r["driver"], r["subagents"]
        print(f"{r['session'][:8]:10} {d['requests']:8d} {d['cost']:10,.2f} "
              f"{s['agents']:7d} {s['cost']:11,.2f} {r['total']:9,.2f}"
              f"  {d['context_median']:,}/{d['context_max']:,}")

    print(f"\n{'TOTAL':10} {'':8} {grand_driver:10,.2f} "
          f"{sum(r['subagents']['agents'] for r in results):7d} "
          f"{grand_sub:11,.2f} {grand:9,.2f}")
    if grand:
        print(f"{'':10} {'':8} {100*grand_driver/grand:9.0f}% {'':7} "
              f"{100*grand_sub/grand:10.0f}%")

    layers: dict[str, dict] = {}
    for r in results:
        for name, row in r["subagents"]["layers"].items():
            acc = layers.setdefault(name, {"agents": 0, "cost": 0.0,
                                           "cache_read": 0, "output": 0})
            for k in acc:
                acc[k] += row[k]

    if layers:
        print(f"\n{'layer':18} {'agents':>7} {'cost $':>9} {'$/agent':>9} "
              f"{'cache read':>13} {'output':>10}  share")
        for name, row in sorted(layers.items(), key=lambda kv: -kv[1]["cost"]):
            share = 100 * row["cost"] / grand if grand else 0
            print(f"{name:18} {row['agents']:7d} {row['cost']:9,.2f} "
                  f"{row['cost']/row['agents']:9,.2f} {row['cache_read']:13,d} "
                  f"{row['output']:10,d}  {share:4.1f}%")
        print(f"{'driver thread':18} {0:7d} {grand_driver:9,.2f} {'--':>9} "
              f"{'':13} {'':10}  {100*grand_driver/grand if grand else 0:4.1f}%")

    print("\nCost-equivalents at list rates, not an invoice. Deduplicated by "
          "message id;\na naive sum over usage records overstates by ~3x.")
    return layers, grand_driver


def print_outcomes(layers: dict, spec: dict) -> None:
    """Cost per SUCCESS, and the incremental cost of an arm that buys some.

    Cost per run says what a layer spent. It cannot say whether the spend
    bought anything, which is the question every keep-or-cut decision in the
    funnel actually asks -- `idea-novelty` costs more per kill than the debate
    it saves, and that is only an argument once the kills have a denominator.

    The tool supplies the numerator from the transcripts and refuses to invent
    the denominator. Successes are declared by the author in the outcomes file,
    per layer, with a one-line definition of what counted and the date the
    definition was fixed. A success definition chosen after reading the costs
    is a rationalization with a decimal point, so the date is printed beside
    every figure and the tool cannot check it.

    A layer may declare SEVERAL counters, keyed `<layer> / <counter name>`.
    `idea-novelty` needs three (occupancy adjudication, displacement
    correction, confirmed kill) because its outputs differ in kind and in
    frequency: pooling a rare irreversible kill with a routine adjudication
    hides the rarity of one and the weight of the other. Counters that share a
    layer share one measured cost, so the cost is printed once for the layer
    and the counters hang under it. Do not sum a layer's counter rows.
    """
    declared = spec.get("declared_on")
    if not declared:
        print("\nFAIL: outcomes file has no `declared_on` date. A success "
              "definition is only worth reporting if it predates the costs.")
        return

    # Group `<layer> / <counter>` keys under their measured layer, order kept.
    grouped: dict[str, list] = {}
    for key, row in spec.get("layers", {}).items():
        if key.startswith("_"):
            continue  # notes in the outcomes file, not counters
        layer, _, counter = key.partition(" / ")
        grouped.setdefault(layer.strip(), []).append((counter.strip(), row))

    print(f"\nOutcomes, declared {declared}")
    for name, counters in grouped.items():
        measured = layers.get(name)
        if measured is None:
            print(f"\n{name}: [MATERIAL GAP: layer not measured in these "
                  f"sessions]")
            continue
        cost = measured["cost"]
        runs = next((r.get("runs") for _, r in counters if r.get("runs")),
                    measured["agents"])
        per_run = cost / runs if runs else 0.0
        print(f"\n{name}: {measured['agents']} agents, ${cost:,.2f}, "
              f"{runs} runs, ${per_run:,.2f} per run")
        for counter, row in counters:
            label = counter or "success"
            definition = row.get("success_is")
            succ = row.get("successes")
            if not definition or succ is None:
                print(f"  {label:34} {'--':>5}  {'--':>10}  "
                      f"[MATERIAL GAP: no declared success definition]")
                continue
            per_succ = f"{cost / succ:,.2f}" if succ else "inf"
            print(f"  {label:34} {succ:5d}  {per_succ:>10}  {definition}")
        if len(counters) > 1:
            print(f"  (one measured cost across {len(counters)} counters; "
                  f"the rows are different denominators, not different spend)")

    for comp in spec.get("comparisons", []):
        arms = {}
        for side in ("with", "without"):
            arm = comp.get(side, {})
            cost = sum(layers[n]["cost"] for n in arm.get("layers", [])
                       if n in layers)
            runs, succ = arm.get("runs"), arm.get("successes")
            if not runs or succ is None:
                print(f"\n{comp.get('name', '?')}: arm `{side}` needs runs and "
                      f"successes; skipped")
                arms = {}
                break
            arms[side] = (cost / runs, succ / runs)
        if not arms:
            continue
        (cost_w, rate_w), (cost_o, rate_o) = arms["with"], arms["without"]
        d_cost, d_rate = cost_w - cost_o, rate_w - rate_o
        print(f"\n{comp.get('name', '?')}: {100*d_rate:+.1f}pp of success at "
              f"{d_cost:+,.3f} per run")
        if abs(d_rate) < 1e-9:
            print("  incremental cost per additional success: undefined "
                  "(the arm bought no measured success)")
        else:
            print(f"  incremental cost per additional success: "
                  f"{d_cost / d_rate:,.2f}")
        print(f"  arms: {comp.get('with', {}).get('layers')} vs "
              f"{comp.get('without', {}).get('layers')}")

    print("\nSuccess counts are the author's declaration, not a measurement. "
          "The date above\nis when the definition was fixed; nothing here can "
          "verify it came first.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", help="project directory slug under ~/.claude/projects")
    ap.add_argument("--session", help="one session id or unique prefix")
    ap.add_argument("--since", help="only sessions modified on/after YYYY-MM-DD")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--outcomes",
                    help="JSON file declaring, per layer, what counted as a "
                         "success and how many there were; adds cost per "
                         "success and the incremental cost of an arm")
    args = ap.parse_args()

    if args.project:
        root = os.path.join(PROJECTS, args.project)
    else:
        cwd = os.path.realpath(os.getcwd())
        slug = "-" + cwd.lstrip("/").replace("/", "-").replace(" ", "-").replace(".", "-")
        root = os.path.join(PROJECTS, slug)

    if not os.path.isdir(root):
        print(f"no transcripts at {root}\n"
              f"pass --project with a directory name from {PROJECTS}", file=sys.stderr)
        return 1

    paths = sorted(glob.glob(os.path.join(root, "*.jsonl")))
    if args.session:
        paths = [p for p in paths if os.path.basename(p).startswith(args.session)]
    if args.since:
        import datetime
        cutoff = datetime.datetime.strptime(args.since, "%Y-%m-%d").timestamp()
        paths = [p for p in paths if os.path.getmtime(p) >= cutoff]
    if not paths:
        print("no matching sessions", file=sys.stderr)
        return 1

    results = [analyse_session(p) for p in paths]
    results = [r for r in results if r["driver"]["requests"]]

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    layers, _ = print_report(results)
    if args.outcomes:
        try:
            spec = json.load(open(args.outcomes))
        except (ValueError, OSError) as exc:
            print(f"\nFAIL: outcomes file unreadable: {exc}", file=sys.stderr)
            return 1
        print_outcomes(layers, spec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
