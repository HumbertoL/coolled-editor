#!/usr/bin/env python3
"""
Binary clock -- the time as BCD, one digit a column, one bit a square.

Each decimal digit is a column of four squares, weight 8 at the top to 1 at
the bottom. A lit square is CYAN, an unlit one a dim BLUE. The clock runs from
10:59:00 one second a frame, so the seconds digits show the count in binary
and the tens digit of the seconds changes at 10:59:10, 10:59:20 and so on.
The colon pairs blink on the even seconds. Each frame is a second, so the
delay is 1000 ms and the loop is 53 real seconds.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 1000
SQUARE = 3
PITCH = 4
COLUMN_GAP = 9
PAIR_GAP = 6
TOP = 0
LEFT = 0


def column_x(digit_index):
    """Left edge of each digit column, with a wider gap between the pairs."""
    pairs = digit_index // 2
    return LEFT + digit_index * COLUMN_GAP + pairs * PAIR_GAP


def digits_for(seconds):
    return [1, 0, 5, 9, seconds // 10, seconds % 10]


def draw_digit(frame, digit, x):
    for bit in range(4):
        weight = 8 >> bit
        y = TOP + bit * PITCH
        lit = digit & weight
        frame.rect(x, y, SQUARE, SQUARE, C.CYAN if lit else C.BLUE, fill=True)


def build():
    total_width = column_x(5) + SQUARE
    offset = (96 - total_width) // 2
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for digit_index, digit in enumerate(digits_for(index)):
            draw_digit(frame, digit, offset + column_x(digit_index))
        if index % 2 == 0:
            for gap in (1, 3):
                x = offset + column_x(gap * 2 - 1) + SQUARE + (PAIR_GAP // 2)
                frame.pixel(x, 5, C.WHITE)
                frame.pixel(x, 10, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/binary_clock.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
