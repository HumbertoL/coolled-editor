#!/usr/bin/env python3
"""
Collatz -- 27, the famous one.

Halve it if even, triple-and-add-one if odd, repeat. Every number anyone has
ever tried reaches 1; nobody can prove they all do. 27 takes 111 steps and
climbs to 9,232 on the way, so its path is drawn on a log scale, revealed two
or three steps a frame with the current value in the corner. It lands on 1
with a frame to spare, and the step count flashes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
START = 27
REVEAL_FRAMES = 48


def sequence(n):
    out = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        out.append(n)
    return out


def build():
    seq = sequence(START)
    steps = len(seq) - 1
    top = math.log(max(seq))
    anim = Animation(delay=DELAY)

    def point(i):
        return round(i * 95 / steps), round(14 - math.log(seq[i]) / top * 13)

    for index in range(FRAMES):
        frame = anim.frame()
        shown = min(steps, round(steps * (index + 1) / REVEAL_FRAMES))
        done = shown >= steps
        prev = None
        for i in range(shown + 1):
            p = point(i)
            if prev is not None:
                frame.line(prev[0], prev[1], p[0], p[1], C.CYAN)
            prev = p
        px, py = point(shown)
        frame.pixel(px, py, C.WHITE)
        frame.pixel(px, py - 1, C.WHITE)
        if done:
            frame.text(f"{steps} STEPS", 40, 0, C.YELLOW if index % 2 else C.WHITE, proportional=True)
            frame.text("1", 2, 0, C.GREEN, proportional=True)
        else:
            frame.text(f"{seq[shown]:,}", 2, 0, C.WHITE, proportional=True)
            frame.text(f"N={START}", 66, 0, C.BLUE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/collatz.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
