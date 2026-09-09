#!/usr/bin/env python3
"""
Invaders -- a row of the 1978 crab, marching.

Five invaders step right and back, legs alternating every frame, so the
travel is seamless. Below them a cannon fires once per loop: the shot climbs
in three-pixel steps, the middle invader bursts into the classic starburst for
two frames and is gone until the loop brings the wave back.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 110

CRAB = [
    [
        "..#.....#..",
        "...#...#...",
        "..#######..",
        ".##.###.##.",
        "###########",
        "#.#######.#",
        "#.#.....#.#",
        "...##.##...",
    ],
    [
        "..#.....#..",
        "#..#...#..#",
        "#.#######.#",
        "###.###.###",
        "###########",
        ".#########.",
        "..#.....#..",
        ".#.......#.",
    ],
]
BURST = [
    "#..#..#",
    ".#.#.#.",
    "..#.#..",
    "##...##",
    "..#.#..",
    ".#.#.#.",
    "#..#..#",
]
CANNON = [
    "....#....",
    "...###...",
    ".#######.",
    "#########",
]

COUNT, PITCH, TOP = 5, 15, 1
TARGET = 2
FIRE_FRAME = 3
HIT_FRAME = 6
CANNON_X = 43


def blit(frame, sprite, x, y, color):
    for row, line in enumerate(sprite):
        for col, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + col, y + row, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        offset = 2 + 2 * (index if index < FRAMES // 2 else FRAMES - index)

        for i in range(COUNT):
            x = offset + i * PITCH
            if i == TARGET and index >= HIT_FRAME:
                if index < HIT_FRAME + 2:
                    blit(frame, BURST, x + 2, TOP, C.YELLOW if index == HIT_FRAME else C.RED)
                continue
            blit(frame, CRAB[index % 2], x, TOP, C.GREEN)

        blit(frame, CANNON, CANNON_X, 12, C.WHITE)
        if FIRE_FRAME <= index < HIT_FRAME:
            y = 11 - 3 * (index - FIRE_FRAME)
            frame.vline(CANNON_X + 4, y - 2, 3, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/invaders.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
