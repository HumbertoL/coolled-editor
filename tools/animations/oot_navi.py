#!/usr/bin/env python3
"""
OoT navi -- hey! listen!

In a dark forest, a fairy -- a white core in a pulsing cyan and blue glow,
with flickering wings -- swoops in from the left on a looping path, leaving a
trail of fading sparkles. She stops by the left edge, flashes yellow, and the
panel says HEY! then LISTEN!, twice, before she zips off up and away to the
right.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
ARRIVE = 22
LEAVE = 45
PERCH = (14.0, 7.0)
TRAIL = 5
WORDS = [(24, "HEY!"), (30, "LISTEN!"), (37, "HEY!"), (41, "LISTEN!")]
TREES = [(3, 9), (34, 11), (60, 10), (86, 12)]


def path(index):
    """The fairy's centre at frame ``index`` (fractional frames allowed)."""
    if index < ARRIVE:
        t = index / ARRIVE
        x = -6 + 140 * math.sin(t * math.pi * 0.85) * (1 - t) + PERCH[0] * t
        y = 7.5 + 5 * math.sin(t * math.pi * 4)
        return x, y
    if index < LEAVE:
        return PERCH[0], PERCH[1] + math.sin(index * 0.9) * 1.2
    t = (index - LEAVE) / (FRAMES - LEAVE)
    return PERCH[0] + 95 * t * t, PERCH[1] - 9 * t + 2 * math.sin(t * 9)


def forest(frame):
    for tx, h in TREES:
        for k in range(h):
            half = k // 2
            y = 15 - h + k
            if y > 13:
                break
            frame.hline(tx - half, y, 2 * half + 1, C.GREEN if (k + tx) % 3 else C.BLUE)
        frame.vline(tx, 14, 2, C.RED)
    for x in range(0, 96, 3):
        frame.pixel(x + (x // 3) % 2, 15, C.GREEN)


def fairy(frame, x, y, index, alert):
    x, y = round(x), round(y)
    ring = C.YELLOW if alert and index % 2 else C.CYAN
    halo = C.BLUE
    pulse = index % 3
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            d = math.hypot(dx, dy)
            if 2.6 + pulse * 0.3 <= d < 3.4 + pulse * 0.3 and (dx + dy + index) % 2 == 0:
                frame.pixel(x + dx, y + dy, halo)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        frame.pixel(x + dx, y + dy, ring)
    frame.pixel(x, y, C.WHITE)
    up = index % 2
    for side in (-1, 1):
        frame.pixel(x + side * 2, y - 2 - up, C.WHITE)
        frame.pixel(x + side * 3, y - 1 - up, C.WHITE if up else C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        forest(frame)
        for back in range(TRAIL, 0, -1):
            if index - back * 0.6 < 0:
                continue
            tx, ty = path(index - back * 0.6)
            frame.pixel(round(tx), round(ty), C.CYAN if back < 3 else C.BLUE)

        talking = ARRIVE + 2 <= index < LEAVE
        word = None
        for start, text in WORDS:
            if index >= start:
                word = text
        if talking and word:
            colour = C.YELLOW if word == "HEY!" else (C.WHITE if index % 2 else C.CYAN)
            for gx in range(26, 28 + frame.text_width(word) + 2):
                for gy in range(3, 12):
                    frame.pixel(gx, gy, C.BLACK)
            frame.text(word, 28, 4, colour)
            # Little shout marks off the fairy.
            if index % 2 == 0:
                frame.pixel(20, 3, C.WHITE)
                frame.pixel(21, 2, C.WHITE)
                frame.pixel(20, 12, C.WHITE)
                frame.pixel(21, 13, C.WHITE)

        x, y = path(index)
        fairy(frame, x, y, index, alert=talking)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/oot_navi.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
