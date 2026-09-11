#!/usr/bin/env python3
"""
Team name -- DONUT HOLES becomes WAFFLING DONUT$.

The old name flips out letter by letter from the left -- each glyph squashes
to a line and vanishes -- and the new one flips in the same way behind it.
At the left, the team icon turns over with the name: a frosted ring becomes
a waffle grid. Then a shine, because a rebrand deserves a shine.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, font, layout_text  # noqa: E402

FRAMES = 53
DELAY = 100
OLD, NEW = "DONUT HOLES", "WAFFLING DONUT$"
TEXT_X, TEXT_Y = 9, 4
OUT_START, OUT_EVERY = 4, 1
IN_START, IN_EVERY = 13, 2
SHINE_AT = 46

DONUT = [
    ".#####.",
    "#######",
    "##...##",
    "##...##",
    "##...##",
    "#######",
    ".#####.",
]
WAFFLE = [
    "#######",
    "#.#.#.#",
    "#######",
    "#.#.#.#",
    "#######",
    "#.#.#.#",
    "#######",
]
ICON_X, ICON_Y = 0, 4


def squashed(frame, char, x, y, scale, color):
    bitmap = font.glyph(char)
    for row in range(font.GLYPH_HEIGHT):
        dest = y + 3 + int((row - 3) * scale)
        for col in range(font.GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                frame.pixel(x + col, dest, color)


def draw_word(frame, word, start, every, index, color, direction):
    positions, _ = layout_text(word, proportional=True)
    for i, (char, cell_x) in enumerate(positions):
        phase = index - (start + i * every)
        x = TEXT_X + cell_x
        if direction == "out":
            if phase < 0:
                frame.text(char, x, TEXT_Y, color, proportional=False)
            elif phase == 0:
                squashed(frame, char, x, TEXT_Y, 0.5, color)
            elif phase == 1:
                frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
        else:
            if phase == 0:
                frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
            elif phase == 1:
                squashed(frame, char, x, TEXT_Y, 0.5, color)
            elif phase >= 2:
                frame.text(char, x, TEXT_Y, color, proportional=False)


def icon(frame, rows, color, scale=1.0):
    for r, line in enumerate(rows):
        dest = ICON_Y + 3 + int((r - 3) * scale)
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(ICON_X + c, dest, color)


def build():
    anim = Animation(delay=DELAY)
    assert TEXT_X + Canvas.text_width(NEW, proportional=True) <= anim.width
    flip_mid = (OUT_START + IN_START) // 2
    for index in range(FRAMES):
        frame = anim.frame()
        draw_word(frame, OLD, OUT_START, OUT_EVERY, index, C.MAGENTA, "out")
        draw_word(frame, NEW, IN_START, IN_EVERY, index, C.YELLOW, "in")

        if index < flip_mid - 2:
            icon(frame, DONUT, C.MAGENTA)
        elif index < flip_mid:
            icon(frame, DONUT, C.MAGENTA, 0.4)
        elif index < flip_mid + 2:
            icon(frame, WAFFLE, C.YELLOW, 0.4)
        else:
            icon(frame, WAFFLE, C.YELLOW)

        if index >= SHINE_AT:
            head = TEXT_X - 3 + (index - SHINE_AT) * 14
            for x, y in list(frame.lit()):
                if abs(x - head) <= 2 and x >= TEXT_X:
                    frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/team_name.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
