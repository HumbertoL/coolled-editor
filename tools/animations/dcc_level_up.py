#!/usr/bin/env python3
"""
Level up -- Dungeon Crawler Carl.

The experience bar fills red under a big level number, tops out, and the
number rolls over -- old digits scrolling up out of the way, new ones sliding
in from below -- while LEVEL UP! flashes and sparks fly. Then the bar empties
back to a sliver and the loop waits to do it again.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, font  # noqa: E402

FRAMES = 53
DELAY = 100

OLD, NEW = "27", "28"
FILL_END, ROLL_END, SHOW_END = 20, 27, 46
NUM_X, NUM_Y = 6, 1
BAR_X, BAR_Y, BAR_W = 34, 12, 56


def text2x(frame, text, x, y, color, clip_top=0, clip_bottom=16):
    for i, ch in enumerate(text):
        bitmap = font.glyph(ch)
        for row in range(font.GLYPH_HEIGHT):
            for col in range(font.GLYPH_WIDTH):
                if bitmap[row][col] != "#":
                    continue
                for dy in range(2):
                    py = y + row * 2 + dy
                    if clip_top <= py < clip_bottom:
                        frame.hline(x + i * 12 + col * 2, py, 2, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index < FILL_END:
            fill = 0.3 + 0.7 * (index + 1) / FILL_END
            text2x(frame, OLD, NUM_X, NUM_Y, C.YELLOW)
            frame.text("LEVEL", BAR_X, 3, C.RED, proportional=True)
        elif index < ROLL_END:
            fill = 1.0
            shift = round(16 * (index - FILL_END + 1) / (ROLL_END - FILL_END))
            text2x(frame, OLD, NUM_X, NUM_Y - shift, C.YELLOW, clip_top=0, clip_bottom=15)
            text2x(frame, NEW, NUM_X, NUM_Y + 16 - shift, C.WHITE, clip_top=0, clip_bottom=15)
            frame.text("LEVEL UP!", BAR_X, 3, C.WHITE if index % 2 else C.YELLOW, proportional=True)
        elif index < SHOW_END:
            fill = 1.0 if index < ROLL_END + 4 else max(0.05, 1.0 - (index - ROLL_END - 4) / 10)
            text2x(frame, NEW, NUM_X, NUM_Y, C.YELLOW if index % 8 < 6 else C.WHITE)
            frame.text("LEVEL UP!", BAR_X, 3, C.YELLOW, proportional=True)
            k = index - ROLL_END
            if k < 8:
                for sx, sy in ((2, 2), (30, 1), (31, 13), (3, 14)):
                    frame.pixel(sx + (k % 3), sy, C.WHITE if k % 2 else C.RED)
        else:
            fill = 0.05
            text2x(frame, NEW, NUM_X, NUM_Y, C.YELLOW)
            frame.text("LEVEL", BAR_X, 3, C.RED, proportional=True)

        frame.rect(BAR_X, BAR_Y, BAR_W, 3, C.RED)
        frame.rect(BAR_X + 1, BAR_Y + 1, round((BAR_W - 2) * fill), 1,
                   C.WHITE if fill >= 1.0 else C.YELLOW, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_level_up.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
