#!/usr/bin/env python3
"""
Dandelion -- a seed head taken apart by the wind.

The clock is a dithered disc of white seeds on a green stem. A breeze
arrives as blue streaks, and the seeds let go from the downwind side first,
about three every two frames. Each is a white tuft over a yellow seed,
carried right at its own speed on its own slow wobble, rising a little as
it goes. By the end only the stem and its yellow receptacle are left. Not
seamless: the loop starts over with a full head.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
HEAD = (13, 6)
RADIUS = 5.3
FIRST_RELEASE = 6
LAST_RELEASE = 33


def seeds(rng):
    spots = []
    for y in range(16):
        for x in range(30):
            distance = math.hypot(x - HEAD[0], y - HEAD[1])
            if distance <= RADIUS and (distance > RADIUS - 1.2 or (x + y) % 2 == 0):
                spots.append((x, y))
    # Downwind side goes first, with a little disorder.
    spots.sort(key=lambda spot: -spot[0] + rng.uniform(-2, 2))
    out = []
    for order, (x, y) in enumerate(spots):
        release = FIRST_RELEASE + (LAST_RELEASE - FIRST_RELEASE) * order / (len(spots) - 1)
        out.append(
            {
                "x": x,
                "y": y,
                "release": round(release),
                "speed": rng.uniform(2.6, 4.2),
                "lift": rng.uniform(0.02, 0.22),
                "wobble": rng.uniform(0.8, 2.0),
                "rate": rng.uniform(0.3, 0.55),
                "phase": rng.uniform(0, 2 * math.pi),
            }
        )
    return out


def build():
    rng = random.Random(11)
    flock = seeds(rng)
    streaks = [(rng.randrange(96), rng.choice([1, 3, 9, 12, 13]), rng.randrange(4, 9)) for _ in range(5)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        # Grass, stem (leaning a pixel in the wind once it blows), receptacle.
        frame.hline(0, 15, 96, C.GREEN)
        for x in (3, 22, 37, 55, 70, 88):
            frame.pixel(x, 14, C.GREEN)
        lean = 1 if index >= FIRST_RELEASE - 2 else 0
        for y in range(HEAD[1] + 1, 15):
            frame.pixel(HEAD[0] - (1 if y > 11 and lean else 0), y, C.GREEN)
        frame.pixel(HEAD[0] - 2, 13, C.GREEN)
        frame.pixel(HEAD[0] - 3, 12, C.GREEN)
        frame.pixel(HEAD[0] + 2, 14, C.GREEN)
        frame.pixel(HEAD[0], HEAD[1], C.YELLOW)
        frame.pixel(HEAD[0], HEAD[1] + 1, C.YELLOW)

        if FIRST_RELEASE - 3 <= index < LAST_RELEASE + 8:
            for x0, y, length in streaks:
                x = (x0 + 7 * index) % 130 - 20
                frame.hline(x, y, length, C.BLUE)

        for seed in flock:
            age = index - seed["release"]
            if age < 0:
                frame.pixel(seed["x"], seed["y"], C.WHITE)
                continue
            x = seed["x"] + seed["speed"] * age
            y = (
                seed["y"]
                - seed["lift"] * age
                + seed["wobble"] * (math.sin(seed["rate"] * age + seed["phase"]) - math.sin(seed["phase"]))
            )
            x, y = round(x), round(min(13, max(0, y)))
            frame.pixel(x - 1, y, C.WHITE)
            frame.pixel(x + 1, y, C.WHITE)
            frame.pixel(x, y, C.WHITE)
            frame.pixel(x, y + 1, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dandelion.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
