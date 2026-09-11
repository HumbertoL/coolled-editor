#!/usr/bin/env python3
"""
The duel -- Hamilton.

The count to ten runs on the left, big digit and the number's name, while
the two duellists stand facing each other on the right. On ten: TEN PACES,
FIRE, and one of them shoots -- a single pixel crosses the gap, the other
flashes and falls. Then it holds on the tableau.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, font  # noqa: E402

FRAMES = 53
DELAY = 130
NAMES = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"]
COUNT_EVERY = 3
DUEL_AT = 30
FIRE_AT = 36
BULLET_FRAMES = 5
LEFT_X, RIGHT_X, FIG_Y = 62, 88, 9
DUELLIST = [
    ".#.",
    "###",
    ".#.",
    ".#.",
    "#.#",
]


def text2x(frame, text, x, y, color):
    for i, ch in enumerate(text):
        bitmap = font.glyph(ch)
        for r in range(font.GLYPH_HEIGHT):
            for c in range(font.GLYPH_WIDTH):
                if bitmap[r][c] == "#":
                    frame.rect(x + i * 12 + c * 2, y + r * 2, 2, 2, color, fill=True)


def figure(frame, x, y, color, facing):
    for r, line in enumerate(DUELLIST):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r, color)
    frame.pixel(x + 1 + 2 * facing, y + 1, color)
    frame.pixel(x + 1 + 3 * facing, y + 1, color)


def fallen(frame, x, y, color):
    frame.hline(x - 3, y + 4, 5, color)
    frame.pixel(x - 4, y + 3, color)


def build():
    anim = Animation(delay=DELAY)
    hit_at = FIRE_AT + BULLET_FRAMES
    for index in range(FRAMES):
        frame = anim.frame()
        if index < DUEL_AT:
            n = min(10, index // COUNT_EVERY + 1)
            text2x(frame, str(n), 4 if n < 10 else 2, 1, C.YELLOW if index % COUNT_EVERY else C.WHITE)
            frame.text(NAMES[n - 1], 28, 4, C.WHITE, proportional=True)
        else:
            flash = FIRE_AT <= index < hit_at and index % 2
            frame.text("TEN PACES", 2, 0, C.WHITE, proportional=True)
            if index >= FIRE_AT:
                frame.text("FIRE", 2, 9, C.RED if flash else C.WHITE, proportional=True)

        figure(frame, LEFT_X, FIG_Y, C.CYAN, 1)
        if index < hit_at:
            figure(frame, RIGHT_X, FIG_Y, C.YELLOW, -1)
        elif index < hit_at + 2:
            figure(frame, RIGHT_X, FIG_Y, C.RED if index % 2 == 0 else C.WHITE, -1)
        else:
            fallen(frame, RIGHT_X, FIG_Y, C.YELLOW)

        if FIRE_AT <= index < hit_at:
            k = index - FIRE_AT
            bx = LEFT_X + 5 + round((RIGHT_X - LEFT_X - 6) * (k + 1) / BULLET_FRAMES)
            frame.pixel(bx, FIG_Y + 1, C.WHITE)
            if k == 0:
                frame.pixel(LEFT_X + 5, FIG_Y, C.YELLOW)
                frame.pixel(LEFT_X + 5, FIG_Y + 2, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hamilton_duel.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
