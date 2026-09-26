#!/usr/bin/env python3
"""
Tusi couple -- dots that only ever move in straight lines, drawing a circle.

Three versions side by side. Each dot slides back and forth along its own
line through the centre in simple harmonic motion, phase-shifted by the line's
angle. Together they trace a circle half the size, rolling round inside the
outer one -- although no dot ever leaves its line. On the left, four lines
drawn in blue; in the middle, eight; on the right the same eight dots with the
lines hidden and only the outer rim drawn, where they just look like a wheel.

Two full turns in 53 frames, so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70
TURNS = 2
RADIUS = 7.4
# (cx, cy, lines, draw the lines?)
CENTRES = [(15.5, 7.5, 4, True), (47.5, 7.5, 8, True), (79.5, 7.5, 8, False)]
DOT_COLORS = [C.YELLOW, C.RED, C.MAGENTA, C.WHITE, C.GREEN, C.CYAN]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        t = 2 * math.pi * TURNS * index / FRAMES
        for cx, cy, lines, show_lines in CENTRES:
            if not show_lines:
                for step in range(64):
                    a = 2 * math.pi * step / 64
                    frame.pixel(round(cx + 7.5 * math.cos(a)), round(cy + 7.5 * math.sin(a)), C.BLUE)
            for k in range(lines if show_lines else 0):
                theta = math.pi * k / lines
                dx, dy = math.cos(theta), math.sin(theta)
                frame.line(
                    round(cx - RADIUS * dx), round(cy - RADIUS * dy),
                    round(cx + RADIUS * dx), round(cy + RADIUS * dy),
                    C.BLUE,
                )
            for k in range(lines):
                theta = math.pi * k / lines
                s = RADIUS * math.cos(t - theta)
                x = cx + s * math.cos(theta)
                y = cy + s * math.sin(theta)
                color = DOT_COLORS[k % len(DOT_COLORS)] if lines > 4 else C.WHITE
                frame.pixel(round(x), round(y), color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tusi_couple.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
