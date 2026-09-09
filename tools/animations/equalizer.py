#!/usr/bin/env python3
"""
Equalizer -- spectrum bars with peak markers.

The look an LED strip is practically built for. Each bar's height is the sum
of two sine waves at different rates, which keeps it lively without any
randomness and makes the loop exactly seamless: both rates complete a whole
number of cycles across the frame count.

Colour encodes height rather than identity -- green low, yellow through the
middle, red at the top -- so a bar changes colour as it rises, the way a real
VU meter does. A white peak marker floats above each bar, driven by a slower
wave so it lags the way a real peak-hold does.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80

BAR_WIDTH, BAR_GAP = 3, 1
HEIGHT = 16


def band_color(row_from_bottom):
    if row_from_bottom >= 12:
        return C.RED
    if row_from_bottom >= 7:
        return C.YELLOW
    return C.GREEN


def build():
    anim = Animation(delay=DELAY)
    step = BAR_WIDTH + BAR_GAP
    bars = anim.width // step

    for index in range(FRAMES):
        turn = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for bar in range(bars):
            phase = bar * 0.7
            # Two whole-number rates -> seamless; different rates per bar
            # keep neighbours from moving in lockstep.
            value = 0.5 + 0.32 * math.sin(turn + phase) + 0.18 * math.sin(
                2 * turn - phase * 1.6
            )
            height = max(1, min(HEIGHT, round(value * HEIGHT)))
            x0 = bar * step

            for row in range(height):
                for dx in range(BAR_WIDTH):
                    frame.pixel(x0 + dx, HEIGHT - 1 - row, band_color(row))

            # Peak marker: a slower wave, never below the bar itself.
            peak_value = 0.5 + 0.34 * math.sin(turn - 0.9 + phase)
            peak = max(height + 1, min(HEIGHT, round(peak_value * HEIGHT) + 2))
            if peak <= HEIGHT:
                for dx in range(BAR_WIDTH):
                    frame.pixel(x0 + dx, HEIGHT - peak, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/equalizer.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
