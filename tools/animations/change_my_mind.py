#!/usr/bin/env python3
"""
Steven Crowder's Change My Mind table (2018) -- a harmless hot take on a sign.

A man sits behind a table at the left, mug in hand, beside a big white sign
that reads CHANGE MY MIND. Above it a hot take is typed out one letter at a
time with a blinking cursor, PINEAPPLE ON PIZZA first, then CEREAL IS A SOUP.
After each one he lifts the mug and takes a slow, confident sip while the
world gets on with arguing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

PAL = {"B": C.BLUE, "F": C.YELLOW, "K": C.BLACK, "R": C.RED, "W": C.WHITE,
       "M": C.MAGENTA, "C": C.CYAN}
HEAD = [
    "..BBBBBB.",
    ".BBBBBBBB",
    ".BFFFFFFF",
    ".FFFFFFFF",
    ".FFKFFKFF",
    ".FFFFFFFF",
    "..FFKKFF.",
    "...FFFF..",
]
BODY = [
    "..MMMMMM..",
    ".MMMMMMMM.",
    "MMMMMMMMMM",
    "MMMMMMMMMM",
    "MMMMMMMMMM",
    "MMMMMMMMMM",
]
SX, SW = 21, 74          # the sign
TAKES = [("PINEAPPLE ON PIZZA", 0), ("CEREAL IS A SOUP", 26)]


def spr(f, rows, x, y):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                f.pixel(x + c, y + r, PAL[ch])


def mug_pos(i):
    """Mug (x, y): resting on the table, raised to the mouth for a sip."""
    rest, up = (12, 10), (10, 5)
    for start in (19, 44):
        if start <= i < start + 2:
            t = (i - start + 1) / 3
        elif start + 2 <= i < start + 6:
            return up
        elif start + 6 <= i < start + 8:
            t = 1 - (i - start - 5) / 3
        else:
            continue
        return (round(rest[0] + (up[0] - rest[0]) * t),
                round(rest[1] + (up[1] - rest[1]) * t))
    return rest


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        spr(f, BODY, 1, 10)
        spr(f, HEAD, 1, 1)
        mx, my = mug_pos(i)
        raised = my < 10
        f.rect(mx, my, 4, 4, C.WHITE, fill=True)
        f.pixel(mx + 4, my + 1, C.WHITE)
        f.pixel(mx + 4, my + 2, C.WHITE)
        f.hline(mx, my, 4, C.YELLOW if not raised else C.CYAN)
        f.rect(mx + 3, my + 2, 2, 2, C.YELLOW, fill=True)   # the hand
        if raised:
            f.pixel(mx + 1, my - 1, C.CYAN)
            f.pixel(mx + 2, my - 2 - (i % 2), C.BLUE)
        # sign
        f.rect(SX, 0, SW, 15, C.WHITE, fill=True)
        f.hline(SX - 1, 15, SW + 1, C.YELLOW)                  # table top
        f.vline(0, 15, 1, C.YELLOW)
        take = TAKES[0] if i < 26 else TAKES[1]
        text, start = take
        n = min(len(text), i - start + 1)
        shown = text[:n]
        tx = SX + (SW - f.small_text_width(text)) // 2
        if i - start < len(text) + 2 and n > 0:
            f.small_text(shown, tx, 2, C.BLACK)
            if i % 2 == 0 and n < len(text) + 1:
                cx = tx + f.small_text_width(shown) + 1 if n else tx
                f.vline(cx, 2, 5, C.RED)
        elif n > 0:
            f.small_text(shown, tx, 2, C.BLACK)
        cm = "CHANGE MY MIND"
        f.small_text(cm, SX + (SW - f.small_text_width(cm)) // 2, 9, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/change_my_mind.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
