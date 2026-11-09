#!/usr/bin/env python3
"""
Prism -- a beam of white light split into its spectrum.

The panel's palette is one bit per channel: besides black and white it has
exactly six colours, and in order they are the spectrum -- red, yellow,
green, cyan, blue, magenta. So this is the one picture the sign can draw
with every colour it owns and none left over.

The loop tells it as an event. A white pulse crosses from the left, climbs
slightly to meet the glass, fans out inside it, and leaves the far face as
six diverging bands that reach the edge of the panel. White glints run down
the bands while the beam holds; then the tail of the pulse sweeps through
and the panel is dark, with only the prism left, ready for the next one.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SPECTRUM = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]
BEAM_SPEED = 4
TAIL_START = 40           # frame the back of the pulse enters from the left
TAIL_SPEED = 9
ENTRY = (42, 9)           # where the beam meets the left face
EXIT_X = 53


def left_face(y):
    return 47 - 9 * y / 15


def right_face(y):
    return 48 + 9 * y / 15


def beam_y(x):
    return round(12 - 3 * x / ENTRY[0])


def light_at(x, y):
    """What the fully lit scene shows at a pixel: a colour, or None for dark."""
    if x < left_face(y) - 0.5:
        return C.WHITE if x <= ENTRY[0] and y == beam_y(x) else None
    if x <= right_face(y) + 0.5:
        # Inside the glass: a fan opening from the entry point.
        t = (x - ENTRY[0]) / (EXIT_X - ENTRY[0])
        if 0 <= t and ENTRY[1] - 1.6 * t - 0.5 <= y <= ENTRY[1] + 1.2 * t + 0.5:
            return C.WHITE
        return None
    t = (x - EXIT_X) / (95 - EXIT_X)
    top = 7.0 - 6.0 * t
    bottom = 10.6 + 4.4 * t
    band = int((y + 0.5 - top) / (bottom - top) * 6)
    if y + 0.5 < top or not 0 <= band < 6:
        return None
    return SPECTRUM[band]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        head = BEAM_SPEED * (index + 1)
        tail = TAIL_SPEED * (index - TAIL_START) if index >= TAIL_START else -1
        for y in range(16):
            for x in range(96):
                color = light_at(x, y) if tail < x <= head else None
                if color is None:
                    continue
                # Glints travel outward along the bands once the beam is established.
                if x > right_face(y) + 1 and (x - 5 * index + 3 * y) % 24 < 2:
                    color = C.WHITE
                frame.pixel(x, y, color)
        # The glass itself, drawn last so its edges stay crisp.
        for y in range(16):
            frame.pixel(round(left_face(y)), y, C.CYAN)
            frame.pixel(round(right_face(y)), y, C.CYAN)
        frame.hline(38, 15, 20, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/prism.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
