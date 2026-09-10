#!/usr/bin/env python3
"""
Dragon -- the encounter nobody's level was ready for.

A dragon fills the left of the panel, wing beating slowly. It draws breath
-- the chest lights up -- and a cone of fire pours out to the right,
flickering red and yellow with a white core, then dies back to embers. Out of
the smoke: ROLL INITIATIVE!
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 5

# Two wing positions; head up on a neck at the right, mouth at row 3.
DRAGON = [
    [
        "..........###.........###.",
        ".........#####.......#####",
        "........#######......####.",
        ".......#########.....###..",
        "......###########....##...",
        ".....#############...##...",
        "....##################....",
        "...###################....",
        "##..#################.....",
        "#....#############........",
        ".....###......###.........",
        "....###........###........",
        "...##...........##........",
    ],
    [
        "......................###.",
        ".....................#####",
        ".....................####.",
        "........#####........###..",
        "......#########......##...",
        ".....###########.....##...",
        "....##################....",
        "...###################....",
        "##..#################.....",
        "#....#############........",
        ".....###......###.........",
        "....###........###........",
        "...##...........##........",
    ],
]
DRAGON_X, DRAGON_Y = 0, 2
MOUTH_X, MOUTH_Y = 26, 3
EYE = (23, 1)
BREATH_IN, FIRE_START, FIRE_PEAK, FIRE_END, TEXT_AT = 8, 12, 24, 36, 40


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        wing = DRAGON[(index // 5) % 2] if index < FIRE_START or index >= FIRE_END else DRAGON[0]
        for r, line in enumerate(wing):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(DRAGON_X + c, DRAGON_Y + r, C.GREEN)
        frame.pixel(DRAGON_X + EYE[0], DRAGON_Y + EYE[1], C.RED if index % 8 < 6 else C.YELLOW)

        if BREATH_IN <= index < FIRE_START:
            glow = index - BREATH_IN
            for r in range(6, 9):
                frame.hline(DRAGON_X + 12 + glow, DRAGON_Y + r, 3 + glow, C.YELLOW)
            frame.vline(DRAGON_X + 21, DRAGON_Y + 2 + (3 - glow), 2, C.YELLOW)

        if FIRE_START <= index < FIRE_END:
            if index < FIRE_PEAK:
                reach = 4 + (index - FIRE_START) * 6
            else:
                reach = max(0, 70 - (index - FIRE_PEAK) * 6)
            for dx in range(reach):
                spread = 1 + dx // 6
                for dy in range(-spread, spread + 1):
                    y = MOUTH_Y + dy + dx // 10 + (1 if rng.random() < 0.15 else 0)
                    x = MOUTH_X + dx
                    if rng.random() < 0.25:
                        continue
                    core = abs(dy) <= spread // 3 and dx < reach - 8
                    frame.pixel(x, y, C.WHITE if core and rng.random() < 0.5 else
                                C.YELLOW if core or rng.random() < 0.5 else C.RED)
            for _ in range(reach // 5):
                frame.pixel(MOUTH_X + rng.randrange(max(1, reach)), rng.randrange(16), C.RED)

        if index >= TEXT_AT:
            k = index - TEXT_AT
            color = C.YELLOW if k % 4 < 2 else C.RED
            frame.text("ROLL", 34, 0, color, proportional=True)
            frame.text("INITIATIVE!", 34, 9, C.WHITE if k % 4 < 2 else C.YELLOW, proportional=True)
        elif index >= FIRE_END:
            for _ in range(12 - (index - FIRE_END) * 3):
                frame.pixel(MOUTH_X + rng.randrange(60), rng.randrange(16), C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dnd_dragon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
