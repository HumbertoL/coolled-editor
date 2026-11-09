#!/usr/bin/env python3
"""
Tower of Hanoi -- four discs moved peg to peg in the minimum 15 moves.

The moves come from the usual recursion. Each takes three frames: the disc
lifted clear above its peg, carried across to the destination, then dropped
onto the stack. Four frames of rest at each end make 53, and the finished
tower flashes white before the loop starts over.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 140
DISCS = 4
PEGS = [16, 48, 80]
BASE_Y = 15
DISC_H = 2
CARRY_Y = 1
COLOURS = {1: C.RED, 2: C.YELLOW, 3: C.GREEN, 4: C.CYAN}


def solve(count, source, target, spare, moves):
    if count == 0:
        return
    solve(count - 1, source, spare, target, moves)
    moves.append((source, target))
    solve(count - 1, spare, target, source, moves)


def draw_disc(frame, size, peg_x, top_y, colour=None):
    half = 3 * size
    frame.rect(peg_x - half, top_y, 2 * half + 1, DISC_H, colour or COLOURS[size], fill=True)


def draw(frame, stacks, flying=None, flash=False):
    frame.hline(0, BASE_Y, 96, C.BLUE)
    for peg_x in PEGS:
        frame.vline(peg_x, 5, BASE_Y - 5, C.BLUE)
    for peg, stack in enumerate(stacks):
        for level, size in enumerate(stack):
            top = BASE_Y - DISC_H * (level + 1)
            draw_disc(frame, size, PEGS[peg], top, C.WHITE if flash else None)
    if flying:
        size, x = flying
        draw_disc(frame, size, x, CARRY_Y)


def build():
    moves = []
    solve(DISCS, 0, 2, 1, moves)
    stacks = [list(range(DISCS, 0, -1)), [], []]
    anim = Animation(delay=DELAY)

    for _ in range(4):
        draw(anim.frame(), stacks)
    for source, target in moves:
        size = stacks[source].pop()
        draw(anim.frame(), stacks, (size, PEGS[source]))
        draw(anim.frame(), stacks, (size, PEGS[target]))
        stacks[target].append(size)
        draw(anim.frame(), stacks)
    for rest in range(4):
        draw(anim.frame(), stacks, flash=rest % 2 == 0)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hanoi.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
