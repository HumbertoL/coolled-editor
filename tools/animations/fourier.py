#!/usr/bin/env python3
"""
Fourier -- a square wave built from four spinning circles.

Epicycles for the first four odd harmonics of a square wave (radii in the
ratio 1, 1/3, 1/5, 1/7) turn on the left, each riding the rim of the last. The
tip's height is fed along a dashed line into a trace that scrolls right, and
four sine waves add up to a square wave with Gibbs ripples at its corners.
One loop is one turn of the largest circle, so it is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70
CENTRE = (10, 7.5)
AMPLITUDE = 5.0       # height of the square wave; the first radius is 4/pi of it
HARMONICS = (1, 3, 5, 7)
CIRCLE_COLOURS = (C.BLUE, C.MAGENTA, C.GREEN, C.RED)
WAVE_X = 24
PERIOD_PX = 36        # one cycle of the trace spans this many columns


def tip(phase):
    """Every joint along the epicycle chain for the given phase."""
    x, y = CENTRE
    joints = [(x, y)]
    for n in HARMONICS:
        r = 4 * AMPLITUDE / (math.pi * n)
        x += r * math.cos(n * phase)
        y -= r * math.sin(n * phase)
        joints.append((x, y))
    return joints


def circle(frame, cx, cy, r, colour):
    steps = max(12, int(r * 8))
    for k in range(steps):
        a = 2 * math.pi * k / steps
        frame.pixel(round(cx + r * math.cos(a)), round(cy + r * math.sin(a)), colour)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()
        joints = tip(phase)
        for (cx, cy), n, colour in zip(joints, HARMONICS, CIRCLE_COLOURS):
            circle(frame, cx, cy, 4 * AMPLITUDE / (math.pi * n), colour)
        for (x0, y0), (x1, y1) in zip(joints, joints[1:]):
            frame.line(round(x0), round(y0), round(x1), round(y1), C.WHITE)
        tx, ty = joints[-1]
        for x in range(round(tx) + 2, WAVE_X, 2):
            frame.pixel(x, round(ty), C.CYAN)
        # The trace: column x shows the tip as it was (x - WAVE_X) columns ago.
        previous = None
        for x in range(WAVE_X, 96):
            past = phase - 2 * math.pi * (x - WAVE_X) / PERIOD_PX
            y = round(tip(past)[-1][1])
            if previous is not None:
                frame.line(x - 1, previous, x, y, C.YELLOW)
            previous = y
        frame.pixel(WAVE_X, round(ty), C.WHITE)
        frame.pixel(round(tx), round(ty), C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fourier.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
