#!/usr/bin/env python3
"""
Coffee -- a hot mug, steaming. The universal "give me a minute".

A mug with a handle sits centre-panel while three ribbons of steam rise and
waver above it, drifting sideways as they climb and fading from white to cyan to
nothing at the top. Every so often a little heart forms in the steam, because
the coffee is loved. A cosy desk-status loop.

Seamless: the steam's sway is driven by one phase that advances 2*pi/FRAMES per
frame, so the ribbons flow back into themselves.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 110
W, H = 96, 16

MUG_X, MUG_Y = 40, 9        # top-left of the mug body
MUG_W, MUG_H = 16, 6
STEAM_XS = [44, 48, 52]     # base columns of the three ribbons


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        # Steam ribbons rising above the mug.
        for i, sx in enumerate(STEAM_XS):
            for step in range(8):
                y = MUG_Y - 1 - step
                if y < 0:
                    break
                x = sx + 2 * math.sin(phase + step * 0.6 + i * 2.0)
                # Fade with height: white low, cyan mid, gone near the top.
                if step < 3:
                    color = C.WHITE
                elif step < 6:
                    color = C.CYAN
                else:
                    color = C.BLUE
                frame.pixel(x, y, color)

        # Mug body, rim and handle.
        frame.rect(MUG_X, MUG_Y, MUG_W, MUG_H, C.WHITE)
        frame.hline(MUG_X, MUG_Y, MUG_W, C.CYAN)              # rim
        # Handle on the right.
        frame.pixel(MUG_X + MUG_W, MUG_Y + 1, C.WHITE)
        frame.pixel(MUG_X + MUG_W + 1, MUG_Y + 2, C.WHITE)
        frame.pixel(MUG_X + MUG_W, MUG_Y + 3, C.WHITE)
        # Coffee surface just under the rim.
        frame.hline(MUG_X + 1, MUG_Y + 1, MUG_W - 2, C.RED)
        # Saucer.
        frame.hline(MUG_X - 2, MUG_Y + MUG_H, MUG_W + 4, C.BLUE)

        # A heart blooms in the steam for part of the loop.
        if 16 <= index < 30:
            hx, hy = 48, 1
            frame.glyph("+HEART", x=hx, y=hy, color=C.RED)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/coffee.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
