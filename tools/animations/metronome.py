#!/usr/bin/env python3
"""
Metronome -- a pyramid ticking at 60 BPM.

A red pyramid with a white rod swinging 0.55 rad either side of vertical and a
yellow weight riding it. The TICK and TOCK lamps light green at the two
extremes of the swing, and the tempo reads off beside them. One loop is a full
there-and-back, so exactly two ticks, and the sine drive closes seamlessly.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52           # one full swing there and back = two ticks
DELAY = 100
PIVOT = (20, 14)
ARM = 12.0
SWING = 0.55          # radians either side of vertical


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        phase = index / FRAMES
        angle = SWING * math.sin(2 * math.pi * phase)
        frame = anim.frame()
        # Wooden pyramid body, drawn as a trapezoid.
        for y in range(1, 16):
            half = 2 + (y * 6) // 15
            frame.hline(PIVOT[0] - half, y, 2 * half + 1, C.RED if y > 1 else C.YELLOW)
        frame.rect(PIVOT[0] - 1, 5, 3, 8, C.BLACK, fill=True)   # slot the rod rides in
        # Rod and sliding weight.
        tip = (PIVOT[0] + ARM * math.sin(angle), PIVOT[1] - ARM * math.cos(angle) - 1)
        frame.line(PIVOT[0], PIVOT[1], round(tip[0]), round(tip[1]), C.WHITE)
        wx = PIVOT[0] + 7.5 * math.sin(angle)
        wy = PIVOT[1] - 7.5 * math.cos(angle)
        frame.rect(round(wx) - 1, round(wy) - 1, 3, 3, C.YELLOW, fill=True)
        # Tick lamps: lit while the arm is within a hair of an extreme.
        left = angle < -SWING * 0.93
        right = angle > SWING * 0.93
        frame.rect(36, 3, 6, 6, C.GREEN if left else C.BLUE, fill=True)
        frame.rect(48, 3, 6, 6, C.GREEN if right else C.BLUE, fill=True)
        frame.text("60", 62, 1, C.CYAN)
        frame.small_text("BPM", 76, 3, C.CYAN)
        frame.small_text("ANDANTE", 62, 10, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/metronome.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
