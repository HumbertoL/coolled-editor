#!/usr/bin/env python3
"""
Zelda dangerous -- it's dangerous to go alone! Take this.

In a dark cave an old man in a red robe stands between two flickering fires
with a sword laid at his feet. His line types out a letter at a time, the
way the very first game's did: IT'S DANGEROUS / TO GO ALONE!, then TAKE
THIS.
The text clears, the hero walks in from the right, the sword vanishes from
the floor and he holds it up over his head in a twinkle.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import HERO, HERO_ARMS_UP, HERO_STEP, sparkle, stamp  # noqa: E402

FRAMES = 53
DELAY = 110
TEXT_X = 38
PAGES = (("IT'S DANGEROUS", "TO GO ALONE!"), ("TAKE THIS.",))
PAGE_AT = (0, 25)
CHARS_PER_FRAME = 1.25
CLEAR_AT = 38
STOP_X = 36
POSE_AT = 47

FIRE = [
    [
        "...R...",
        "..RR...",
        "..RYR..",
        ".RYYR..",
        ".RYWYR.",
        "RYYWYRR",
        "RYWWWYR",
        ".RRRRR.",
    ],
    [
        "....R..",
        "...RR..",
        "..RYR..",
        "..RYYR.",
        ".RYWYR.",
        "RRYWYYR",
        "RYWWWYR",
        ".RRRRR.",
    ],
]
OLD_MAN = [
    "...YYY...",
    "..YYYYY..",
    "..YKYKY..",
    "..WWWWW..",
    ".RWWWWWR.",
    "RRRWWWRRR",
    "RYRRWRRYR",
    ".RRRRRRR.",
    ".RRRRRRR.",
    ".RRRRRRR.",
    "RRRRRRRRR",
    "RRRRRRRRR",
]
SWORD = [
    ".B.......",
    "BBYCWWWWW",
    ".B.......",
]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        stamp(frame, FIRE[index % 2], 1, 4)
        stamp(frame, FIRE[(index + 1) % 2], 26, 4)
        stamp(frame, OLD_MAN, 13, 0)
        if index < POSE_AT:
            stamp(frame, SWORD, 13, 13)

        if index < CLEAR_AT:
            page = 1 if index >= PAGE_AT[1] else 0
            lines = PAGES[page]
            budget = int((index - PAGE_AT[page]) * CHARS_PER_FRAME)
            tops = (2, 9) if len(lines) == 2 else (6,)
            for line, top in zip(lines, tops):
                frame.small_text(line[:max(0, budget)], TEXT_X, top, C.WHITE)
                budget -= len(line)
        elif index < POSE_AT:
            hx = max(STOP_X, 96 - (index - CLEAR_AT + 1) * 7)
            stamp(frame, HERO_STEP if index % 2 else HERO, hx, 3, flip=True)
        else:
            stamp(frame, HERO_ARMS_UP, STOP_X, 3)
            stamp(frame, SWORD, STOP_X, 0)
            phase = index - POSE_AT
            sparkle(frame, STOP_X + 11, 1, min(3, phase + 1), C.WHITE)
            if phase >= 2:
                frame.small_text("GOT IT!", 52, 6, C.YELLOW if index % 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_dangerous.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
