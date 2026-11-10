"""Locked pilot slice: 80 trader-meeting cells across 14 meetings."""
import itertools

takers = [f"t{i}" for i in range(20)]
meetings = [f"m{j}" for j in range(14)]
pairs = list(itertools.product(takers, meetings))[:80]


class Frame:
    def __init__(self, rows):
        self.rows = rows

    @property
    def taker(self):
        return [r[0] for r in self.rows]

    @property
    def meeting(self):
        return [r[1] for r in self.rows]


df = Frame(pairs)
