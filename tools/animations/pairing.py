#!/usr/bin/env python3
"""
Pairing -- the sign finding its Bluetooth connection.

Anyone who has read docs/SENDING_TO_THE_SIGN.md has lived this. The rune sits
blue while signal arcs ripple out of it and SEARCHING cycles its dots; then
the rune goes white, the text turns green, and a tick lands. Sixteen frames
of waiting to eight of relief, which is about the real ratio.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 150

RUNE = [
    "...#...",
    "...##..",
    "...#.#.",
    "#..#..#",
    ".#.#.#.",
    "..###..",
    ".#.#.#.",
    "#..#..#",
    "...#.#.",
    "...##..",
    "...#...",
]
RUNE_X, RUNE_Y = 5, 2
CONNECT_FRAME = 16
TEXT_X = 24


def arcs(frame, index):
    cx, cy = RUNE_X + 3, RUNE_Y + 5
    for ring in range(2):
        r = 5 + ((index + ring * 3) % 6)
        color = C.CYAN if r < 8 else C.BLUE
        for deg in range(-55, 56, 5):
            a = math.radians(deg)
            frame.pixel(round(cx + 2 + r * math.cos(a)), round(cy + r * 0.55 * math.sin(a)), color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        connected = index >= CONNECT_FRAME
        for row, line in enumerate(RUNE):
            for col, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(RUNE_X + col, RUNE_Y + row, C.WHITE if connected else C.BLUE)
        if connected:
            frame.text("CONNECTED", TEXT_X, 4, C.GREEN)
            frame.glyph("+CHECK", TEXT_X + 56, 4, C.WHITE if index % 2 == 0 or index > 18 else C.GREEN)
        else:
            arcs(frame, index)
            frame.text("SEARCHING" + "." * ((index // 2) % 4), TEXT_X, 4, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pairing.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
