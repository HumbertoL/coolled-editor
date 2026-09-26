#!/usr/bin/env python3
"""
Stained Glass -- a Voronoi window whose panes drift and trade territory.

Fourteen seeds wander on closed Lissajous paths; every pixel takes the colour
of its nearest seed, and pixels almost equidistant from two seeds become the
lead came between panes. As the seeds move, panes swell, shrink, pinch off
and reappear, the leading redrawing itself continuously -- the window is
alive, but never loses its structure.

A band of sunlight sweeps across diagonally once a loop, turning each pane
it crosses WHITE, the glint you catch walking past a real window. Every seed
path and the sweep have periods dividing 53 frames, so the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
W, H = 96, 16
TAU = 2 * math.pi
PANES = [C.RED, C.BLUE, C.YELLOW, C.GREEN, C.MAGENTA, C.CYAN]
LEAD = 0.9  # pixels within this distance of a border are lead
YS = 1.6  # vertical stretch: panes read squatter on a 16-row window otherwise


def seeds():
    rnd = random.Random(14)
    out = []
    n = 14
    for i in range(n):
        base_x = (i + 0.5) * W / n + rnd.uniform(-2, 2)
        base_y = rnd.uniform(3, 13)
        out.append(
            dict(
                bx=base_x,
                by=base_y,
                ax=rnd.uniform(3, 6),
                ay=rnd.uniform(2, 5),
                fx=rnd.choice([1, 1, 2]),
                fy=rnd.choice([1, 2]),
                px=rnd.uniform(0, TAU),
                py=rnd.uniform(0, TAU),
                color=PANES[(i * 4) % len(PANES)] if i % 2 else PANES[(i * 5 + 1) % len(PANES)],
            )
        )
    # Neighbours by index are spatial neighbours, so make sure no two
    # consecutive seeds share a colour.
    for i in range(1, n):
        if out[i]["color"] == out[i - 1]["color"]:
            out[i]["color"] = PANES[(PANES.index(out[i]["color"]) + 1) % len(PANES)]
    return out


SEEDS = seeds()


def main():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        pts = [
            (
                s["bx"] + s["ax"] * math.sin(TAU * s["fx"] * t + s["px"]),
                s["by"] + s["ay"] * math.sin(TAU * s["fy"] * t + s["py"]),
                s["color"],
            )
            for s in SEEDS
        ]
        sweep = -30 + (W + 60) * t  # x of the glint's centre at row 0
        frame = anim.frame()
        for y in range(H):
            for x in range(W):
                best = second = 1e9
                colour = C.BLACK
                for sx, sy, c in pts:
                    d = math.hypot(x - sx, (y - sy) * YS)
                    if d < best:
                        second, best, colour = best, d, c
                    elif d < second:
                        second = d
                if second - best < LEAD or y in (0, H - 1) or x in (0, W - 1):
                    continue  # lead
                glint = x - (sweep + y * 1.2)
                if -3 < glint < 1:
                    colour = C.WHITE
                frame.pixel(x, y, colour)
    out = Path(__file__).resolve().parents[2] / "src/sample/stained_glass.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
