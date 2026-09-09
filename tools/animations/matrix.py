#!/usr/bin/env python3
"""
Matrix -- glyphs cascading down the panel.

Sixteen columns of the 5x7 font, each dropping a character through the frame.
A 16-pixel panel only fits two glyph rows, so instead of a dense curtain each
column slides a single character down at its own speed and swaps it for a new
one on the way, which reads as a cascade without the space for one.

Colour marks age: a glyph enters white, turns green as it falls, and dims to
blue as it leaves. Columns start at staggered offsets and every speed divides
the travel distance evenly, so the loop closes.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 95
SEED = 23

GLYPH_STEP = 6          # 5px cell plus tracking
TRAVEL = 24             # rows of travel before wrapping: -8 .. 16
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@$%&*+"


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    columns = anim.width // GLYPH_STEP

    # Speeds that divide TRAVEL, so each column returns to its start.
    lanes = [
        {
            "speed": rng.choice([1, 2, 3]),
            "offset": rng.randrange(TRAVEL),
            "chars": [rng.choice(ALPHABET) for _ in range(TRAVEL)],
        }
        for _ in range(columns)
    ]

    for index in range(FRAMES):
        frame = anim.frame()
        for column, lane in enumerate(lanes):
            position = (lane["offset"] + index * lane["speed"]) % TRAVEL
            y = position - 8
            # The character changes as it travels, so a column never looks
            # like one letter sliding down a groove.
            char = lane["chars"][position]

            # Thresholds are about what is VISIBLE: a glyph at y < -2 is
            # only showing its lower rows at the top edge, which is the head.
            if y < -2:
                color = C.WHITE
            elif y < 7:
                color = C.GREEN
            else:
                color = C.BLUE

            frame.text(char, column * GLYPH_STEP, y, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/matrix.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
