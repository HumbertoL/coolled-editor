#!/usr/bin/env python3
"""
Loot box -- Dungeon Crawler Carl.

A chest rattles harder and harder, the lid flies open, light pours out and
GOLD LOOT BOX! flashes beside it. Red chest with a gold clasp, rays in yellow
and white, to match the covers. The rays die down and the lid drops shut for
the loop.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

LID = [
    ".###########.",
    "#...........#",
    "#############",
]
BODY = [
    "#.....#.....#",
    "#....###....#",
    "#.....#.....#",
    "#############",
]
BOX_X, BODY_Y = 8, 9
LIFT_MAX = 3
RATTLE_END, OPEN_END, SHOW_END = 18, 24, 47


def blit(frame, rows, x, y, color, accent=None):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "#":
                inner = 0 < c < len(line) - 1 and 0 < r < len(rows) - 1
                frame.pixel(x + c, y + r, accent if (accent and inner) else color)


def build():
    anim = Animation(delay=DELAY)
    cx = BOX_X + 6
    for index in range(FRAMES):
        frame = anim.frame()

        if index < RATTLE_END:
            amp = 1 if index < 10 else 2
            shake = (index % 2 * 2 - 1) * amp if index > 3 else 0
            lift = 0
            label, label_color = "LOOT BOX", C.YELLOW if index % 4 < 2 else C.RED
        elif index < OPEN_END:
            shake = 0
            lift = min(LIFT_MAX, index - RATTLE_END + 1)
            label, label_color = "LOOT BOX", C.WHITE
        elif index < SHOW_END:
            shake = 0
            lift = LIFT_MAX
            label, label_color = "GOLD BOX!", C.WHITE if index % 6 < 2 else C.YELLOW
        else:
            shake = 0
            lift = max(0, LIFT_MAX - (index - SHOW_END + 1))
            label, label_color = "GOLD BOX!", C.RED

        # Rays fanning out of the gap under the lid, brighter the wider it is.
        if lift > 0:
            seam_y = BODY_Y - 1 - lift // 2
            flicker = index % 2
            for k, (dx, dy) in enumerate(((-3, -1), (-2, -1), (-1, -2), (0, -1), (1, -2), (2, -1), (3, -1))):
                length = lift + 2 + ((k + flicker) % 2)
                for step in range(1, length + 1):
                    x = cx + dx * step
                    y = seam_y + dy * step
                    frame.pixel(x, y, C.WHITE if step <= 1 else C.YELLOW)
                    if abs(dx) >= 2:
                        frame.pixel(x + (1 if dx > 0 else -1), y, C.YELLOW)
        blit(frame, BODY, BOX_X + shake, BODY_Y, C.RED, accent=C.YELLOW)
        blit(frame, LID, BOX_X + shake, BODY_Y - len(LID) - lift, C.RED)
        frame.text(label, 28, 4, label_color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_loot_box.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
