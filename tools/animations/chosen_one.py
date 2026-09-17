#!/usr/bin/env python3
"""
You were the chosen one (2005) -- the shouting match after the high ground.

Obi-Wan stands on the bank at the right, two lightsabres in hand now, and
shouts down at what is left of his brother on the left while the fire takes
him. His lines come in cyan, the one answer from below in yellow, and the
flames climb through the loop until they have the whole panel.

The companion piece to `high_ground`, which is the ten seconds before it.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
SEED = 20051
SKY_TOP = 8             # the words own everything above this
OBI_X = 78
ANAKIN_X = 14

#: (first frame, line, colour). One line at a time -- two would leave no
#: room for the fire, and the fire is the point.
BEATS = [
    (0, "YOU WERE THE", C.CYAN),
    (10, "CHOSEN ONE!", C.CYAN),
    (20, "YOU WERE", C.CYAN),
    (26, "MY BROTHER!", C.CYAN),
    (34, "I HATE YOU!", C.YELLOW),
]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, 15, 96, C.RED)

        # The fire: taller as the loop goes on, and it reaches for him
        # first. Capped at SKY_TOP so it never eats the words.
        for x in range(96):
            near = max(0.0, 1.0 - abs(x - ANAKIN_X) / 40.0)
            height = 1 + int(near * 4) + rng.randrange(0, 2 + int(near * index / 5))
            height = min(height, 16 - SKY_TOP)
            for y in range(16 - height, 16):
                if rng.random() < 0.2:
                    continue
                heat = (y - (16 - height)) / max(1, height)
                frame.pixel(x, y, C.YELLOW if heat < 0.4 else C.RED)

        # Both of them go on over the fire, so neither is ever lost in it.
        for row, line in enumerate(("###", ".#.", ".#.", "#.#")):
            for col, cell in enumerate(line):
                if cell == "#":
                    frame.pixel(OBI_X + col, 11 + row, C.CYAN)
        frame.vline(OBI_X + 4, 9, 3, C.CYAN)
        frame.vline(OBI_X - 2, 9, 3, C.BLUE)

        # Anakin, prone at the edge of the flow, less of him as it goes on.
        left = max(0, 5 - index // 12)
        frame.hline(ANAKIN_X, 14, left, C.YELLOW)
        if index < 30:
            frame.pixel(ANAKIN_X - 1, 13, C.YELLOW)

        start, line, color = BEATS[0]
        for beat_at, beat_line, beat_color in BEATS:
            if index >= beat_at:
                start, line, color = beat_at, beat_line, beat_color
        age = index - start
        shouting = color if age % 4 < 2 or age > 5 else C.WHITE
        frame.text(line[: max(1, age * 4)], "center", 0, shouting, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/chosen_one.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
