#!/usr/bin/env python3
"""
Galton board -- a bean machine laid on its side.

Balls enter at the left and meet seven columns of pegs. At each peg a ball goes
up or down one row at random, so it leaves on one of eight rows with binomial
odds: 1, 7, 21, 35, 35, 21, 7, 1 in 128. Each row is a bin, and balls run along
it to stack against the right wall, so the stacks grow leftwards into a bell
curve. At the end the expected heights appear as red markers beside the real
ones.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
LEVELS = 7
PEG_X0 = 6           # x of the first peg column
PEG_DX = 4           # columns of pegs every 4px
CENTRE = 8           # row of the first peg
BALLS = 128
RELEASE_FRAMES = 40
RUN_SPEED = 4        # px a frame once out of the pegs


def peg_rows(level):
    return [CENTRE - level + 2 * j for j in range(level + 1)]


def path_for(rng):
    """Rows at each level, then the bin row it leaves on."""
    rows = [CENTRE]
    for _ in range(LEVELS):
        rows.append(rows[-1] + rng.choice((-1, 1)))
    return rows


def position(rows, age, stack_end):
    """Where a ball is ``age`` half-steps after entering, or None once stacked."""
    x = 2 * age - 4          # enters from just off the left edge
    first = PEG_X0 - 1
    if x < first:
        return x, CENTRE
    last = PEG_X0 + PEG_DX * (LEVELS - 1) - 1
    if x <= last + PEG_DX:
        level, offset = divmod(x - first, PEG_DX)
        level = min(level, LEVELS - 1)
        y0, y1 = rows[level], rows[level + 1]
        # Drop to the next row halfway between pegs.
        return x, y0 if offset < PEG_DX // 2 else y1
    run_from = last + PEG_DX
    steps = (x - run_from) // 2
    x = run_from + steps * RUN_SPEED
    if x >= stack_end:
        return None
    return x, rows[-1]


def build():
    rng = random.Random(1873)
    balls = []
    for n in range(BALLS):
        start = n * RELEASE_FRAMES // BALLS
        balls.append((start, path_for(rng), (n * 7) % 2))
    pegs = [(PEG_X0 + PEG_DX * level, row) for level in range(LEVELS) for row in peg_rows(level)]
    bins = sorted({CENTRE - LEVELS + 2 * j for j in range(LEVELS + 1)})
    expected = {row: BALLS * math.comb(LEVELS, j) / 2 ** LEVELS for j, row in enumerate(bins)}

    anim = Animation(delay=DELAY)
    stacks = {row: 0 for row in bins}
    landed = set()
    for index in range(FRAMES):
        frame = anim.frame()
        for x, y in pegs:
            frame.pixel(x, y, C.BLUE)
        frame.vline(95, 0, 16, C.BLUE)
        in_flight = []
        for n, (start, rows, _) in enumerate(balls):
            if index < start or n in landed:
                continue
            age = (index - start) * 2
            stack_end = 95 - stacks[rows[-1]]
            where = position(rows, age, stack_end)
            if where is None:
                landed.add(n)
                stacks[rows[-1]] += 1
                continue
            in_flight.append(where)
        for row, height in stacks.items():
            frame.hline(95 - height, row, height, C.CYAN)
            if height:
                frame.pixel(95 - height, row, C.WHITE if index < RELEASE_FRAMES + 8 else C.CYAN)
        for x, y in in_flight:
            frame.pixel(x, y, C.YELLOW)
        if index >= RELEASE_FRAMES + 8 and (index // 2) % 2 == 0:
            for row, height in expected.items():
                frame.pixel(95 - round(height) - 1, row, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/galton_board.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
