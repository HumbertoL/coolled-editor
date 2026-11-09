#!/usr/bin/env python3
"""
Moon phases -- six moons, each a sixth of a lunation ahead of the last.

Every disc is 15 pixels across. The lit part is bounded by the terminator, a
half-ellipse whose width is the cosine of the phase angle, so crescents and
gibbous shapes come out of the geometry rather than being drawn. The unlit
limb shows as a blue rim of earthshine, and a few fixed maria are picked out
in yellow where the light reaches them. One lunation is 48 frames, so the
light sweeps along the row and the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 110
MOONS = 6
RADIUS = 7.5
MARIA = {(-3, -3), (-2, -3), (-3, -2), (-2, -2), (2, -1), (3, -1), (2, 0), (-1, 3), (0, 3), (0, 4)}


def draw_moon(frame, left, top, phase):
    swing = math.cos(2 * math.pi * phase)
    for row in range(15):
        dy = row - 7
        reach_sq = RADIUS * RADIUS - dy * dy
        if reach_sq <= 0:
            continue
        reach = math.sqrt(reach_sq)
        for col in range(15):
            dx = col - 7
            if abs(dx) > reach:
                continue
            if phase < 0.5:
                lit = dx > reach * swing
            else:
                lit = dx < -reach * swing
            if lit:
                colour = C.YELLOW if (dx, dy) in MARIA else C.WHITE
            else:
                # Rim only: a pixel whose neighbour falls outside the disc.
                rim = (abs(dx) + 1) ** 2 + dy * dy > RADIUS**2 or dx * dx + (abs(dy) + 1) ** 2 > RADIUS**2
                colour = C.BLUE if rim else C.BLACK
            frame.pixel(left + col, top + row, colour)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for moon in range(MOONS):
            phase = (index / FRAMES + moon / MOONS) % 1.0
            draw_moon(frame, 16 * moon, 0, phase)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/moon_phases.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
