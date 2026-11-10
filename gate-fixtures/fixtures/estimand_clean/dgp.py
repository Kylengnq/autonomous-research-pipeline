"""Locked staggered-adoption panel, seed 20260515.

Three treated cohorts with heterogeneous effects and deliberately unequal
sizes, so uniform and group-size weighting of the cohort-time effects give
different numbers. Never-treated firms are the control group.
"""
import json
import random

SEED = 20260515
COHORTS = {4: (1.0, 5), 6: (2.0, 10), 8: (3.0, 40)}   # g: (effect, n_firms)
LAST_PERIOD = 9
N_CONTROL = 40


def panel():
    rng = random.Random(SEED)
    rows = []
    for firm in range(N_CONTROL):
        fe = rng.gauss(0, 0.1)
        for t in range(1, LAST_PERIOD + 1):
            rows.append({"firm": f"c{firm}", "cohort": 0, "t": t,
                         "y": fe + 0.05 * t})
    fid = 0
    for g, (tau, n) in COHORTS.items():
        for _ in range(n):
            fe = rng.gauss(0, 0.1)
            for t in range(1, LAST_PERIOD + 1):
                rows.append({"firm": f"g{g}_{fid}", "cohort": g, "t": t,
                             "y": fe + 0.05 * t + (tau if t >= g else 0.0)})
            fid += 1
    return rows


def cell_mean(rows, cohort, t):
    vals = [r["y"] for r in rows if r["cohort"] == cohort and r["t"] == t]
    return sum(vals) / len(vals)


def att(rows, g, t):
    """Callaway-Sant'Anna long difference against the never-treated."""
    return ((cell_mean(rows, g, t) - cell_mean(rows, g, g - 1))
            - (cell_mean(rows, 0, t) - cell_mean(rows, 0, g - 1)))


def supported(rows):
    return [(g, t) for g in COHORTS for t in range(g, LAST_PERIOD + 1)]


if __name__ == "__main__":
    json.dump(panel(), open("panel.json", "w"))
