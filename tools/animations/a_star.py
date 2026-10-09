#!/usr/bin/env python3
"""
A* -- pathfinding through a field of walls, one expansion at a time.

A 48x8 grid of 2px cells with seeded blue walls. A* searches from the cyan
start on the left to the white goal on the right using the Manhattan
heuristic: the green frontier is the open set, red cells are closed. When
the goal is reached the shortest path traces back from it in yellow, then
blinks.
"""

from __future__ import annotations

import heapq
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
GW, GH = 48, 8
START = (0, 4)
GOAL = (47, 3)
SEARCH_FRAMES = 32
TRACE_FRAMES = 10


def walls_for(seed):
    rng = random.Random(seed)
    walls = set()
    # Vertical barriers with a gap or two, plus scattered rubble.
    for x in range(4, GW - 3, 5):
        gaps = set(rng.sample(range(GH), 2))
        for y in range(GH):
            if y not in gaps and rng.random() < 0.9:
                walls.add((x, y))
    for _ in range(40):
        walls.add((rng.randrange(GW), rng.randrange(GH)))
    walls -= {START, GOAL}
    return walls


def search(walls):
    def h(cell):
        return abs(cell[0] - GOAL[0]) + abs(cell[1] - GOAL[1])

    open_heap = [(h(START), 0, START)]
    came = {START: None}
    cost = {START: 0}
    closed = set()
    steps = []  # (cell closed, snapshot of open set) per expansion
    while open_heap:
        _, g, cell = heapq.heappop(open_heap)
        if cell in closed:
            continue
        closed.add(cell)
        if cell == GOAL:
            steps.append((cell, set()))
            break
        x, y = cell
        for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nxt[0] < GW and 0 <= nxt[1] < GH) or nxt in walls:
                continue
            if g + 1 < cost.get(nxt, 1 << 30):
                cost[nxt] = g + 1
                came[nxt] = cell
                # Tie-break toward deeper nodes so the search runs straight.
                heapq.heappush(open_heap, (g + 1 + h(nxt), -(g + 1), nxt))
        steps.append((cell, {c for _, _, c in open_heap if c not in closed}))
    else:
        return None
    path = [GOAL]
    while came[path[-1]] is not None:
        path.append(came[path[-1]])
    return steps, path[::-1]


def cell(frame, c, colour):
    frame.rect(2 * c[0], 2 * c[1], 2, 2, colour, fill=True)


def build():
    seed = 7
    while (result := search(walls := walls_for(seed))) is None:
        seed += 1
    steps, path = result
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for w in walls:
            cell(frame, w, C.BLUE)
        done = min(len(steps), round(len(steps) * (index + 1) / SEARCH_FRAMES))
        for closed_cell, _ in steps[:done]:
            cell(frame, closed_cell, C.RED)
        if done and done < len(steps):
            for c in steps[done - 1][1]:
                cell(frame, c, C.GREEN)
        if index >= SEARCH_FRAMES:
            shown = min(len(path), round(len(path) * (index - SEARCH_FRAMES + 1) / TRACE_FRAMES))
            blink = index >= SEARCH_FRAMES + TRACE_FRAMES and index % 2
            for c in path[len(path) - shown:]:
                cell(frame, c, C.WHITE if blink else C.YELLOW)
        cell(frame, START, C.CYAN)
        cell(frame, GOAL, C.WHITE if index % 2 == 0 else C.MAGENTA)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/a_star.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
