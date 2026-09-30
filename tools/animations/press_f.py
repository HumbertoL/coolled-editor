#!/usr/bin/env python3
"""
Press F to Pay Respects (2014) -- a tombstone, a flag and one very large key.

A small gravestone stands under a rippling red flag while PRESS F TO PAY
RESPECTS sits in the middle. Then the F key on the right starts getting
hammered: it dips and flashes on every press, tiny blue Fs drift up from it,
and a RESPECTS counter climbs faster and faster until the loop resets.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100
SEED = 2014
PRESS_AT = [16, 19, 22, 24, 26, 28, 29, 31, 32, 34, 35, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46]
CROSS = ["..#..", "#####", "..#..", "..#..", "..#.."]
STONE = [
    "..#####..",
    ".#######.",
    "#########",
] + ["#########"] * 8


def stone(f, x, y):
    for r, line in enumerate(STONE):
        for c, ch in enumerate(line):
            if ch == "#":
                f.pixel(x + c, y + r, C.CYAN if c in (0, 8) else C.WHITE)
    for r, line in enumerate(CROSS):
        for c, ch in enumerate(line):
            if ch == "#":
                f.pixel(x + 2 + c, y + 2 + r, C.BLUE)
    f.hline(0, 15, 20, C.GREEN)
    f.hline(x - 1, 14, 11, C.GREEN)


def flag(f, i):
    f.vline(13, 4, 11, C.WHITE)
    for c in range(5):
        wave = round(1.2 * ((c + i / 2) % 4 > 2))
        f.vline(14 + c, 4 + wave, 3, C.RED)


def key(f, pressed):
    dy = 1 if pressed else 0
    body = C.CYAN if pressed else C.BLUE
    f.rect(81, 1 + dy, 14, 13 - dy, C.WHITE, fill=False)
    f.rect(82, 2 + dy, 12, 11 - dy, body, fill=True)
    f.text("F", 85, 4 + dy, C.YELLOW if pressed else C.WHITE)
    if not pressed:
        f.hline(82, 14, 13, C.BLUE)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    floaters = []  # [x, y, speed]
    count = 0
    step = 1
    for i in range(FRAMES):
        f = anim.frame()
        pressed = i in PRESS_AT
        if pressed:
            count = min(99, count + step)
            step += 1 if len(PRESS_AT) and i > 30 else 0
            floaters.append([rng.randint(60, 90), 12, 1 + rng.random()])
        for fl in floaters:
            fl[1] -= fl[2]
        floaters = [fl for fl in floaters if fl[1] > -6]
        for fl in floaters:
            f.small_text("F", int(fl[0]), int(fl[1]), C.BLUE)
        stone(f, 2, 4)
        flag(f, i)
        f.text("PRESS F", 22, 1, C.WHITE)
        if i < 15:
            f.small_text("TO PAY RESPECTS", 22, 10, C.WHITE)
        else:
            f.small_text("RESPECTS:", 22, 10, C.WHITE)
            f.small_text(str(count), 62, 10, C.YELLOW if pressed else C.GREEN)
        key(f, pressed)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/press_f.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
