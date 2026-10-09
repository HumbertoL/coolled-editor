#!/usr/bin/env python3
"""
Vinyl record -- 33 RPM.

A black record with blue grooves and a red-and-yellow label spins at the left
while two cyan sheens sweep round it, a white marker dot on the label proving
the direction of rotation. The tonearm rides the groove with a tiny wobble,
and a bank of green-yellow-red equaliser bars bounces beside a "33 RPM"
legend. Two full revolutions per loop, seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100
CX, CY, R = 9.0, 8.0, 7.6


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        spin = 2 * math.pi * t * 2          # two turns a loop
        frame = anim.frame()
        for y in range(16):
            for x in range(20):
                dx, dy = x - CX, y - CY
                d = math.hypot(dx, dy)
                if d > R:
                    continue
                if d < 2.0:
                    frame.pixel(x, y, C.RED)
                elif d < 3.0:
                    frame.pixel(x, y, C.YELLOW)
                else:
                    ang = (math.atan2(dy, dx) - spin) % (2 * math.pi)
                    sheen = ang < 0.5 or math.pi < ang < math.pi + 0.5
                    groove = int(d * 1.5) % 2 == 0
                    frame.pixel(x, y, C.CYAN if sheen and groove else (C.BLUE if groove else C.BLACK))
        frame.pixel(round(CX + 1.5 * math.cos(spin)), round(CY + 1.5 * math.sin(spin)), C.WHITE)
        # Tonearm: pivot top right, headshell sitting in the groove, a hair of wobble.
        wob = round(math.sin(2 * math.pi * t * 4) * 0.6)
        frame.line(26, 1, 15, 6 + wob, C.WHITE)
        frame.rect(25, 0, 3, 3, C.YELLOW, fill=True)
        frame.pixel(14, 6 + wob, C.RED)
        # Equaliser bars and a note drifting up.
        for i in range(16):
            x = 34 + i * 4
            h = 2 + int(5 * (0.5 + 0.5 * math.sin(2 * math.pi * (2 * t + i / 5.0))) *
                        (0.6 + 0.4 * math.sin(2 * math.pi * (3 * t + i / 3.0 + 0.2))))
            color = C.GREEN if h < 5 else (C.YELLOW if h < 7 else C.RED)
            frame.rect(x, 12 - h, 3, h, color, fill=True)
        frame.small_text("33", 34, 13, C.CYAN)
        frame.small_text("RPM", 42, 13, C.BLUE)
        ny = 11 - (t * 11)
        frame.pixel(86, ny, C.MAGENTA)
        frame.pixel(87, ny, C.MAGENTA)
        frame.vline(87, ny - 2, 2, C.MAGENTA)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/vinyl_record.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
