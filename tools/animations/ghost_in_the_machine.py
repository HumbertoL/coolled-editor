#!/usr/bin/env python3
"""
Ghost in the machine -- the sign says NO GHOSTS. A ghost disagrees.

The panel shows a sober yellow "NO GHOSTS". The scanlines jitter -- rows
slide sideways, a cyan and a magenta tear flicker through -- and a little
white pixel ghost with a wavy hem and black eyes floats in from the left.
It grabs the "N" and the "O", lifts them a pixel and drags them off the
edge, leaving the sign reading just "GHOSTS" with the ghost bobbing in the
gap, giggling "HEE HEE".

Then a red "!" -- it heard something. Eyes snap right, it dashes off, comes
straight back pushing "NO" ahead of it, drops the letters into place,
fades out through cyan and blue, and the sign is back to "NO GHOSTS"...
except the O came down one pixel too high.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16

MESSAGE = "NO GHOSTS"
TEXT_Y = 5
TEXT_COLOR = C.YELLOW
TEXT_X = (W - Canvas.text_width(MESSAGE)) // 2
HOME = {i: TEXT_X + 6 * i for i, ch in enumerate(MESSAGE) if ch != " "}
MOVERS = (0, 1)          # the N and the O
GAP_X = TEXT_X + 2       # where the ghost hangs out once NO is gone

# 9x10 ghost; E marks where the eyes go (drawn separately so they can look).
GHOST_BODY = [
    "..#####..",
    ".#######.",
    "#########",
    "#########",
    "#########",
    "#########",
    "#########",
    "#########",
]
HEMS = [
    ["#########", "##..##..#"],
    ["#########", "#..##..##"],
]
GHOST_W = 9


def draw_ghost(c, gx, gy, f, color=C.WHITE, look=0, giggle=False, arm=0):
    rows = GHOST_BODY + HEMS[f % 2]
    for r, line in enumerate(rows):
        for k, ch in enumerate(line):
            if ch == "#":
                c.pixel(gx + k, gy + r, color)
    if color == C.WHITE:
        # eyes: 1x2, shifted by look (-1 left, 0 ahead, +1 right)
        for ex in (2, 5):
            c.pixel(gx + ex + look, gy + 2, C.BLACK)
            c.pixel(gx + ex + look, gy + 3, C.BLACK)
        if giggle:
            c.pixel(gx + 3 + look, gy + 5, C.BLACK)
            c.pixel(gx + 4 + look, gy + 6, C.BLACK)
            c.pixel(gx + 5 + look, gy + 5, C.BLACK)
    if arm:
        # a stubby arm reaching toward whatever it carries
        c.pixel(gx + GHOST_W, gy + 5, color)


def bob(f, amp=1):
    return [0, -1, 0, 1][f % 4] * amp


def glitch(c, f, rnd):
    """Shift rows sideways and splash a colour tear."""
    src = c.clone()
    c.clear()
    shifts = [0] * H
    for _ in range(3 + f % 3):
        y0 = rnd.randrange(H)
        h = rnd.randint(1, 3)
        dx = rnd.choice((-4, -3, -2, 2, 3, 5))
        for y in range(y0, min(H, y0 + h)):
            shifts[y] = dx
    for (x, y) in src.lit():
        c.pixel(x + shifts[y], y, src.get(x, y))
    tear_y = rnd.randrange(3, 13)
    tint = C.CYAN if f % 2 else C.MAGENTA
    for x in range(W):
        if rnd.random() < 0.35:
            c.pixel(x, tear_y, tint)


def main():
    rnd = random.Random(1987)
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        letters = {i: (x, TEXT_Y) for i, x in HOME.items()}
        ghost = None          # (x, y, kwargs)
        extras = []

        if f < 6:
            pass                                       # all normal
        elif f < 10:
            pass                                       # glitch applied below
        elif f < 15:
            # float in from the left, bobbing
            t = (f - 10) / 4
            gx = int(-10 + t * (HOME[0] - GHOST_W - 1 + 10))
            ghost = (gx, 5 + bob(f), dict(look=1))
        elif f < 17:
            # grab: letters lift one pixel
            gx = HOME[0] - GHOST_W - 1
            ghost = (gx, 5, dict(look=1, arm=1))
            for i in MOVERS:
                letters[i] = (HOME[i], TEXT_Y - 1)
        elif f < 22:
            # drag them off the left edge
            t = (f - 16) / 5
            gx = int(HOME[0] - GHOST_W - 1 - t * 34)
            ghost = (gx, 5 + bob(f), dict(look=-1, arm=1))
            for i in MOVERS:
                letters[i] = (HOME[i] + (gx - (HOME[0] - GHOST_W - 1)), TEXT_Y - 1)
        elif f < 31:
            # back, empty-handed, giggling in the gap: the sign says GHOSTS
            for i in MOVERS:
                letters[i] = None
            if f < 24:
                gx = [GAP_X - 16, GAP_X - 6][f - 22]
                ghost = (gx, 5, dict(look=1))
            else:
                ghost = (GAP_X + (1 if f % 2 else -1), 5 + bob(f, 1),
                         dict(look=0, giggle=True))
                if f >= 25:
                    extras.append(("HEE HEE", 44 + (f % 2), 0, C.CYAN))
        elif f < 34:
            # a noise! eyes snap right, it jumps
            for i in MOVERS:
                letters[i] = None
            ghost = (GAP_X, 4, dict(look=1))
            extras.append(("!!", GAP_X + 10, 0, C.RED))
        elif f < 36:
            # dash off left
            for i in MOVERS:
                letters[i] = None
            gx = [GAP_X - 12, GAP_X - 30][f - 34]
            ghost = (gx, 5, dict(look=-1))
        elif f < 40:
            # rush back pushing NO ahead of it
            t = (f - 35) / 4
            home_gx = HOME[0] - GHOST_W - 1
            gx = int(-28 + t * (home_gx + 28))
            ghost = (gx, 5 + bob(f), dict(look=1, arm=1))
            for i in MOVERS:
                letters[i] = (HOME[i] + gx - home_gx, TEXT_Y - 1)
        elif f < 42:
            # set them down -- the O a pixel high
            home_gx = HOME[0] - GHOST_W - 1
            ghost = (home_gx, 5, dict(look=0))
            letters[1] = (HOME[1], TEXT_Y - 1)
        elif f < 45:
            # fade out: white -> cyan -> blue
            home_gx = HOME[0] - GHOST_W - 1
            color = [C.WHITE, C.CYAN, C.BLUE][f - 42]
            ghost = (home_gx, 5 - (f - 42), dict(look=0, color=color))
            letters[1] = (HOME[1], TEXT_Y - 1)
        else:
            letters[1] = (HOME[1], TEXT_Y - 1)          # the crooked O, forever

        for i, pos in letters.items():
            if pos is not None:
                c.text(MESSAGE[i], pos[0], pos[1], TEXT_COLOR)
        if ghost is not None:
            gx, gy, kw = ghost
            draw_ghost(c, gx, gy, f, **kw)
        for text, x, y, color in extras:
            if text == "!!":
                c.text("!", x, y, color)            # the big 5x7 one
            else:
                c.small_text(text, x, y, color)
        if 6 <= f < 10:
            glitch(c, f, rnd)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/ghost_in_the_machine.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
