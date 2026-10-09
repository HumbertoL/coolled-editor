#!/usr/bin/env python3
"""
Tic-tac-toe -- a finished game played out on the board, ending in a draw.

X and O alternate through a fixed game that is drawn with best play. Each move
takes three frames: a yellow cursor on the chosen cell for two, then the mark
is placed. Xs are RED diagonals, Os CYAN rings, the grid is BLUE. When the
board fills, DRAW blinks in the margin for the rest of the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 260
ORIGIN_X, ORIGIN_Y = 2, 1
CELL = 4
PITCH = 5
# (cell index 0..8 row-major, mark). A draw with best play from both sides.
MOVES = [(4, "X"), (0, "O"), (2, "X"), (6, "O"), (3, "X"), (5, "O"), (7, "X"), (1, "O"), (8, "X")]
RING = [(1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (1, 3), (2, 3)]


def cell_origin(cell):
    row, col = divmod(cell, 3)
    return ORIGIN_X + col * PITCH, ORIGIN_Y + row * PITCH


def draw_grid(frame):
    for offset in (CELL, CELL + PITCH):
        frame.vline(ORIGIN_X + offset, ORIGIN_Y, 3 * PITCH - 1, C.BLUE)
        frame.hline(ORIGIN_X, ORIGIN_Y + offset, 3 * PITCH - 1, C.BLUE)


def draw_mark(frame, cell, mark):
    x, y = cell_origin(cell)
    if mark == "X":
        for k in range(CELL):
            frame.pixel(x + k, y + k, C.RED)
            frame.pixel(x + CELL - 1 - k, y + k, C.RED)
    else:
        for dx, dy in RING:
            frame.pixel(x + dx, y + dy, C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    placed = {}
    for turn, (cell, mark) in enumerate(MOVES):
        base = turn * 3
        for step in range(3):
            frame = anim.frame()
            draw_grid(frame)
            for done_cell, done_mark in placed.items():
                draw_mark(frame, done_cell, done_mark)
            if step < 2:
                x, y = cell_origin(cell)
                frame.rect(x, y, CELL, CELL, C.YELLOW, fill=False)
            else:
                placed[cell] = mark
                draw_mark(frame, cell, mark)
        del base
    board_end = len(MOVES) * 3
    frame_index = board_end
    while len(anim) < FRAMES:
        frame = anim.frame()
        draw_grid(frame)
        for done_cell, done_mark in placed.items():
            draw_mark(frame, done_cell, done_mark)
        frame.small_text("TIC TAC TOE", x=24, y=2, color=C.WHITE)
        if (frame_index // 4) % 2 == 0:
            frame.text("DRAW", x=24, y=8, color=C.YELLOW)
        frame_index += 1
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tic_tac_toe.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
