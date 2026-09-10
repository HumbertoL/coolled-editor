#!/usr/bin/env python3
"""
Night drive -- a city skyline, a road, traffic both ways.

Buildings in blue with yellow windows that flicker on and off, a few stars,
and a two-lane road below with dashed centre line. Cars pass in both lanes
at different speeds -- white headlights front, red tail lights behind -- and
every car makes a whole number of crossings per loop, so it is seamless.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 9

SKYLINE_BASE = 8         # last row of the buildings
ROAD_TOP = 9
CAR = ["######", "######"]
CAR_W = 6
LAP = 96 + CAR_W + 4

# (row of the car's top, crossings per loop (negative = leftward), phase, body colour)
CARS = [
    (ROAD_TOP + 0, 2, 0.0, C.CYAN),
    (ROAD_TOP + 0, 2, 0.55, C.MAGENTA),
    (ROAD_TOP + 4, -1, 0.2, C.YELLOW),
    (ROAD_TOP + 4, -2, 0.7, C.GREEN),
]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    buildings = []
    x = 0
    while x < 96:
        w = rng.randrange(5, 12)
        h = rng.randrange(3, 9)
        buildings.append((x, w, h))
        x += w + rng.randrange(0, 2)
    windows = [(bx + 1 + 2 * i, SKYLINE_BASE - 1 - 2 * j, rng.random())
               for bx, bw, bh in buildings
               for i in range((bw - 1) // 2) for j in range(bh // 2)]
    stars = [(rng.randrange(96), rng.randrange(0, 3), rng.randrange(FRAMES)) for _ in range(10)]

    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES
        for sx, sy, twinkle in stars:
            if (index + twinkle) % 9 < 7:
                frame.pixel(sx, sy, C.WHITE if (index + twinkle) % 9 == 3 else C.BLUE)
        for bx, bw, bh in buildings:
            frame.rect(bx, SKYLINE_BASE - bh + 1, bw, bh, C.BLUE, fill=True)
        for wx, wy, seed in windows:
            on = ((seed * 100 + index * 0.07) % 1.0) < 0.6
            if on:
                frame.pixel(wx, wy, C.YELLOW)

        frame.hline(0, ROAD_TOP - 1, 96, C.BLUE)
        for dash in range(0, 96, 8):
            frame.hline(dash, ROAD_TOP + 3, 4, C.YELLOW)

        for top, laps, phase, color in CARS:
            pos = ((t * laps + phase) % 1.0) * LAP - CAR_W - 2
            if laps < 0:
                pos = 96 - pos - CAR_W
            x = round(pos)
            frame.rect(x, top, CAR_W, 2, color, fill=True)
            frame.pixel(x + 1, top + 2, C.BLACK)
            head, tail = (x + CAR_W, x - 1) if laps > 0 else (x - 1, x + CAR_W)
            frame.pixel(head, top + 1, C.WHITE)
            frame.pixel(head + (1 if laps > 0 else -1), top + 1, C.WHITE)
            frame.pixel(tail, top + 1, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/night_drive.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
