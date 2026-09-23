#!/usr/bin/env python3
"""
Scholar's Mate -- four moves, and black resigns before the tea is cold.

An 8x8 board at two pixels a square is exactly sixteen rows, so a real
chessboard fills the left edge of the panel: blue and black squares, white's
army in white, black's in magenta. Pieces are solid 2x2 blocks and pawns
half-height dashes, which is all the resolution allows. Each move lifts off
a highlighted square, slides across the board and lands in green, while the score sheet on the right
writes itself in proportional type and scrolls: 1.E4 E5, 2.BC4 NC6,
3.QH5 NF6?? -- and then 4.QXF7#. The black king's square blinks red and
CHECKMATE flashes underneath.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 170

LIGHT, DARK = C.BLUE, C.BLACK
HIGHLIGHT = C.GREEN
SIDE_COLOR = {"w": C.WHITE, "b": C.MAGENTA}

# Pixel offsets inside a piece's 2x2 cell. Solid blocks read far better on
# the LEDs than per-piece glyphs; pawns are the half-height bottom row, so the
# pawn ranks look like pawns and a moving pawn is a two-pixel dash.
SHAPES = {
    "P": [(0, 1), (1, 1)],
    "N": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "B": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "Q": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "R": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "K": [(0, 0), (1, 0), (0, 1), (1, 1)],
}

# (from, to, text appended to the score sheet)
PLIES = [
    ("e2", "e4", "1.E4"),
    ("e7", "e5", "E5"),
    ("f1", "c4", "2.BC4"),
    ("b8", "c6", "NC6"),
    ("d1", "h5", "3.QH5"),
    ("g8", "f6", "NF6??"),
    ("h5", "f7", "4.QXF7#"),
]
START_HOLD = 3
PLY_FRAMES = 5  # lift, slide, slide, land, hold
MATE_AT = START_HOLD + PLY_FRAMES * (len(PLIES) - 1) + 4
TEXT_X = 20
LINE_GAP = 9


def square_xy(name):
    file = ord(name[0]) - ord("a")
    rank = int(name[1])
    return file * 2, (8 - rank) * 2


def starting_position():
    board = {}
    back = "RNBQKBNR"
    for i, piece in enumerate(back):
        f = "abcdefgh"[i]
        board[f + "1"] = ("w", piece)
        board[f + "8"] = ("b", piece)
        board[f + "2"] = ("w", "P")
        board[f + "7"] = ("b", "P")
    return board


def draw_board(frame, highlights, red=None):
    for file in range(8):
        for rank in range(8):
            light = (file + rank) % 2 == 0
            color = LIGHT if light else DARK
            name = "abcdefgh"[file] + str(8 - rank)
            if name in highlights:
                color = HIGHLIGHT
            if name == red:
                color = C.RED
            frame.rect(file * 2, rank * 2, 2, 2, color, fill=True)


def draw_piece(frame, x, y, piece, color=None):
    side, kind = piece
    for dx, dy in SHAPES[kind]:
        frame.pixel(x + dx, y + dy, color or SIDE_COLOR[side])


def build():
    anim = Animation(delay=DELAY)

    # Precompute the board before each ply.
    boards = [starting_position()]
    for src, dst, _ in PLIES:
        board = dict(boards[-1])
        board[dst] = board.pop(src)
        boards.append(board)

    scroll = 0
    for index in range(FRAMES):
        frame = anim.frame()
        t = index - START_HOLD
        ply = -1 if t < 0 else min(len(PLIES) - 1, t // PLY_FRAMES)
        phase = -1 if t < 0 else (t - ply * PLY_FRAMES)
        mating = index >= MATE_AT

        # Which plies have been written down so far?
        written = 0
        if ply >= 0:
            written = ply + (1 if phase >= 3 else 0)

        highlights = set()
        moving = None
        if ply < 0:
            board = boards[0]
        elif phase >= 3:
            board = boards[ply + 1]
            highlights = {PLIES[ply][0], PLIES[ply][1]}
        else:
            board = dict(boards[ply])
            src, dst, _ = PLIES[ply]
            piece = board.pop(src)
            highlights = {src}
            sx, sy = square_xy(src)
            dx, dy = square_xy(dst)
            f = phase / 3
            moving = (round(sx + (dx - sx) * f), round(sy + (dy - sy) * f), piece)

        blink_on = mating and (index - MATE_AT) % 2 == 0
        draw_board(frame, highlights, red="e8" if blink_on else None)
        for name, piece in board.items():
            x, y = square_xy(name)
            color = None
            if mating and name == "e8" and blink_on:
                color = C.RED
            draw_piece(frame, x, y, piece, color)
        if moving:
            draw_piece(frame, *moving)
        # Board edge, so the right-hand side reads as a separate panel.
        frame.vline(17, 0, 16, C.BLUE)

        # Score sheet: one line per move number, black's reply appended.
        lines = []
        for i in range(written):
            text = PLIES[i][2]
            if i % 2 == 0:
                lines.append([(text, SIDE_COLOR["w"])])
            else:
                lines[-1].append((text, SIDE_COLOR["b"]))
        if mating:
            lines.append([("CHECKMATE", C.RED if blink_on else C.YELLOW)])
        target = LINE_GAP * max(0, len(lines) - 2)
        scroll = min(target, scroll + 3) if scroll < target else target
        for row, parts in enumerate(lines):
            y = row * LINE_GAP - scroll
            if y < -7 or y > 15:
                continue
            x = TEXT_X
            for text, color in parts:
                frame.text(text, x, y, color, proportional=True)
                x += frame.text_width(text, proportional=True) + 4
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/chess_mate.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
