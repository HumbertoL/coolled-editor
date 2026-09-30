#!/usr/bin/env python3
"""
Hampster Dance (1998) -- the original Geocities dancing rodents.

Six hamsters stand in a row on a tiled, slowly drifting starfield background,
swaying in alternating rhythm: one raises its paws and leans while its
neighbour drops and leans the other way. A tiny rainbow marquee scrolls
HAMPSTER DANCE across the top, looping seamlessly every 40 frames.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 40
DELAY = 110
PERIOD = 80          # marquee repeat distance in px; 2 px per frame

COLORS = {"Y": C.YELLOW, "W": C.WHITE, "K": C.BLACK, "R": C.RED, "B": C.RED}
UP = [
    "Y.R...R.Y",
    "Y.YY.YY.Y",
    "YYYYYYYYY",
    ".YKYYYKY.",
    ".YWWRWWY.",
    ".YWWWWWY.",
    "..YWWWY..",
    "..YYYYY..",
    "..Y...Y..",
]
DOWN = [
    "..R...R..",
    "..YY.YY..",
    ".YYYYYYY.",
    ".YKYYYKY.",
    ".YWWRWWY.",
    "YYWWWWWYY",
    "Y.YWWWY.Y",
    "..YYYYY..",
    ".YY...YY.",
]


def hamster(f, x, y, sprite):
    for r, row in enumerate(sprite):
        for c, ch in enumerate(row):
            if ch != ".":
                f.pixel(x + c, y + r, COLORS[ch])


def build():
    anim = Animation(delay=DELAY)
    rainbow = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA]
    for i in range(FRAMES):
        f = anim.frame()
        # tiled background: a 6x5 star motif, drifting one px per 2 frames
        off = i * 6 // FRAMES
        for ty in range(-1, 4):
            for tx in range(-1, 17):
                bx = tx * 6 + off % 6
                by = ty * 5 + 6
                if 6 <= by + 1 <= 15:
                    f.pixel(bx, by, C.BLUE)
                    f.pixel(bx + 3, by + 2, C.BLUE)
        f.rect(0, 0, 96, 6, C.BLACK, fill=True)
        f.hline(0, 6, 96, C.MAGENTA if i % 8 < 4 else C.BLUE)
        for k in range(2):
            x = k * PERIOD - 2 * i
            f.small_text("HAMPSTER", x, 0, C.YELLOW)
            f.small_text("DANCE", x + 36, 0, C.CYAN)
            f.pixel(x + 60, 2, rainbow[(i // 4) % 5])
            f.pixel(x + 62, 2, rainbow[(i // 4 + 2) % 5])
        for n in range(6):
            up = (i // 4 + n) % 2 == 0
            x = 3 + 16 * n
            hamster(f, x, 7, UP if up else DOWN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hampster_dance.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
