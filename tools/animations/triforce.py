#!/usr/bin/env python3
"""
Triforce -- A Link to the Past.

Three golden triangles fly in from off-panel, one from above and one from
each side, spinning as they come, and lock together into the Triforce at the
centre. It pulses white once, then a diagonal shine sweeps across it. Filled
triangles are rasterised with a barycentric test so they stay solid while
rotating.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
ARRIVE = 24
SHINE_AT = 34
SIDE = 15.0
H = SIDE * math.sqrt(3) / 2        # ~13, but we squash to fit 16 rows
SQUASH = 0.6


def tri_points(cx, cy, angle):
    pts = []
    for k in range(3):
        a = angle + 2 * math.pi * k / 3 - math.pi / 2
        pts.append((cx + SIDE / math.sqrt(3) * math.cos(a), cy + SIDE / math.sqrt(3) * SQUASH * math.sin(a)))
    return pts


def fill_triangle(frame, pts, color):
    (ax, ay), (bx, by), (cx, cy) = pts

    def edge(px, py, qx, qy, rx, ry):
        return (rx - px) * (qy - py) - (ry - py) * (qx - px)

    for y in range(math.floor(min(ay, by, cy)), math.ceil(max(ay, by, cy)) + 1):
        for x in range(math.floor(min(ax, bx, cx)), math.ceil(max(ax, bx, cx)) + 1):
            px, py = x + 0.5, y + 0.5
            w0, w1, w2 = edge(bx, by, cx, cy, px, py), edge(cx, cy, ax, ay, px, py), edge(ax, ay, bx, by, px, py)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                frame.pixel(x, y, color)


def build():
    anim = Animation(delay=DELAY)
    mid_x = (anim.width - 1) / 2
    top_y = 4.0
    bottom_y = top_y + H * SQUASH
    homes = [(mid_x, top_y), (mid_x - SIDE / 2, bottom_y), (mid_x + SIDE / 2, bottom_y)]
    origins = [(mid_x, -16.0), (-20.0, 14.0), (115.0, 14.0)]

    for index in range(FRAMES):
        frame = anim.frame()
        t = min(1.0, index / ARRIVE)
        ease = 1 - (1 - t) ** 3
        for (hx, hy), (ox, oy) in zip(homes, origins):
            cx = ox + (hx - ox) * ease
            cy = oy + (hy - oy) * ease
            angle = (1 - ease) * 2 * math.pi
            pulse = ARRIVE <= index < ARRIVE + 4 and index % 2 == 0
            fill_triangle(frame, tri_points(cx, cy, angle), C.WHITE if pulse else C.YELLOW)
        if index >= SHINE_AT:
            head = 28 + (index - SHINE_AT) * 3
            for x, y in list(frame.lit()):
                if abs((x + y) - head) <= 1:
                    frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/triforce.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
