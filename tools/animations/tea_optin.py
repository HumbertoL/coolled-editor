#!/usr/bin/env python3
"""
tea_optin -- a keyword opt-in landing.

The Text-Em-All subscribe flow as a loop: a phone on the left, a green bubble
sliding out of it carrying the keyword JOIN, a check that draws itself once
the message lands, and a subscriber count on the right that ticks up and
flashes for each new opt-in. Two opt-ins per loop, so the counter visibly
climbs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

BUBBLE_X, BUBBLE_Y = 15, 2
COUNT_X, COUNT_Y = 66, 4
BASE_COUNT = 1047

#: (cycle start, frame the counter ticks). Two opt-ins per loop.
CYCLES = [(0, 18), (26, 44)]


def draw_phone(frame, ringing):
    frame.rect(2, 1, 10, 14, C.WHITE)
    frame.hline(5, 2, 4, C.BLUE)
    frame.pixel(6, 13, C.WHITE)
    frame.pixel(7, 13, C.WHITE)
    if ringing:
        frame.pixel(10, 3, C.GREEN)


def draw_bubble(frame, offset):
    x = BUBBLE_X + offset
    frame.rect(x, BUBBLE_Y, 28, 11, C.GREEN)
    frame.pixel(x, BUBBLE_Y + 11, C.GREEN)  # tail toward the phone
    frame.pixel(x - 1, BUBBLE_Y + 12, C.GREEN)
    frame.text("JOIN", x + 3, BUBBLE_Y + 2, C.WHITE)


def draw_check(frame, progress):
    """The tick, drawn in two strokes as ``progress`` goes 0 -> 1."""
    down = [(48, 8), (49, 9), (50, 10), (51, 11)]
    up = [(52, 10), (53, 9), (54, 8), (55, 7), (56, 6), (57, 5)]
    points = down + up
    shown = round(progress * len(points))
    for x, y in points[:shown]:
        frame.pixel(x, y, C.GREEN)
        frame.pixel(x, y - 1, C.GREEN)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()

        count = BASE_COUNT + sum(1 for _start, tick in CYCLES if index >= tick)
        ticked = any(0 <= index - tick < 3 for _start, tick in CYCLES)
        cycle_pos = None
        for start, _tick in CYCLES:
            if index >= start:
                cycle_pos = index - start

        draw_phone(frame, ringing=cycle_pos is not None and cycle_pos < 8 and index % 2 == 0)

        if cycle_pos is not None:
            # Bubble slides out of the phone over 8 frames, then holds.
            offset = min(0, -28 + cycle_pos * 4)
            draw_bubble(frame, offset)
            if cycle_pos >= 8:
                draw_check(frame, (cycle_pos - 8) / 6)

        frame.text(str(count), COUNT_X, COUNT_Y, C.WHITE if ticked else C.CYAN)
        frame.hline(COUNT_X, COUNT_Y + 9, 23, C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_optin.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
