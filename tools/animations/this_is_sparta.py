#!/usr/bin/env python3
"""
This Is Sparta (2007) -- the kick, from 300.

A Spartan in a red-crested helmet and red cape faces a messenger at the edge
of a dark pit. The messenger's line comes first: MADNESS? Then the answer, a
word at a time: THIS IS. A one-frame white flash, the kick, and SPARTA!!!
strobes in while the panel shakes. The messenger sails out over the pit and,
in proper cartoon physics, hangs there for a beat -- a little "!" over his
head -- before he drops out of the bottom of the panel. Then the payoff goes
big: SPARTA!!! at double size, strobing red, yellow and white, with the
Spartan bobbing in triumph at the left.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 300
PALETTE = {"R": C.RED, "Y": C.YELLOW, "W": C.WHITE, "M": C.MAGENTA, "C": C.CYAN, "B": C.BLUE}

SPARTAN_TOP = [
    "....RRRR....",
    "...RRRRRR...",
    "...YYYYYY...",
    "...YYYYY.Y..",
    "...YYYYY.Y..",
    "...YYYYYY...",
    ".RRRWWWW....",
    "RRRWWWWWWW..",
    "RRRWWWW.....",
    "RRRYYYY.....",
]
SPARTAN_STAND = SPARTAN_TOP + [
    "RRRWW.WW....",
    "RR.WW..WW...",
    "R..WW..WW...",
    "...YY..YY...",
]
SPARTAN_KICK = SPARTAN_TOP + [
    "RRRWWWWWWWWW",
    "RR.WW....WYY",
    "R..WW.......",
    "...YY.......",
]
MESSENGER = [
    "..YYYY.",
    ".WWWW..",
    ".W.WW..",
    ".WWWW..",
    "..WW...",
    ".MMMMM.",
    "MMMMMMM",
    "M.MMM.M",
    "..MMM..",
    "..MMM..",
    "..Y.Y..",
]
# Mid-air: arms up, mouth open, legs kicking.
MESSENGER_FLAIL = [
    "M.YYYY.M",
    "M.WWWW.M",
    "M.W.WW.M",
    ".MW..WM.",
    "..MWWM..",
    "..MMMM..",
    "..MMMM..",
    "..MMMM..",
    ".MM..MM.",
    ".W....W.",
]

PIT_X0, PIT_X1 = 26, 37  # inclusive gap in the ground
TEXT_X0 = 40  # left edge of the caption area
FLASH_AT = 30
BIG_AT = 41


def sprite(canvas, art, x, y):
    for r, line in enumerate(art):
        for c, ch in enumerate(line):
            if ch in PALETTE:
                canvas.pixel(x + c, y + r, PALETTE[ch])


def caption(canvas, text, y, color):
    width = Canvas.text_width(text, proportional=True)
    x = TEXT_X0 + (96 - TEXT_X0 - width) // 2
    canvas.text(text, x, y, color, proportional=True)


def big_text(canvas, text, x, y, color, scale=2):
    """The 5x7 font at ``scale``x: each pixel becomes a block."""
    small = Canvas(200, 7)
    small.text(text, 0, 0, C.WHITE, proportional=True)
    for sx, sy in small.lit():
        canvas.rect(x + sx * scale, y + sy * scale, scale, scale, color, fill=True)


def big_width(text, scale=2):
    # Tracking scales too: 1px becomes `scale` px.
    return Canvas.text_width(text, proportional=True) * scale


def ground(canvas):
    # The ground stops short of the caption, so SPARTA!!! has its rows clear.
    for x in range(TEXT_X0):
        if PIT_X0 <= x <= PIT_X1:
            continue
        canvas.pixel(x, 14, C.YELLOW if x % 3 else C.RED)
        canvas.pixel(x, 15, C.RED)
    # The pit's walls fall away into the dark.
    for y in range(13, 16):
        canvas.pixel(PIT_X0, y, C.BLUE)
        canvas.pixel(PIT_X1, y, C.BLUE)


STROBE = [C.RED, C.YELLOW, C.WHITE]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index == FLASH_AT:
            frame.fill(C.WHITE)
            continue

        scene = Canvas()
        loud = index > FLASH_AT
        strobe = STROBE[index % 3]

        if index < BIG_AT:
            ground(scene)

            # The Spartan: standing, then winding back, then the kick.
            if index < 26:
                sprite(scene, SPARTAN_STAND, 3, 0)
            elif index < FLASH_AT:
                sprite(scene, SPARTAN_STAND, 2 - (index % 2), 0)
            elif index < 35:
                sprite(scene, SPARTAN_KICK, 7, 0)
            else:
                sprite(scene, SPARTAN_STAND, 6, 0)

            # The messenger: at the edge, launched, hanging, gone.
            if index < FLASH_AT:
                sprite(scene, MESSENGER, 18, 3)
            elif index < 34:
                step = index - FLASH_AT
                sprite(scene, MESSENGER_FLAIL, 18 + step * 3, 3 - step)
            elif index < 37:
                sprite(scene, MESSENGER_FLAIL, 28, -1 if index % 2 else 0)
                # The cartoon beat: he looks down, then at us.
                scene.vline(37, 0, 3, C.WHITE)
                scene.pixel(37, 4, C.WHITE)
            else:
                drop = [2, 5, 9, 14][index - 37]
                sprite(scene, MESSENGER_FLAIL, 28, drop)

            # Captions.
            if 3 <= index < 15:
                caption(scene, "MADNESS?", 4, C.CYAN)
            if 18 <= index < 23:
                caption(scene, "THIS", 0, C.WHITE)
            elif 23 <= index < FLASH_AT:
                caption(scene, "THIS IS", 0, C.WHITE)
            elif loud:
                caption(scene, "THIS IS", 0, C.WHITE)
                caption(scene, "SPARTA!!!", 8, strobe)
        else:
            # Payoff: the Spartan bobs, SPARTA!!! at double size.
            sprite(scene, SPARTAN_STAND, 0, 1 if index % 2 else 2)
            word = "SPARTA!!!"
            x = 11 + (85 - big_width(word)) // 2
            big_text(scene, word, x, 1, strobe)

        if loud:
            reach = 2 if index in (31, 32, BIG_AT, BIG_AT + 1) else 1
            dx = rng.randint(-reach, reach)
            # Two caption lines fill rows 0-14, so they only shake downward.
            dy = rng.randint(-1, 1) if index >= BIG_AT else rng.randint(0, 1)
        else:
            dx = dy = 0
        frame.blit(scene, dx, dy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/this_is_sparta.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
