#!/usr/bin/env python3
"""
Hazard -- diagonal warning stripes on a conveyor.

Pure graphic design rather than simulation: the stripe a pixel belongs to is
just ``(x + y + offset) // width mod 2``, which makes clean 45-degree diagonals
because the panel's pixels are square. Advancing the offset one pixel per frame
sends the whole field sliding sideways.

Thin cyan pinstripes ride between the yellow bands to stop the black gaps
looking empty. Seamless: the stripe period divides the travel exactly.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 75

STRIPE = 6              # width of one band; 2 * STRIPE divides FRAMES * SPEED
SPEED = 1


def build():
    anim = Animation(delay=DELAY)
    period = STRIPE * 2

    for index in range(FRAMES):
        frame = anim.frame()
        offset = index * SPEED
        for y in range(anim.height):
            for x in range(anim.width):
                phase = (x + y + offset) % period
                if phase < STRIPE - 1:
                    frame.pixel(x, y, C.YELLOW)
                elif phase == STRIPE + 1:
                    frame.pixel(x, y, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hazard.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
