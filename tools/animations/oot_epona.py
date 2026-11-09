#!/usr/bin/env python3
"""
OoT epona -- galloping across Hyrule Field.

A chestnut horse with a white mane, tail and socks gallops left to right in a
four-beat leg cycle, the green-capped hero riding on her back. The field scrolls under them: grass streaks fast along the ground,
blue hills slow in the distance, a yellow sun overhead. Twice a low wooden
fence comes rushing in and she gathers her legs and clears it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import stamp  # noqa: E402

FRAMES = 53
DELAY = 90
HORSE_X = 30
SPEED = 4                 # ground pixels per frame
FENCES = [14, 40]         # frame at which a fence is directly under the horse
FENCE_W = 9
JUMP = 9                  # frames in the air
LIFT = 4

HORSE = [
    "................RR..",
    "...............RRRR.",
    "..............WRRKRRR",
    ".............WRRRR.RR",
    ".WW.RRRRRRRRWRRR.....",
    "W..RRRRRRRRRRRRR.....",
    "W..RRRRRRRRRRRR......",
    "W...RRRRRRRRRR.......",
]
RIDER = [
    ".GGG..",
    "GGGGG.",
    "G.YYY.",
    "..YKY.",
    ".GGGGY",
    ".GGG..",
    ".GW...",
]
# (hip dx, foot dx) for back and front pairs, per beat of the gallop.
GAIT = [
    ((-2, -3), (2, 3)),     # stretched out
    ((0, -1), (0, 1)),
    ((2, 1), (-2, -1)),     # gathered
    ((0, 1), (0, -1)),
]
HIPS = (5, 13)            # columns of the back and front legs in HORSE


def legs(frame, x, top, beat, tucked):
    back, front = GAIT[beat]
    for (offset, (spread, reach)) in zip(HIPS, ((back[0], back[1]), (front[0], front[1]))):
        for pair in (0, 1):
            hip_x = x + offset + pair
            length = 2 if tucked else 4
            foot_x = hip_x + (reach if pair == 0 else spread)
            for k in range(length):
                lx = round(hip_x + (foot_x - hip_x) * k / max(1, length - 1))
                frame.pixel(lx, top + 8 + k, C.WHITE if k == length - 1 else C.RED)


def fence(frame, fx):
    for px in (fx, fx + FENCE_W - 1, fx + FENCE_W // 2):
        frame.vline(px, 11, 4, C.YELLOW)
    frame.hline(fx, 12, FENCE_W, C.YELLOW)
    frame.hline(fx, 14, FENCE_W, C.RED)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Sun, hills, ground.
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 5:
                    frame.pixel(84 + dx, 3 + dy, C.YELLOW)
        for x in range(96):
            h = 2 + 1.5 * math.sin((x + index) * 0.11) + math.sin((x + index) * 0.27)
            frame.pixel(x, round(12 - h), C.BLUE)
        for x in range(96):
            if (x + index * SPEED) % 7 < 3:
                frame.pixel(x, 15, C.GREEN)
            if (x * 5 + index * SPEED) % 23 == 0:
                frame.pixel(x, 14, C.GREEN)

        lift = 0
        tucked = False
        for at in FENCES:
            fx = HORSE_X + 7 - (index - at) * SPEED
            if -FENCE_W < fx < 96:
                fence(frame, fx)
            t = index - (at - JUMP // 2)
            if 0 <= t < JUMP:
                lift = round(LIFT * math.sin(math.pi * (t + 0.5) / JUMP))
                tucked = True

        beat = index % 4
        bob = 1 if beat in (1, 3) and not tucked else 0
        top = 3 - lift - bob
        legs(frame, HORSE_X, top, 2 if tucked else beat, tucked)
        stamp(frame, HORSE, HORSE_X, top)
        # Mane and tail stream with the stride.
        if beat % 2 and not tucked:
            frame.pixel(HORSE_X, top + 4, C.WHITE)
        stamp(frame, RIDER, HORSE_X + 7, top - 3)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/oot_epona.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
