#!/usr/bin/env python3
"""
My Shot -- Hamilton.

The gold star from the poster, at double size on the left, with the line
arriving word by word on the beat: I AM NOT / THROWING AWAY. Then the panel
clears and MY SHOT lands at double size, flashing, with sparks in the
corners. Rise up.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, font  # noqa: E402

FRAMES = 53
DELAY = 120
LINE_1 = ["I", "AM", "NOT"]
LINE_2 = ["THROWING", "AWAY"]
WORD_AT = [4, 8, 12, 17, 23]
SHOT_AT = 30
STAR_X, STAR_Y = 3, 1
TEXT_X = 30


def star2x(frame, color):
    bitmap = font.glyph("+STAR")
    for r in range(font.GLYPH_HEIGHT):
        for c in range(font.GLYPH_WIDTH):
            if bitmap[r][c] == "#":
                frame.rect(STAR_X + c * 2, STAR_Y + r * 2, 2, 2, color, fill=True)


def text2x(frame, text, x, y, color):
    for i, ch in enumerate(text):
        bitmap = font.glyph(ch)
        for r in range(font.GLYPH_HEIGHT):
            for c in range(font.GLYPH_WIDTH):
                if bitmap[r][c] == "#":
                    frame.rect(x + i * 12 + c * 2, y + r * 2, 2, 2, color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index >= SHOT_AT:
            k = index - SHOT_AT
            text2x(frame, "MY SHOT", 7, 1, C.YELLOW if k % 4 < 2 else C.WHITE)
            for i, (sx, sy) in enumerate(((2, 2), (93, 3), (3, 13), (92, 12), (48, 0))):
                if (k + i) % 3 == 0:
                    frame.pixel(sx, sy, C.WHITE)
                    frame.pixel(sx + 1, sy, C.YELLOW)
            continue
        said = sum(1 for at in WORD_AT if index >= at)
        star2x(frame, C.YELLOW if index % 6 else C.WHITE)
        top = " ".join(LINE_1[:min(said, len(LINE_1))])
        bottom = " ".join(LINE_2[:max(0, said - len(LINE_1))])
        if top:
            frame.text(top, TEXT_X, 0, C.WHITE, proportional=True)
        if bottom:
            frame.text(bottom, TEXT_X, 9, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hamilton_shot.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
