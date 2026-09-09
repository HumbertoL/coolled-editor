#!/usr/bin/env python3
"""
Boss battle -- Dungeon Crawler Carl.

WARNING flashes, then the line becomes BOSS BATTLE with a skull whose eyes
glow red, while a red border strobes round the panel -- faster as it goes.
The system's boss-fight alert, as close as sixteen rows allow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

SKULL = [
    "..#####..",
    ".#######.",
    "##.###.##",
    "##.###.##",
    "#########",
    ".###.###.",
    "..#####..",
    "..#.#.#..",
]
EYES = [(2, 2), (2, 3), (6, 2), (6, 3)]
SKULL_X, SKULL_Y = 6, 4
WARN_END = 16


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        period = 6 if index < 30 else 4 if index < 44 else 2
        border_on = (index // period) % 2 == 0
        if border_on:
            frame.rect(0, 0, anim.width, anim.height, C.RED)

        for r, line in enumerate(SKULL):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(SKULL_X + c, SKULL_Y + r, C.WHITE if index >= WARN_END else C.YELLOW)
        if index >= WARN_END:
            eye = C.RED if (index // 3) % 2 == 0 else C.YELLOW
            for c, r in EYES:
                frame.pixel(SKULL_X + c, SKULL_Y + r, eye)

        if index < WARN_END:
            if index % 4 < 3:
                frame.text("WARNING", 30, 4, C.RED if index % 2 else C.YELLOW, proportional=True)
        else:
            frame.text("BOSS BATTLE", 24, 4, C.YELLOW if not border_on else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_boss_battle.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
