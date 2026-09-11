#!/usr/bin/env python3
"""
Turing machine -- the 3-state busy beaver, run to the end.

A tape of cells, a head above it, and the current state in the corner. The
rules are the three-state busy beaver champion: the machine that writes the
most ones before halting, of all three-state machines. It takes fourteen
steps and leaves six ones, then halts -- and halting is the point, because
in general you cannot know whether a machine will.

Each step is three frames: read (head lights), write (cell changes), move.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
# state -> symbol -> (write, move, next). H halts.
RULES = {
    "A": {0: (1, +1, "B"), 1: (1, +1, "H")},
    "B": {0: (0, +1, "C"), 1: (1, +1, "B")},
    "C": {0: (1, -1, "C"), 1: (1, -1, "A")},
}
CELLS = 15
CELL_W = 6
TAPE_X, TAPE_Y = 3, 9
FRAMES_PER_STEP = 3
START_CELL = 6


def run():
    tape = {}
    pos, state = START_CELL, "A"
    history = []
    while state != "H":
        symbol = tape.get(pos, 0)
        write, move, nxt = RULES[state][symbol]
        history.append((dict(tape), pos, state, write, move))
        tape[pos] = write
        pos += move
        state = nxt
    history.append((dict(tape), pos, "H", None, 0))
    return history


def build():
    history = run()
    anim = Animation(delay=DELAY)
    steps = len(history) - 1
    for index in range(FRAMES):
        frame = anim.frame()
        step = min(steps, index // FRAMES_PER_STEP)
        phase = index % FRAMES_PER_STEP if step < steps else 2
        tape, pos, state, write, move = history[step]
        halted = state == "H"
        shown = dict(tape)
        if not halted and phase >= 1:
            shown[pos] = write
        head_pos = pos + (move if (not halted and phase >= 2) else 0)

        for cell in range(CELLS):
            x = TAPE_X + cell * CELL_W
            value = shown.get(cell, 0)
            if value:
                frame.rect(x, TAPE_Y, 5, 5, C.YELLOW if halted else C.WHITE, fill=True)
            else:
                frame.rect(x, TAPE_Y, 5, 5, C.BLUE)
        hx = TAPE_X + head_pos * CELL_W + 2
        head = C.RED if halted else (C.WHITE if phase == 0 else C.CYAN)
        frame.pixel(hx, TAPE_Y - 2, head)
        frame.hline(hx - 1, TAPE_Y - 3, 3, head)
        frame.hline(hx - 2, TAPE_Y - 4, 5, head)

        if halted:
            ones = sum(tape.values())
            frame.text(f"HALT  {ones} ONES", 2, 0, C.RED if index % 2 else C.YELLOW, proportional=True)
        else:
            frame.text(f"STATE {state}", 2, 0, C.WHITE, proportional=True)
            frame.text(f"STEP {step}", 60, 0, C.CYAN, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/turing_machine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
