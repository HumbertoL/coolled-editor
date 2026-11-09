#!/usr/bin/env python3
"""
Sky lanterns -- paper lanterns rising off a lake at night.

The closest lanterns are five pixels wide, the middle ones three, each with
a red flame under a yellow or magenta shade; far ones are a two-pixel spark. Each climbs a whole number of
sky-heights per loop and sways on a whole number of periods, so every one is
back where it started after 53 frames. The lake below the horizon carries a
squashed reflection of each lantern, broken into dashes that shift with the
ripples, and a few stars blink above.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
HORIZON = 11
TRAVEL = 19  # rows from the launch point to fully off the top


def make_lanterns(rng):
    lanterns = []
    for slot in range(13):
        near = slot % 3 != 2
        lanterns.append(
            {
                "x": 4 + slot * 7.2 + rng.uniform(-2, 2),
                "phase": rng.random(),
                "laps": 1,
                "sway": rng.choice([1, 2]),
                "sway_phase": rng.random() * 2 * math.pi,
                "near": near,
                "close": slot % 3 == 0 and slot % 2 == 0,
                "shade": rng.choice([C.YELLOW, C.YELLOW, C.MAGENTA]),
            }
        )
    return lanterns


def place(lantern, index):
    t = index / FRAMES
    climb = (t * lantern["laps"] + lantern["phase"]) % 1.0
    y = HORIZON - 1 - climb * TRAVEL
    x = lantern["x"] + 1.6 * math.sin(2 * math.pi * lantern["sway"] * t + lantern["sway_phase"])
    return round(x), round(y)


def build():
    rng = random.Random(5)
    lanterns = make_lanterns(rng)
    stars = [(rng.randrange(96), rng.randrange(0, 8), rng.randrange(FRAMES)) for _ in range(9)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        for x, y, offset in stars:
            if (index + offset) % FRAMES < 44:
                frame.pixel(x, y, C.BLUE if (index + offset) % FRAMES < 6 else C.WHITE)

        # Far shore, then ripples that drift one pixel every other frame.
        frame.hline(0, HORIZON, 96, C.BLUE)
        for y in range(HORIZON + 1, 16):
            for x in range(96):
                if (x + y * 5 + (index * 16 // FRAMES) * (1 if y % 2 else -1)) % 8 == 0:
                    frame.pixel(x, y, C.BLUE)

        for lantern in sorted(lanterns, key=lambda item: item["near"]):
            x, y = place(lantern, index)
            # Reflection: height above the water squashed three to one.
            height = HORIZON - y
            if 0 < height <= 12:
                ry = HORIZON + 1 + (height - 1) // 3
                wobble = (index // 2 + ry) % 2
                colour = C.RED if lantern["near"] else C.MAGENTA
                span = 3 if lantern["near"] else 1
                for dx in range(span):
                    if (dx + wobble) % 2 == 0 or span == 1:
                        frame.pixel(x + dx - span // 2 + wobble, ry, colour)
            if y > HORIZON - 1:
                continue
            if lantern["close"]:
                shade = lantern["shade"]
                frame.hline(x - 1, y - 4, 3, shade)
                frame.hline(x - 2, y - 3, 5, shade)
                frame.hline(x - 2, y - 2, 5, shade)
                frame.hline(x - 1, y - 1, 3, shade)
                frame.pixel(x, y - 2, C.WHITE)
                frame.pixel(x, y - 1, C.RED)
                frame.pixel(x, y, C.RED)
            elif lantern["near"]:
                shade = lantern["shade"]
                frame.pixel(x, y - 3, shade)
                frame.hline(x - 1, y - 2, 3, shade)
                frame.hline(x - 1, y - 1, 3, shade)
                frame.pixel(x, y - 1, C.WHITE)
                frame.pixel(x, y, C.RED)
            else:
                frame.pixel(x, y - 1, C.YELLOW)
                frame.pixel(x, y, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sky_lanterns.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
