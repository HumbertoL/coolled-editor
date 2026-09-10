#!/usr/bin/env python3
"""
Eclipse -- a total solar eclipse, first contact to last.

The moon crosses the sun over the loop. As coverage grows the sky darkens and
stars come out; at totality the disc goes black inside a white-and-cyan
corona, and the instants either side of totality get the diamond-ring flash --
one brilliant point on the rim where the last sliver of photosphere shows.

The moon starts and ends fully clear of the sun, so the wrap point is just
"plain sun" both sides and the loop reads clean.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

SUN = (48, 8)
SUN_R = 5.6
MOON_R = 6.0

STARS = [
    (6, 3), (14, 11), (22, 2), (30, 13), (68, 12),
    (74, 2), (82, 9), (90, 4), (10, 7), (88, 13),
]


def build():
    anim = Animation(delay=DELAY)
    sx, sy = SUN

    for index in range(FRAMES):
        t = index / (FRAMES - 1)
        frame = anim.frame()

        # Moon travels well past the sun on both sides.
        mx = 18 + t * 60
        my = sy
        coverage = max(0.0, 1.0 - abs(mx - sx) / (SUN_R + MOON_R))

        # Stars come out as the sky darkens.
        if coverage > 0.55:
            for i, (x, y) in enumerate(STARS):
                if coverage > 0.55 + 0.04 * i:
                    twinkle = (index + i * 3) % 8 < 6
                    frame.pixel(x, y, C.WHITE if twinkle else C.BLUE)

        # Corona: radial glow just outside the disc, only near totality.
        if coverage > 0.8:
            reach = (coverage - 0.8) / 0.2
            for i in range(24):
                a = 2 * math.pi * i / 24
                length = 1.5 + reach * (2.5 if i % 3 == 0 else 1.2)
                for rr in (SUN_R + 1, SUN_R + length):
                    px = round(sx + rr * math.cos(a))
                    py = round(sy + rr * math.sin(a) * 0.9)
                    color = C.WHITE if rr <= SUN_R + 1.5 else C.CYAN
                    frame.pixel(px, py, color)

        # The sun, minus wherever the moon sits.
        for y in range(16):
            for x in range(32, 65):
                d_sun = math.hypot(x - sx, y - sy)
                if d_sun > SUN_R:
                    continue
                if math.hypot(x - mx, y - my) <= MOON_R:
                    continue
                frame.pixel(x, y, C.WHITE if d_sun < 2.5 else C.YELLOW)

        # Diamond ring: a flare on the rim just before and after totality.
        if 0.86 < coverage < 0.97:
            side = -1 if mx < sx else 1
            px = round(sx + side * SUN_R)
            frame.pixel(px, sy, C.WHITE)
            frame.pixel(px + side, sy, C.WHITE)
            frame.pixel(px, sy - 1, C.WHITE)
            frame.pixel(px, sy + 1, C.WHITE)
            frame.pixel(px + 2 * side, sy, C.CYAN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/eclipse.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
