#!/usr/bin/env python3
"""
Zelda hearts -- the life meter, from full to one and back.

Under a red -LIFE- label, eight hearts take five hits, each one flashing the
meter white and knocking off a heart or two in halves, until one is left and
blinks its warning. A heart container drops in from the top right, bounces,
and is collected in a sparkle: a ninth slot opens and the meter refills half a
heart at a time, left to right, before a shine runs along the row.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import HEART, heart, sparkle, stamp  # noqa: E402

FRAMES = 53
DELAY = 110
HEART_Y = 8
START_HEARTS = 8
HITS = {4: 2, 8: 3, 12: 2, 16: 4, 20: 3}   # frame -> halves lost
DROP_AT, LAND_AT, GRAB_AT = 27, 34, 38
REFILL_AT = 40
CONTAINER_X = 84

# A heart container: bigger, white-rimmed.
CONTAINER = [
    ".WW.WW.",
    "WRRWRRW",
    "WRRRRRW",
    ".WRRRW.",
    "..WRW..",
    "...W...",
]


def heart_x(slot):
    return 2 + slot * 8


def build():
    anim = Animation(delay=DELAY)
    halves = START_HEARTS * 2
    for index in range(FRAMES):
        frame = anim.frame()
        if index in HITS:
            halves -= HITS[index]
        slots = START_HEARTS + (1 if index >= GRAB_AT else 0)
        if index >= REFILL_AT:
            halves = min(slots * 2, 2 + 2 * (index - REFILL_AT + 1))

        frame.small_text("-LIFE-", 2, 1, C.RED)

        hit = any(0 <= index - h < 2 for h in HITS)
        low = halves <= 2 and index < GRAB_AT
        for slot in range(slots):
            fill = max(0, min(2, halves - slot * 2))
            if hit:
                heart(frame, heart_x(slot), HEART_Y, fill, empty=C.BLUE, full=C.WHITE)
            elif low and fill and index % 2:
                heart(frame, heart_x(slot), HEART_Y, 0, empty=C.MAGENTA)
            else:
                heart(frame, heart_x(slot), HEART_Y, fill)

        if hit:
            frame.small_text("OW!", 62, 1, C.YELLOW)
        if low and index % 4 < 2:
            frame.small_text("LOW!", 30, 1, C.MAGENTA)

        # The container falls, bounces once and is taken.
        if DROP_AT <= index < GRAB_AT:
            t = index - DROP_AT
            if index < LAND_AT:
                y = -6 + round(14 * (t / (LAND_AT - DROP_AT)) ** 2)
            else:
                y = HEART_Y - [0, 2, 3, 2, 0][min(4, index - LAND_AT)]
            stamp(frame, CONTAINER, CONTAINER_X, y)
            if index % 2 == 0:
                frame.pixel(CONTAINER_X - 2, y + 1, C.WHITE)
        if GRAB_AT <= index < GRAB_AT + 4:
            size = index - GRAB_AT + 1
            sparkle(frame, CONTAINER_X + 3, HEART_Y + 2, size)
            sparkle(frame, heart_x(8) + 3, HEART_Y + 2, 4 - size, C.YELLOW)
        if index >= GRAB_AT + 1 and index < REFILL_AT + 10:
            frame.small_text("+1 HEART", 52, 1, C.WHITE if index % 2 else C.YELLOW)

        # A diagonal glint along the full meter.
        full_at = REFILL_AT + 8
        if index > full_at:
            head = (index - full_at) * 20 - 6
            for x in range(head, head + 3):
                for y in range(HEART_Y, HEART_Y + len(HEART)):
                    gx = x + (y - HEART_Y) // 2
                    if frame.get(gx, y) == C.RED:
                        frame.pixel(gx, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_hearts.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
