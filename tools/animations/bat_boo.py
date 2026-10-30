#!/usr/bin/env python3
"""
Bat boo -- a bat drone show that spells BOO.

A big yellow full moon sits low on the right of a twinkling starry sky.
Forty-eight magenta bats, each a 3x2 sprite with a two-frame wing flap,
stream out of the moon one after another (dark silhouettes while they cross
its face) and swing round the sky in a long looping ribbon.

Then every bat peels off to its own assigned spot, and they lock together
into a huge "BOO" fourteen rows tall -- the 5x7 letters doubled, each bat
one 2x2 cell of a stroke. BOO holds, flashes white once, holds again, then
bursts outward like a firework and every bat curves back into the moon,
the last ones vanishing into it just as the first ones re-emerge.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.font import FONT_5X7  # noqa: E402

FRAMES = 53
DELAY = 100
W, H = 96, 16

MOON_X, MOON_Y, MOON_R = 85, 10, 7.4
BAT_COLOR = C.MAGENTA
FLASH_COLOR = C.WHITE

# Beat sheet (frame numbers)
LAUNCH_SPAN = 13       # bats leave the moon over frames 0..12
GATHER_START = 19      # peel off the swirl toward their spots
SETTLED = 29           # BOO complete
FLASH = (35, 36)       # white flash
BURST = 41             # explode and return to the moon
HOME_BY = 52.6         # everyone is back inside by the loop point

# BOO: 5x7 glyphs at 2x, so each lit glyph cell is a 2x2 bat.
WORD = "BOO"
CELL = 2
GAP = 4
LETTER_W = 5 * CELL
WORD_W = len(WORD) * LETTER_W + (len(WORD) - 1) * GAP
WORD_X = (MOON_X - MOON_R - WORD_W) // 2 + 1
WORD_Y = 1
WORD_CX, WORD_CY = WORD_X + WORD_W / 2, WORD_Y + 7


def targets():
    out = []
    for li, ch in enumerate(WORD):
        lx = WORD_X + li * (LETTER_W + GAP)
        for r, row in enumerate(FONT_5X7[ch]):
            for k, bit in enumerate(row):
                if bit == "#":
                    out.append((lx + k * CELL, WORD_Y + r * CELL))
    return out


def in_moon(x, y):
    return (x - MOON_X) ** 2 + (y - MOON_Y) ** 2 <= MOON_R ** 2


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def swirl(u, wobble):
    """The flock's ribbon: out of the moon and round a long ellipse."""
    theta = u * 0.24
    rx, ry = MOON_X - 46, 5 + wobble * 0.6
    cx, cy = 46, 8
    x = cx + rx * math.cos(theta)
    y = cy - ry * math.sin(theta) + 2 * math.sin(u * 0.7) * min(1.0, u / 6)
    # start from the moon's centre and fan out over the first frames
    k = min(1.0, u / 3)
    return MOON_X + (x - MOON_X) * (0.35 + 0.65 * k), MOON_Y + (y - MOON_Y) * k


def draw_bat(c, x, y, f, color):
    x, y = int(round(x)), int(round(y))
    up = f % 2 == 0
    pts = [(-1, 0), (1, 0), (0, 1)] if up else [(0, 0), (-1, 1), (1, 1)]
    for dx, dy in pts:
        px, py = x + dx, y + dy
        c.pixel(px, py, C.BLACK if in_moon(px, py) else color)


def main():
    rnd = random.Random(1031)
    goals = targets()
    n = len(goals)
    order = list(range(n))
    rnd.shuffle(order)
    launch = {b: LAUNCH_SPAN * i / n for i, b in enumerate(order)}
    wobble = {b: rnd.uniform(-1.8, 1.8) for b in range(n)}
    flap0 = {b: rnd.randrange(2) for b in range(n)}
    # burst: fling outward from the word, then arc into the moon
    burst = {}
    for b, (tx, ty) in enumerate(goals):
        dx, dy = tx + 1 - WORD_CX, ty + 1 - WORD_CY
        d = math.hypot(dx, dy) or 1
        ctrl = (tx + dx / d * 22 + rnd.uniform(-4, 4), ty + dy / d * 9 + rnd.uniform(-3, 3))
        start = BURST + rnd.uniform(0, 1.5)
        burst[b] = (ctrl, start)

    stars = []
    while len(stars) < 26:
        x, y = rnd.randrange(W), rnd.randrange(H - 1)
        if not in_moon(x, y) and (x - MOON_X) ** 2 + (y - MOON_Y) ** 2 > 90:
            stars.append((x, y, rnd.randrange(5), rnd.random() < 0.3))

    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        for (x, y, phase, blue) in stars:
            # whole cycles per loop, so the twinkle wraps cleanly
            v = math.sin(2 * math.pi * (3 + phase % 3) * f / FRAMES + phase)
            if v < -0.6:
                continue
            c.pixel(x, y, C.BLUE if (blue or v < 0.2) else C.WHITE)
        for y in range(H):
            for x in range(MOON_X - 8, W):
                if in_moon(x, y):
                    c.pixel(x, y, C.YELLOW)

        flashing = f in FLASH
        for b, (tx, ty) in enumerate(goals):
            flap = f + flap0[b]
            if f < GATHER_START:
                u = f - launch[b]
                if u < 0:
                    continue
                draw_bat(c, *swirl(u, wobble[b]), flap, BAT_COLOR)
            elif f < BURST:
                t = (f - GATHER_START) / (SETTLED - GATHER_START)
                # each bat leaves on a slight personal delay
                t = t * 1.15 - (launch[b] / LAUNCH_SPAN) * 0.15
                if t >= 1:
                    color = FLASH_COLOR if flashing else BAT_COLOR
                    c.rect(tx, ty, CELL, CELL, color, fill=True)
                    continue
                sx, sy = swirl(f - launch[b], wobble[b])
                e = ease(t)
                draw_bat(c, sx + (tx + 1 - sx) * e, sy + (ty + 1 - sy) * e, flap, BAT_COLOR)
            else:
                (cx, cy), start = burst[b]
                t = (f - start) / (HOME_BY - start)
                if t < 0:
                    c.rect(tx, ty, CELL, CELL, BAT_COLOR, fill=True)
                    continue
                if t >= 1:
                    continue
                t = 1 - (1 - t) ** 1.6  # fast out, gliding home
                a, bb, cc = (1 - t) ** 2, 2 * t * (1 - t), t * t
                x = a * (tx + 1) + bb * cx + cc * MOON_X
                y = a * (ty + 1) + bb * cy + cc * MOON_Y
                if math.hypot(x - MOON_X, y - MOON_Y) < 1.5:
                    continue
                draw_bat(c, x, y, flap, BAT_COLOR)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/bat_boo.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
