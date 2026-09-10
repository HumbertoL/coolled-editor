#!/usr/bin/env python3
"""
Pendulum wave -- ten pendulums, each one swing per loop faster than the last.

Seen end-on, so every bob moves up and down its own column. Because their
frequencies are consecutive whole numbers of cycles per loop, they start in a
line, drift into a travelling wave, break up into apparent chaos, gather into
two alternating groups, and fall back into line exactly as the loop closes.
The physical demonstration takes a minute; this one takes five seconds.

Each bob leaves a one-frame blue ghost so the motion reads at 100ms.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
BOBS = 10
BASE_CYCLES = 2
AMPLITUDE = 6.0
COLORS = [C.WHITE, C.CYAN, C.YELLOW, C.MAGENTA, C.GREEN]


def bob_y(k, index):
    cycles = BASE_CYCLES + k
    return 7.5 + AMPLITUDE * math.sin(2 * math.pi * cycles * index / FRAMES)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, 0, anim.width, C.BLUE)
        for k in range(BOBS):
            x = round(5 + k * 9.5)
            y_prev = round(bob_y(k, index - 1))
            y = round(bob_y(k, index))
            frame.rect(x, y_prev, 2, 2, C.BLUE, fill=True)
            frame.rect(x, y, 2, 2, COLORS[k % len(COLORS)], fill=True)
            frame.pixel(x, 1, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pendulum_wave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
