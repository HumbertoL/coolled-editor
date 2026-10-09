#!/usr/bin/env python3
"""
Jellyfish -- two drifting jellies pulsing over a field of rising bubbles.

Each bell is the top half of an ellipse that squashes and stretches on the
loop's period, with a MAGENTA rim and a BLUE body. Four tentacles per bell
wave as travelling sines, and the bubbles climb one full panel per loop by
moving 16 rows over 53 frames. Every motion is periodic in the loop, so the
animation has no seam.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
# (cx, cy, rx, ry, phase)
JELLIES = [(28, 5, 9.0, 5.0, 0.0), (68, 7, 6.0, 4.0, 2.2)]
BUBBLES = [(6, 0), (14, 7), (40, 3), (52, 11), (84, 5), (92, 13)]


def draw_bubbles(frame, index):
    for x, y0 in BUBBLES:
        y = (y0 - round(16 * index / FRAMES)) % 16
        frame.pixel(x, y, C.WHITE)


def draw_jelly(frame, index, cx, cy, rx, ry, phase):
    theta = 2 * math.pi * index / FRAMES
    pulse = math.sin(2 * theta + phase)
    rx_now = rx * (1 - 0.08 * pulse)
    ry_now = ry * (1 + 0.12 * pulse)
    cx_now = cx + 1.5 * math.sin(theta + phase)
    cy_now = cy + round(1.0 * math.sin(theta + phase))
    for y in range(round(cy_now - ry_now), round(cy_now) + 1):
        for x in range(round(cx_now - rx_now), round(cx_now + rx_now) + 1):
            dx = (x - cx_now) / rx_now
            dy = (y - cy_now) / ry_now
            value = dx * dx + dy * dy
            if value <= 1.0:
                frame.pixel(x, y, C.MAGENTA if value > 0.55 else C.BLUE)
    for k, offset in enumerate((-0.7, -0.25, 0.25, 0.7)):
        base_x = cx_now + offset * rx_now
        bottom = round(cy_now) + 1
        for segment in range(1, 6):
            wave = 1.6 * math.sin(2 * theta + segment * 0.9 + k + phase)
            frame.pixel(round(base_x + wave), bottom + segment, C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_bubbles(frame, index)
        for jelly in JELLIES:
            draw_jelly(frame, index, *jelly)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/jellyfish.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
