#!/usr/bin/env python3
"""
Vice City sunset -- the postcard GTA 6 opens on.

A striped retro sun sits on the horizon between two palm silhouettes, its
bands sliding down into the sea. The sky runs blue to magenta to red, the
water carries a shimmering reflection, and VICE / CITY glints on either side.
48 frames so every moving part (stripes, glint, waves) loops exactly.
"""

from __future__ import annotations

import math

from gta6_art import palm, save
from jtkit import Animation, colors as C, highlight

FRAMES = 48
DELAY = 110
HORIZON = 10
SUN_X, SUN_R = 48, 9


def sky(y):
    if y <= 2:
        return C.BLUE
    if y <= 6:
        return C.MAGENTA
    return C.RED


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        for y in range(HORIZON):
            f.hline(0, y, 96, sky(y))
        # Sun: a half disc on the horizon, lower half cut by sliding bands.
        for y in range(HORIZON):
            for x in range(SUN_X - SUN_R, SUN_X + SUN_R + 1):
                if (x - SUN_X) ** 2 + ((y - HORIZON + 0.5) * 1.15) ** 2 > SUN_R ** 2:
                    continue
                if y >= 4 and (y - i // 4) % 3 == 0:
                    continue  # a band of sky through the sun, sliding down
                f.pixel(x, y, C.YELLOW)
        # Sea with a broken reflection under the sun.
        for y in range(HORIZON, 16):
            depth = y - HORIZON
            for x in range(96):
                wave = math.sin(x * 0.45 + i * 2 * math.pi / FRAMES * 3 + depth * 1.3)
                colour = C.BLUE
                if wave > 0.97 and depth > 0:
                    colour = C.CYAN
                half = SUN_R - depth - 1
                if abs(x - SUN_X) <= half:
                    shimmer = math.sin(x * 1.7 + depth * 2.1 + i * 2 * math.pi / 8)
                    if shimmer > 0.1:
                        colour = C.YELLOW if depth < 3 else C.RED
                    elif shimmer > -0.4:
                        colour = C.BLUE
                f.pixel(x, y, colour)
        f.hline(0, HORIZON, 96, C.BLUE)
        f.hline(SUN_X - SUN_R + 1, HORIZON, 2 * SUN_R - 1, C.YELLOW)

        sway = math.sin(i * 2 * math.pi / FRAMES * 2)
        palm(f, 3, 15, 11, C.BLACK, sway=sway)
        palm(f, 89, 15, 9, C.BLACK, sway=-sway)
        palm(f, 92, 15, 12, C.BLACK, sway=sway * 0.7)

        head = -10 + i * 140 / FRAMES
        f.text("VICE", 12, 1, highlight(C.WHITE, C.YELLOW, head=head, half_width=2))
        f.text("CITY", 62, 1, highlight(C.WHITE, C.YELLOW, head=head, half_width=2))
    return anim


if __name__ == "__main__":
    save(build(), "gta6_vice_sunset")
