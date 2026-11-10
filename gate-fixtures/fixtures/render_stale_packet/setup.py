"""Stamp fixture mtimes so the staleness comparison is deterministic.

Rewriting the tree in a temp copy gives every file the copy time, so a fixture
about ordering has to set the order it is asserting."""
import os, time

BASE = time.time() - 600
order = [('comparative_final.md', 0), ('G1_review.pdf', 100), ('data_requests.md', 200)]
for name, offset in order:
    if os.path.exists(name):
        os.utime(name, (BASE + offset, BASE + offset))
