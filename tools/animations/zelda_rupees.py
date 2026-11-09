#!/usr/bin/env python3
"""
Zelda rupees -- a shower of them, and a wallet that keeps count.

The hero walks right across the panel and back while rupees drop out of the
sky ahead of him, bounce once and are snatched up as he passes: green for 1,
blue for 5, red for 20 and one purple 50. Each grab pops a sparkle and a
floating +N, and the counter on the right rolls up toward the total the way
the games' wallet does, a few at a time rather than all at once, ending on
100.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import HERO, HERO_STEP, rupee, sparkle, stamp  # noqa: E402

FRAMES = 53
DELAY = 100
LEFT, RIGHT = 1, 60
TURN = 26
GROUND_TOP = 7     # a rupee's top row when it rests on the floor
HERO_Y = 3

# (frame the hero reaches it, value). Sums to 100.
DROPS = [(6, 1), (9, 5), (12, 20), (16, 1), (20, 5), (30, 1), (33, 50),
         (36, 5), (39, 1), (42, 5), (44, 1), (46, 5)]


def hero_x(index):
    if index <= TURN:
        return LEFT + (RIGHT - LEFT) * index / TURN
    return RIGHT - (RIGHT - LEFT) * (index - TURN) / (FRAMES - TURN)


def build():
    assert sum(v for _, v in DROPS) == 100
    anim = Animation(delay=DELAY)
    shown = 0
    for index in range(FRAMES):
        frame = anim.frame()
        facing_left = index > TURN
        hx = round(hero_x(index))
        banked = sum(v for c, v in DROPS if c <= index)
        if shown < banked:
            shown += max(1, (banked - shown + 1) // 2)

        for catch, value in DROPS:
            # Land just ahead of the hero, where his front reaches it.
            x = round(hero_x(catch)) + (-4 if catch > TURN else 7)
            t = index - catch
            if -9 <= t < -3:                       # falling
                y = GROUND_TOP - round(16 * ((-3 - t) / 6) ** 2)
                rupee(frame, x, y, value)
            elif -3 <= t < 0:                      # one small bounce
                rupee(frame, x, GROUND_TOP - [0, 2, 1][t + 3], value)
            elif 0 <= t < 3:                       # taken
                sparkle(frame, x + 2, 9, t + 1, C.YELLOW if value >= 20 else C.WHITE)
            if 0 <= t < 4:
                label = f"+{value}"
                lx = min(68 - frame.small_text_width(label), max(0, x - 1))
                frame.small_text(label, lx, max(0, 1 - t // 2), C.YELLOW)

        sprite = HERO_STEP if (index // 2) % 2 else HERO
        stamp(frame, sprite, hx, HERO_Y, flip=facing_left)

        # The wallet.
        frame.vline(70, 0, 16, C.BLUE)
        rupee(frame, 73, 4, 1)
        digits = f"{shown:03d}"
        colour = C.WHITE if shown < 100 or index % 2 else C.YELLOW
        frame.text(digits, 79, 5, colour)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_rupees.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
