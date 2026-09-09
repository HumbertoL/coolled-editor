#!/usr/bin/env python3
"""
Hourglass -- three of them, out of phase.

Sand drains from the top bulb, funnelling from the centre, and heaps into a
cone below. When the top is empty the glass turns over with a card flip --
squashing to a line and reopening mirrored -- and lands upside down, which
is the starting picture again. Each
glass runs the same 24-frame cycle a third of a loop apart.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 24
DELAY = 130

HALF_WIDTH = [5, 5, 4, 3, 2, 1, 0, 0, 1, 2, 3, 4, 5, 5]   # rows 1..14
GRAINS = 40
DRAIN_FRAMES = 20
CENTRES = [16, 48, 80]
FLIP_SCALES = [0.55, 0.12, -0.55]     # frames 21..23; frame 24 (= 0) is -1


def glass(cx):
    canvas = Canvas(32, 16)
    x = 16
    canvas.hline(x - 6, 0, 13, C.WHITE)
    canvas.hline(x - 6, 15, 13, C.WHITE)
    for row, hw in enumerate(HALF_WIDTH, start=1):
        canvas.pixel(x - hw - 1, row, C.CYAN)
        canvas.pixel(x + hw + 1, row, C.CYAN)
    return canvas


def bulb_cells(rows):
    cells = []
    for row in rows:
        hw = HALF_WIDTH[row - 1]
        cells.extend((16 + dx, row) for dx in range(-hw, hw + 1))
    return cells


TOP = sorted(bulb_cells(range(1, 7)), key=lambda c: (c[1], abs(c[0] - 16)))
BOTTOM = sorted(bulb_cells(range(9, 15)), key=lambda c: (-c[1] + 0.7 * abs(c[0] - 16), abs(c[0] - 16)))


def render_state(step):
    """One hourglass at drain step 0..DRAIN_FRAMES, as a 32x16 canvas."""
    canvas = glass(16)
    moved = round(GRAINS * step / DRAIN_FRAMES)
    for x, y in TOP[len(TOP) - (GRAINS - moved):] if moved < GRAINS else []:
        canvas.pixel(x, y, C.YELLOW)
    for x, y in BOTTOM[:moved]:
        canvas.pixel(x, y, C.YELLOW)
    if 0 < moved < GRAINS:
        canvas.vline(16, 7, 2, C.YELLOW)
        canvas.pixel(16, 9 + (step % 3), C.WHITE)
    return canvas


def flipped(source, scale):
    """
    Scale the tile vertically about its middle; a negative scale mirrors it.

    Stepping the scale 1 -> 0 -> -1 is a card flip: the glass squashes to a
    line and reopens upside down, which is how it turns over without any part
    of the 16-row picture being clipped.
    """
    out = Canvas(source.width, source.height)
    cy = (source.height - 1) / 2
    for y in range(out.height):
        sy = round(cy + (y - cy) / scale)
        if 0 <= sy < source.height:
            for x in range(out.width):
                out.pixel(x, y, source.get(x, sy))
    return out


def build():
    anim = Animation(delay=DELAY)
    drained = render_state(DRAIN_FRAMES)
    for index in range(FRAMES):
        frame = anim.frame()
        for i, cx in enumerate(CENTRES):
            step = (index + i * FRAMES // 3) % FRAMES
            if step <= DRAIN_FRAMES:
                tile = render_state(step)
            else:
                tile = flipped(drained, FLIP_SCALES[step - DRAIN_FRAMES - 1])
            frame.blit(tile, cx - 16, 0)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hourglass.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
