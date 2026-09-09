#!/usr/bin/env python3
"""
Lissajous -- an oscilloscope figure, slowly turning.

x = sin(3t + d), y = sin(2t). Advancing the phase d through a full circle over
the loop makes the figure appear to rotate in three dimensions while staying
exactly periodic. The whole curve is drawn as sparse blue dots; a comet runs along it,
completing two laps per loop, white at the tip fading through cyan.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80

A, B = 3, 2
SAMPLES = 600
LAPS = 2
COMET = 80
TIP = 10
GHOST_EVERY = 4


def build():
    anim = Animation(delay=DELAY)
    cx, cy = (anim.width - 1) / 2, (anim.height - 1) / 2
    rx, ry = 46.0, 7.4

    for index in range(FRAMES):
        frame = anim.frame()
        delta = 2 * math.pi * index / FRAMES
        points = []
        for i in range(SAMPLES):
            t = 2 * math.pi * i / SAMPLES
            points.append((
                round(cx + rx * math.sin(A * t + delta)),
                round(cy + ry * math.sin(B * t)),
            ))

        for i in range(0, SAMPLES, GHOST_EVERY):
            frame.pixel(*points[i], C.BLUE)

        head = (index * SAMPLES * LAPS // FRAMES) % SAMPLES
        for k in range(COMET, -1, -1):
            x, y = points[(head - k) % SAMPLES]
            frame.pixel(x, y, C.WHITE if k < TIP else C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lissajous.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
