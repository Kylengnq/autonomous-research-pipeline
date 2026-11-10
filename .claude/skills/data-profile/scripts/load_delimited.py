"""Stage a delimited file (CSV/TSV) into SQLite so it can be profiled.

A delivered extract is a held source like any other, but it carries no
schema, so profiling it starts by staging it. Everything loads as TEXT
and blanks load as NULL: the point of F-1 is to see the source as it
is, and coercing types at load would hide exactly the contamination the
profile is supposed to report.

Column names are sanitised to snake_case for SQL; the mapping back to
the source header is written alongside, so a card that names a field can
be traced to the delivered column.

Usage:
  load_delimited.py --src <file.csv> --db <staging.sqlite> --table <name>
                    [--delimiter ,] [--encoding utf-8]
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import sys


def sanitise(name, taken):
    """snake_case a delivered header into a usable SQL identifier."""
    clean = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip()).strip("_").lower()
    if not clean:
        clean = "col"
    if re.match(r"^[0-9]", clean):
        clean = "c_" + clean
    base, n = clean, 2
    while clean in taken:
        clean = "%s_%d" % (base, n)
        n += 1
    taken.add(clean)
    return clean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--encoding", default="utf-8")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.db)), exist_ok=True)
    with open(args.src, newline="", encoding=args.encoding, errors="replace") as fh:
        reader = csv.reader(fh, delimiter=args.delimiter)
        header = next(reader)
        taken = set()
        columns = [sanitise(h, taken) for h in header]

        con = sqlite3.connect(args.db)
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS "%s"' % args.table)
        cur.execute('CREATE TABLE "%s" (%s)' % (args.table, ", ".join('"%s" TEXT' % c for c in columns)))
        placeholders = ",".join("?" * len(columns))
        insert = 'INSERT INTO "%s" VALUES (%s)' % (args.table, placeholders)

        batch, rows, ragged = [], 0, 0
        for record in reader:
            if len(record) != len(columns):
                ragged += 1
                record = (record + [""] * len(columns))[: len(columns)]
            batch.append(tuple(v.strip() if v.strip() != "" else None for v in record))
            if len(batch) >= 5000:
                cur.executemany(insert, batch)
                rows += len(batch)
                batch = []
        if batch:
            cur.executemany(insert, batch)
            rows += len(batch)
        con.commit()
        con.close()

    mapping = {
        "source_file": os.path.abspath(args.src),
        "table": args.table,
        "rows_loaded": rows,
        "ragged_rows_padded_or_truncated": ragged,
        "columns": [{"delivered": h, "staged": c} for h, c in zip(header, columns)],
    }
    with open(os.path.splitext(args.db)[0] + "_columns.json", "w") as fh:
        json.dump(mapping, fh, indent=2)

    print("loaded %d rows into %s.%s" % (rows, args.db, args.table))
    if ragged:
        print("WARNING: %d rows did not match the header width and were padded or truncated" % ragged)
    return 0


if __name__ == "__main__":
    sys.exit(main())
