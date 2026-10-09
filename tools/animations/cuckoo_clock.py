#!/usr/bin/env python3
"""
Cuckoo clock -- the hour strikes three.

A red-roofed chalet clock with a yellow case, a pendulum swinging below it
and chain weights beside. Three times the little door opens and a cyan bird
lunges out, beak first, while CUCK and OO flash on opposite sides of the
panel, alternating each strike.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
CX = 47
STRIKES = (13, 23, 33)       # frames at which the bird is fully out


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Chalet roof: a red pitched triangle, apex at the top.
        for y in range(5):
            half = 1 + 2 * y
            frame.hline(CX - half, y, 2 * half + 1, C.RED)
        # Body, with the door and the clock face below it.
        frame.rect(CX - 7, 5, 15, 6, C.YELLOW)
        frame.rect(CX - 3, 6, 7, 5, C.BLACK, fill=True)
        # Bird: out when near a strike.
        out = max(((1 - abs(index - s) / 3) for s in STRIKES), default=0)
        out = max(0.0, out)
        if out > 0.05:
            frame.rect(CX - 3, 6, 7, 5, C.BLUE, fill=True)
            reach = round(out * 3)
            frame.rect(CX - 1, 7, 3 + reach, 3, C.CYAN, fill=True)
            frame.pixel(CX + 1 + reach, 8, C.YELLOW)                    # beak
            frame.pixel(CX + 2 + reach, 8, C.YELLOW)
            frame.pixel(CX + reach, 7, C.BLACK)                         # eye
        # Clock face + pendulum below.
        swing = math.sin(2 * math.pi * index / 13.25)
        frame.pixel(CX, 11, C.WHITE)
        bx = CX + swing * 4
        frame.line(CX, 11, round(bx), 14, C.WHITE)
        frame.rect(round(bx) - 1, 13, 3, 3, C.YELLOW, fill=True)
        # CUCK / OO text alternating sides.
        for k, s in enumerate(STRIKES):
            if abs(index - s) <= 1:
                if k % 2 == 0:
                    frame.text("CUCK", 8, 4, C.YELLOW)
                    frame.text("OO", 76, 4, C.CYAN)
                else:
                    frame.text("OO", 18, 4, C.CYAN)
                    frame.text("CUCK", 66, 4, C.YELLOW)
        # Weights hang either side of the case.
        for wx, drop in ((CX - 16, 0), (CX + 16, 2)):
            frame.vline(wx, 5, 5 + drop + (index // 10), C.BLUE)
            frame.rect(wx - 1, 10 + drop + (index // 10), 3, 3, C.GREEN, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cuckoo_clock.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
