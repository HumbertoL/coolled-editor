#!/usr/bin/env python3
"""
Zelda master sword -- drawn from the pedestal.

Shafts of cyan light shimmer down onto a stone pedestal where a blue-hilted
sword stands buried to the guard. The hero walks in from the left, takes the
grip, and the sword shudders and rises; the panel flashes white. Then the
whole blade is laid out across the panel: blue winged guard with its yellow
gem, wrapped grip, a white-edged blade, while a shine runs from hilt to tip
and sparkles come and go around it.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import HERO, HERO_STEP, sparkle, stamp  # noqa: E402

FRAMES = 53
DELAY = 100
SWORD_X = 50          # left column of the 7-wide upright sword
STUCK_Y = 3
WALK_END = 12
GRAB_AT = 14
FLASH_AT = 23
SHOW_AT = 26

UPRIGHT = [
    "...B...",
    "..BYB..",
    "...B...",
    "...M...",
    "B..B..B",
    "BBBYBBB",
    "..CWC..",
    "..CWC..",
    "..CWC..",
    "..CWC..",
    "..CWC..",
    "..CWC..",
    "...W...",
]

PEDESTAL = [
    "...BBBBBBBBB...",
    "..BCCCCCCCCCB..",
    ".BBBBBBBBBBBBB.",
    "BBBBBBBBBBBBBBB",
]


def temple(frame, index, rng):
    # Light shafts falling from the upper right.
    for k in range(4):
        x0 = 62 + k * 9 - 2 * math.sin(index * 0.5 + k)
        for y in range(16):
            x = round(x0 - y * 1.6)
            if (y + index + k) % 3:
                frame.pixel(x, y, C.BLUE if (y + k) % 4 else C.CYAN)
    stamp(frame, PEDESTAL, SWORD_X - 4, 12)
    for _ in range(2):
        frame.pixel(rng.randrange(40, 70), rng.randrange(0, 11), C.WHITE)


def sideways(frame, shine):
    """The sword laid horizontally, pommel left, tip right."""
    cy = 7
    # Pommel and grip.
    for dx, dy in ((0, 0), (1, -1), (1, 1), (2, 0)):
        frame.pixel(9 + dx, cy + dy, C.BLUE)
    frame.pixel(10, cy, C.YELLOW)
    for x in range(12, 24):
        frame.pixel(x, cy, C.MAGENTA if x % 3 == 0 else C.BLUE)
        frame.pixel(x, cy - 1, C.BLUE)
        frame.pixel(x, cy + 1, C.BLUE)
    # Guard: a vertical bar whose wings curl toward the blade.
    for y in range(1, 14):
        frame.pixel(24, y, C.BLUE)
        frame.pixel(25, y, C.BLUE if abs(y - cy) > 1 else C.YELLOW)
    for y in (1, 13):
        frame.pixel(26, y, C.BLUE)
        frame.pixel(27, y + (1 if y == 1 else -1), C.BLUE)
    frame.pixel(26, cy, C.YELLOW)
    # Blade, then a tapering tip.
    for x in range(27, 84):
        frame.pixel(x, cy - 2, C.WHITE)
        for dy in (-1, 0, 1):
            frame.pixel(x, cy + dy, C.CYAN)
        frame.pixel(x, cy + 2, C.WHITE)
    for k in range(5):
        half = 2 - k // 2
        for dy in range(-half, half + 1):
            edge = abs(dy) == half
            frame.pixel(84 + k, cy + dy, C.WHITE if edge else C.CYAN)
    frame.pixel(89, cy, C.WHITE)
    # A small yellow inlay just below the guard.
    frame.hline(29, cy, 3, C.YELLOW)
    if shine is not None:
        for x in range(shine - 2, shine + 3):
            for y in range(cy - 2, cy + 3):
                if 27 <= x <= 89 and frame.get(x, y) != C.BLACK:
                    frame.pixel(x, y, C.YELLOW if abs(x - shine) < 2 else C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    rng = random.Random(7)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < FLASH_AT:
            temple(frame, index, rng)
            rise = 0
            jitter = 0
            if index >= GRAB_AT:
                rise = min(4, (index - GRAB_AT) // 2)
                jitter = (index % 2) * 2 - 1
            stamp(frame, UPRIGHT, SWORD_X + jitter, STUCK_Y - rise)
            # Re-draw the pedestal so the blade sits inside the stone.
            stamp(frame, PEDESTAL, SWORD_X - 4, 12)
            hx = min(SWORD_X - 8, -8 + index * 4)
            walking = index < WALK_END
            stamp(frame, HERO_STEP if walking and index % 2 else HERO, hx, 3)
            if index >= GRAB_AT and index % 2 == 0:
                sparkle(frame, SWORD_X + 3, STUCK_Y - rise + 5, 1 + (index - GRAB_AT) // 3)
        elif index < SHOW_AT:
            if index - FLASH_AT < 2:
                frame.fill(C.WHITE)
            else:
                frame.fill(C.CYAN)
        else:
            t = index - SHOW_AT
            shine = 20 + t * 5 if t * 5 < 80 else None
            sideways(frame, shine)
            for k in range(3):
                phase = (index + k * 3) % 9
                if phase < 4:
                    x = [40, 64, 80][k] + (index // 9) % 3 * 3
                    y = [2, 12, 3][k]
                    sparkle(frame, x, y, phase if phase < 3 else 1, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_master_sword.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
