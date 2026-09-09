#!/usr/bin/env python3
"""
Cubes -- three wireframe cubes tumbling.

Each cube rotates a full turn about two axes over the loop, so the motion is
seamless. A cheap perspective divide gives the near face a larger footprint
than the far one, and edges whose midpoint is behind the centre are drawn blue
while the near ones take the cube's colour -- which is enough of a depth cue
for the eye to read a solid tumbling object rather than a flat lattice.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80

SIZE = 4.3
CAMERA = 4.0
TILT = 0.6

VERTICES = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
EDGES = [
    (i, j)
    for i in range(8)
    for j in range(i + 1, 8)
    if sum(a != b for a, b in zip(VERTICES[i], VERTICES[j])) == 1
]

CUBES = [(16, 0.0, C.CYAN), (48, 2.1, C.YELLOW), (80, 4.2, C.MAGENTA)]


def rotate(v, ax, ay):
    x, y, z = v
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    return x, y, z


def project(v, cx, cy):
    x, y, z = v
    scale = CAMERA / (CAMERA + z)
    return cx + SIZE * x * scale, cy + SIZE * y * scale, z


def build():
    anim = Animation(delay=DELAY)
    cy = (anim.height - 1) / 2

    for index in range(FRAMES):
        frame = anim.frame()
        turn = 2 * math.pi * index / FRAMES
        for cx, phase, color in CUBES:
            points = [
                project(rotate(v, TILT + turn, turn + phase), cx, cy)
                for v in VERTICES
            ]
            # Far edges first so near ones win where they cross.
            ordered = sorted(EDGES, key=lambda e: -(points[e[0]][2] + points[e[1]][2]))
            for i, j in ordered:
                depth = points[i][2] + points[j][2]
                frame.line(points[i][0], points[i][1], points[j][0], points[j][1],
                           C.BLUE if depth > 0 else color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cubes.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
