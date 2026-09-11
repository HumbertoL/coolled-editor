#!/usr/bin/env python3
"""
Key quest -- a little explorer hunts through a maze for the key.

A maze is carved with a depth-first search on a 3-pixel grid, so corridors are
two pixels wide with one-pixel walls. The explorer follows the shortest path
from the entrance to a blinking key, one cell per frame; the route is chosen
so the search fills the loop. Reaching the key, they flash gold together and
the door at the far end swings open. Seeded, so the maze is the same every
time.
"""

from __future__ import annotations

import random
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 12
CELL = 3
COLS, ROWS = 31, 5
TRAVEL_FRAMES = 44


def carve(rng):
    """Cells are (col, row); open[(a, b)] means the wall between a and b is gone."""
    visited = {(0, 0)}
    stack = [(0, 0)]
    open_walls = set()
    while stack:
        c, r = stack[-1]
        options = [(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if 0 <= c + dc < COLS and 0 <= r + dr < ROWS and (c + dc, r + dr) not in visited]
        if not options:
            stack.pop()
            continue
        nxt = rng.choice(options)
        visited.add(nxt)
        open_walls.add(frozenset(((c, r), nxt)))
        stack.append(nxt)
    return open_walls


def shortest_paths(open_walls, start):
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        c, r = cur
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (c + dc, r + dr)
            if frozenset((cur, nxt)) in open_walls and nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)
    return prev


def path_to(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]


def cell_px(cell):
    c, r = cell
    return 1 + c * CELL, 1 + r * CELL


def build():
    rng = random.Random(SEED)
    open_walls = carve(rng)
    start = (0, ROWS - 1)
    prev = shortest_paths(open_walls, start)
    # Put the key where the walk is as close as possible to the travel budget.
    key = min(prev, key=lambda cell: abs(len(path_to(prev, cell)) - 1 - TRAVEL_FRAMES))
    path = path_to(prev, key)

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Walls: everything blue, then knock passages out.
        frame.fill(C.BLUE)
        for c in range(COLS):
            for r in range(ROWS):
                x, y = cell_px((c, r))
                frame.rect(x, y, 2, 2, C.BLACK, fill=True)
                for dc, dr in ((1, 0), (0, 1)):
                    if frozenset(((c, r), (c + dc, r + dr))) in open_walls:
                        frame.rect(x + 2 * dc, y + 2 * dr, 2 - dc, 2 - dr, C.BLACK, fill=True)
        frame.rect(0, 0, anim.width, anim.height, C.BLUE)

        step = min(index, len(path) - 1)
        arrived = step >= len(path) - 1
        for visited in path[:step]:
            vx, vy = cell_px(visited)
            frame.pixel(vx, vy + 1, C.CYAN)

        kx, ky = cell_px(key)
        if not arrived or index % 2:
            frame.rect(kx, ky, 2, 2, C.YELLOW if index % 4 < 2 else C.WHITE, fill=True)
        hx, hy = cell_px(path[step])
        frame.rect(hx, hy, 2, 2, C.WHITE if not arrived or index % 2 else C.YELLOW, fill=True)

        # The exit door on the right wall, open once the key is found.
        door_y = cell_px((COLS - 1, 0))[1]
        frame.rect(anim.width - 1, door_y, 1, 2, C.YELLOW if arrived else C.RED, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/key_quest.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
