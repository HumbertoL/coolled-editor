#!/usr/bin/env python3
"""
Windmill -- a Dutch windmill on a breezy afternoon.

A red tapering tower with a white cap, four sails turning on the hub, tulips
nodding in a travelling gust and clouds drifting across a blue sky. The sails
are four-fold symmetric, so one loop is a quarter turn and the clouds go
exactly one panel width -- both close perfectly.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52
DELAY = 130
HUB = (47, 7)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        frame.rect(0, 0, 96, 12, C.BLUE, fill=True)
        # Clouds drift exactly one panel width, so the loop closes.
        for cx, cy in ((10, 2), (46, 1), (74, 3)):
            x = (cx + 96 * t) % 96
            for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, -1), (2, -1), (3, 1), (1, 1), (2, 1)):
                frame.pixel((x + dx) % 96, cy + dy, C.CYAN if dy else C.WHITE)
        # Green hill and verge.
        for x in range(96):
            top = 12 - int(1.6 * math.sin(x / 9.0) + 1.2)
            frame.vline(x, top, 16 - top, C.GREEN)
        # Tulips alternate colour and nod in a breeze.
        for i, x in enumerate(range(4, 96, 8)):
            if abs(x - 47) < 9:
                continue
            sway = 1 if math.sin(2 * math.pi * (t - i / 12)) > 0.5 else 0
            frame.pixel(x + sway, 13, (C.RED, C.YELLOW, C.MAGENTA)[i % 3])
        # Tower: a tapering red-brick body with a white door, cap above.
        for y in range(7, 15):
            half = 2 + (y - 7) // 3
            frame.hline(HUB[0] - half, y, 2 * half + 1, C.RED)
        frame.rect(HUB[0] - 1, 12, 3, 3, C.YELLOW, fill=True)
        frame.hline(HUB[0] - 2, 6, 5, C.WHITE)
        # Four sails; the picture repeats every quarter turn.
        angle = t * math.pi / 2
        for k in range(4):
            a = angle + k * math.pi / 2
            ex, ey = HUB[0] + 7 * math.cos(a), HUB[1] + 7 * math.sin(a)
            frame.line(HUB[0], HUB[1], round(ex), round(ey), C.YELLOW)
            # Cloth on the trailing side of the outer half of each sail.
            bx, by = HUB[0] + 3 * math.cos(a), HUB[1] + 3 * math.sin(a)
            nx, ny = -math.sin(a), math.cos(a)
            frame.line(round(bx + nx), round(by + ny), round(ex + nx), round(ey + ny), C.WHITE)
        frame.pixel(*HUB, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/windmill.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
