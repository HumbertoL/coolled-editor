#!/usr/bin/env python3
"""
Sunrise -- a full day/night cycle in one seamless loop.

The sun tracks an arc from horizon to horizon; when it dips below the
waterline the moon rises in its place on the far side. The sky is painted by
elevation: near the horizon it flushes red/yellow at low sun angles and stays
black at night. The sea is blue with a moving shimmer band that reflects the
sun's colour.

Seamless: everything is a function of theta = 2*pi * i / FRAMES, so the last
frame flows straight into the first.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

HORIZON = 10        # sea starts at row 10
ARC_APEX = 1        # highest row the sun reaches (small y = high on screen)
ARC_R_X = 46        # horizontal radius of the arc
ARC_R_Y = HORIZON - ARC_APEX


def sky_color(y, sun_h, is_night):
    """Colour a sky pixel by row and sun elevation (0..1)."""
    if is_night:
        # Deep blue near horizon fading to black overhead.
        if y >= HORIZON - 2:
            return C.BLUE
        return C.BLACK
    # Day: warmth concentrates at the horizon, thinning as the sun climbs.
    horizon_dist = (HORIZON - 1) - y   # 0 at horizon, positive upward
    warmth = max(0.0, 1.0 - horizon_dist / (HORIZON + 3.0)) * (1.0 - sun_h)
    if warmth > 0.65:
        return C.RED
    if warmth > 0.35:
        return C.YELLOW
    if sun_h > 0.35:
        return C.CYAN
    return C.BLUE


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        theta = 2 * math.pi * index / FRAMES
        # Sun rises in the east (x=0 side) and sets in the west. sin() is
        # elevation; cos() is its horizontal position.
        sun_elev = math.sin(theta)
        sun_x = 48 - ARC_R_X * math.cos(theta)
        sun_y = HORIZON - 1 - ARC_R_Y * max(0.0, sun_elev)
        # Moon rides the opposite arc.
        moon_elev = -sun_elev
        moon_x = 48 + ARC_R_X * math.cos(theta)
        moon_y = HORIZON - 1 - ARC_R_Y * max(0.0, moon_elev)

        is_night = sun_elev <= 0
        sun_h = max(0.0, sun_elev)

        frame = anim.frame()

        # Sky
        for y in range(HORIZON):
            frame.hline(0, y, frame.width, sky_color(y, sun_h, is_night))

        # A handful of stars come out at night; their positions are stable
        # from frame to frame so they don't jitter.
        if is_night:
            for sx, sy in ((7, 2), (23, 5), (41, 1), (58, 4), (75, 2), (88, 6)):
                frame.pixel(sx, sy, C.WHITE)

        # Sea: blue base with a shimmer band that tracks the light source.
        for y in range(HORIZON, frame.height):
            frame.hline(0, y, frame.width, C.BLUE)

        # Shimmer: a moving cyan/white streak on the water, colour matches
        # whichever body is up.
        shine_x = sun_x if not is_night else moon_x
        shine_color = C.YELLOW if sun_h > 0.35 else (
            C.RED if not is_night else C.CYAN
        )
        for y in range(HORIZON + 1, frame.height):
            # Ripples spaced by row; only the ones near the light source draw.
            offset = int(4 * math.sin(theta * 3 + y * 1.1))
            cx = int(shine_x) + offset
            for dx in (-2, 0, 2):
                x = cx + dx
                if 0 <= x < frame.width:
                    frame.pixel(x, y, shine_color)

        # Sun disc: a 3x3 blob when up, coloured by elevation.
        if sun_h > 0:
            sun_color = C.YELLOW if sun_h > 0.35 else C.RED
            cx, cy = int(sun_x), int(sun_y)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if abs(dx) + abs(dy) <= 2:
                        frame.pixel(cx + dx, cy + dy, sun_color)

        # Moon: a white crescent (offset dark pixel gives the phase).
        if moon_elev > 0:
            cx, cy = int(moon_x), int(moon_y)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if abs(dx) + abs(dy) <= 2:
                        frame.pixel(cx + dx, cy + dy, C.WHITE)
            frame.pixel(cx + 1, cy, C.BLACK)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sunrise.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
