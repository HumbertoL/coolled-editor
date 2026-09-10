#!/usr/bin/env python3
"""
Galaxy -- a barred spiral rotating in the void.

Stars are seeded onto two logarithmic spiral arms plus a scattered halo, then
the whole disc is rotated a full turn over the loop. Colour stands in for
distance from the core: the nucleus burns white/yellow, the mid-disc reads cyan
and the faint outer arms blue. The disc is squashed vertically so a round
galaxy fits a 96x16 panel as an inclined ellipse.

Seamless: the rotation advances by exactly 2*pi/FRAMES per frame, and every
star is a function of that single angle, so the last frame rolls into the first.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

CX, CY = 48.0, 8.0
ASPECT = 0.34          # vertical squash: an inclined disc, not a face-on one
ARMS = 2
TWIST = 2.6           # how tightly the arms wind
MAX_R = 46.0


def seed_stars():
    """(radius, base_angle, arm_jitter) for each star, densest near the core."""
    rng = random.Random(7)
    stars = []
    for _ in range(150):
        # r^2 distribution crowds stars toward the centre.
        r = MAX_R * math.sqrt(rng.random())
        arm = rng.randrange(ARMS)
        base = arm * (2 * math.pi / ARMS) + r / MAX_R * TWIST * 2 * math.pi
        jitter = rng.gauss(0.0, 0.18 + 0.25 * (r / MAX_R))
        stars.append((r, base + jitter, rng.random()))
    return stars


def star_color(r):
    if r < 6:
        return C.WHITE
    if r < 12:
        return C.YELLOW
    if r < 24:
        return C.CYAN
    return C.BLUE


def build():
    anim = Animation(delay=DELAY)
    stars = seed_stars()

    for index in range(FRAMES):
        rot = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        # Bright core glow.
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                if dx * dx + (dy / ASPECT) ** 2 <= 6:
                    frame.pixel(CX + dx, CY + dy, C.WHITE)

        for r, base, _ in stars:
            angle = base + rot
            x = CX + r * math.cos(angle)
            y = CY + r * math.sin(angle) * ASPECT
            frame.pixel(x, y, star_color(r))

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/galaxy.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
