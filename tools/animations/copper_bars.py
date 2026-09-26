#!/usr/bin/env python3
"""
Copper Bars -- an Amiga demoscene intro, in 3 bits.

Three raster bars swing up and down on sines, each a shaded tube (dark edge,
bright core), passing in front of and behind each other as their depth
changes -- the effect the Amiga's Copper chip made famous by changing the
palette mid-scanline. The 3-bit palette gives them their shading:
blue-cyan-white, magenta-red-yellow and green-yellow-white.

Over them the word GREETZ, in white with a black keyline so it stays legible on
any bar, rides a sine that travels along it letter by letter, the other
demo staple. A three-layer starfield drifts behind everything. Every motion
has a period that divides 53 frames, so the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70
W, H = 96, 16
TAU = 2 * math.pi

# (shade ramp from edge to core, cycles per loop, phase)
BARS = [
    ([C.BLUE, C.CYAN, C.WHITE, C.CYAN, C.BLUE], 1, 0.0),
    ([C.MAGENTA, C.RED, C.YELLOW, C.RED, C.MAGENTA], 1, 1 / 3),
    ([C.GREEN, C.YELLOW, C.WHITE, C.YELLOW, C.GREEN], 1, 2 / 3),
]
WORD = "GREETZ"


def stars():
    rnd = random.Random(5)
    out = []
    for layer, speed in ((C.BLUE, 1), (C.CYAN, 2), (C.WHITE, 3)):
        # speed * FRAMES must be a multiple of W for a seamless wrap, so
        # each layer travels W, 2W or 3W... over the loop: speed in px per
        # frame is W * k / FRAMES.
        for _ in range(9):
            out.append((rnd.uniform(0, W), rnd.randrange(H), layer, speed))
    return out


STARS = stars()


def word_mask():
    """Lit cells of the word, each tagged with its letter's index."""
    cells = []
    x0 = Canvas(W, H).center_x(WORD, tracking=3)
    for i, char in enumerate(WORD):
        canvas = Canvas(W, H)
        canvas.text(char, x=x0 + i * 8, y=0, color=C.WHITE)
        cells += [(x, y, i) for x in range(W) for y in range(7) if canvas.get(x, y) != C.BLACK]
    return cells


MASK = word_mask()


def main():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        for sx, sy, color, speed in STARS:
            x = (sx - W * speed * t) % W
            frame.pixel(int(x), sy, color)
        # Depth is the cosine of the same angle, so bars heading down pass
        # in front of bars heading up -- they appear to orbit a cylinder.
        bars = []
        for ramp, cycles, phase in BARS:
            angle = TAU * (cycles * t + phase)
            centre = 7.5 + 5.5 * math.sin(angle)
            bars.append((math.cos(angle), centre, ramp))
        for _depth, centre, ramp in sorted(bars):
            top = centre - len(ramp) / 2
            for i, color in enumerate(ramp):
                row = round(top + i)
                if 0 <= row < H:
                    frame.hline(0, row, W, color)
        # Sine-scrolled word: each letter rides a travelling sine, whole, so
        # it stays legible. White with a black keyline, readable on any bar.
        lifted = set()
        for x, y, letter in MASK:
            dy = round(4.5 + 4.5 * math.sin(TAU * (2 * t) - letter * 0.9))
            lifted.add((x, y + dy))
        for (x, y) in lifted:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if (x + dx, y + dy) not in lifted:
                    frame.pixel(x + dx, y + dy, C.BLACK)
        for (x, y) in lifted:
            frame.pixel(x, y, C.WHITE)
    out = Path(__file__).resolve().parents[2] / "src/sample/copper_bars.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
