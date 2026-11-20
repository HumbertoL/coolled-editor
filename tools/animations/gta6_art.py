"""
Shared pieces for the gta6_* animations: a sprite stamper, two cars and a palm.

All the art is drawn for the 96x16 panel, not taken from the game.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import colors as C  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# '.' is transparent; 'k' paints black, so a sprite can cut holes in what is
# already drawn (sunglasses, door seams).
PALETTE = {
    "k": C.BLACK, "b": C.BLUE, "g": C.GREEN, "c": C.CYAN,
    "r": C.RED, "m": C.MAGENTA, "y": C.YELLOW, "w": C.WHITE,
}


def stamp(frame, rows, x, y, palette=None, flip=False):
    """Draw a sprite given as strings, top-left at (x, y)."""
    colours = dict(PALETTE, **(palette or {}))
    for dy, line in enumerate(rows):
        if flip:
            line = line[::-1]
        for dx, cell in enumerate(line):
            if cell != ".":
                frame.pixel(x + dx, y + dy, colours[cell])


# A sedan facing right, 13x5. 'B' is the body colour, 'L' a light bar slot.
SEDAN = [
    "...BBBBB.....",
    "..BcBBcB.....",
    "BBBBBBBBBBBBy",
    "rBBBBBBBBBBBB",
    ".ww......ww..",
]


def sedan(frame, x, y, body, lights=None):
    """The sedan with its roof at row y. ``lights`` is a pair for a light bar."""
    stamp(frame, SEDAN, x, y, {"B": body})
    if lights:
        frame.pixel(x + 4, y - 1, lights[0])
        frame.pixel(x + 5, y - 1, lights[0])
        frame.pixel(x + 6, y - 1, lights[1])
        frame.pixel(x + 7, y - 1, lights[1])


def palm(frame, x, base, height, colour, sway=0.0, frond=None):
    """A palm whose trunk leans right as it rises, fronds at the top."""
    frond = frond or colour
    top_x = x
    for step in range(height):
        lean = round((step / height) ** 2 * (2 + sway))
        top_x = x + lean
        frame.pixel(top_x, base - step, colour)
    top_y = base - height
    for angle, length in ((-170, 5), (-140, 4), (-40, 4), (-10, 5), (-90, 2)):
        a = math.radians(angle + sway * 6)
        for r in range(1, length + 1):
            droop = (r * r) // 6
            frame.pixel(top_x + round(math.cos(a) * r), top_y + round(math.sin(a) * r) + droop, frond)
    return top_x, top_y


def out_path(name):
    return ROOT / "src/sample" / f"{name}.jt"


def save(animation, name):
    path = out_path(name)
    animation.save(path)
    print(f"{path.name}: {animation.describe()}")
