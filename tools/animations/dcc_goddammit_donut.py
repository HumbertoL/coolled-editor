#!/usr/bin/env python3
"""
Goddammit, Donut -- Dungeon Crawler Carl.

Carl's most-used line, typed out one letter at a time in yellow, with the
cat herself sitting at the right end of the panel looking entirely
unbothered: slow blink, ear flick, tail swish. The exclamation mark lands
last and flashes red.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

CAT = [
    "#.....#",
    "##...##",
    "#######",
    "#.#.#.#",
    "#######",
    ".##.##.",
    "..###..",
]
CAT_X, CAT_Y = 84, 3
EYES = [(2, 3), (4, 3)]
TOP, BOTTOM = "GODDAMMIT,", "DONUT!"
TYPE_EVERY = 2
TYPE_START = 4


def build():
    anim = Animation(delay=DELAY)
    letters = TOP + BOTTOM
    for index in range(FRAMES):
        frame = anim.frame()
        typed = min(len(letters), max(0, (index - TYPE_START) // TYPE_EVERY + 1))
        done = typed >= len(letters)
        cursor_on = index % 2 == 0 and not done

        top_shown = TOP[:typed]
        bottom_shown = BOTTOM[:max(0, typed - len(TOP))]
        frame.text(top_shown, 4, 0, C.YELLOW, proportional=True)
        if bottom_shown:
            color = C.YELLOW
            if done and bottom_shown.endswith("!"):
                frame.text(bottom_shown[:-1], 4, 9, C.YELLOW, proportional=True)
                bang_x = 4 + frame.text_width(bottom_shown[:-1], proportional=True) + 1
                frame.text("!", bang_x - 2, 9, C.RED if index % 4 < 2 else C.WHITE, proportional=True)
            else:
                frame.text(bottom_shown, 4, 9, color, proportional=True)
        if cursor_on:
            if typed < len(TOP):
                x = 4 + frame.text_width(top_shown, proportional=True) + (1 if top_shown else 0)
                frame.vline(x, 0, 7, C.RED)
            else:
                x = 4 + frame.text_width(bottom_shown, proportional=True) + (1 if bottom_shown else 0)
                frame.vline(x, 9, 7, C.RED)

        # Donut: ear flick early, slow blink late, tail swishing throughout.
        ear_flick = 8 <= index < 11
        blink = 30 <= index < 33
        for r, line in enumerate(CAT):
            for c, ch in enumerate(line):
                if ch == "#":
                    if ear_flick and (c, r) == (6, 0):
                        continue
                    frame.pixel(CAT_X + c, CAT_Y + r, C.WHITE)
        if ear_flick:
            frame.pixel(CAT_X + 7, CAT_Y + 1, C.WHITE)
        for c, r in EYES:
            frame.pixel(CAT_X + c, CAT_Y + r, C.WHITE if blink else C.YELLOW)
        tail = (index // 6) % 2
        frame.pixel(CAT_X - 2 + tail, CAT_Y + 8, C.WHITE)
        frame.pixel(CAT_X - 1 + tail, CAT_Y + 7, C.WHITE)
        frame.hline(CAT_X - 1, CAT_Y + 9, 9, C.WHITE)      # she is sitting on something
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_goddammit_donut.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
