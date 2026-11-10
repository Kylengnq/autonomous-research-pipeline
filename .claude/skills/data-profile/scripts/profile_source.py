"""F-1 held-data profile, source-agnostic.

Reference implementation of the `data-profile` skill. Reads a manifest,
profiles every declared source read-only behind the peek firewall, and
writes the machine-readable profile (with the `field_index` the F1
anchor-existence gate consumes), the readable companion, the handoff
extract later funnel layers may see, the quarantined query log, and the
append-only peek ledger.

Nothing here knows any particular schema. Keys, time fields, entity
fields, and the unit of observation are inferred from the data and can
be overridden per source in the manifest (`unit_hint`, `prior_table`).

Every query goes through run_query(), which enforces the firewall before
execution: a statement naming both a declared candidate outcome and a
declared candidate treatment is refused, because that is a relation
between two substantive variables. Refusals are logged, not hidden.

Usage:
  profile_source.py --manifest <manifest.md> --root <project root>
                    [--out-dir ideas] [--probes ideas/expansion_probes.json]
                    [--registry-rules ideas/registry_recheck_rules.json]
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime

SCRIPT_NAME = "skills/data-profile/scripts/profile_source.py"
REQUIRED_MANIFEST_KEYS = ["name", "kind", "access", "licence", "redistribution", "refresh_cadence"]
DATE_PATTERNS = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
    (re.compile(r"^\d{4}-\d{2}$"), "%Y-%m"),
    (re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$"), "%m/%d/%Y"),
]
ID_HINT = re.compile(r"(^|_)(id|code|number|key|ssn|ein|cik|fips)($|_)")
MAX_CATEGORICAL = 400


def q(ident):
    """Quote a SQL identifier: real headers collide with reserved words."""
    return '"%s"' % ident.replace('"', '""')


class FirewallViolation(Exception):
    """Raised when a query would relate two substantive variables."""


class Ledger:
    """Append-only peek ledger plus the quarantined raw query log."""

    def __init__(self, outcomes, treatments):
        self.outcomes = [o.lower() for o in outcomes]
        self.treatments = [t.lower() for t in treatments]
        self.entries = []
        self.raw = []
        self.refusals = 0

    def check(self, sql):
        lowered = sql.lower()
        hit_out = [f for f in self.outcomes if re.search(r"\b%s\b" % re.escape(f), lowered)]
        hit_treat = [f for f in self.treatments if re.search(r"\b%s\b" % re.escape(f), lowered)]
        if hit_out and hit_treat:
            raise FirewallViolation("query names outcome %s and treatment %s together" % (hit_out, hit_treat))

    def record(self, source, sql, purpose, rows, refused=""):
        stamp = datetime.now().isoformat(timespec="seconds")
        tables = sorted(set(re.findall(r"from\s+([a-z_][a-z0-9_]*)", sql.lower())))
        self.entries.append({"timestamp": stamp, "script": SCRIPT_NAME, "source": source,
                             "tables": tables, "purpose": purpose, "rows": rows, "refused": refused})
        self.raw.append("%s  %s\n%s\n" % (stamp, purpose, sql.strip()))


def run_query(cur, ledger, source, sql, purpose, params=()):
    try:
        ledger.check(sql)
    except FirewallViolation as exc:
        ledger.refusals += 1
        ledger.record(source, sql, purpose, 0, refused=str(exc))
        raise
    cur.execute(sql, params)
    rows = cur.fetchall()
    ledger.record(source, sql, purpose, len(rows))
    return rows


def parse_manifest(path):
    with open(path) as fh:
        text = fh.read()
    sources = []
    for block in re.findall(r"```text\n(.*?)```", text, flags=re.S):
        source = {}
        for line in block.strip().splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            source[key.strip()] = value.strip()
        if source:
            sources.append(source)
    return sources


def split_list(value):
    if not value or value.strip().lower() == "none":
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def classify(cur, ledger, source_name, table, field, n_rows):
    """Decide whether a column reads as a date, a number, or text.

    Counted over the whole column, not a head sample. A delivered extract
    is usually ordered by something (state, date, source system), so the
    first rows are systematically unrepresentative: a 500-row head of
    this WARN file called a mixed column numeric because the early states
    happened to use numeric region codes.
    """
    counts = run_query(
        cur, ledger, source_name,
        "SELECT COUNT(%s), "
        "SUM(CASE WHEN %s GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]*' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN %s GLOB '*[0-9]*' AND %s NOT GLOB '*[^0-9.,+-]*' THEN 1 ELSE 0 END) "
        "FROM %s" % (q(field), q(field), q(field), q(field), q(table)),
        "type census of %s.%s" % (table, field),
    )[0]
    non_null, dated, numeric = counts[0], counts[1] or 0, counts[2] or 0
    if not non_null:
        return "empty", 0.0
    if dated / non_null >= 0.8:
        return "date", dated / non_null
    if numeric / non_null >= 0.95:
        return "number", numeric / non_null
    return "text", numeric / non_null


def profile_table(cur, ledger, source_name, table):
    cols = run_query(cur, ledger, source_name, "PRAGMA table_info(%s)" % q(table), "schema of %s" % table)
    n_rows = run_query(cur, ledger, source_name, "SELECT COUNT(*) FROM %s" % q(table),
                       "row count of %s" % table)[0][0]
    fields = []
    for col in cols:
        name = col[1]
        stats = run_query(
            cur, ledger, source_name,
            "SELECT COUNT(%s), COUNT(DISTINCT %s), MIN(%s), MAX(%s) FROM %s" % (q(name), q(name), q(name), q(name), q(table)),
            "univariate summary of %s.%s" % (table, name),
        )[0]
        non_null, distinct, lo, hi = stats
        kind, purity = classify(cur, ledger, source_name, table, name, n_rows) if non_null else ("empty", 0.0)
        fields.append({
            "name": name,
            "reads_as": kind,
            "type_purity": round(purity, 4),
            "missing_rate": round(1 - (non_null / n_rows), 4) if n_rows else None,
            "distinct": distinct,
            "min": lo,
            "max": hi,
        })
    return {"name": table, "rows": n_rows, "fields": fields}


def infer_unit(cur, ledger, source_name, table_profile, hint):
    """Name the unit of observation, and count duplicates on that key."""
    table, n_rows = table_profile["name"], table_profile["rows"]
    fields = table_profile["fields"]
    present = {f["name"] for f in fields}
    key = []
    if hint:
        wanted = [k.strip() for k in hint.split(",") if k.strip()]
        # The hint describes the source's main table; a dimension table in
        # the same database will not have those columns, so fall back to
        # inference rather than failing the whole profile.
        key = wanted if all(k in present for k in wanted) else []
    if not key:
        unique = [f["name"] for f in fields
                  if f["distinct"] and n_rows and f["distinct"] / n_rows > 0.98 and f["reads_as"] != "date"]
        if unique:
            key = [unique[0]]
        else:
            entity = sorted([f for f in fields if f["reads_as"] == "text" and f["distinct"]],
                            key=lambda f: -f["distinct"])
            dates = [f for f in fields if f["reads_as"] == "date"]
            key = ([entity[0]["name"]] if entity else []) + ([dates[0]["name"]] if dates else [])
    if not key:
        return {"key": [], "label": "unknown", "duplicate_rows_on_key": None}
    cols = ", ".join(q(k) for k in key)
    dupes = run_query(
        cur, ledger, source_name,
        "SELECT COUNT(*) FROM (SELECT %s FROM %s GROUP BY %s HAVING COUNT(*) > 1)" % (cols, q(table), cols),
        "duplicate rows on the candidate unit key (%s)" % cols,
    )[0][0]
    return {"key": key, "label": "-".join(key), "duplicate_rows_on_key": dupes}


def identifier_map(cur, ledger, source_name, table_profile, prior_table, unit_key):
    """Coverage, uniqueness and cross-vintage stability of candidate keys."""
    table, n_rows = table_profile["name"], table_profile["rows"]
    out = []
    candidates = [f for f in table_profile["fields"]
                  if ID_HINT.search(f["name"]) or (f["distinct"] and n_rows and f["distinct"] / n_rows > 0.5)]
    if not candidates:
        candidates = [f for f in table_profile["fields"] if f["reads_as"] == "text"][:3]
    for field in candidates[:6]:
        name = field["name"]
        entry = {
            "key": [name],
            "coverage": round(1 - (field["missing_rate"] or 0), 4),
            "distinct": field["distinct"],
            "unique_per_row": bool(field["distinct"] == n_rows),
            "stable_across_vintages": None,
            "vintage_evidence": None,
        }
        if prior_table and unit_key:
            anchor = unit_key[0]
            changed = run_query(
                cur, ledger, source_name,
                "SELECT COUNT(*) FROM ("
                "SELECT c.%s FROM (SELECT DISTINCT %s, %s AS v FROM %s) c "
                "JOIN (SELECT DISTINCT %s, %s AS v FROM %s) p ON c.%s = p.%s "
                "WHERE c.v IS NOT p.v)" % (q(anchor), q(anchor), q(name), q(table), q(anchor), q(name), q(prior_table), q(anchor), q(anchor)),
                "vintage stability of %s" % name,
            )[0][0]
            compared = run_query(cur, ledger, source_name,
                                 "SELECT COUNT(DISTINCT %s) FROM %s" % (q(anchor), q(prior_table)),
                                 "units present in the prior vintage")[0][0]
            entry["stable_across_vintages"] = changed == 0
            entry["vintage_evidence"] = {
                "units_compared": compared,
                "units_whose_value_changed": changed,
                "share_changed": round(changed / compared, 4) if compared else None,
            }
        else:
            entry["vintage_evidence"] = {"note": "single vintage declared: stability cannot be checked"}
        out.append(entry)
    return out


def variation_inventory(cur, ledger, source_name, table_profile, unit_key):
    """Level counts, cluster counts and within-unit switching."""
    table = table_profile["name"]
    out = []
    for field in table_profile["fields"]:
        distinct = field["distinct"] or 0
        if not (2 <= distinct <= MAX_CATEGORICAL) or field["reads_as"] == "date":
            continue
        switches = None
        if unit_key:
            anchor = unit_key[0]
            switches = run_query(
                cur, ledger, source_name,
                "SELECT COUNT(*) FROM (SELECT %s FROM %s GROUP BY %s HAVING COUNT(DISTINCT %s) > 1)"
                % (q(anchor), q(table), q(anchor), q(field["name"])),
                "within-unit switching of %s" % field["name"],
            )[0][0]
        clusterable = bool(ID_HINT.search(field["name"])) or field["name"] in (
            "state", "county", "msa", "zip", "region", "city", "industry")
        note = ""
        if clusterable and distinct < 30:
            note = "fewer than 30 clusters: cluster-robust inference at this level is fragile"
        out.append({
            "field": field["name"],
            "levels": distinct,
            "clusters_if_used_for_clustering": distinct if clusterable else None,
            "units_with_within_unit_variation": switches,
            "note": note,
        })
    return out


def quality_report(cur, ledger, source_name, table_profile, manifest, unit):
    """Missingness, contamination, top-coding, masking, sprawl, coverage."""
    issues = []
    table, n_rows = table_profile["name"], table_profile["rows"]
    notes = manifest.get("notes", "").lower()
    for field in table_profile["fields"]:
        name = field["name"]
        if field["reads_as"] == "empty":
            issues.append({"field": name, "issue": "entirely_empty",
                           "evidence": "no non-null values in %d rows" % n_rows})
            continue
        if field["missing_rate"] and field["missing_rate"] > 0.05:
            issues.append({"field": name, "issue": "missingness",
                           "evidence": "%.1f%% of rows are null" % (100 * field["missing_rate"])})
        if field["reads_as"] == "number":
            try:
                cap = float(str(field["max"]).replace(",", ""))
            except (TypeError, ValueError):
                cap = None
            if cap and cap >= 1000 and cap % 1000 == 0:
                at_cap = run_query(cur, ledger, source_name,
                                   "SELECT COUNT(*) FROM %s WHERE %s GLOB '*[0-9]*' AND %s NOT GLOB "
                                   "'*[^0-9.,+-]*' AND CAST(%s AS REAL) = ?"
                                   % (q(table), q(name), q(name), q(name)),
                                   "mass at the maximum of %s" % name, (cap,))[0][0]
                if n_rows and at_cap / n_rows > 0.002:
                    issues.append({"field": name, "issue": "top_coded",
                                   "evidence": "%.2f%% of rows sit exactly at the round maximum %s"
                                               % (100 * at_cap / n_rows, cap)})
        if field["reads_as"] == "text" and 0 < field["type_purity"] < 0.95 and field["type_purity"] > 0.05:
            issues.append({"field": name, "issue": "mixed_types",
                           "evidence": "%.0f%% of non-null values parse as numbers, the rest do not"
                                       % (100 * field["type_purity"])})
        if ID_HINT.search(name) and field["distinct"] and field["distinct"] < 100 and n_rows > 1000:
            declared = "mask" in notes and name in notes
            issues.append({"field": name, "issue": "masked_or_coarsened",
                           "evidence": "%d distinct values across %d rows%s"
                                       % (field["distinct"], n_rows,
                                          "; manifest declares this field masked" if declared else "")})
        if field["reads_as"] == "date":
            # A date column that mostly parses can still carry typo years.
            # String min/max hide them, so check the shape and the range.
            malformed = run_query(
                cur, ledger, source_name,
                "SELECT COUNT(*) FROM %s WHERE %s IS NOT NULL AND %s NOT GLOB "
                "'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*'" % (q(table), q(name), q(name)),
                "malformed date shapes in %s" % name,
            )[0][0]
            if malformed:
                samples = run_query(
                    cur, ledger, source_name,
                    "SELECT DISTINCT %s FROM %s WHERE %s IS NOT NULL AND %s NOT GLOB "
                    "'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*' LIMIT 5" % (q(name), q(table), q(name), q(name)),
                    "sample malformed dates in %s" % name,
                )
                issues.append({"field": name, "issue": "malformed_dates",
                               "evidence": "%d values do not match YYYY-MM-DD, e.g. %s"
                                           % (malformed, ", ".join(str(s[0]) for s in samples))})
            this_year = datetime.now().year
            out_of_range = run_query(
                cur, ledger, source_name,
                "SELECT COUNT(*) FROM %s WHERE %s IS NOT NULL AND "
                "(CAST(substr(%s,1,4) AS INTEGER) < 1970 OR CAST(substr(%s,1,4) AS INTEGER) > %d)"
                % (q(table), q(name), q(name), q(name), this_year + 5),
                "implausible years in %s" % name,
            )[0][0]
            if out_of_range:
                issues.append({"field": name, "issue": "implausible_dates",
                               "evidence": "%d values fall outside 1970-%d" % (out_of_range, this_year + 5)})
        if field["reads_as"] == "number":
            zeros = run_query(
                cur, ledger, source_name,
                "SELECT COUNT(*) FROM %s WHERE %s GLOB '*[0-9]*' AND %s NOT GLOB '*[^0-9.,+-]*' "
                "AND CAST(%s AS REAL) = 0" % (q(table), q(name), q(name), q(name)),
                "mass at zero in %s" % name,
            )[0][0]
            if n_rows and zeros / n_rows > 0.001:
                issues.append({"field": name, "issue": "zero_mass",
                               "evidence": "%d rows (%.2f%%) are exactly zero, which may be a sentinel for unknown "
                                           "rather than a measured zero" % (zeros, 100 * zeros / n_rows)})
        coded = split_list(manifest.get("coded_fields", ""))
        if name in coded and field["distinct"] and field["distinct"] > 50:
            issues.append({"field": name, "issue": "vocabulary_sprawl",
                           "evidence": "declared a coded field but carries %d distinct values"
                                       % field["distinct"]})
    if unit.get("duplicate_rows_on_key"):
        issues.append({"field": "-".join(unit["key"]), "issue": "duplicate_units",
                       "evidence": "%d key values appear on more than one row; the unit of observation is not unique"
                                   % unit["duplicate_rows_on_key"]})
    universe = manifest.get("expected_universe", "")
    universe_field = manifest.get("universe_field", "")
    declared_members = split_list(manifest.get("expected_members", ""))
    if declared_members and universe_field:
        observed = [r[0] for r in run_query(cur, ledger, source_name,
                                            "SELECT DISTINCT %s FROM %s ORDER BY 1" % (q(universe_field), q(table)),
                                            "observed values of %s" % universe_field) if r[0] is not None]
        absent = [m for m in declared_members if m not in observed]
        unexpected = [o for o in observed if o not in declared_members]
        if absent:
            issues.append({"field": universe_field, "issue": "coverage_gap",
                           "evidence": "declared members absent from the data: %s" % ", ".join(absent)})
        if unexpected:
            issues.append({"field": universe_field, "issue": "unexpected_members",
                           "evidence": "present but outside the declared universe: %s" % ", ".join(unexpected)})
    declared_units = re.findall(r"\b[A-Z]{2}\b", universe)
    if declared_units and universe_field and not declared_members:
        observed = [r[0] for r in run_query(cur, ledger, source_name,
                                            "SELECT DISTINCT %s FROM %s ORDER BY 1" % (q(universe_field), q(table)),
                                            "observed values of %s" % universe_field)]
        missing = [u for u in declared_units if u not in observed]
        if missing:
            issues.append({"field": universe_field, "issue": "coverage_gap",
                           "evidence": "manifest declares %d, %d observed; absent: %s"
                                       % (len(declared_units), len(observed), ", ".join(missing))})
    expected_count = re.search(r"(\d+)\s+(states|entities|units)", universe)
    if expected_count and universe_field and not declared_members:
        observed_n = run_query(cur, ledger, source_name,
                               "SELECT COUNT(DISTINCT %s) FROM %s" % (q(universe_field), q(table)),
                               "observed count of %s" % universe_field)[0][0]
        if observed_n < int(expected_count.group(1)):
            issues.append({"field": universe_field, "issue": "coverage_gap",
                           "evidence": "manifest declares %s %s, %d observed. This is a count comparison only: "
                                       "declare expected_members to learn which are absent and which are extra"
                                       % (expected_count.group(1), expected_count.group(2), observed_n)})
    return issues


def time_span(cur, ledger, source_name, table_profile):
    dates = [f for f in table_profile["fields"] if f["reads_as"] == "date"]
    spans = {}
    for field in dates:
        spans[field["name"]] = {"min": field["min"], "max": field["max"]}
    return spans


def recheck_registry(profile, rules_path):
    """Test blocked-registry ingredients against the profile, by rule file."""
    if not rules_path or not os.path.exists(rules_path):
        return [{"idea": "(none)", "ingredient": "-", "verdict": "not run",
                 "evidence": "no registry_recheck_rules.json for this project; recheck is manual"}]
    with open(rules_path) as fh:
        rules = json.load(fh)["rules"]
    index = set(profile["field_index"])
    results = []
    for rule in rules:
        req = rule["requires"]
        reasons, satisfied = [], True
        for suffix in req.get("fields_present", []):
            hit = [f for f in index if f.endswith("." + suffix)]
            if hit:
                reasons.append("%s present" % suffix)
            else:
                satisfied = False
                reasons.append("%s absent" % suffix)
        for field, floor in (req.get("min_coverage") or {}).items():
            ident = next((i for source in profile["sources"] for i in source["identifiers"]
                          if i["key"] == [field]), None)
            if ident and ident["coverage"] >= floor:
                reasons.append("%s coverage %.1f%% >= %.0f%%" % (field, 100 * ident["coverage"], 100 * floor))
            else:
                satisfied = False
                reasons.append("%s coverage below %.0f%%" % (field, 100 * floor))
        stable = req.get("stable_key")
        if stable:
            ident = next((i for source in profile["sources"] for i in source["identifiers"]
                          if i["key"] == [stable]), None)
            evidence = (ident or {}).get("vintage_evidence") or {}
            if ident and ident["stable_across_vintages"]:
                reasons.append("%s stable across vintages" % stable)
            else:
                satisfied = False
                reasons.append("%s changed for %s of %s units"
                               % (stable, evidence.get("units_whose_value_changed"),
                                  evidence.get("units_compared")))
        results.append({"idea": rule["idea"], "ingredient": rule["ingredient"],
                        "verdict": "unblocked" if satisfied else "still blocked",
                        "evidence": "; ".join(reasons)})
    return results


def render(profile, out_dir):
    source = profile["sources"][0]
    lines = ["# Held-data profile — %s" % profile["generated"], ""]
    for src in profile["sources"]:
        lines.append("Source `%s` (%s). Licence: %s. Refresh cadence: %s."
                     % (src["name"], src["kind"], src["licence"], src["refresh_cadence"]))
    lines += ["", "## Inventory", "", "| Table | Rows | Unit | Duplicates on unit key | Date fields |",
              "|---|---|---|---|---|"]
    for src in profile["sources"]:
        for tbl in src["tables"]:
            spans = "; ".join("%s %s..%s" % (k, v["min"], v["max"]) for k, v in tbl["time_span"].items()) or "none"
            lines.append("| %s | %d | %s | %s | %s |" % (tbl["name"], tbl["rows"], tbl["unit"]["label"],
                                                         tbl["unit"]["duplicate_rows_on_key"], spans))
    lines += ["", "## Fields", "", "| Field | Reads as | Missing | Distinct |", "|---|---|---|---|"]
    for tbl in source["tables"]:
        for f in tbl["fields"]:
            lines.append("| %s.%s | %s | %.1f%% | %s |" % (tbl["name"], f["name"], f["reads_as"],
                                                          100 * (f["missing_rate"] or 0), f["distinct"]))
    lines += ["", "## Identifier map", "",
              "| Key | Coverage | Distinct | Unique per row | Stable across vintages | Evidence |",
              "|---|---|---|---|---|---|"]
    for ident in source["identifiers"]:
        ev = ident.get("vintage_evidence") or {}
        detail = ev.get("note") or ("%s of %s units changed" % (ev.get("units_whose_value_changed"),
                                                               ev.get("units_compared")))
        lines.append("| %s | %.1f%% | %s | %s | %s | %s |" % (", ".join(ident["key"]), 100 * ident["coverage"],
                                                              ident["distinct"], ident["unique_per_row"],
                                                              ident["stable_across_vintages"], detail))
    lines += ["", "## Variation", "", "| Field | Levels | Clusters | Units with within-unit variation | Note |",
              "|---|---|---|---|---|"]
    for var in source["variation"]:
        lines.append("| %s | %d | %s | %s | %s |" % (var["field"], var["levels"],
                                                     var["clusters_if_used_for_clustering"] or "n/a",
                                                     var["units_with_within_unit_variation"], var["note"]))
    lines += ["", "## Measurement quality", "", "| Field | Issue | Evidence |", "|---|---|---|"]
    for issue in source["quality"]:
        lines.append("| %s | %s | %s |" % (issue["field"], issue["issue"], issue["evidence"]))
    lines += ["", "## Expansion map", "", "| External source | Join key | Match rate | Verified |", "|---|---|---|---|"]
    for exp in profile["expansion"]:
        rate = "unverified" if exp["match_rate"] is None else "%.1f%%" % (100 * exp["match_rate"])
        lines.append("| %s | %s | %s | %s |" % (exp["external"], ", ".join(exp["join_key"]), rate, exp["verified"]))
    lines += ["", "## Blocked-registry recheck", "", "| Idea | Ingredient | Verdict | Evidence |", "|---|---|---|---|"]
    for rec in profile["blocked_registry_recheck"]:
        lines.append("| %s | %s | %s | %s |" % (rec["idea"], rec["ingredient"], rec["verdict"], rec["evidence"]))
    lines += ["", "## Publication", "",
              "Redistributable: %s. Not redistributable: %s."
              % (profile["publication"]["redistributable"], profile["publication"]["not_redistributable"]), ""]
    with open(os.path.join(out_dir, "data_profile.md"), "w") as fh:
        fh.write("\n".join(lines))

    extract = ["# Data capability extract (handoff) — %s" % profile["generated"], "",
               "Facts only. F0, F1, F2, and the F3 briefing pack may read this file.",
               "It carries no statistic relating two substantive variables.", ""]
    for src in profile["sources"]:
        tbl = src["tables"][0]
        spans = "; ".join("%s %s to %s" % (k, v["min"], v["max"]) for k, v in tbl["time_span"].items())
        extract.append("**%s.** %d rows, unit %s%s.%s"
                       % (src["name"], tbl["rows"], tbl["unit"]["label"],
                          ", " + spans if spans else "",
                          " %d rows share a unit key, so the unit is not unique."
                          % tbl["unit"]["duplicate_rows_on_key"] if tbl["unit"]["duplicate_rows_on_key"] else ""))
    extract += ["", "**Keys that join.**"]
    for ident in source["identifiers"]:
        ev = ident.get("vintage_evidence") or {}
        detail = ev.get("note") or ("%s of %s units changed value across vintages"
                                    % (ev.get("units_whose_value_changed"), ev.get("units_compared")))
        extract.append("- `%s`: %.1f%% coverage, %s distinct, unique per row: %s. %s"
                       % (ident["key"][0], 100 * ident["coverage"], ident["distinct"],
                          ident["unique_per_row"], detail))
    extract += ["", "**What varies.**"]
    for var in source["variation"][:12]:
        extract.append("- `%s`: %d levels.%s" % (var["field"], var["levels"],
                                                 " " + var["note"] if var["note"] else ""))
    extract += ["", "**Measurement caveats that bind any design.**"]
    for issue in source["quality"]:
        extract.append("- `%s` — %s: %s." % (issue["field"], issue["issue"], issue["evidence"]))
    extract += ["", "**Verified outside joins.**"]
    for exp in profile["expansion"]:
        if exp["verified"]:
            extract.append("- %s on `%s`: %.1f%% of probed rows match."
                           % (exp["external"], ", ".join(exp["join_key"]), 100 * exp["match_rate"]))
        else:
            extract.append("- %s on `%s`: candidate only, no probe run — treat as unverified."
                           % (exp["external"], ", ".join(exp["join_key"])))
    extract += ["", "**What may be published.** %s. Not: %s."
                % (profile["publication"]["redistributable"], profile["publication"]["not_redistributable"]), ""]
    os.makedirs(os.path.join(out_dir, "handoff"), exist_ok=True)
    with open(os.path.join(out_dir, "handoff", "data_profile_extract.md"), "w") as fh:
        fh.write("\n".join(extract))


def write_ledger(out_dir, ledger):
    os.makedirs(os.path.join(out_dir, "quarantine"), exist_ok=True)
    with open(os.path.join(out_dir, "quarantine", "profile_queries.log"), "w") as fh:
        fh.write("\n".join(ledger.raw))
    peek = os.path.join(out_dir, "peek_log.md")
    if not os.path.exists(peek):
        with open(peek, "w") as fh:
            fh.write("# Peek ledger\n\nAppend-only. Every query run against held data during S1 and S1b.\n"
                     "The pre-registration reads this file to declare its retrospective elements.\n\n")
            fh.write("| timestamp | script | source | tables | purpose | rows | refused |\n|---|---|---|---|---|---|---|\n")
    with open(peek, "a") as fh:
        for e in ledger.entries:
            fh.write("| %s | %s | %s | %s | %s | %s | %s |\n"
                     % (e["timestamp"], e["script"], e["source"], " ".join(e["tables"]),
                        e["purpose"], e["rows"], e["refused"] or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out-dir", default="ideas")
    ap.add_argument("--probes", default="ideas/expansion_probes.json")
    ap.add_argument("--registry-rules", default="ideas/registry_recheck_rules.json")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    out_dir = os.path.join(root, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    declared = parse_manifest(os.path.join(root, args.manifest) if not os.path.isabs(args.manifest)
                              else args.manifest)
    profiled, absent = [], []
    all_entries = Ledger([], [])

    for manifest in declared:
        for key in REQUIRED_MANIFEST_KEYS:
            if not manifest.get(key):
                sys.exit("manifest source '%s' is missing required key '%s' — profiling stops "
                         "before touching the source" % (manifest.get("name", "?"), key))
        db_rel = manifest["access"].replace("sqlite:///", "")
        db_path = db_rel if os.path.isabs(db_rel) else os.path.join(root, db_rel)
        if not os.path.exists(db_path):
            absent.append({"name": manifest["name"], "reason": "declared in the manifest, not present at %s" % db_rel,
                           "redistribution": manifest.get("redistribution", "")})
            continue

        ledger = Ledger(split_list(manifest.get("candidate_outcomes", "")),
                        split_list(manifest.get("candidate_treatments", "")))
        con = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
        cur = con.cursor()
        tables = [r[0] for r in run_query(cur, ledger, manifest["name"],
                                          "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
                                          "table listing")]
        prior = manifest.get("prior_table") or None
        table_profiles = []
        for table in tables:
            tp = profile_table(cur, ledger, manifest["name"], table)
            tp["unit"] = infer_unit(cur, ledger, manifest["name"], tp, manifest.get("unit_hint"))
            tp["time_span"] = time_span(cur, ledger, manifest["name"], tp)
            table_profiles.append(tp)
        primary = next((t for t in table_profiles if t["name"] != prior), table_profiles[0])
        idents = identifier_map(cur, ledger, manifest["name"], primary, prior, primary["unit"]["key"])
        variation = variation_inventory(cur, ledger, manifest["name"], primary, primary["unit"]["key"])
        quality = quality_report(cur, ledger, manifest["name"], primary, manifest, primary["unit"])
        con.close()

        profiled.append({
            "name": manifest["name"], "kind": manifest["kind"], "licence": manifest["licence"],
            "refresh_cadence": manifest["refresh_cadence"], "primary_table": primary["name"],
            "tables": table_profiles, "identifiers": idents, "variation": variation, "quality": quality,
        })
        all_entries.entries.extend(ledger.entries)
        all_entries.raw.extend(ledger.raw)
        all_entries.refusals += ledger.refusals

    if not profiled:
        sys.exit("no declared source is present on disk; nothing profiled")

    probes_path = os.path.join(root, args.probes)
    expansion = json.load(open(probes_path))["probes"] if os.path.exists(probes_path) else []

    first = declared[0]
    field_index = sorted("%s.%s.%s" % (src["name"], t["name"], f["name"])
                         for src in profiled for t in src["tables"] for f in t["fields"])
    profile = {
        "generated": datetime.now().date().isoformat(),
        "manifest": args.manifest,
        "refresh_cadence": first["refresh_cadence"],
        "sources": profiled,
        "sources_declared_but_absent": absent,
        "expansion": expansion,
        "publication": {
            "redistributable": first["redistribution"],
            "not_redistributable": "row-level records" if "nothing" not in first["redistribution"] else "everything",
            "licence": first["licence"],
        },
        "field_index": field_index,
        "peek_queries": len(all_entries.entries),
        "firewall_refusals": all_entries.refusals,
    }
    profile["blocked_registry_recheck"] = recheck_registry(profile, os.path.join(root, args.registry_rules))

    with open(os.path.join(out_dir, "data_profile.json"), "w") as fh:
        json.dump(profile, fh, indent=2)
    render(profile, out_dir)
    write_ledger(out_dir, all_entries)

    print("sources profiled:    %d (%d declared but absent)" % (len(profiled), len(absent)))
    print("tables profiled:     %d" % sum(len(s["tables"]) for s in profiled))
    print("fields indexed:      %d" % len(field_index))
    print("quality issues:      %d" % sum(len(s["quality"]) for s in profiled))
    print("expansion entries:   %d (%d probe-verified)" % (len(expansion), sum(1 for e in expansion if e["verified"])))
    print("peek-ledger entries: %d (%d refused)" % (len(all_entries.entries), all_entries.refusals))
    for rec in profile["blocked_registry_recheck"]:
        print("registry recheck:    %-38s %s" % (rec["idea"][:38], rec["verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
