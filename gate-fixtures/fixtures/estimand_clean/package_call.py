"""The package call under test: uniform aggregation over supported cells."""
import json

from dgp import att, panel, supported

rows = panel()
cells = supported(rows)

json.dump({"call": "aggte(type=\"group\", balanced=TRUE) equivalent",
           "value": sum(att(rows, g, t) for g, t in cells) / len(cells),
           "convention": "uniform over supported cohort-time cells"},
          open("package.json", "w"), indent=2)
