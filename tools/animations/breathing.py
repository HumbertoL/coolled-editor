#!/usr/bin/env python3
"""
Breathing -- a box-breathing coach.

A ring on the left grows and shrinks through a four-count box-breathing cycle --
in, hold, out, hold -- while the current instruction reads out to its right. The
ring is filled through the GLOW ramp so it looks like it swells with light on the
inhale and dims on the exhale. Meant to be watched and followed.

Seamless: the whole in-hold-out-hold cycle spans the loop exactly once.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52          # 4 equal phases of 13 frames
DELAY = 150
PHASE = FRAMES // 4

RCX, RCY = 9.0, 8.0
RMIN, RMAX = 1.5, 6.5


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        phase = index // PHASE
        p = (index % PHASE) / PHASE          # 0..1 within the phase
        frame = anim.frame()

        if phase == 0:                        # inhale: grow
            radius = RMIN + (RMAX - RMIN) * p
            label, lab_color = "BREATHE IN", C.CYAN
        elif phase == 1:                      # hold full
            radius = RMAX
            label, lab_color = "HOLD", C.WHITE
        elif phase == 2:                      # exhale: shrink
            radius = RMAX - (RMAX - RMIN) * p
            label, lab_color = "BREATHE OUT", C.BLUE
        else:                                 # hold empty
            radius = RMIN
            label, lab_color = "HOLD", C.WHITE

        # Filled ring, brightness by fraction of full size.
        frac = (radius - RMIN) / (RMAX - RMIN)
        for y in range(16):
            for x in range(0, 19):
                d = math.hypot(x - RCX, y - RCY)
                if d <= radius:
                    level = 1 + int(frac * 2.99)   # 1..3 of the GLOW ramp
                    frame.pixel(x, y, C.GLOW[min(level, 3)])
                elif d <= radius + 0.8:
                    frame.pixel(x, y, C.WHITE)      # crisp rim

        frame.text(label, x=24, y=5, color=lab_color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/breathing.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
