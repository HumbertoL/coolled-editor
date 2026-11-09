#!/usr/bin/env python3
"""
Split-flap -- a station departure board clattering between two flights.

Every cell is its own little drum of flaps in a fixed order: blank, A to Z,
0 to 9, then punctuation. A drum can only turn forwards, so a cell that needs
to go from T to M has to rattle all the way round through the digits, while
its neighbour going from K to L is done in one step. Cells therefore settle
at different moments, which is the whole charm of the real thing.

Drums turn three flaps a frame. A moving cell is drawn white with the
horizontal split of a flap caught mid-fall; it takes its line's colour when
it lands. The second flight is to Mars and is delayed forty years.

14 frames on the first board, 13 turning, 13 on the second, 13 turning back:
53, and the last turn lands on frame 0, so the loop is seamless.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
DRUM = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:?"
SPEED = 3
TURN = 13             # frames allowed for a change; ceil(len(DRUM) / SPEED)
HOLD_A = 14
HOLD_B = FRAMES - HOLD_A - 2 * TURN

BOARDS = [
    (("09:40 TOKYO   B7", C.YELLOW), ("NOW BOARDING    ", C.GREEN)),
    (("11:05 MARS    ??", C.YELLOW), ("DELAYED 40 YEARS", C.RED)),
]
LINE_Y = (0, 9)

assert TURN * SPEED >= len(DRUM) - 1
for board in BOARDS:
    for text, _color in board:
        assert len(text) == 16 and all(ch in DRUM for ch in text), text


def cell_at(old, new, turned):
    """The flap showing after ``turned`` frames of turning, and whether it has landed."""
    start = DRUM.index(old)
    steps = (DRUM.index(new) - start) % len(DRUM)
    moved = min(SPEED * turned, steps)
    return DRUM[(start + moved) % len(DRUM)], moved == steps


def schedule(index):
    """(board showing, board arriving, frames into the turn) for a frame."""
    if index < HOLD_A:
        return 0, 0, 0
    index -= HOLD_A
    if index < TURN:
        return 0, 1, index + 1
    index -= TURN
    if index < HOLD_B:
        return 1, 1, 0
    return 1, 0, index - HOLD_B + 1


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        old, new, turned = schedule(index)
        for line in range(2):
            old_text = BOARDS[old][line][0]
            new_text, color = BOARDS[new][line]
            for cell in range(16):
                char, landed = cell_at(old_text[cell], new_text[cell], turned)
                x, y = cell * 6, LINE_Y[line]
                if landed:
                    frame.text(char, x, y, color)
                else:
                    frame.text(char, x, y, C.WHITE)
                    frame.hline(x, y + 3, 5, C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/split_flap.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
