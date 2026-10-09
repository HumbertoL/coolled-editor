#!/usr/bin/env python3
"""
Mandelbrot -- the zoom, one pixel at a time.

A dive into Seahorse Valley: every pixel runs the z -> z^2 + c escape loop and
takes its colour from how many steps it needed, so the filaments and spirals
the set is famous for come out as bands of the palette. The iteration cap
climbs as the view tightens (about 270x deeper at the bottom), and the zoom
follows a cosine in and back out, so the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
TARGET = (-0.743643887037151, 0.131825904205330)
WIDE, TIGHT = 3.2, 0.012
PALETTE = [C.BLUE, C.CYAN, C.GREEN, C.YELLOW, C.RED, C.MAGENTA, C.WHITE]


def escape(cr, ci, limit):
    zr = zi = 0.0
    for n in range(limit):
        zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
        if zr * zr + zi * zi > 4:
            return n
    return None


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        # Zoom in and back out on a cosine, so the loop is seamless.
        phase = (1 - math.cos(2 * math.pi * index / FRAMES)) / 2
        width = WIDE * (TIGHT / WIDE) ** phase
        limit = int(40 + 160 * phase)
        step = width / 96
        frame = anim.frame()
        for y in range(16):
            for x in range(96):
                n = escape(TARGET[0] + (x - 48) * step, TARGET[1] + (y - 7.5) * step, limit)
                if n is not None:
                    frame.pixel(x, y, PALETTE[(n // 2) % len(PALETTE)])
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/mandelbrot.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
