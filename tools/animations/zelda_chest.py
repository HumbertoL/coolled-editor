#!/usr/bin/env python3
"""
Zelda chest -- you got a small key!

The hero walks up to a red, gold-banded treasure chest and stops. A line of
light leaks from under the lid, the chest gives a shiver, and the lid swings
up as rays fan out of it. A small gold key rises out of the glow; the hero
turns to face us and holds it up over his head, both hands, while YOU GOT A /
SMALL KEY! types out beside him and the key twinkles.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import HERO, HERO_ARMS_UP, HERO_STEP, sparkle, stamp  # noqa: E402

FRAMES = 53
DELAY = 110
CHEST_X, CHEST_Y = 30, 7
HERO_STOP = 19
WALK_END = 11
CRACK_AT, OPEN_AT, RISE_AT, POSE_AT = 13, 18, 23, 30
TYPE_AT = 32

LID = [
    ".RRRRRRRRRRRR.",
    "RYRRRRRRRRRRYR",
    "RYRRRRRRRRRRYR",
    "YYYYYYYYYYYYYY",
]
BASE = [
    "RYRRRRYYRRRRYR",
    "RYRRRRKKRRRRYR",
    "RYRRRRRRRRRRYR",
    "RYRRRRRRRRRRYR",
    "YYYYYYYYYYYYYY",
]
OPEN_LID = [
    "RRRRRRRRRRRRRR",
    "YYYYYYYYYYYYYY",
]
KEY = [
    "YYY....",
    "Y.YYYYY",
    "YYY..Y.",
]
LINES = ("YOU GOT A", "SMALL KEY!")


def rays(frame, index):
    cx, cy = CHEST_X + 7, CHEST_Y + 3
    for k, angle in enumerate((-50, -20, 20, 50)):
        a = math.radians(angle)
        for r in range(3, 10):
            if (r + index) % 3 == 0:
                continue
            x = round(cx + math.sin(a) * r * 1.3)
            y = round(cy - math.cos(a) * r)
            if y < CHEST_Y - 2 or not 0 <= x - CHEST_X < 14:
                frame.pixel(x, y, C.WHITE if (r + index + k) % 3 == 1 else C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        is_open = index >= OPEN_AT

        if is_open:
            rays(frame, index)
            stamp(frame, OPEN_LID, CHEST_X, CHEST_Y - 2)
            # The open box: its sides, and the glow inside.
            for y in range(CHEST_Y, CHEST_Y + 4):
                frame.pixel(CHEST_X, y, C.RED)
                frame.pixel(CHEST_X + 13, y, C.RED)
            frame.hline(CHEST_X + 1, CHEST_Y + 2, 12, C.YELLOW if index % 2 else C.WHITE)
            frame.hline(CHEST_X + 1, CHEST_Y + 3, 12, C.WHITE)
        else:
            shiver = (index % 2) if CRACK_AT + 2 <= index < OPEN_AT else 0
            stamp(frame, LID, CHEST_X, CHEST_Y - shiver)
            if index >= CRACK_AT:
                frame.hline(CHEST_X + 1, CHEST_Y + 4 - shiver, 12, C.WHITE)
        stamp(frame, BASE, CHEST_X, CHEST_Y + 4)

        if index < POSE_AT:
            hx = min(HERO_STOP, -8 + index * 3)
            walking = index < WALK_END
            stamp(frame, HERO_STEP if walking and index % 2 else HERO, hx, 3)
        else:
            stamp(frame, HERO_ARMS_UP, HERO_STOP, 3)

        if RISE_AT <= index < POSE_AT:
            ky = max(0, CHEST_Y + 2 - (index - RISE_AT) * 2)
            stamp(frame, KEY, CHEST_X + 4, ky)
        elif index >= POSE_AT:
            stamp(frame, KEY, HERO_STOP, 0)
            phase = (index - POSE_AT) % 6
            if phase < 3:
                sparkle(frame, HERO_STOP + 9, 1, phase + 1, C.WHITE)

        if index >= TYPE_AT:
            typed = (index - TYPE_AT) * 2
            first, second = LINES
            frame.small_text(first[:typed], 50, 2, C.WHITE)
            frame.small_text(second[:max(0, typed - len(first))], 50, 9, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_chest.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
