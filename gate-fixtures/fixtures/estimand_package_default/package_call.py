"""The package call under test: group-size weighted aggregation.

This is the aggregate the common defaults return -- `aggte(type="simple")`
weights each cohort-time effect by its group size. It runs clean and returns
a number. It is not the pre-registered estimand.
"""
import json

from dgp import COHORTS, att, panel, supported

rows = panel()
num = den = 0.0
for g, t in supported(rows):
    weight = COHORTS[g][1]
    num += weight * att(rows, g, t)
    den += weight

json.dump({"call": "aggte(type=\"simple\")",
           "value": num / den,
           "convention": "cohort-time effects weighted by group size, not "
                         "uniformly over supported cells"},
          open("package.json", "w"), indent=2)
