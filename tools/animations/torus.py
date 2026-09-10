#!/usr/bin/env python3
"""
Torus -- the spinning, shaded donut, on 96x16.

The direct descendant of Andy Sloane's donut.c: a torus is swept as a grid of
(theta, phi) points, rotated in 3D on two axes, perspective-projected, and
z-buffered so nearer surface hides farther. Each point's brightness is the dot
product of its surface normal with a fixed light, quantised into the panel's
BLUE -> CYAN -> WHITE glow ramp with a yellow specular tip.

Seamless: over the loop it turns exactly once about one axis and twice about the
other, so the pose at the last frame is the pose at the first.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80

R1 = 1.0             # tube radius
R2 = 2.0             # centre-of-tube radius
K2 = 5.0             # viewer distance
K1X = 13.0           # horizontal projection scale
K1Y = 13.0           # vertical projection scale (panel is only 16 tall)
CX, CY = 48.0, 8.0

THETA_STEP = 0.09
PHI_STEP = 0.025

# Light coming from the upper-left-front, normalised.
_L = (0.0, 0.7, -0.7)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        t = index / FRAMES
        a = 2 * math.pi * t          # one turn about X
        b = 2 * 2 * math.pi * t      # two turns about Z
        frame = anim.frame()

        cos_a, sin_a = math.cos(a), math.sin(a)
        cos_b, sin_b = math.cos(b), math.sin(b)

        zbuf = {}

        theta = 0.0
        while theta < 2 * math.pi:
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            # Point on the tube cross-section.
            circle_x = R2 + R1 * cos_t
            circle_y = R1 * sin_t

            phi = 0.0
            while phi < 2 * math.pi:
                cos_p, sin_p = math.cos(phi), math.sin(phi)

                # 3D point of the untilted torus (hole along z).
                px = circle_x * cos_p
                py = circle_x * sin_p
                pz = circle_y

                # Rotate about X by a, then about Z by b.
                x1 = px
                y1 = py * cos_a - pz * sin_a
                z1 = py * sin_a + pz * cos_a
                x = x1 * cos_b - y1 * sin_b
                y = x1 * sin_b + y1 * cos_b
                z = z1

                ooz = 1.0 / (z + K2)
                sx = int(CX + K1X * ooz * x)
                sy = int(CY - K1Y * ooz * y)
                if not (0 <= sx < frame.width and 0 <= sy < frame.height):
                    phi += PHI_STEP
                    continue

                # Surface normal, rotated the same way.
                nx0 = cos_t * cos_p
                ny0 = cos_t * sin_p
                nz0 = sin_t
                nx1 = nx0
                ny1 = ny0 * cos_a - nz0 * sin_a
                nz1 = ny0 * sin_a + nz0 * cos_a
                nx = nx1 * cos_b - ny1 * sin_b
                ny = nx1 * sin_b + ny1 * cos_b
                nz = nz1

                lum = nx * _L[0] + ny * _L[1] + nz * _L[2]

                key = (sx, sy)
                if ooz > zbuf.get(key, 0.0):
                    zbuf[key] = ooz
                    if lum > 0.85:
                        color = C.YELLOW
                    elif lum > 0.55:
                        color = C.WHITE
                    elif lum > 0.2:
                        color = C.CYAN
                    else:
                        color = C.BLUE
                    frame.pixel(sx, sy, color)

                phi += PHI_STEP
            theta += THETA_STEP

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/torus.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
