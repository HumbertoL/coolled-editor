#!/usr/bin/env python3
"""
Nameplate -- the panel owner's name, at twice the font size.

Eight letters at 2x fill 94 of the 96 columns, which is the biggest a name can
go here. They drop in from above one at a time with a one-pixel overshoot on
landing, then once all eight have settled a rainbow ripples through them until
the loop comes round and they fall again.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, font  # noqa: E402

FRAMES = 24
DELAY = 100

NAME = "HUMBERTO"
SCALE = 2
TRACKING = 2
REST_Y = 1
DROP_EVERY = 2
DROP_PATH = [-14, -6, 2, REST_Y]      # y per frame after the letter's start
RIPPLE_FROM = 18


def text2x(frame, char, x, y, color):
    bitmap = font.glyph(char)
    for row in range(font.GLYPH_HEIGHT):
        for col in range(font.GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                frame.rect(x + col * SCALE, y + row * SCALE, SCALE, SCALE, color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    advance = font.GLYPH_WIDTH * SCALE + TRACKING
    x0 = (anim.width - (advance * len(NAME) - TRACKING)) // 2
    for index in range(FRAMES):
        frame = anim.frame()
        for i, char in enumerate(NAME):
            phase = index - i * DROP_EVERY
            if phase < 0:
                continue
            if phase < len(DROP_PATH):
                y, color = DROP_PATH[phase], C.WHITE
            else:
                y = REST_Y
                shift = max(0, index - RIPPLE_FROM)
                color = C.SPECTRUM[(i + shift) % len(C.SPECTRUM)]
            text2x(frame, char, x0 + i * advance, y, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/humberto.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
