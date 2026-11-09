#!/usr/bin/env python3
"""
Missile Command -- six cities, one battery, five incoming.

Red trails fall from the top of the panel toward the cities. For each, a
magenta crosshair marks where the battery is aiming, a cyan interceptor
climbs to it at 4 pixels a frame, and a fireball blooms there, timed to be
two pixels across when the warhead arrives. Four are stopped. The fifth
shot goes off a frame late and a little wide, the last warhead lands, and
the city on the far left is gone. The loop starts over with all six
standing.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
GROUND_Y = 15
BATTERY = (48, 12)
CITIES = [8, 22, 34, 58, 70, 84]
LOST_CITY = 8
RADII = [1, 2, 3, 4, 4, 3, 2]
FLASH = [C.WHITE, C.YELLOW, C.WHITE, C.YELLOW, C.RED, C.RED, C.MAGENTA]

# start frame, (x0, y0), (x1, y1), flight frames, frame it is destroyed (or None)
INCOMING = [
    (0, (20, 0), (30, 13), 26, 16),
    (4, (70, 0), (60, 13), 26, 21),
    (14, (92, 0), (73, 13), 24, 30),
    (22, (50, 0), (37, 13), 24, 38),
    (20, (2, 0), (11, 13), 24, None),
]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def plan():
    """Interceptor shots as (launch frame, burst frame, target point)."""
    shots = []
    for start, origin, target, flight, killed in INCOMING:
        if killed is None:
            # The miss: aimed where the warhead was, a frame too late.
            point = lerp(origin, target, (41 - start) / flight)
            point = (point[0] + 5, point[1] - 2)
            burst = 43
        else:
            point = lerp(origin, target, (killed - start) / flight)
            burst = killed - 1
        distance = math.hypot(point[0] - BATTERY[0], point[1] - BATTERY[1])
        shots.append((burst - math.ceil(distance / 4), burst, point))
    return shots


def fireball(frame, centre, age):
    radius = RADII[age]
    for y in range(16):
        for x in range(96):
            if math.hypot(x - centre[0], y - centre[1]) <= radius + 0.3:
                frame.pixel(x, y, FLASH[age])


def scenery(frame, index):
    frame.hline(0, GROUND_Y, 96, C.GREEN)
    for x in CITIES:
        if x == LOST_CITY and index >= 44:
            if index >= 51:
                frame.pixel(x + 1, 14, C.RED)
                frame.pixel(x + 4, 14, C.RED)
            continue
        for dx in (1, 4):
            frame.pixel(x + dx, 13, C.CYAN)
        frame.hline(x, 14, 6, C.BLUE)
    frame.hline(BATTERY[0] - 1, 13, 3, C.YELLOW)
    frame.hline(BATTERY[0] - 2, 14, 5, C.YELLOW)


def build():
    shots = plan()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        scenery(frame, index)

        for start, origin, target, flight, killed in INCOMING:
            end = killed if killed is not None else start + flight
            if start <= index < end:
                head = lerp(origin, target, (index - start) / flight)
                frame.line(*origin, round(head[0]), round(head[1]), C.RED)
                frame.pixel(round(head[0]), round(head[1]), C.WHITE)

        for launch, burst, point in shots:
            px, py = round(point[0]), round(point[1])
            if launch <= index < burst:
                head = lerp(BATTERY, point, (index - launch + 1) / (burst - launch))
                frame.line(*BATTERY, round(head[0]), round(head[1]), C.BLUE)
                frame.pixel(round(head[0]), round(head[1]), C.CYAN)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    frame.pixel(px + dx, py + dy, C.MAGENTA)
            elif burst <= index < burst + len(RADII):
                fireball(frame, (px, py), index - burst)

        # The one that got through.
        if 44 <= index < 44 + len(RADII):
            fireball(frame, (11, 13), index - 44)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/missile_command.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
