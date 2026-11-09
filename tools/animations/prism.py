#!/usr/bin/env python3
"""
Prism -- a pulse of white light split into the six colours the panel has.

A finite pulse enters from the left at 4 pixels a frame, climbs slightly to
the glass, crosses it, and leaves as a fan: red on top, bending least, down
through yellow, green, cyan and blue to magenta. Its tail follows 26 frames
behind, so the light switches off the same way it switched on and the loop
closes on a dark panel. While the fan is lit, white glints travel out along
each band.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52
DELAY = 90
SPEED = 4
PULSE = 26  # frames between the head and the tail of the pulse

APEX = (48, 1)
BASE_Y = 14
HALF_BASE = 9
ENTRY = (43, 8)
EXIT = (53, 7)
BANDS = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]


def beam_pixels():
    """Every lit pixel of the full beam as (path position, x, y, colour)."""
    out = []
    for x in range(ENTRY[0]):
        out.append((x, x, round(12 - 4 * x / ENTRY[0]), C.WHITE))
    for x in range(ENTRY[0], EXIT[0] + 1):
        out.append((x, x, 8 if x < 49 else 7, C.WHITE))
    for x in range(EXIT[0] + 1, 96):
        t = (x - EXIT[0]) / (95 - EXIT[0])
        top = 7 - 4.4 * t
        bottom = 7.9 + 7.0 * t
        for y in range(16):
            if top <= y + 0.5 <= bottom + 0.6:
                band = int((y + 0.5 - top) / (bottom + 0.6 - top) * len(BANDS))
                out.append((x, x, y, BANDS[min(band, len(BANDS) - 1)]))
    return out


def draw_prism(frame):
    left = (APEX[0] - HALF_BASE, BASE_Y)
    right = (APEX[0] + HALF_BASE, BASE_Y)
    frame.line(*APEX, *left, C.CYAN)
    frame.line(*APEX, *right, C.CYAN)
    frame.line(*left, *right, C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    beam = beam_pixels()
    for index in range(FRAMES):
        frame = anim.frame()
        head = SPEED * index
        tail = SPEED * (index - PULSE)
        for position, x, y, colour in beam:
            if tail <= position < head:
                if x > EXIT[0] + 6 and (x - 3 * index) % 14 == 0:
                    colour = C.WHITE
                frame.pixel(x, y, colour)
        draw_prism(frame)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/prism.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
