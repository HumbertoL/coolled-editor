#!/usr/bin/env python3
"""
Kermit Sipping Tea (2014) -- "but that's none of my business".

A green frog with goggling eyes lifts a cup of tea to his wide mouth and takes
a slow sip, steam wisps curling off the top. His eyes slide sideways towards
the text as it wipes in on the right: BUT THAT'S NONE / OF MY BUSINESS. He
lowers the cup, keeps looking, and sips again before the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import wipe  # noqa: E402

FRAMES = 48
DELAY = 120

PAL = {"G": C.GREEN, "W": C.WHITE, "K": C.BLACK, "R": C.RED, "Y": C.YELLOW, "C": C.CYAN}

HEAD_X, HEAD_Y = 3, 1
FACE = [
    ".WWW.GGGG.WWW.",
    "GWWWGGGGGGWWWG",
    "GWWWGGGGGGWWWG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GRRRRRRRRRRRRG",
    ".GGGGGGGGGGGG.",
    "..GGGGGGGGGG..",
    "..WGWGWGWGWG..",
]
BODY = [
    ".GGGGGGGG.",
    "GGGGGGGGGG",
    "GGGGGGGGGG",
    "GGGGGGGGGG",
    "GGGGGGGGGG",
    "GGGGGGGGGG",
]
CUP = [
    "YYYYY.",
    "WWWWWW",
    "WWWWW.",
    "WWWWWW",
    ".WWW..",
]


def spr(f, rows, x, y):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                f.pixel(x + c, y + r, PAL[ch])


def cup_pos(i):
    """Cup (x, y): rest, raised to the mouth, held, lowered -- twice."""
    rest, up = (20, 8), (14, 5)
    def lerp(a, b, t):
        return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t))
    for start in (4, 34):
        if start <= i < start + 5:
            return lerp(rest, up, (i - start + 1) / 5), False
        if start + 5 <= i < start + 13:
            return up, i >= start + 7
        if start + 13 <= i < start + 18:
            return lerp(up, rest, (i - start - 12) / 5), False
    return rest, False


def build():
    anim = Animation(delay=DELAY)
    tx = 32
    for i in range(FRAMES):
        f = anim.frame()
        (cx, cy), sipping = cup_pos(i)
        spr(f, BODY, 5, 10)
        spr(f, FACE, HEAD_X, HEAD_Y)
        # pupils: centre, then sliding sideways towards the text
        look = 1 if 14 <= i < 34 or i >= 44 else 0
        if i in (1, 2):
            look = -1
        for ex in (HEAD_X + 1, HEAD_X + 10):
            f.pixel(ex + 1 + look, HEAD_Y + 1, C.BLACK)
            f.pixel(ex + 1 + look, HEAD_Y + 2, C.BLACK)
        if 20 <= i < 24 or 50 <= i:
            pass
        # cup, hand, steam
        spr(f, CUP, cx, cy)
        if sipping:
            f.hline(cx, cy, 5, C.BLACK)  # tea gulped down a little
            f.hline(cx, cy + 1, 5, C.YELLOW)
        f.rect(cx + 4, cy + 3, 2, 2, C.GREEN, fill=True)
        for k in range(3):
            phase = (i + k * 2) % 6
            wob = 1 if phase in (2, 3) else 0
            sy = cy - 1 - phase // 2
            if sy >= 0:
                f.pixel(cx + 1 + k + wob, sy, C.CYAN if phase < 4 else C.BLUE)
        # the words
        if 16 <= i < 46:
            e1 = tx - 2 + (i - 16) * 13
            f.small_text("BUT THAT'S NONE", tx, 3, wipe(C.WHITE, C.BLACK, e1))
        if 22 <= i < 46:
            e2 = tx - 2 + (i - 22) * 13
            f.small_text("OF MY BUSINESS", tx, 9, wipe(C.YELLOW, C.BLACK, e2))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/kermit_tea.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
