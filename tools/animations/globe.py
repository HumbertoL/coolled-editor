#!/usr/bin/env python3
"""
Globe -- a wireframe planet turning, with a moon.

A latitude/longitude grid on a sphere, spun about its axis. Only the near
hemisphere is drawn, coloured by depth so the front rim reads white, curving
back through cyan to a dim blue near the limb -- the illusion of roundness on a
flat grid. A small moon swings around it on an inclined ellipse, passing in
front and behind, and a scatter of fixed stars fills the wide margins.

Seamless: the globe turns exactly once and the moon completes two orbits.
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
W, H = 96, 16
CX, CY = 48.0, 8.0
RG = 7.0                 # globe radius (fits the height)
MOON_ORBITS = 2


def depth_color(z):
    if z > 0.80 * RG:
        return C.WHITE
    if z > 0.35 * RG:
        return C.CYAN
    return C.BLUE


def build():
    anim = Animation(delay=DELAY)

    rng = random.Random(3)
    stars = [(rng.randrange(W), rng.randrange(H)) for _ in range(24)]

    # A sparse grid so the lines stay distinct instead of filling the disc:
    # meridians every 45 deg, a handful of parallels.
    lats = [math.radians(d) for d in (-60, -30, 0, 30, 60)]
    lons = [math.radians(d) for d in range(0, 360, 45)]

    for index in range(FRAMES):
        rot = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        # Background stars (skip any under the globe's disc).
        for sx, sy in stars:
            if math.hypot((sx - CX), (sy - CY) * (RG / 3)) > RG + 4:
                frame.pixel(sx, sy, C.BLUE)

        def plot(lat, lon):
            x = RG * math.cos(lat) * math.sin(lon + rot)
            y = RG * math.sin(lat)
            z = RG * math.cos(lat) * math.cos(lon + rot)
            if z < 0:
                return
            sx = CX + x
            sy = CY - y * (RG / 7.5)     # slight vertical squeeze to fit 16px
            frame.pixel(sx, sy, depth_color(z))

        # Meridians.
        for lon in lons:
            la = -math.pi / 2
            while la <= math.pi / 2:
                plot(la, lon)
                la += 0.16
        # Parallels.
        for lat in lats:
            lo = 0.0
            while lo < 2 * math.pi:
                plot(lat, lo)
                lo += 0.16

        # Moon on an inclined ellipse.
        ma = 2 * math.pi * MOON_ORBITS * index / FRAMES
        mx = CX + 40 * math.cos(ma)
        my = CY + 5 * math.sin(ma)
        frame.pixel(mx, my, C.WHITE)
        frame.pixel(mx + 1, my, C.CYAN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/globe.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
