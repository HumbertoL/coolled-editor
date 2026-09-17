#!/usr/bin/env python3
"""
I don't like sand (2002) -- Anakin's attempt at flirting.

The complaint types itself out a line at a time while grains stream across
the panel on the wind and a dune builds along the bottom. By the last line
the sand has taken the lower half, then the whole panel, and the words with
it -- because it is coarse and rough and irritating and it gets everywhere.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
SEED = 2002
GRAINS = 26
BURY_AT = 38            # the dune starts climbing in earnest

BEATS = [
    (0, "I DON'T LIKE", "SAND."),
    (11, "IT'S COARSE", "AND ROUGH"),
    (21, "AND", "IRRITATING"),
    (31, "AND IT GETS", "EVERYWHERE"),
]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    # Each grain has its own row, speed and phase, so the stream has depth.
    grains = [
        (rng.randrange(96), rng.randrange(16), rng.choice((2, 3, 5)))
        for _ in range(GRAINS)
    ]

    for index in range(FRAMES):
        frame = anim.frame()

        start, one, two = BEATS[0]
        for beat_at, line_one, line_two in BEATS:
            if index >= beat_at:
                start, one, two = beat_at, line_one, line_two
        age = index - start
        frame.text(one[: max(1, age * 4)], 2, 0, C.WHITE, proportional=True)
        if age >= 2:
            frame.text(two[: max(1, (age - 2) * 4)], 2, 8, C.YELLOW, proportional=True)

        # The wind, drawn over the words: that is the whole point.
        for x0, y, speed in grains:
            x = (x0 + index * speed) % 96
            frame.pixel(x, y, C.WHITE if speed == 5 else C.YELLOW)

        # The dune. Flat for most of the loop, then it takes everything.
        base = 1 + index // 12
        climb = 0 if index < BURY_AT else (index - BURY_AT) * 11 // (FRAMES - 1 - BURY_AT)
        for x in range(96):
            height = base + climb + (1 if (x * 7 + index) % 5 < 2 else 0)
            crest = 16 - height
            for y in range(crest, 16):
                # Lit crest over a dithered body: the palette has no dimmer
                # yellow, so every other pixel has to stand in for one.
                frame.pixel(x, y, C.YELLOW if y == crest or (x + y) % 2 == 0 else C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/i_dont_like_sand.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
