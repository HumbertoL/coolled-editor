#!/usr/bin/env python3
"""
Deal With It (2010) -- the sunglasses descend.

A face waits. A pair of pixel sunglasses drops in from the top of the panel,
slowing as it comes, and lands over the eyes with a one-frame flash. Then the
caption slides in from the right in the meme's block capitals: DEAL WITH IT.
Hold. The shades come off for the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
FACE = [
    "..#######..",
    ".#########.",
    "###########",
    "###########",
    "###########",
    "###########",
    "###########",
    ".#########.",
    "..#######..",
]
FACE_X, FACE_Y = 6, 3
EYES = [(3, 3), (7, 3)]
SHADES = ["####.####", "###...###"]
LAND_AT, TEXT_AT = 14, 18


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for r, line in enumerate(FACE):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(FACE_X + c, FACE_Y + r, C.YELLOW)
        for ex, ey in EYES:
            frame.pixel(FACE_X + ex, FACE_Y + ey, C.BLACK)
        smirk = index >= LAND_AT
        for k in range(5):
            frame.pixel(FACE_X + 3 + k, FACE_Y + 6 + (0 if not smirk or k < 3 else -1), C.BLACK)

        target_y = FACE_Y + 2
        if index < LAND_AT:
            t = index / LAND_AT
            y = round(-3 + (target_y + 3) * (1 - (1 - t) ** 2))
        else:
            y = target_y
        for r, line in enumerate(SHADES):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(FACE_X + 1 + c, y + r, C.WHITE if index == LAND_AT else C.BLACK if False else C.CYAN)
        if index == LAND_AT:
            for dx, dy in ((-2, 0), (12, 0), (5, -2), (5, 4)):
                frame.pixel(FACE_X + 1 + dx, y + dy, C.WHITE)

        if index >= TEXT_AT:
            k = index - TEXT_AT
            x = max(24, 96 - k * 12)
            frame.text("DEAL WITH IT", x, 4, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/deal_with_it.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
