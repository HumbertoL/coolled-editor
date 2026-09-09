#!/usr/bin/env python3
"""
Tetris -- sideways, because the panel is.

Gravity points left. Pieces fly in from the right edge and slide until they
hit the stack growing from the left wall; a full column is a cleared line. The
cells are 2x2 pixels so the well is 48 wide by 8 high, which is enough for the
pieces to be recognisable.

The game is already in progress. The stack is drawn as fourteen actual
tetrominoes, each in its shape's colour -- the same colours the falling pieces
use -- with four covered holes, the way a board looks mid-game. Six pieces
then drop in: J, Z, T, I, S, O. The Z and T rotate in flight and the S is
steered up three rows before it lands, so someone appears to be playing. The
I clears three columns at once, and the S and O each clear one more. The
sequence came from a search over placements that leave no new hole.

The loop cuts back to the starting board rather than pretending to be
seamless. 53 frames, the measured device maximum.
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

# One colour per tetromino shape, shared by the stack and the falling pieces.
SHAPE_COLOR = {
    "I": C.CYAN, "O": C.YELLOW, "T": C.MAGENTA, "S": C.GREEN,
    "Z": C.RED, "J": C.BLUE, "L": C.WHITE,
}

# The board mid-game, one letter per piece, rows top to bottom and columns
# from the left wall. Every letter is a real tetromino; BOARD_SHAPES says
# which, so it takes that shape's colour.
BOARD = [
    "AAABB....",
    "ADDBBCEEE",
    "..DDCCC.E",
    "FFGG.H...",
    "FF.GGHHH.",
    "IIIIJJKK.",
    "LLL.JJNKK",
    "LMMMMNNN.",
]
BOARD_SHAPES = {
    "A": "L", "B": "O", "C": "T", "D": "Z", "E": "J", "F": "O", "G": "Z",
    "H": "J", "I": "I", "J": "O", "K": "Z", "L": "L", "M": "I", "N": "T",
}

# Each falling piece: shape, final cells, final row, and an optional flight
# plan of (slide step, cells, row) states it passes through on the way in --
# rotations and row shifts, as if from a player. Found by search over this
# board: every one lands flush, none leaves a new hole.
PIECES = [
    ("J", [(0, 0), (1, 0), (2, 0), (2, 1)], 3, []),
    ("Z", [(0, 1), (1, 0), (1, 1), (2, 0)], 4,
     [(0, [(0, 0), (0, 1), (1, 1), (1, 2)], 4)]),                # rotates at step 2
    ("T", [(0, 1), (1, 0), (1, 1), (2, 1)], 6,
     [(0, [(0, 0), (0, 1), (0, 2), (1, 1)], 5)]),                # rotates at step 3
    ("I", [(0, 0), (1, 0), (2, 0), (3, 0)], 0, []),
    ("S", [(0, 0), (1, 0), (1, 1), (2, 1)], 2,
     [(0, None, 5), (1, None, 4), (2, None, 3)]),                # steered up a row per step
    ("O", [(0, 0), (0, 1), (1, 0), (1, 1)], 0, []),
]
ROTATE_AT = {1: 2, 2: 3}     # piece index -> slide step where the rotation lands


def fits(grid, cells, col, row):
    for dc, dr in cells:
        c, r = col + dc, row + dr
        if c < 0 or c >= COLS or r < 0 or r >= ROWS or (c, r) in grid:
            return False
    return True


def width(cells):
    return max(dc for dc, _ in cells) + 1


def landing_col(grid, cells, row):
    col = COLS - width(cells)
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


def flight_state(index, cells, row, flight, step):
    """Where the piece is and how it is turned at this slide step."""
    rotate_at = ROTATE_AT.get(index, 0)
    for at, plan_cells, plan_row in flight:
        if step >= at and step < (rotate_at if plan_cells else at + 1):
            return plan_cells or cells, plan_row
    return cells, row


def initial_grid():
    grid = {}
    for r, line in enumerate(BOARD):
        for c, letter in enumerate(line):
            if letter != ".":
                grid[(c, r)] = SHAPE_COLOR[BOARD_SHAPES[letter]]
    assert not full_columns(grid), "the starting board has a full column"
    return grid


def build():
    anim = Animation(delay=DELAY)
    grid = initial_grid()
    for index, (shape, cells, row, flight) in enumerate(PIECES):
        color = SHAPE_COLOR[shape]
        start = COLS - width(cells)
        target = landing_col(grid, cells, row)
        for step in range(SLIDE_FRAMES):
            t = (step + 1) / SLIDE_FRAMES
            now_cells, now_row = flight_state(index, cells, row, flight, step)
            col = target if step == SLIDE_FRAMES - 1 else round(start - (start - target) * t)
            col = min(col, COLS - width(now_cells))
            frame = anim.frame()
            draw(frame, grid)
            draw(frame, {(col + dc, now_row + dr): color for dc, dr in now_cells})
        for dc, dr in cells:
            grid[(target + dc, row + dr)] = color
        full = full_columns(grid)
        if full:
            for k in range(FLASH_FRAMES):
                draw(anim.frame(), grid, flashing=full, flash_on=k != 1)
            grid = clear(grid, full)
        draw(anim.frame(), grid)
    assert len(anim) <= FRAMES, len(anim)
    while len(anim) < FRAMES:
        draw(anim.frame(), grid)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tetris.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
