#!/usr/bin/env python3
"""
Black hole -- an accretion disc seen almost edge-on, with the background
stars bent round the hole as they drift behind it.

Three things are drawn, back to front:

* Stars. Each is put through the point-mass lens equation: a source at
  angle b from the hole appears at (b +- sqrt(b^2 + 4E^2)) / 2, E being the
  Einstein radius. So every star has two images -- the main one pushed
  outward, and a second on the far side of the hole, just inside the
  Einstein ring. As a star passes close behind, both images stretch into
  arcs and swing round the shadow.
* The shadow and its ring: the black disc of the hole, wrapped in the light
  of the disc's far side, which gravity lifts into view over the top.
* The near side of the disc, crossing in front. Its streaks orbit faster
  toward the middle, and the approaching (left) side is drawn hotter than
  the receding side -- relativistic beaming, in four colours.

Every motion is a whole number of cycles per loop, so it is seamless.
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
CX, CY = 47.5, 7.5
SHADOW = 4.6          # radius of the black disc
EINSTEIN = 8.0        # Einstein radius for the star lensing
TILT = 0.085          # disc inclination: its minor/major axis ratio
DISC_IN, DISC_OUT = 7.0, 37.0
STRIP = 2 * FRAMES    # star field wraps here; stars move 2px a frame
HEAT = [C.BLACK, C.RED, C.YELLOW, C.WHITE]


def disc_heat(dx, dy, index):
    """Heat 0-3 of the disc at an offset from the hole, or None off the disc."""
    rho = math.hypot(dx, dy / TILT)
    if not DISC_IN <= rho <= DISC_OUT:
        return None
    phi = math.atan2(dy / TILT, dx)
    # Inner bands complete more orbits per loop, as a Keplerian disc would.
    orbits = 3 if rho < 13 else 2 if rho < 23 else 1
    streak = math.sin(3 * phi + rho * 0.45 + 2 * math.pi * orbits * index / FRAMES)
    heat = 2
    if dx < -5:
        heat += 1          # approaching side, beamed toward us
    if dx > 16:
        heat -= 1          # receding side
    if streak < -0.1:
        heat -= 1
    if rho > 30 and streak < 0.5:
        heat -= 1          # ragged outer edge
    return max(0, min(3, heat))


def ring_heat(dx, dy, radius, index):
    """The lensed far side of the disc, hugging the shadow."""
    outer = 6.5 if dy < 0 else 5.6
    if not SHADOW <= radius < outer:
        return None
    theta = math.atan2(dy, dx)
    glint = math.sin(2 * theta + 2 * math.pi * 2 * index / FRAMES)
    heat = 3 if dx < 0 else 2
    if glint < -0.5:
        heat -= 1
    return heat


def draw_stars(frame, index, stars):
    for sx, sy, color in stars:
        bx = (sx - 2 * index) % STRIP - 5 - CX
        by = sy - CY
        beta = math.hypot(bx, by) or 1e-6
        ux, uy = bx / beta, by / beta
        root = math.sqrt(beta * beta + 4 * EINSTEIN * EINSTEIN)
        for theta in ((beta + root) / 2, (beta - root) / 2):
            if abs(theta) < SHADOW:
                continue
            # Close alignment magnifies the image along the tangent: an arc.
            spread = 2 if beta < 2.5 else 1 if beta < 6 else 0
            for k in range(-spread, spread + 1):
                swing = k / abs(theta)
                c, s = math.cos(swing), math.sin(swing)
                x = CX + theta * (ux * c - uy * s)
                y = CY + theta * (ux * s + uy * c)
                frame.pixel(math.floor(x + 0.5), math.floor(y + 0.5), color)


def build():
    rng = random.Random(52)
    stars = []
    for i in range(26):
        # Bias the rows toward the middle so several pass right behind the hole.
        sy = rng.choice([rng.randint(0, 15), rng.randint(5, 10)])
        color = rng.choice([C.WHITE, C.WHITE, C.CYAN, C.BLUE, C.BLUE])
        stars.append((i * STRIP / 26 + rng.uniform(0, 3), sy, color))

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_stars(frame, index, stars)
        for y in range(16):
            for x in range(96):
                dx, dy = x - CX, y - CY
                radius = math.hypot(dx, dy)
                disc = disc_heat(dx, dy, index)
                if disc is not None and (dy > 0 or radius >= SHADOW):
                    frame.pixel(x, y, HEAT[disc])
                    continue
                ring = ring_heat(dx, dy, radius, index)
                if ring is not None:
                    frame.pixel(x, y, HEAT[ring])
                elif radius < SHADOW:
                    frame.pixel(x, y, C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/black_hole.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
