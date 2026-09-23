#!/usr/bin/env python3
"""
timelapse_garden -- five days in a flower bed, about a second each.

Eight yellow seeds sit in a strip of red earth under a grass line. The sun
rises on the left, arcs over and sets on the right, with a magenta band on
the horizon at dawn and dusk; then the sky goes black, seeded stars come
out and a moon crosses. The plants grow only while it is light, so each
night freezes them and each morning they have jumped: a sprout, a stem,
leaves that open a pixel at a time on alternating sides, a green bud, and
then a flower opening in three steps -- a dot, a plus, a full head with a
yellow or white centre -- each in its own colour. A 3x5 DAY counter ticks
in the corner. By day five the bed is in full bloom, and the loop ends on
its last night before the seeds go back in.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
SEED = 5
DAYS = 5
DAYLIGHT = 0.7      # fraction of each day the sun is up
GROUND = 13         # grass row; stems start at GROUND - 1

# (x, petal colour, centre colour, sprout at, growth rows per daylight-day, height)
PLANTS = [
    (8, C.WHITE, C.YELLOW, 0.10, 4.0, 4),   # short, clear of the DAY label
    (19, C.MAGENTA, C.WHITE, 0.35, 4.0, 6),
    (30, C.YELLOW, C.RED, 0.20, 6.0, 10),
    (41, C.RED, C.YELLOW, 0.50, 5.0, 8),
    (54, C.CYAN, C.WHITE, 0.25, 4.5, 7),
    (65, C.RED, C.WHITE, 0.60, 5.0, 9),
    (76, C.MAGENTA, C.YELLOW, 0.15, 4.0, 6),
    (87, C.YELLOW, C.WHITE, 0.45, 5.5, 8),
]

MINI = {
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "##.", "..#", "##."],
}


def mini_text(frame, text, x, y, colour):
    for char in text:
        if char != " ":
            for r, line in enumerate(MINI[char]):
                for c, cell in enumerate(line):
                    if cell == "#":
                        frame.pixel(x + c, y + r, colour)
        x += 4 if char != " " else 2
    return x


def draw_plant(frame, plant, light):
    x, petal, centre, start, rate, tall = plant
    if light < start:
        frame.pixel(x, GROUND, C.YELLOW)  # the seed
        return
    grown = (light - start) * rate
    height = min(tall, int(grown) + 1)
    top = GROUND - height
    frame.vline(x, top, height, C.GREEN)
    # Leaves every two rows, alternating sides, opening one pixel then two.
    for k, leaf_y in enumerate(range(GROUND - 2, top + 1, -2)):
        side = -1 if k % 2 == 0 else 1
        age = grown - (GROUND - leaf_y)
        if age > 0.5:
            frame.pixel(x + side, leaf_y - 1 if age < 1.5 else leaf_y, C.GREEN)
        if age > 1.5:
            frame.pixel(x + 2 * side, leaf_y - 1, C.GREEN)
    # Bud and bloom once full height is reached.
    after = grown - tall
    if after <= 0:
        return
    head = top - 1
    if after < 0.6:
        frame.pixel(x, head, C.GREEN)
    elif after < 1.2:
        frame.pixel(x, head, petal)
    elif after < 1.8:
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            frame.pixel(x + dx, head + dy, petal)
        frame.pixel(x, head, centre)
    else:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                frame.pixel(x + dx, head + dy, petal)
        for dx, dy in ((0, -2), (-2, 0), (2, 0)):
            frame.pixel(x + dx, head + dy, petal)
        frame.pixel(x, head, centre)


def build():
    rng = random.Random(SEED)
    stars = [(rng.randrange(96), rng.randrange(0, 10)) for _ in range(22)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES * DAYS
        day, phase = int(t), t % 1
        light = day * DAYLIGHT + min(phase, DAYLIGHT)  # accumulated daylight
        is_day = phase < DAYLIGHT
        # Sky.
        if is_day:
            s = phase / DAYLIGHT
            for y in range(GROUND):
                for x in range(96):
                    frame.pixel(x, y, C.BLUE)
            if s < 0.14 or s > 0.86:
                for x in range(96):
                    frame.pixel(x, GROUND - 1, C.MAGENTA)
                    if x % 2 == 0:
                        frame.pixel(x, GROUND - 2, C.MAGENTA)
            sx = round(-2 + s * 99)
            sy = round(11 - 9 * math.sin(math.pi * s))
            for dx in range(-1, 3):
                for dy in range(-1, 3):
                    if (dx in (-1, 2)) and (dy in (-1, 2)):
                        continue
                    frame.pixel(sx + dx, sy + dy, C.YELLOW)
        else:
            s = (phase - DAYLIGHT) / (1 - DAYLIGHT)
            for i, (x, y) in enumerate(stars):
                if (i + index) % 7:
                    frame.pixel(x, y, C.WHITE if i % 3 else C.CYAN)
            mx = round(8 + s * 80)
            my = round(8 - 6 * math.sin(math.pi * s))
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, -1), (0, 2), (-1, 0), (-1, 1)):
                frame.pixel(mx + dx - 1, my + dy, C.WHITE)
            for dy in range(-1, 3):
                frame.pixel(mx + 1, my + dy, C.BLACK)  # carve the crescent
        # Ground: grass line and red earth.
        frame.hline(0, GROUND, 96, C.GREEN)
        for x in range(96):
            for y in (GROUND + 1, GROUND + 2):
                if (x + y) % 3:
                    frame.pixel(x, y, C.RED)
        for plant in PLANTS:
            draw_plant(frame, plant, light)
        mini_text(frame, f"DAY {day + 1}", 1, 0, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/timelapse_garden.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
