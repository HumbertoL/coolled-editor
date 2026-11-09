#!/usr/bin/env python3
"""
Voxel flyover -- a low pass over an island chain, rendered the way Comanche
did it in 1992.

There are no polygons. The land is only a height function, and each of the
96 screen columns marches one ray outward from the camera: at every step it
looks up the terrain height, projects that to a screen row, and if the row is
higher than anything this column has drawn so far, fills the gap. Near
terrain therefore hides far terrain with no sorting at all.

Height picks the colour: blue sea with cyan shallows, yellow beach, green
lowland, magenta rock, white snow. The terrain is a sum of sines whose
forward frequencies are whole multiples of one period, and the camera flies
exactly one period per loop while banking once left and right, so the loop is
seamless.
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
PERIOD = 212.0        # terrain repeats this far ahead; 4 units a frame
HORIZON = 8.0
CAMERA_HEIGHT = 11.0
SCALE = 30.0          # screen rows per unit height at distance 1
FOV = 0.75            # half-width of the view at distance 1
FAR = 300.0
TAU = 2 * math.pi
TRACK_X = -178.0     # the valley the camera follows...
SWAY = 14.0         # ...and how far it banks to either side


def height(x, y):
    v = TAU * y / PERIOD
    return (
        9.0 * math.sin(x * 0.045 + 1.3) * math.cos(v)
        + 6.0 * math.sin(x * 0.085 + 2 * v + 0.7)
        + 3.5 * math.sin(x * 0.19 - 3 * v + 2.0)
        + 1.5 * math.sin(x * 0.41 + 5 * v)
        - 2.0
    )


def shade(h, x, y):
    if h <= 0:
        # Glints on the swell, on a lattice that also repeats with the terrain.
        glint = math.sin(x * 0.9) * math.sin(TAU * 9 * y / PERIOD) > 0.8
        return C.CYAN if h > -1.2 or glint else C.BLUE
    if h < 1.3:
        return C.YELLOW
    if h < 7:
        return C.GREEN
    if h < 11.5:
        return C.MAGENTA
    return C.WHITE


def render(frame, cam_x, cam_y):
    for column in range(96):
        slope = (column - 47.5) / 48 * FOV
        lowest = 16          # everything from this row down is already drawn
        z, dz = 8.0, 0.5
        while z < FAR and lowest > 0:
            wx, wy = cam_x + slope * z, cam_y + z
            h = height(wx, wy)
            surface = max(h, 0.0)
            row = int(math.floor(HORIZON + (CAMERA_HEIGHT - surface) * SCALE / z))
            if row < lowest:
                color = shade(h, wx, wy)
                for y in range(max(row, 0), lowest):
                    frame.pixel(column, y, color)
                lowest = row
            z += dz
            dz *= 1.03


def camera_x(phase):
    return TRACK_X + SWAY * math.sin(TAU * phase)


def check_clearance():
    """The flight path must never pass through, or just over, a hill."""
    worst = max(
        height(camera_x(i / 400) + side, PERIOD * i / 400 + ahead)
        for i in range(400)
        for side in (-3, 0, 3)
        for ahead in (0, 3, 6)
    )
    if worst > CAMERA_HEIGHT - 5:
        raise AssertionError(f"terrain reaches {worst:.1f} under the camera")


def build():
    check_clearance()
    rng = random.Random(11)
    stars = [(rng.randint(0, 95), rng.randint(0, 4)) for _ in range(14)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        phase = index / FRAMES
        frame = anim.frame()
        for k, (sx, sy) in enumerate(stars):
            if (index + 5 * k) % 13 > 2:
                frame.pixel(sx, sy, C.BLUE if k % 3 else C.WHITE)
        frame.rect(80, 0, 3, 3, C.YELLOW, fill=True)   # a low moon
        render(frame, camera_x(phase), PERIOD * phase)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/voxel_flyover.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
