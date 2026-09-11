#!/usr/bin/env python3
"""
Bifurcation -- the logistic map, drawn left to right.

x -> r x (1 - x), the simplest model of a population with a carrying capacity.
Each column is one value of r from 3.3 to 4.0: iterate a few hundred times to
settle, then plot where the population lands. On the left it alternates between
two values; then four, then eight, then the doublings pile up into chaos, with windows of order reopening inside it. The diagram reveals two
columns a frame, and pixels hit more often are brighter.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
R_MIN, R_MAX = 3.3, 4.0
SETTLE, PLOT = 300, 120
COLS_PER_FRAME = 2


def column(col):
    r = R_MIN + (R_MAX - R_MIN) * col / 95
    x = 0.5
    for _ in range(SETTLE):
        x = r * x * (1 - x)
    hits = {}
    for _ in range(PLOT):
        x = r * x * (1 - x)
        y = round(15 - x * 15)
        hits[y] = hits.get(y, 0) + 1
    return hits


def build():
    anim = Animation(delay=DELAY)
    columns = [column(c) for c in range(96)]
    for index in range(FRAMES):
        frame = anim.frame()
        revealed = min(96, (index + 1) * COLS_PER_FRAME)
        for c in range(revealed):
            for y, n in columns[c].items():
                frame.pixel(c, y, C.WHITE if n >= 30 else C.CYAN if n >= 6 else C.BLUE)
        if revealed < 96:
            frame.vline(revealed, 0, 16, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bifurcation.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
