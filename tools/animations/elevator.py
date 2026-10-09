#!/usr/bin/env python3
"""
Elevator -- doors, floors, DING.

A lobby scene in the lift: the car's doors rest open on L1 with a rider inside,
slide shut, the red floor numeral counts up 1 to 5 under a blinking up arrow,
then DING and the doors part again and the rider steps forward. The doors are two
sliding panels in a white frame with a lit yellow interior.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
DX = 52                      # left edge of the car interior
W = 34                       # door opening width


def person(frame, x, y, color):
    frame.rect(x, y, 2, 2, C.YELLOW, fill=True)           # head
    frame.rect(x, y + 2, 2, 5, color, fill=True)          # body


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Schedule: 0-8 doors open at L1, 9-13 close, 14-35 rise 1->5, 36-40 open, 41-52 step out.
        if index < 9:
            floor, opening, arrow = 1, 1.0, None
        elif index < 14:
            floor, opening, arrow = 1, 1.0 - (index - 8) / 5, None
        elif index < 36:
            floor = 1 + min(4, int((index - 14) / 5.5))
            opening, arrow = 0.0, "U"
        elif index < 41:
            floor, opening, arrow = 5, (index - 35) / 5, None
        else:
            floor, opening, arrow = 5, 1.0, None
        # Floor display: big digit in a bezel, arrow beside it.
        frame.rect(6, 1, 15, 14, C.BLUE)
        frame.text(str(floor), 11, 4, C.RED)
        if arrow:
            lit = (index // 2) % 2 == 0
            frame.pixel(26, 4, C.RED if lit else C.BLUE)
            frame.hline(25, 5, 3, C.RED if lit else C.BLUE)
            frame.hline(24, 6, 5, C.RED if lit else C.BLUE)
            frame.vline(26, 7, 5, C.RED if lit else C.BLUE)
        if 36 <= index < 39:
            frame.text("DING", 26, 4, C.YELLOW)
        # Door frame, lit interior, two sliding doors.
        frame.rect(DX - 2, 0, W + 4, 16, C.WHITE)
        shown = int(round(opening * (W // 2)))
        if shown:
            frame.rect(DX, 1, W, 15, C.YELLOW, fill=True)
            frame.rect(DX, 14, W, 2, C.MAGENTA, fill=True)             # carpet
            if index < 14:
                person(frame, DX + 20, 7, C.CYAN)                        # rider waits inside
            elif index >= 36:
                walk = min(1.0, (index - 41) / 11) if index >= 41 else 0
                person(frame, DX + 20 + int(walk * 18), 7, C.CYAN)
        for side in (0, 1):
            width = W // 2 - shown
            if width > 0:
                x = DX + (0 if side == 0 else W - width)
                frame.rect(x, 1, width, 15, C.CYAN if side == 0 else C.BLUE, fill=True)
                frame.vline(x if side else x + width - 1, 1, 15, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/elevator.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
