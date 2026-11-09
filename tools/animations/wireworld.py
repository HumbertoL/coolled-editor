#!/usr/bin/env python3
"""
Wireworld -- Brian Silverman's four-state automaton, running a real circuit.

Rules: an electron head becomes a tail, a tail becomes wire, and wire becomes
a head when exactly one or two of its eight neighbours are heads. That is
enough for clocks and logic.

The circuit here is two clocks and an OR gate. The top loop is 12 cells round
and the bottom one 16, so they tick every 12 and 16 generations; each is
tapped by a wire into one input of the gate, whose output runs off along a
meander to the right edge, where electrons fall off the end of the wire. The
whole thing repeats every lcm(12, 16) = 48 generations, which is the frame
count, so the loop is exact -- build() asserts it.

Wire is blue, heads yellow, tails red.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
WIRE, HEAD, TAIL = 1, 2, 3
COLOUR = {WIRE: C.BLUE, HEAD: C.YELLOW, TAIL: C.RED}


def polyline(cells, points):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for step in range(steps + 1):
            x = x0 + (x1 - x0) * step // max(steps, 1)
            y = y0 + (y1 - y0) * step // max(steps, 1)
            cells[(x, y)] = WIRE


def loop(cells, x0, y0, x1, y1):
    polyline(cells, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])


def circuit():
    cells = {}
    # Clock A: 12 cells. Tapped on its right side, down into the gate's top input.
    loop(cells, 2, 1, 5, 4)
    polyline(cells, [(6, 2), (10, 2), (10, 6), (13, 6)])
    # Clock B: 16 cells. Tapped on its right side, up into the bottom input.
    loop(cells, 1, 11, 6, 14)
    polyline(cells, [(7, 12), (9, 10), (13, 10)])
    # The OR gate: each input touches all three centre cells, so the far
    # input sees three heads at once and stays quiet.
    for cell in [(14, 7), (13, 8), (14, 8), (15, 8), (14, 9)]:
        cells[cell] = WIRE
    # Output meander.
    path = [(16, 8), (20, 8)]
    x, up = 20, True
    while x + 6 <= 92:
        y = 1 if up else 14
        path += [(x, y), (x + 6, y)]
        x += 6
        up = not up
    path += [(x, 8), (95, 8)]
    polyline(cells, path)
    # One electron in each clock, both heading clockwise. They start mid-side:
    # beside a corner the head would also touch the cell round the bend and
    # launch a second electron the other way.
    cells[(4, 1)], cells[(3, 1)] = HEAD, TAIL
    cells[(4, 11)], cells[(3, 11)] = HEAD, TAIL
    return cells


def step(cells):
    after = {}
    for (x, y), state in cells.items():
        if state == HEAD:
            after[(x, y)] = TAIL
        elif state == TAIL:
            after[(x, y)] = WIRE
        else:
            heads = sum(
                cells.get((x + dx, y + dy)) == HEAD
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if dx or dy
            )
            after[(x, y)] = HEAD if heads in (1, 2) else WIRE
    return after


def build():
    cells = circuit()
    for _ in range(FRAMES * 12):  # let the meander fill
        cells = step(cells)
    start = dict(cells)
    anim = Animation(delay=DELAY)
    for _ in range(FRAMES):
        frame = anim.frame()
        for (x, y), state in cells.items():
            frame.pixel(x, y, COLOUR[state])
        cells = step(cells)
    assert cells == start, "circuit is not periodic in FRAMES generations"
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/wireworld.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
