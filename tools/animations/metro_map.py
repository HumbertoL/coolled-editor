#!/usr/bin/env python3
"""
Metro map -- a transit diagram in the Harry Beck manner, with the trains
running on it.

Five lines, drawn only in horizontals, verticals and 45-degree diagonals as
the London diagram has been since 1933. Stations are ticks off the side of
their line; interchanges are white rings wherever two lines share a pixel. Trains are white,
three pixels long, and follow their line's pixels in order.

Trains on a line are spaced 53 pixels apart and move one pixel a frame, so
after 53 frames every train is exactly where the one ahead of it was and the
loop is seamless. Alternate lines run in opposite directions, and the two
short cross-town lines carry one train each.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
TRAIN = 3

# (colour, direction, phase, corner points, distances along the line of its stations)
LINES = [
    (C.RED, 1, 0, [(0, 8), (95, 8)], [6, 26, 56, 70, 90]),
    (C.CYAN, -1, 20, [(0, 3), (12, 3), (21, 12), (40, 12), (49, 3), (68, 3), (77, 12), (95, 12)],
     [5, 28, 52, 63, 88]),
    (C.YELLOW, 1, 35, [(0, 14), (24, 14), (37, 1), (58, 1), (71, 14), (95, 14)],
     [4, 14, 44, 51, 78, 88]),
    (C.GREEN, 1, 10, [(86, 0), (86, 5), (89, 8), (89, 12)], []),
    (C.MAGENTA, -1, 40, [(4, 0), (4, 5), (9, 10), (9, 14)], []),
]


def trace(points):
    """Every pixel of a polyline, in order, corners not repeated."""
    path = [points[0]]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        assert abs(x1 - x0) in (0, steps) and abs(y1 - y0) in (0, steps), "not 45 degrees"
        for i in range(1, steps + 1):
            path.append((x0 + (x1 - x0) * i // steps, y0 + (y1 - y0) * i // steps))
    return path


def draw_network(frame, paths, interchanges):
    for (color, _direction, _phase, _points, stations), path in zip(LINES, paths):
        for x, y in path:
            frame.pixel(x, y, color)
        for distance in stations:
            x, y = path[distance]
            before, after = path[distance - 1], path[distance + 1]
            # A tick at right angles: beside a horizontal run, above; else to the side.
            if before[1] == y == after[1]:
                frame.pixel(x, y - 1, color)
            else:
                frame.pixel(x + 1, y, color)
    for x, y in interchanges:
        frame.rect(x - 1, y - 1, 3, 3, C.WHITE)
        frame.pixel(x, y, C.BLACK)


def build():
    paths = [trace(points) for _c, _d, _p, points, _s in LINES]
    # An interchange is wherever two lines share a pixel -- found, not listed.
    seen = Counter(pixel for path in paths for pixel in set(path))
    interchanges = sorted(pixel for pixel, count in seen.items() if count > 1)

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_network(frame, paths, interchanges)
        for (_color, direction, phase, _points, _stations), path in zip(LINES, paths):
            for distance, (x, y) in enumerate(path):
                # Position of this pixel in the 53-pixel pattern sliding along the line.
                if (direction * distance - index - phase) % FRAMES < TRAIN:
                    frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/metro_map.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
