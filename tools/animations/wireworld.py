#!/usr/bin/env python3
"""
Wireworld -- Brian Silverman's four-state cellular automaton, running a small
circuit of clocks, diodes and XOR junctions.

The rule: an electron head becomes a tail, a tail becomes wire, and wire
becomes a head when exactly one or two of its eight neighbours are heads.
That is enough to build logic. On the panel wire is blue, heads are yellow
and tails red, so each electron reads as a small comet.

The circuit, left to right:

* Two clocks -- loops tapped by a wire. The upper is 24 generations round
  and holds two electrons; the lower is 16 round and holds one.
* A diode on each output (the two-cell stub either side of a gap), so nothing
  can run backwards into a clock.
* A junction where the two lines meet. Electrons arriving alone pass; two
  arriving in the same generation put three heads next to the output cell
  and cancel -- which makes the junction an XOR.
* A splitter into a short and a long branch, each ending in a diode, joined
  by a second XOR junction: a delay line, so each pulse meets its own echo.
* A zigzag to the right edge, where electrons fall off the end of the wire.

The circuit is feed-forward, so once the first electrons have flushed
through it repeats with period lcm(24, 16) = 48. The script warms it up,
then records exactly one period and asserts the state really did return, so
the loop is seamless by construction rather than by eye.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
WARMUP = 480  # a multiple of the period, and long enough to flush the start-up

WIRE, HEAD, TAIL = 1, 2, 3
COLOR = {WIRE: C.BLUE, HEAD: C.YELLOW, TAIL: C.RED}


def wire(grid, *points):
    """Lay wire along a polyline of horizontal, vertical or 45-degree runs."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            grid[(x, y)] = WIRE


def loop(grid, x, y, width, height):
    """A rectangular clock loop with its top-left cell at (x, y)."""
    wire(
        grid,
        (x, y),
        (x + width - 1, y),
        (x + width - 1, y + height - 1),
        (x, y + height - 1),
        (x, y),
    )


def diode(grid, gap_x, y):
    """Cut the wire on row ``y`` at ``gap_x`` and add the stubs: passes left to right."""
    del grid[(gap_x, y)]
    for dx in (-1, 0):
        grid[(gap_x + dx, y - 1)] = WIRE
        grid[(gap_x + dx, y + 1)] = WIRE


def circuit():
    grid = {}

    # Clock A, period 24, top left; clock B, period 16, bottom left.
    loop(grid, 1, 0, 10, 6)
    loop(grid, 1, 11, 8, 4)
    wire(grid, (11, 3), (24, 3), (27, 6))
    wire(grid, (9, 13), (22, 13), (27, 8))
    diode(grid, 17, 3)
    diode(grid, 15, 13)

    # First XOR junction, then on to the splitter.
    wire(grid, (27, 7), (36, 7))

    # Short branch over the top, long branch underneath with a detour.
    wire(grid, (37, 6), (41, 2), (58, 2), (62, 6))
    wire(grid, (37, 8), (41, 12), (45, 12), (47, 14), (52, 14), (54, 12), (58, 12), (62, 8))
    diode(grid, 52, 2)
    diode(grid, 44, 12)

    # Second XOR junction and the zigzag out.
    wire(
        grid,
        (62, 7),
        (67, 7),
        (72, 2),
        (74, 2),
        (84, 12),
        (86, 12),
        (91, 7),
        (95, 7),
    )

    grid[(1, 3)] = HEAD
    grid[(1, 2)] = TAIL
    grid[(5, 0)] = HEAD
    grid[(6, 0)] = TAIL
    grid[(1, 13)] = HEAD
    grid[(1, 12)] = TAIL
    return grid


def step(grid):
    after = {}
    for (x, y), state in grid.items():
        if state == HEAD:
            after[(x, y)] = TAIL
        elif state == TAIL:
            after[(x, y)] = WIRE
        else:
            heads = sum(
                1
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if (dx or dy) and grid.get((x + dx, y + dy)) == HEAD
            )
            after[(x, y)] = HEAD if heads in (1, 2) else WIRE
    return after


def build():
    grid = circuit()
    for _ in range(WARMUP):
        grid = step(grid)
    start = grid

    anim = Animation(delay=DELAY)
    for _ in range(FRAMES):
        frame = anim.frame()
        for (x, y), state in grid.items():
            frame.pixel(x, y, COLOR[state])
        grid = step(grid)
    if grid != start:
        raise AssertionError("circuit did not return to its start: loop is not seamless")
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/wireworld.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
