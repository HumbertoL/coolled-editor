#!/usr/bin/env python3
"""
Dominoes -- a run of sixteen, tipping in turn.

Each domino stands two pixels wide and ten tall. When its turn comes it
rotates about its base over four frames -- white standing, yellow while it
falls, cyan once it is down -- and its tip reaches the next one's shoulder
just as that one starts to go. The fallen tiles overlap the way real ones do.
A moment of stillness at the end, then the loop stands them up again.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
COUNT = 16
PITCH = 6
HEIGHT = 10
GROUND = 14
FIRST_AT, EVERY, FALL_FRAMES = 2, 3, 4


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, GROUND + 1, anim.width, C.BLUE)
        for i in range(COUNT):
            base_x = 3 + i * PITCH
            start = FIRST_AT + i * EVERY
            progress = max(0.0, min(1.0, (index - start + 1) / FALL_FRAMES)) if index >= start else 0.0
            angle = progress * (math.pi / 2)
            if progress <= 0:
                frame.rect(base_x, GROUND - HEIGHT + 1, 2, HEIGHT, C.WHITE, fill=True)
                continue
            tip_x = base_x + HEIGHT * math.sin(angle)
            tip_y = GROUND - HEIGHT * math.cos(angle)
            color = C.CYAN if progress >= 1 else C.YELLOW
            # Second edge offset perpendicular to the tile, so it stays two
            # pixels thick lying down as well as standing up.
            ox, oy = math.cos(angle), -math.sin(angle)
            frame.line(base_x, GROUND, tip_x, tip_y, color)
            frame.line(base_x + ox, GROUND + oy, tip_x + ox, tip_y + oy, color)
            if 0 < progress < 1:
                frame.pixel(round(tip_x), round(tip_y) - 1, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dominoes.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
