#!/usr/bin/env python3
"""Review-rendering gate check (stdlib only).

`pipeline-design.md` §4: every artifact presented at a human
gate is delivered as a PDF, rendered into one packet per gate, and the
checkpoint names the PDF path. Markdown stays the machine-readable source; it is
not what the author is asked to read.

Four failures, each of which leaves the author reading the wrong thing or
reading it in the wrong state:

1. **The packet does not exist.** A checkpoint naming a PDF nobody rendered.
2. **The packet is stale.** Older than a source bound into it, so the author is
   deciding from a document that no longer matches the record. This is the one
   that will actually happen: the driver renders early, then fixes a number.
3. **The checkpoint hands over Markdown.** The easy mistake, because the driver
   has just written those `.md` paths into the run log.
4. **A source is missing from the packet.** The gate's review set is fixed per
   gate; quietly dropping one shortens the reading rather than the decision.

Inputs:

  --checkpoint FILE   the checkpoint message as presented to the author
  --packet FILE       the rendered PDF
  --sources FILE...   every source bound into it

Usage:
    python3 review_render_check.py --checkpoint msg.md --packet G1.pdf \
        --sources slate.md proposal.md
"""

import argparse
import os
import re
import sys
from pathlib import Path


# A .md path named in the checkpoint. Excludes paths inside a fenced block or
# after "source:", which are provenance rather than an instruction to read.
MD_PATH = re.compile(r"[\w./-]+\.md\b")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--packet", required=True)
    ap.add_argument("--sources", nargs="*", default=[])
    args = ap.parse_args()

    failures: list = []
    packet = Path(args.packet)
    checkpoint = Path(args.checkpoint)

    if not checkpoint.is_file():
        print(f"FAIL: checkpoint {checkpoint} not found")
        return 1
    text = checkpoint.read_text(encoding="utf-8", errors="replace")

    if not packet.is_file():
        failures.append(
            f"the checkpoint names {packet}, which does not exist. A gate "
            f"presented as a PDF that was never rendered is a gate presented as "
            f"nothing."
        )
    else:
        if packet.suffix.lower() != ".pdf":
            failures.append(f"{packet} is not a PDF; review documents are "
                            f"delivered as PDF, never as Markdown")
        p_mtime = packet.stat().st_mtime
        for src in args.sources:
            sp = Path(src)
            if not sp.is_file():
                failures.append(f"source {sp} bound into the packet does not exist")
                continue
            if sp.stat().st_mtime > p_mtime:
                failures.append(
                    f"the packet is stale: {sp} changed after {packet} was "
                    f"rendered. The author would decide from a document that no "
                    f"longer matches the record. Re-render as the last act "
                    f"before presenting the checkpoint."
                )

        if packet.name not in text and str(packet) not in text:
            failures.append(
                f"the checkpoint never names {packet.name}; the author is not "
                f"told what to read"
            )

    # Markdown offered as the thing to read.
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = "\n".join(
        line for line in body.splitlines()
        if not re.match(r"\s*(source|rendered from|bound from)\s*:", line, re.I)
    )
    md_hits = [m for m in MD_PATH.findall(body)]
    if md_hits:
        failures.append(
            f"the checkpoint hands the author Markdown: {', '.join(sorted(set(md_hits))[:4])}. "
            f"The sources are listed on the packet's own cover; naming them here "
            f"is the failure this gate exists to prevent."
        )

    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1

    print(f"review rendering OK: {packet.name} exists, is newer than all "
          f"{len(args.sources)} source(s), and is what the checkpoint names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
