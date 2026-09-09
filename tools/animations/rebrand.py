#!/usr/bin/env python3
"""
Rebrand -- CALL-EM-ALL becomes TEXT-EM-ALL.

The company's old name is still in this repo's git history (the commit email
domain), so here it is turning into the new one: the first four letters flip
over one at a time, each squashing to a line and expanding as its replacement,
while the -EM-ALL stays put. Once the new word is complete a shine passes
across it.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, font  # noqa: E402

FRAMES = 24
DELAY = 150

OLD, NEW, REST = "CALL", "TEXT", "-EM-ALL"
TEXT_Y = 4
HOLD = 5
FLIP_FRAMES = 3


def squashed(frame, char, x, y, scale, color):
    """Draw a glyph scaled vertically about its middle row."""
    bitmap = font.glyph(char)
    for row in range(font.GLYPH_HEIGHT):
        dest = y + 3 + int((row - 3) * scale)
        for col in range(font.GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                frame.pixel(x + col, dest, color)


def build():
    anim = Animation(delay=DELAY)
    width = Canvas.text_width(OLD + REST)
    x0 = (anim.width - width) // 2
    rest_x = x0 + len(OLD) * (font.GLYPH_WIDTH + 1)
    flips_done = HOLD + FLIP_FRAMES * len(OLD)

    for index in range(FRAMES):
        frame = anim.frame()
        frame.text(REST, rest_x, TEXT_Y, C.WHITE)
        for i, (old, new) in enumerate(zip(OLD, NEW)):
            x = x0 + i * (font.GLYPH_WIDTH + 1)
            start = HOLD + i * FLIP_FRAMES
            phase = index - start
            if phase < 0:
                frame.text(old, x, TEXT_Y, C.YELLOW)
            elif phase == 0:
                squashed(frame, old, x, TEXT_Y, 0.5, C.YELLOW)
            elif phase == 1:
                frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
            elif phase == 2:
                squashed(frame, new, x, TEXT_Y, 0.5, C.GREEN)
            else:
                frame.text(new, x, TEXT_Y, C.GREEN)
        if index >= flips_done:
            head = x0 - 4 + (index - flips_done) * (width + 8) // (FRAMES - flips_done)
            for x, y in list(frame.lit()):
                if abs(x - head) <= 2 and y >= TEXT_Y:
                    frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rebrand.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
