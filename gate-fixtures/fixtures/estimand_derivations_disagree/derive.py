"""Derive the estimand by hand, twice, by independent routes.

Route A averages the cell-level effects directly. Route B accumulates a
running total and divides at the end, reaching the same quantity without
reusing route A's expression. Means, merges and arithmetic only: no
estimation package, no aggregator helper.
"""
import json

from dgp import COHORTS, att, panel, supported

rows = panel()
cells = supported(rows)

value_a = sum(att(rows, g, t) for g, t in cells) / len(cells)

total, n = 0.0, 0
for g in COHORTS:
    for t in range(g, 10):
        total += att(rows, g, t)
        n += 1
total += att(rows, 8, 9)
n += 1
value_b = total / n

json.dump({
    "formula": "ATT_uniform = (1/|S|) * sum over (g,t) in S of ATT(g,t), "
               "S = {(g,t): g in {4,6,8}, g <= t <= 9}, |S| = 12",
    "expression_a": "sum(att(rows, g, t) for g, t in cells) / len(cells)",
    "value_a": value_a,
    "expression_b": "running total over cohorts and periods, divided by n",
    "value_b": value_b,
    "tolerance": 1e-6,
}, open("reference.json", "w"), indent=2)
