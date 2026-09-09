#!/usr/bin/env python3
"""
Starfield -- three parallax layers streaking left.

Depth is conveyed two ways at once, since the palette has no brightness:
nearer stars move faster, and they leave longer streaks. Far stars are single
blue pixels, mid ones cyan pairs, near ones white with a three-pixel tail.

Seamless. Every layer's speed divides the 96-pixel width a whole number of
times across 24 frames, so the field returns exactly to its start.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 90
SEED = 3

# (pixels per frame, colour, tail length, how many). 24 * speed is a whole
# multiple of 96 for each, which is what makes the loop seamless.
LAYERS = [
    (4, C.BLUE, 1, 14),
    (8, C.CYAN, 2, 10),
    (12, C.WHITE, 3, 6),
]


def build():
    rng = random.Random(SEED)
    stars = [
        (rng.randrange(96), rng.randrange(16), speed, color, tail)
        for speed, color, tail, count in LAYERS
        for _ in range(count)
    ]

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for x0, y, speed, color, tail in stars:
            head = (x0 - speed * index) % anim.width
            frame.pixel(head, y, color)
            # Tail trails behind the direction of travel.
            for step in range(1, tail):
                frame.pixel((head + step) % anim.width, y, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/starfield.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
