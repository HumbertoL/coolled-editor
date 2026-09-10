#!/usr/bin/env python3
"""
Natural 20 -- a d20 rolls across the panel and lands on a twenty.

A wireframe icosahedron tumbles in from the left, slowing as it goes, the
way a die does on a table. Once it stops, the face nearest the viewer fills
in and the result pops up beside it: a big 20, then NAT 20! flashing in gold.

The far edges are drawn blue and the near ones cyan, then everything goes
white on the freeze frame -- a 3-bit palette's version of a spotlight. The
same roll code serves d20_nat1, which just lands on the other number.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, font  # noqa: E402

FRAMES = 53
DELAY = 100

ROLL_END = 30            # die is stationary from here
REVEAL = 34              # result face fills
BANNER = 38              # text pops
RADIUS = 7.0
CAMERA = 5.0
REST_X = 14.0
START_X = -12.0

PHI = (1 + 5 ** 0.5) / 2
_RAW = [(0, s1, s2 * PHI) for s1 in (-1, 1) for s2 in (-1, 1)]
_RAW += [(s1, s2 * PHI, 0) for s1 in (-1, 1) for s2 in (-1, 1)]
_RAW += [(s1 * PHI, 0, s2) for s1 in (-1, 1) for s2 in (-1, 1)]
_LEN = (1 + PHI * PHI) ** 0.5
VERTICES = [(x / _LEN, y / _LEN, z / _LEN) for x, y, z in _RAW]
EDGES = [
    (i, j) for i in range(12) for j in range(i + 1, 12)
    if abs(math.dist(VERTICES[i], VERTICES[j]) - 2 / _LEN) < 1e-6
]
FACES = [
    (i, j, k) for i, j in EDGES for k in range(12)
    if k > j and (j, k) in EDGES and (i, k) in EDGES
]
assert len(EDGES) == 30 and len(FACES) == 20


def rotate(v, ax, ay, az):
    x, y, z = v
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return x, y, z


def project(v, cx, cy):
    x, y, z = v
    scale = CAMERA / (CAMERA - z)          # z toward the viewer
    return cx + RADIUS * x * scale, cy - RADIUS * y * scale, z


def fill_triangle(frame, a, b, c, color):
    xs = [a[0], b[0], c[0]]
    ys = [a[1], b[1], c[1]]

    def edge(p, q, r):
        return (r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])

    area = edge(a, b, c)
    if abs(area) < 1e-9:
        return
    for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
        for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
            p = (x + 0.5, y + 0.5)
            w0, w1, w2 = edge(b, c, p), edge(c, a, p), edge(a, b, p)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                frame.pixel(x, y, color)


def text2x(frame, text, x, y, color):
    for i, ch in enumerate(text):
        bitmap = font.glyph(ch)
        for row in range(font.GLYPH_HEIGHT):
            for col in range(font.GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    frame.rect(x + i * 12 + col * 2, y + row * 2, 2, 2, color, fill=True)


def roll_state(index):
    """Die centre x and cumulative rotation, decelerating to a stop."""
    t = min(1.0, index / ROLL_END)
    ease = 1 - (1 - t) ** 3
    x = START_X + (REST_X - START_X) * ease
    travelled = x - START_X
    angle = travelled / RADIUS * 1.15
    return x, angle


def build(result="20", banner="NAT 20!", accent=C.YELLOW, flash=C.WHITE,
          number_x=30, banner_x=56):
    anim = Animation(delay=DELAY)
    cy = (anim.height - 1) / 2

    for index in range(FRAMES):
        frame = anim.frame()
        cx, angle = roll_state(index)
        stopped = index >= ROLL_END
        wobble = 0.08 * math.sin(index * 2.2) if ROLL_END <= index < REVEAL else 0.0

        points = [
            project(rotate(v, 0.5 + wobble, angle * 0.35, -angle), cx, cy)
            for v in VERTICES
        ]

        if index >= REVEAL:
            nearest = max(FACES, key=lambda f: sum(points[i][2] for i in f))
            fill_triangle(frame, points[nearest[0]], points[nearest[1]], points[nearest[2]],
                          accent if index % 6 < 3 or index < BANNER else flash)

        ordered = sorted(EDGES, key=lambda e: points[e[0]][2] + points[e[1]][2])
        for i, j in ordered:
            depth = points[i][2] + points[j][2]
            if index >= REVEAL:
                color = C.WHITE if depth > 0 else C.BLUE
            else:
                color = C.CYAN if depth > 0 else C.BLUE
            frame.line(points[i][0], points[i][1], points[j][0], points[j][1], color)

        if index >= BANNER:
            k = index - BANNER
            pop = min(k, 2)                          # rises over the first frames
            text2x(frame, result, number_x, 3 - pop + 2, accent if k % 4 < 2 else flash)
            if k >= 3:
                frame.text(banner, banner_x, 4, flash if k % 4 < 2 else accent, proportional=True)
        elif stopped and index >= REVEAL:
            frame.text("...", 32, 4, C.BLUE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/d20_nat20.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
