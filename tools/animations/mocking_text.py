#!/usr/bin/env python3
"""
Mocking Text (2017) -- i LoVe MoNdAyS, as said by a hunched sponge.

The font is uppercase only, so the alternating-case voice is done with shape
instead: a plain sentence types out, then every second letter is flipped
upside down and turned yellow, one letter per frame. Once flipped, the odd
letters bob up and down against the even ones while a square yellow face
on the right, buck teeth and all, rocks from side to side in a chicken-like
slouch.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import layout_text  # noqa: E402
from jtkit.font import glyph  # noqa: E402

FRAMES = 48
DELAY = 100
TEXT = "I LOVE MONDAYS"
X0, Y0 = 2, 5
TYPE_END = 14
FLIP_END = 28


def letter(f, ch, x, y, color, flipped):
    rows = glyph(ch)
    if flipped:
        rows = rows[::-1]
    for r, line in enumerate(rows):
        for c, cell in enumerate(line):
            if cell == "#":
                f.pixel(x + c, y + r, color)


def face(f, ox, oy, tilt, mouth_open):
    for row in range(13):
        shift = round(tilt * (6 - row) / 6)
        x = ox + shift
        f.hline(x, oy + row, 12, C.YELLOW)
        if row in (0, 12):
            f.pixel(x, oy + row, C.BLACK)
            f.pixel(x + 11, oy + row, C.BLACK)
        if row == 3 or row == 4 or row == 5:
            for ex in (2, 7):
                f.hline(x + ex, oy + row, 3, C.WHITE)
        if row == 4:
            f.pixel(x + 3, oy + row, C.BLACK)
            f.pixel(x + 8, oy + row, C.BLACK)
        if row == 6:
            f.pixel(x + 5, oy + row, C.RED)
            f.pixel(x + 6, oy + row, C.RED)
        if row in (8, 9, 10):
            f.hline(x + 2, oy + row, 8, C.BLACK)
        if row == 8:
            f.hline(x + 2, oy + row, 8, C.RED if not mouth_open else C.BLACK)
    # buck teeth
    shift = round(tilt * (6 - 9) / 6)
    f.rect(ox + shift + 4, oy + 8, 2, 3, C.WHITE, fill=True)
    f.rect(ox + shift + 6, oy + 8, 2, 3, C.WHITE, fill=True)
    f.vline(ox + shift + 6, oy + 9, 2, C.BLACK)


def build():
    anim = Animation(delay=DELAY)
    positions, _ = layout_text(TEXT, proportional=True)
    for i in range(FRAMES):
        f = anim.frame()
        typed = min(len(TEXT), i + 1)
        flipped_upto = max(0, i - TYPE_END + 1) if i >= TYPE_END else 0
        wobble = i >= TYPE_END
        for n, (ch, cx) in enumerate(positions[:typed]):
            odd = n % 2 == 1
            is_flipped = odd and (n < flipped_upto * 2 + 1 and i >= TYPE_END)
            y = Y0
            if odd and wobble and n < flipped_upto * 2:
                phase = (i - TYPE_END) * 0.9 + n * 0.8
                y += round(2 * math.sin(phase))
            color = C.YELLOW if is_flipped else C.WHITE
            if odd and n == flipped_upto * 2 - 1 and i < FLIP_END:
                color = C.CYAN
            if ch != " ":
                letter(f, ch, X0 + cx, y, color, is_flipped)
        if i < TYPE_END:
            face(f, 82, 2, 0, False)
        else:
            k = i - TYPE_END
            tilt = round(3 * math.sin(k * 0.7))
            face(f, 82, 2, tilt, k % 2 == 0)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/mocking_text.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
