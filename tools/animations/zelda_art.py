"""
Shared pixel art for the Legend of Zelda animations (zelda_*.py, oot_*.py).

Sprites are lists of strings, one character per pixel. ``.`` is transparent;
``K`` is opaque black, for punching an eye or a gap through art drawn behind.
Every other letter is a palette color. All art here is drawn for this panel,
not lifted from the games.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import colors as C  # noqa: E402

INK = {
    "K": C.BLACK,
    "B": C.BLUE,
    "G": C.GREEN,
    "C": C.CYAN,
    "R": C.RED,
    "M": C.MAGENTA,
    "Y": C.YELLOW,
    "W": C.WHITE,
}

# The hero, facing right: cap trailing back, yellow hair, green tunic, white
# tights, red boots. 8 wide, 13 tall. Two walk frames share the top half.
_HERO_TOP = [
    "...GGG..",
    "..GGGGG.",
    ".GGGGGGG",
    "GG.YYYYY",
    "G..YYKYY",
    "...YYYY.",
    "..GGGGG.",
    ".GGGGGYY",
    ".GYGGGG.",
    "..GGGGG.",
]
HERO = _HERO_TOP + ["..GGGGG.", "..W..W..", "..R..R.."]
HERO_STEP = _HERO_TOP + [".GGGGGG.", ".W....W.", "RR....RR"]

# Arms up, holding something overhead: the treasure pose. Hands on row 0.
HERO_ARMS_UP = [
    ".Y....Y.",
    ".G.GG.G.",
    ".GGGGGG.",
    "GGGGGGGG",
    "G.YYYY.G",
    "..YKYK..",
    "..YYYY..",
    "..GGGG..",
    ".GGYGGG.",
    "..GGGG..",
    "..GGGG..",
    "..W..W..",
    "..R..R..",
]

HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]

RUPEE = [
    "..#..",
    ".#h#.",
    "##h##",
    "##h##",
    "##h##",
    "##h##",
    "##h##",
    ".###.",
    "..#..",
]

#: (body, highlight) for each rupee value, as in the series' color code.
RUPEE_COLORS = {
    1: (C.GREEN, C.WHITE),
    5: (C.BLUE, C.CYAN),
    20: (C.RED, C.YELLOW),
    50: (C.MAGENTA, C.WHITE),
}


def stamp(frame, rows, x, y, ink=None, flip=False):
    """Draw ``rows`` with its top-left at (x, y). ``ink`` maps extra letters
    (or overrides) to colors; ``flip`` mirrors left to right."""
    palette = dict(INK)
    if ink:
        palette.update(ink)
    for row, line in enumerate(rows):
        if flip:
            line = line[::-1]
        for col, cell in enumerate(line):
            if cell != "." and cell in palette:
                frame.pixel(x + col, y + row, palette[cell])


def heart(frame, x, y, halves, empty=C.BLUE, full=C.RED):
    """A heart with 0, 1 or 2 halves full: left half fills first."""
    for row, line in enumerate(HEART):
        for col, cell in enumerate(line):
            if cell == "#":
                filled = halves >= 2 or (halves == 1 and col <= 3)
                frame.pixel(x + col, y + row, full if filled else empty)


def rupee(frame, x, y, value=1):
    body, shine = RUPEE_COLORS[value]
    stamp(frame, RUPEE, x, y, {"#": body, "h": shine})


def sparkle(frame, x, y, size, color=C.WHITE):
    """A four-point twinkle: a dot, then a plus, then a longer plus."""
    frame.pixel(x, y, color)
    for d in range(1, size + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            frame.pixel(x + dx, y + dy, color if d < size else C.CYAN)
