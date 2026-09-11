#!/usr/bin/env python3
"""
The duel -- Hamilton.

The count to ten, big digits on the left with the number's name beside it.
On ten, two silhouettes stand facing each other. A white flash. One of them
raises his pistol to the sky instead, and the other line from the finale
follows: THE WORLD WAS WIDE ENOUGH.
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
FLASH_AT = 38
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


def figure(frame, x, y, color, pistol_dx, pistol_up=False):
    for r, line in enumerate(DUELLIST):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r, color)
    if pistol_up:
        frame.pixel(x + 1 + pistol_dx, y - 1, color)
        frame.pixel(x + 1 + pistol_dx, y - 2, color)
    else:
        frame.pixel(x + 1 + 2 * pistol_dx, y + 1, color)
        frame.pixel(x + 1 + 3 * pistol_dx, y + 1, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < DUEL_AT:
            n = min(10, index // COUNT_EVERY + 1)
            text2x(frame, str(n), 4 if n < 10 else 2, 1, C.YELLOW if index % COUNT_EVERY else C.WHITE)
            frame.text(NAMES[n - 1], 34, 4, C.WHITE, proportional=True)
            continue
        if index == FLASH_AT:
            frame.fill(C.WHITE)
            continue
        after = index > FLASH_AT
        figure(frame, 20, 9, C.CYAN, 1, pistol_up=after)
        figure(frame, 72, 9, C.YELLOW, -1)
        if after:
            k = index - FLASH_AT
            frame.text("THE WORLD WAS", "center", 0, C.WHITE, proportional=True)
            if k >= 3:
                frame.text("WIDE ENOUGH", 30, 9, C.WHITE, proportional=True)
        else:
            frame.text("TEN PACES", "center", 0, C.RED if index % 2 else C.WHITE, proportional=True)
            frame.text("FIRE", 40, 9, C.RED if index % 2 else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hamilton_duel.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
