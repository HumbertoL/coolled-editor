#!/usr/bin/env python3
"""
CHAOS CORNER -- the sign's own name, living up to it.

The words hold steady in white while the space around them misbehaves: sparks
flicker in the margins in random colours, and a few pixels of the lettering
itself glitch to a random hue each frame before snapping back. Legible, but
never quite still.

Deliberately not seamless -- a fixed seed keeps it reproducible, but chaos
that looped cleanly would rather miss the point.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

WORDS = "CHAOS CORNER"
FRAMES = 24
DELAY = 110
SEED = 42

TEXT_Y = 4
SPARKS = 7
GLITCHES = 5

PALETTE = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA, C.WHITE]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    width = Canvas.text_width(WORDS, proportional=True)
    x0 = (anim.width - width) // 2

    for _ in range(FRAMES):
        frame = anim.frame()
        frame.text(WORDS, x0, TEXT_Y, C.WHITE, proportional=True)

        # Glitch a few of the lit letter pixels to a random colour.
        letters = frame.lit()
        for x, y in rng.sample(letters, min(GLITCHES, len(letters))):
            frame.pixel(x, y, rng.choice(PALETTE))

        # Sparks in the margins, clear of the words.
        for _ in range(SPARKS):
            if rng.random() < 0.5:
                x = rng.randrange(0, max(1, x0 - 1))
            else:
                x = rng.randrange(min(anim.width - 1, x0 + width + 1), anim.width)
            frame.pixel(x, rng.randrange(anim.height), rng.choice(PALETTE))

        # Occasional full-height streak, like a bad connection.
        if rng.random() < 0.3:
            x = rng.randrange(anim.width)
            for y in range(anim.height):
                if rng.random() < 0.6:
                    frame.pixel(x, y, rng.choice([C.BLUE, C.MAGENTA]))

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/chaos_corner.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
