#!/usr/bin/env python3
"""
Execute Order 66 (2005).

A row of clone helmets stands white and dutiful while the order types out.
Then the transmission goes down the line: a cyan pulse sweeps left to right
and every helmet it touches turns, visor going red, one after another. The
answer comes back from all of them at once -- IT WILL BE DONE, MY LORD.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
ORDER_AT = 2
PULSE_AT = 18
PULSE_EVERY = 2         # frames per helmet turned
REPLY_AT = 40
HELMETS = 10
HELMET_X0, HELMET_STEP, HELMET_Y = 4, 9, 10

HELMET = [
    ".###.",
    "#####",
    "#...#",
    "#####",
    ".#.#.",
]


def helmet(frame, x, turned, flash):
    for row, line in enumerate(HELMET):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, HELMET_Y + row, C.WHITE)
    # The shell stays white -- it is the visor that tells you. Dark while
    # they are still your men, red once the order has landed.
    visor = C.WHITE if flash else (C.RED if turned else C.BLACK)
    frame.hline(x + 1, HELMET_Y + 2, 3, visor)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        turned_count = 0
        if index >= PULSE_AT:
            turned_count = min(HELMETS, (index - PULSE_AT) // PULSE_EVERY + 1)

        for i in range(HELMETS):
            x = HELMET_X0 + i * HELMET_STEP
            reply_flash = index >= REPLY_AT and index % 4 < 2
            helmet(frame, x, i < turned_count,
                   flash=reply_flash or i == turned_count - 1)

        # The transmission itself, a column running ahead of the turning.
        if PULSE_AT <= index < PULSE_AT + HELMETS * PULSE_EVERY:
            edge = HELMET_X0 + turned_count * HELMET_STEP
            frame.vline(edge, 8, 8, C.CYAN)
            frame.vline(edge + 1, 9, 6, C.BLUE)

        if index >= REPLY_AT:
            shown = "IT WILL BE DONE"[: max(1, (index - REPLY_AT) * 3)]
            frame.text(shown, "center", 0, C.RED if index % 4 < 2 else C.YELLOW,
                       proportional=True)
        elif index >= ORDER_AT:
            typed = "EXECUTE ORDER 66"[: max(1, (index - ORDER_AT) * 2)]
            frame.text(typed, "center", 0, C.WHITE, proportional=True)
            if len(typed) == 16 and index % 4 < 2:
                frame.text("EXECUTE ORDER 66", "center", 0, C.RED, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/order_66.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
