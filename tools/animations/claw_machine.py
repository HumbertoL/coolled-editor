#!/usr/bin/env python3
"""
Claw machine -- so close.

The claw trundles along its rail, stops over the magenta prize, drops,
closes and lifts it clear. Halfway back to the chute the grip gives out and
the prize falls into the one gap in the pile. The claw finishes the trip
anyway, opens over the chute, and delivers nothing while SO CLOSE! blinks.
The loop puts the prize back where it started.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
CHUTE_X = 5
TARGET_X = 58
GAP_X = 34
PRIZE_Y = 11
UP, DOWN = 3, PRIZE_Y - 2

PRIZE = [".###.", "#.#.#", "#####", ".###."]
PILE = [
    (16, C.CYAN), (22, C.YELLOW), (28, C.GREEN), (40, C.RED), (46, C.CYAN),
    (52, C.YELLOW), (64, C.GREEN), (70, C.RED), (76, C.YELLOW), (82, C.CYAN), (88, C.RED),
]
OPEN = [".###.", "#...#", "#...#"]
SHUT = [".###.", ".#.#.", "#...#"]


def stamp(frame, rows, centre_x, top, colour):
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(centre_x - 2 + col, top + row, colour)


def script(index):
    """(claw x, claw top, closed?, prize position or None for 'in the pile')."""
    if index < 4:
        return CHUTE_X, UP, False, None
    if index < 17:  # out along the rail
        x = min(TARGET_X, CHUTE_X + round((TARGET_X - CHUTE_X) * (index - 3) / 13))
        return x, UP, False, None
    if index < 23:  # down
        return TARGET_X, min(DOWN, UP + (index - 16)), False, None
    if index < 25:  # grab
        return TARGET_X, DOWN, True, None
    if index < 31:  # up
        top = max(UP, DOWN - (index - 24))
        return TARGET_X, top, True, (TARGET_X, top + 2)
    if index < 37:  # back toward the chute, carrying
        x = TARGET_X - 4 * (index - 30)
        return x, UP, True, (x, UP + 2)
    # The slip: the claw carries on, the prize falls where it was let go.
    x = max(CHUTE_X, TARGET_X - 4 * (index - 30))
    fall = index - 36
    return x, UP, index < 46, (GAP_X, min(PRIZE_Y, UP + 2 + fall * fall))


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        x, top, shut, carried = script(index)

        frame.hline(0, 0, 96, C.WHITE)
        frame.hline(0, 15, 96, C.BLUE)
        # The chute: a walled-off corner with a yellow lip.
        frame.vline(11, 9, 6, C.BLUE)
        frame.hline(0, 9, 2, C.YELLOW)
        frame.hline(10, 9, 2, C.YELLOW)

        for pile_x, colour in PILE:
            stamp(frame, PRIZE, pile_x, PRIZE_Y, colour)
        if carried is None:
            stamp(frame, PRIZE, TARGET_X, PRIZE_Y, C.MAGENTA)
        else:
            stamp(frame, PRIZE, carried[0], carried[1], C.MAGENTA)

        frame.rect(x - 2, 1, 5, 2, C.WHITE, fill=True)
        frame.vline(x, 3, top - 3, C.BLUE)
        stamp(frame, SHUT if shut else OPEN, x, top, C.WHITE)

        if index >= 44 and index % 2 == 0:
            frame.small_text("SO CLOSE!", 52, 3, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/claw_machine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
