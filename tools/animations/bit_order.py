#!/usr/bin/env python3
"""
bit_order -- the panel paints itself the way this file is stored.

A .jt keeps its three colour planes one after another: every red bit first,
then every green, then every blue, and within a plane each column is walked
top to bottom before moving right. This piece draws a small landscape -- sky,
sun, cloud, a tree, a red house with a magenta roof, a pond, and the word LED
-- in exactly that order. A white scan head sweeps the columns, ~93 bits a
frame so it stops part way down a column each time; first only the red bits
land, so the picture appears in red and black. The green pass goes over it
and red turns yellow where both are set, and the blue pass finishes the
eight colours: sky, cyan pond, magenta roof, white text. The plane being
written is labelled R, G or B at the left, with a progress square for each,
and the finished picture holds under a check mark before the loop.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
PIC_X = 9                      # picture occupies columns 9..95
PIC_W = 96 - PIC_X
PER_PLANE = 15                 # frames per colour plane
BITS = PIC_W * 16
PLANE_NAMES = ("R", "G", "B")
PLANE_COLOURS = (C.RED, C.GREEN, C.BLUE)


def picture():
    """The finished full-colour scene, in panel coordinates."""
    pic = Canvas()
    for x in range(PIC_X, 96):
        for y in range(16):
            pic.pixel(x, y, C.BLUE if y < 12 else C.GREEN)
    # Sun.
    for x in range(84, 93):
        for y in range(0, 8):
            if math.hypot(x - 88, y - 3.5) < 3.4:
                pic.pixel(x, y, C.YELLOW)
    # Cloud.
    for x in range(62, 78):
        for y in range(1, 6):
            if any(math.hypot(x - bx, y - by) < br for bx, by, br in
                   ((66, 4, 2.2), (70, 2.8, 2.6), (74, 4, 2.0))):
                pic.pixel(x, y, C.WHITE)
    # Word.
    pic.text("LED", 12, 2, C.WHITE)
    # Tree: crown and trunk.
    for x in range(32, 39):
        for y in range(3, 10):
            if math.hypot(x - 35, y - 6) < 3.2:
                pic.pixel(x, y, C.GREEN)
    pic.vline(35, 9, 3, C.RED)
    # House: magenta roof, red walls, black door, cyan window.
    for r in range(4):
        pic.hline(47 - r, 4 + r, 3 + 2 * r, C.MAGENTA)
    pic.rect(44, 8, 9, 4, C.RED, fill=True)
    pic.rect(49, 9, 2, 3, C.BLACK, fill=True)
    pic.rect(45, 9, 2, 1, C.CYAN, fill=True)
    # Pond.
    for x in range(58, 78):
        for y in range(12, 16):
            if ((x - 67.5) / 9.5) ** 2 + ((y - 13.5) / 1.6) ** 2 < 1:
                pic.pixel(x, y, C.CYAN)
    # Flowers in the grass.
    for x, colour in ((14, C.MAGENTA), (19, C.YELLOW), (24, C.RED), (40, C.MAGENTA),
                      (55, C.YELLOW), (82, C.RED), (87, C.MAGENTA), (92, C.YELLOW)):
        pic.pixel(x, 13 + (x % 2), colour)
    return pic


def draw_label(frame, plane, index):
    if plane is None:
        frame.glyph("+CHECK", 1, 1, C.WHITE)
    else:
        frame.text(PLANE_NAMES[plane], 1, 1, PLANE_COLOURS[plane])
    for p in range(3):
        colour = PLANE_COLOURS[p]
        done = plane is None or p < plane
        if done or (p == plane and index % 2 == 0):
            frame.rect(p * 3, 11, 2, 2, colour, fill=True)
        elif p == plane:
            frame.pixel(p * 3, 12, colour)


def build():
    pic = picture()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        plane = index // PER_PLANE if index < 3 * PER_PLANE else None
        if plane is None:
            frame.blit(pic)
            draw_label(frame, None, index)
            continue
        step = index % PER_PLANE
        written = round((step + 1) * BITS / PER_PLANE)
        head_col, head_row = divmod(written, 16)
        for x in range(PIC_X, 96):
            for y in range(16):
                bit = ((x - PIC_X) * 16 + y) < written
                full = pic.get(x, y)
                # Planes before this one are complete; this one is complete
                # up to the head; later planes are not written yet.
                shown = tuple(
                    full[ch] if (ch < plane or (ch == plane and bit)) else 0
                    for ch in range(3)
                )
                frame.pixel(x, y, shown)
        if head_col < PIC_W:
            frame.vline(PIC_X + head_col, head_row, 16 - head_row, C.WHITE)
        draw_label(frame, plane, index)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bit_order.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
