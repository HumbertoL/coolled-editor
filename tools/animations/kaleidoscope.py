#!/usr/bin/env python3
"""
Kaleidoscope -- mirrored wedges of an evolving field.

The panel is treated as polar space around its centre. The angle is folded into
a single wedge with mirror symmetry, so whatever is drawn in that wedge is
reflected N times around the circle -- the classic kaleidoscope tube. The field
inside the wedge is three drifting sine ripples in radius and folded angle,
mapped onto SPECTRUM so the petals keep changing hue.

Seamless: the field's only time term advances by 2*pi/FRAMES per frame.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90

CX, CY = 47.5, 7.5
WEDGES = 6            # petals around the circle
ASPECT = 3.0         # stretch y so petals aren't crushed by the 6:1 panel


def build():
    anim = Animation(delay=DELAY)
    wedge = 2 * math.pi / WEDGES

    for index in range(FRAMES):
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for y in range(frame.height):
            for x in range(frame.width):
                dx = x - CX
                dy = (y - CY) * ASPECT
                r = math.hypot(dx, dy)
                if r < 0.5:
                    frame.pixel(x, y, C.WHITE)
                    continue
                angle = math.atan2(dy, dx)
                # Fold into one wedge, then mirror the wedge onto itself.
                folded = angle % wedge
                if folded > wedge / 2:
                    folded = wedge - folded

                value = (
                    math.sin(r * 0.45 - phase * 2)
                    + math.sin(folded * 5 + phase)
                    + math.sin(r * 0.2 + folded * 3 - phase)
                )
                # Only the brighter crests light up, so petals have gaps.
                if value < 0.6:
                    continue
                hue = ((r * 0.06 + folded * 0.5 + phase / (2 * math.pi)) % 1.0)
                frame.pixel(x, y, C.ramp(C.SPECTRUM, hue))

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/kaleidoscope.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
