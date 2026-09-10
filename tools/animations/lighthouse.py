#!/usr/bin/env python3
"""
Lighthouse -- a beam sweeping the night.

A banded tower on rocks at the left, its lamp throwing a wedge of light that
sweeps a full circle each loop. Stars hold the sky except where the beam
washes over them, and the sea keeps rolling underneath.

Seamless: the beam turns exactly once and the waves advance a whole cycle.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100

LAMP = (10, 2)

STARS = [
    (26, 1), (34, 5), (44, 2), (52, 7), (60, 1),
    (68, 4), (78, 2), (86, 6), (92, 1), (38, 9),
    (72, 9), (90, 10),
]


def ang_diff(a, b):
    d = (a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def build():
    anim = Animation(delay=DELAY)
    lx, ly = LAMP

    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        beam = 2 * math.pi * t

        # The beam wedge, over the sky only.
        for y in range(12):
            for x in range(96):
                dx, dy = x - lx, y - ly
                if dx == 0 and dy == 0:
                    continue
                if math.hypot(dx, dy) < 2:
                    continue
                d = ang_diff(math.atan2(dy, dx), beam)
                if d < 0.07:
                    frame.pixel(x, y, C.WHITE)
                elif d < 0.16:
                    frame.pixel(x, y, C.YELLOW)

        # Stars, only where the beam is not.
        for i, (x, y) in enumerate(STARS):
            if frame.get(x, y) == C.BLACK:
                twinkle = (index + i * 5) % 12 < 9
                frame.pixel(x, y, C.WHITE if twinkle else C.BLUE)

        # Sea: three rows of rolling swell.
        for y in (13, 14, 15):
            for x in range(96):
                phase = math.sin(0.25 * x + 2 * math.pi * t * (y - 11) + y * 1.8)
                if phase > 0.15:
                    frame.pixel(x, y, C.CYAN if phase > 0.85 else C.BLUE)

        # Rocks and tower, drawn last so the beam never cuts through them.
        frame.rect(6, 12, 10, 3, C.BLUE, fill=True)
        frame.pixel(5, 13, C.BLUE)
        frame.pixel(16, 13, C.BLUE)
        for row in range(4, 12):
            color = C.RED if (row // 2) % 2 else C.WHITE
            width = 3 if row < 8 else 5
            frame.hline(lx - width // 2, row, width, color)
        # Lamp room, flashing with the sweep as it faces us.
        facing = ang_diff(beam, math.pi / 2) > 2.4
        frame.rect(lx - 1, 1, 3, 3, C.YELLOW if facing else C.RED, fill=True)
        frame.pixel(lx, 0, C.RED)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lighthouse.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
