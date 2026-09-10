#!/usr/bin/env python3
"""
Cassette -- a tape deck playing, reels turning.

A compact cassette drawn to fill the panel: the shell outline, a label strip,
the two spool windows with hubs whose spokes rotate, and the span of tape
between them. The left spool empties as the right fills over the loop, the tape
level shifting with it, and a small triangular PLAY marker sits in the corner.

Seamless: the hubs turn a whole number of times and the tape swap returns to
its start.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
W, H = 96, 16

LX, RX, HY = 30, 66, 8      # spool centres and their y


def hub(frame, cx, cy, radius, angle, color):
    for t in range(6):
        a = angle + 2 * math.pi * t / 6
        for rr in range(radius + 1):
            frame.pixel(cx + rr * math.cos(a), cy + rr * math.sin(a), color)
    frame.pixel(cx, cy, C.WHITE)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()

        # Shell.
        frame.rect(4, 1, 88, 14, C.CYAN)
        # Label strip along the top.
        frame.hline(8, 3, 80, C.BLUE)

        # Tape spans between the spools, its bulk shifting left->right.
        left_radius = 5 - int(round(3 * t))
        right_radius = 2 + int(round(3 * t))
        frame.hline(LX, HY - 6, RX - LX, C.WHITE)   # tape path along the top

        angle = 2 * math.pi * 2 * t                 # two turns over the loop
        hub(frame, LX, HY, left_radius, angle, C.YELLOW)
        hub(frame, RX, HY, right_radius, -angle, C.YELLOW)

        # PLAY marker: a clean right-pointing triangle, bottom-left of shell.
        for col in range(3):
            half = 2 - col
            for dy in range(-half, half + 1):
                frame.pixel(7 + col, 11 + dy, C.GREEN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cassette.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
