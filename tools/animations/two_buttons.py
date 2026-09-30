#!/usr/bin/env python3
"""
Two Buttons (2016) -- the sweating man and his impossible choice.

Two big red buttons, GYM and PIZZA, sit on the right while a worried yellow
head with a blue cap sweats on the left, his eyes following a shaky white
hand that hovers first over one button, then the other. Sweat drops fly off
his face. Finally he gives up and mashes both buttons at once, both domes
flashing while the drops spray.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100
SEED = 2016
SMASH_AT = 32
BUTTONS = [("GYM", 46), ("PIZZA", 80)]


def head(f, look, worry, frame_i, smash):
    ox, oy = 2, 1
    dx = 1 if (frame_i % 4 in (1, 2)) else 0
    x = ox + dx
    f.rect(x + 1, oy, 12, 4, C.BLUE, fill=True)         # cap
    f.hline(x + 10, oy + 3, 5, C.BLUE)                  # brim
    f.rect(x + 1, oy + 4, 12, 9, C.YELLOW, fill=True)   # face
    f.hline(x + 2, oy + 13, 10, C.YELLOW)
    # worried brows
    f.pixel(x + 3, oy + 5, C.RED)
    f.pixel(x + 4, oy + 4 + (1 if worry else 0), C.RED)
    f.pixel(x + 9, oy + 4 + (1 if worry else 0), C.RED)
    f.pixel(x + 10, oy + 5, C.RED)
    # eyes: white, pupil follows the hand
    for ex in (3, 8):
        f.rect(x + ex, oy + 6, 3, 3, C.WHITE, fill=True)
        px = x + ex + 1 + look
        if smash:
            f.pixel(x + ex, oy + 6, C.BLACK)
            f.pixel(x + ex + 2, oy + 6, C.BLACK)
        else:
            f.pixel(px, oy + 7, C.BLACK)
    # wobbly mouth
    wob = frame_i % 2
    if smash:
        f.rect(x + 5, oy + 10, 4, 3, C.BLACK, fill=True)
    else:
        for c in range(5):
            f.pixel(x + 4 + c, oy + 11 + (1 if (c + wob) % 2 else 0), C.BLACK)


def button(f, cx, pressed, lit):
    x = cx - 7
    f.rect(x, 13, 15, 3, C.BLUE, fill=True)
    if pressed:
        f.rect(x + 1, 11, 13, 2, C.RED if not lit else C.MAGENTA, fill=True)
        f.hline(x + 3, 11, 5, C.WHITE if lit else C.RED)
    else:
        f.rect(x + 1, 9, 13, 4, C.RED, fill=True)
        f.hline(x + 2, 10, 4, C.WHITE)
        f.pixel(x + 1, 9, C.BLACK)
        f.pixel(x + 13, 9, C.BLACK)


def hand(f, cx, y):
    f.rect(cx - 2, y, 4, 3, C.WHITE, fill=True)
    f.vline(cx - 1, y + 3, 2, C.WHITE)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    drops = []  # x, y, vx, vy
    for i in range(FRAMES):
        f = anim.frame()
        smash = i >= SMASH_AT
        if i % 3 == 0 or (smash and i % 2 == 0):
            drops.append([16, 4, rng.uniform(1.0, 2.5), rng.uniform(-2.2, -1.0)])
        for d in drops:
            d[0] += d[2]
            d[1] += d[3]
            d[3] += 0.45
        drops = [d for d in drops if d[1] < 16 and d[0] < 96]
        for d in drops:
            f.pixel(d[0], d[1], C.CYAN)
            f.pixel(d[0], d[1] + 1, C.BLUE)

        if not smash:
            # sweep over A (46) and B (80), shaking, with a dwell on each
            t = (i / 8.0) % 2.0
            sway = 0.5 + 0.5 * math.cos(math.pi * t)       # 1 at A, 0 at B
            hx = 46 + (1 - sway) * 34 + (1 if i % 2 else -1)
            hy = 5 + (1 if i % 3 == 0 else 0)
            look = 1 if hx > 62 else 0
            pressed = [False, False]
            head(f, look, i % 2 == 0, i, False)
        else:
            k = i - SMASH_AT
            pressed = [k % 4 < 2 or k < 2, k % 4 >= 2 or k < 2]
            head(f, 0, True, i, True)
        for n, (label, cx) in enumerate(BUTTONS):
            lit = smash and pressed[n]
            button(f, cx, pressed[n], lit)
            color = C.YELLOW if lit else C.WHITE
            f.small_text(label, cx - f.small_text_width(label) // 2, 0, color)
        if smash:
            for n, (_, cx) in enumerate(BUTTONS):
                hand(f, cx + (1 if pressed[n] else 0), 7 if pressed[n] else 5)
        else:
            hand(f, int(hx), hy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/two_buttons.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
