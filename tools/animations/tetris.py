#!/usr/bin/env python3
"""
Tetris -- sideways, because the panel is.

Gravity points left. Pieces fly in from the right edge and slide until they
hit the stack growing from the left wall; a full column is a cleared line. The
cells are 2x2 pixels so the well is 48 wide by 8 high, which is enough for the
pieces to be recognisable.

Six pieces -- I, O, T, L, Z, T -- land per loop. The L completes a column,
which flashes and drops out; the final T completes two at once, a double,
and the well is empty again. So the loop is a perfect clear that starts and
ends on nothing, and ALL CLEAR flashes across the empty well before the next
I piece arrives. The sequence came out of a search over piece orders, since
a hand-designed one kept leaving a stray cell behind.

Uses 53 frames, the measured device maximum, for a six-frame slide per piece.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

COLS, ROWS = 48, 8
SLIDE_FRAMES = 6
FLASH_FRAMES = 3

# (cells relative to (col, row), row, colour). Found by search: from an empty
# well these six land, clear three columns, and leave it empty.
PIECES = [
    ([(0, 0), (0, 1), (0, 2), (0, 3)], 1, C.CYAN),             # I
    ([(0, 0), (0, 1), (1, 0), (1, 1)], 5, C.YELLOW),           # O
    ([(0, 0), (1, 0), (1, 1), (2, 0)], 0, C.MAGENTA),          # T, nub down
    ([(0, 1), (1, 1), (2, 0), (2, 1)], 6, C.RED),              # L  -> clears 1
    ([(0, 0), (0, 1), (1, 1), (1, 2)], 3, C.GREEN),            # Z
    ([(0, 1), (1, 0), (1, 1), (1, 2)], 1, C.BLUE),             # T  -> clears 2
]


def fits(grid, cells, col, row):
    for dc, dr in cells:
        c, r = col + dc, row + dr
        if c < 0 or c >= COLS or r < 0 or r >= ROWS or (c, r) in grid:
            return False
    return True


def entry_col(cells):
    return COLS - 1 - max(dc for dc, _ in cells)


def landing_col(grid, cells, row):
    col = entry_col(cells)
    while col > 0 and fits(grid, cells, col - 1, row):
        col -= 1
    return col


def full_columns(grid):
    return [c for c in range(COLS) if all((c, r) in grid for r in range(ROWS))]


def clear(grid, columns):
    for col in sorted(columns, reverse=True):
        grid = {
            (c - 1 if c > col else c, r): color
            for (c, r), color in grid.items()
            if c != col
        }
    return grid


def draw(frame, grid, flashing=(), flash_on=True):
    for (c, r), color in grid.items():
        if c in flashing:
            color = C.WHITE if flash_on else color
        frame.rect(c * 2, r * 2, 2, 2, color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    grid = {}
    for cells, row, color in PIECES:
        start = entry_col(cells)
        target = landing_col(grid, cells, row)
        for step in range(SLIDE_FRAMES):
            t = (step + 1) / SLIDE_FRAMES
            col = target if step == SLIDE_FRAMES - 1 else round(start - (start - target) * t)
            frame = anim.frame()
            draw(frame, grid)
            draw(frame, {(col + dc, row + dr): color for dc, dr in cells})
        for dc, dr in cells:
            grid[(target + dc, row + dr)] = color
        full = full_columns(grid)
        if full:
            for k in range(FLASH_FRAMES):
                draw(anim.frame(), grid, flashing=full, flash_on=k != 1)
            grid = clear(grid, full)
        draw(anim.frame(), grid)
    assert not grid, grid
    while len(anim) < FRAMES:
        frame = anim.frame()
        frame.text("ALL CLEAR", "center", 4, C.GREEN if len(anim) % 2 else C.WHITE)
    assert len(anim) == FRAMES, len(anim)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tetris.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
