#!/usr/bin/env python3
"""
Kaprekar's constant -- every four-digit number falls into 6174.

Take a four-digit number whose digits are not all the same. Sort the digits
descending, sort them ascending, subtract. Repeat. Within seven steps you
reach 6174, and 6174 maps to itself: 7641 - 1467 = 6174.

This starts from 3524 and shows each subtraction being written out: the
descending arrangement in yellow, the ascending in cyan, the difference
typed a digit at a time. It takes three steps to arrive, then a fourth shows
the fixed point. The arithmetic is computed, not typed in, and build()
asserts the chain ends where it should.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 170
START = 3524
CONSTANT = 6174
STEP_FRAMES = 12
TEXT_Y = 8


def kaprekar_step(number):
    digits = sorted(f"{number:04d}")
    low = "".join(digits)
    high = "".join(reversed(digits))
    return high, low, int(high) - int(low)


def chain():
    steps, number = [], START
    while True:
        high, low, result = kaprekar_step(number)
        steps.append((number, high, low, result))
        if number == CONSTANT:
            return steps
        number = result


def build():
    steps = chain()
    assert len(steps) == 4 and steps[-1][3] == CONSTANT
    anim = Animation(delay=DELAY)
    for count, (number, high, low, result) in enumerate(steps, start=1):
        answer = f"{result:04d}"
        arrived = result == CONSTANT
        for k in range(STEP_FRAMES):
            frame = anim.frame()
            frame.small_text(f"STEP {count}", 2, 0, C.MAGENTA)
            frame.small_text(f"{number:04d}", 79, 0, C.BLUE)
            frame.hline(0, 6, 96, C.BLUE)
            frame.text(high, 2, TEXT_Y, C.YELLOW)
            if k >= 1:
                frame.text("-", 27, TEXT_Y, C.WHITE)
            if k >= 2:
                frame.text(low, 35, TEXT_Y, C.CYAN)
            if k >= 3:
                frame.text("=", 60, TEXT_Y, C.WHITE)
            shown = min(4, k - 3)
            if shown > 0:
                colour = C.WHITE
                if arrived and shown == 4:
                    colour = C.GREEN if k % 2 == 0 else C.WHITE
                frame.text(answer[:shown], 68, TEXT_Y, colour)
    for k in range(5):
        frame = anim.frame()
        frame.small_text("ALWAYS", "center", 0, C.MAGENTA)
        frame.hline(0, 6, 96, C.BLUE)
        frame.text(str(CONSTANT), "center", TEXT_Y, C.GREEN if k % 2 == 0 else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/kaprekar.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
