#!/usr/bin/env python3
"""
Harlem Shake (2013) -- thirty seconds of internet, condensed to five.

Eight figures stand in a row doing nothing while one in a helmet bobs to
the beat alone. Then the drop: the panel flashes white and every figure
flails in a random pose every frame, arms and legs everywhere, colours
changing, until it cuts to black. Then, deadpan, they are all standing still
again.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 2013
DROP_AT, CUT_AT = 22, 48
STAND = [".#.", "###", ".#.", ".#.", "#.#"]
POSES = [
    ["#.#", ".#.", "##.", ".#.", "#.#"],
    [".#.", "###", ".##", "#..", ".##"],
    ["#..", ".##", "##.", ".#.", "#.#"],
    [".##", "#.#", ".#.", "##.", "..#"],
    ["#.#", ".#.", ".##", ".#.", "##."],
]
COLORS = [C.CYAN, C.YELLOW, C.MAGENTA, C.GREEN, C.WHITE, C.RED]
DANCER = 3


def figure(frame, x, y, rows, color):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r, color)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index == DROP_AT:
            frame.fill(C.WHITE)
            continue
        wild = DROP_AT < index < CUT_AT
        for i in range(8):
            x = 6 + i * 12
            if wild:
                pose = rng.choice(POSES)
                y = 8 + rng.randint(-2, 2)
                figure(frame, x + rng.randint(-2, 2), y, pose, rng.choice(COLORS))
            elif i == DANCER and index < DROP_AT:
                y = 8 - (index % 2)
                figure(frame, x, y, STAND if index % 4 < 2 else POSES[0], C.YELLOW)
                frame.hline(x, y - 1, 3, C.RED)          # the helmet
            else:
                figure(frame, x, 8, STAND, C.CYAN)
        if wild and rng.random() < 0.3:
            for _ in range(20):
                frame.pixel(rng.randrange(96), rng.randrange(16), rng.choice(COLORS))
        frame.hline(0, 14, 96, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/harlem_shake.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
