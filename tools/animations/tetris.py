#!/usr/bin/env python3
"""
Tetris -- sideways, because the panel is.

Gravity points left. Pieces fly in from the right edge and slide until they
hit the stack growing from the left wall; a full column is a cleared line. The
cells are 2x2 pixels so the well is 48 wide by 8 high, which is enough for the
pieces to be recognisable.

Three pieces land per loop. The I completes a column, which flashes white
and drops out, shifting everything past it back by one; the T then plugs the
gap in the wall column and clears that too. Place, clear, shift, twice over.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 120

COLS, ROWS = 48, 8
ENTRY_COL = 46
SLIDE_FRAMES = 5

INITIAL = {
    **{(0, r): C.BLUE for r in range(ROWS) if r != 3},
    **{(1, r): C.GREEN for r in (0, 1, 6, 7)},
    **{(2, r): C.RED for r in (0, 7)},
}
# (cells relative to (col, row), row offset, colour)
PIECES = [
    ([(0, 0), (0, 1), (0, 2), (0, 3)], 2, C.CYAN),           # I, fills column 1
    ([(1, 0), (0, 1), (1, 1), (1, 2)], 2, C.MAGENTA),        # T, pointing left
    ([(0, 0), (0, 1), (0, 2), (1, 2)], 4, C.YELLOW),         # L
]


def fits(grid, cells, col, row):
    for dc, dr in cells:
        c, r = col + dc, row + dr
        if c < 0 or c >= COLS or r < 0 or r >= ROWS or (c, r) in grid:
            return False
    return True


def landing_col(grid, cells, row):
    col = ENTRY_COL
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


def draw(frame, grid, flashing=()):
    for (c, r), color in grid.items():
        frame.rect(c * 2, r * 2, 2, 2, C.WHITE if c in flashing else color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    grid = dict(INITIAL)
    for cells, row, color in PIECES:
        target = landing_col(grid, cells, row)
        for step in range(SLIDE_FRAMES):
            col = round(ENTRY_COL - (ENTRY_COL - target) * (step + 1) / SLIDE_FRAMES) if step < SLIDE_FRAMES - 1 else target
            frame = anim.frame()
            draw(frame, grid)
            draw(frame, {(col + dc, row + dr): color for dc, dr in cells})
        for dc, dr in cells:
            grid[(target + dc, row + dr)] = color
        full = full_columns(grid)
        if full:
            for _ in range(2):
                draw(anim.frame(), grid, flashing=full)
            grid = clear(grid, full)
        draw(anim.frame(), grid)
    while len(anim) < FRAMES:
        draw(anim.frame(), grid)
    assert len(anim) == FRAMES, len(anim)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tetris.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
