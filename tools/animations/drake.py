#!/usr/bin/env python3
"""
Drakeposting (2015) -- the Hotline Bling two-panel verdict, laid on its side.

The meme's two stacked panels sit side by side on the wide panel. On the left,
the figure in the orange puffer jacket turns his head away and holds a hand up
to 54 FRAMES, flinching from it. Then the right-hand panel lights: the same
jacket, now facing the other way, grinning and pointing at 53 FRAMES. It is a
sign in-joke -- 53 frames is the most this panel will actually apply, and 54
transfers "successfully" and is silently ignored -- so the verdict is also the
spec. This file is, of course, 53 frames.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
# S skin, Y jacket, R the puffer's quilting seams, k a cut-out (eye, mouth).
# The body stays in columns 0-8 so FRAMES can sit right beside it.
NOPE = [
    "..........S.S",
    "..SSSS...SSSS",
    ".SSSSSS..SSSS",
    ".kkSSSS..SSSS",
    ".SSSSSS..SSS.",
    "..kkSSS...YY.",
    "...SSS...YY..",
    "..YYYYYYYYY..",
    ".YYYYYYYYY...",
    "RRRRRRRRR....",
    "YYYYYYYYY....",
    "YYYYYYYYY....",
    "RRRRRRRRR....",
    "YYYYYYYYY....",
    "YYYYYYYYY....",
    "RRRRRRRRR....",
]
YEP = [
    "............S",
    "...SSSS....S.",
    "..SSSSSS.SSS.",
    "..SSSSkS.SSS.",
    "..SSSSSSYY...",
    "..SSSkkSY....",
    "...SSSSYY....",
    "..YYYYYYY....",
    ".YYYYYYYY....",
    "RRRRRRRRR....",
    "YYYYYYYYY....",
    "YYYYYYYYY....",
    "RRRRRRRRR....",
    "YYYYYYYYY....",
    "YYYYYYYYY....",
    "RRRRRRRRR....",
]
COLORS = {"S": C.RED, "Y": C.YELLOW, "R": C.RED, "k": C.BLACK}
YEP_AT = 20


def sprite(frame, rows, x, y, colors=COLORS):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in colors:
                frame.pixel(x + c, y + r, colors[ch])


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Left panel: the refusal, with a little flinch every few frames.
        flinch = index % 8 in (0, 1) and index < YEP_AT + 4
        sprite(frame, NOPE, -1 if flinch else 0, 0)
        frame.text("54", 22, 0, C.RED, proportional=True)
        frame.text("FRAMES", 10, 9, C.WHITE, proportional=True)
        if index >= 6:
            # A strike through the rejected number.
            frame.line(20, 5, 34, 1, C.WHITE)
        frame.vline(47, 0, 16, C.BLUE)

        if index >= YEP_AT:
            k = index - YEP_AT
            bob = 1 if k % 6 in (3, 4, 5) else 0
            sprite(frame, YEP, 49, bob)
            frame.text("53", 66, 0, C.GREEN if k % 4 < 2 or k > 12 else C.WHITE, proportional=True)
            frame.text("FRAMES", 59, 9, C.WHITE, proportional=True)
            if k >= 6:
                frame.glyph("+CHECK", 80, 0, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/drake.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
