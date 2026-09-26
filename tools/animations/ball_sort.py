#!/usr/bin/env python3
"""
Ball sort -- the tube puzzle, solved move by move.

Five colours, four balls each, in seven tubes (two start empty). A ball may
only land on an empty tube or on its own colour. Each move lifts the top ball
clear, carries it across and drops it in, three frames a move. When a tube holds four of one colour
its walls light up in that colour, and once all five are done they flash.

The deal is a plain shuffle, and a breadth-first search finds its shortest
solution -- 13 moves for this seed -- so what plays is a real, optimal solve.
"""

from __future__ import annotations

import random
from collections import deque
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
BALL_COLORS = [C.RED, C.YELLOW, C.GREEN, C.MAGENTA, C.CYAN]
TUBES = 7
CAPACITY = 4
HOLD_START = 4
MOVE_FRAMES = 3
SEED = 29  # a fully shuffled deal whose shortest solution is 13 moves
TUBE_X = [4 + i * 13 for i in range(TUBES)]
FLOOR = 14  # bottom row of the lowest ball


def solved(state):
    return all(not t or (len(t) == CAPACITY and len(set(t)) == 1) for t in state)


def solve(start):
    """Breadth-first search, so the solution shown is a shortest one."""
    start = tuple(tuple(t) for t in start)
    seen = {tuple(sorted(start))}
    queue = deque([(start, [])])
    while queue:
        state, path = queue.popleft()
        if solved(state):
            return path
        for i, src in enumerate(state):
            if not src or (len(src) == CAPACITY and len(set(src)) == 1):
                continue
            for j, dst in enumerate(state):
                if i == j or len(dst) >= CAPACITY or (dst and dst[-1] != src[-1]):
                    continue
                if not dst and len(set(src)) == 1:
                    continue
                nxt = list(state)
                nxt[i], nxt[j] = src[:-1], dst + (src[-1],)
                nxt = tuple(nxt)
                key = tuple(sorted(nxt))
                if key not in seen:
                    seen.add(key)
                    queue.append((nxt, path + [(i, j)]))
    raise ValueError("unsolvable deal")


def deal():
    balls = [k for k in range(len(BALL_COLORS)) for _ in range(CAPACITY)]
    random.Random(SEED).shuffle(balls)
    tubes = [balls[i * CAPACITY:(i + 1) * CAPACITY] for i in range(len(BALL_COLORS))]
    return tubes + [[] for _ in range(TUBES - len(tubes))]


def ball(frame, x, y, color):
    frame.rect(x, y, 3, 3, color, fill=True)
    frame.pixel(x, y, C.BLACK)
    frame.pixel(x + 2, y, C.BLACK)
    frame.pixel(x, y + 2, C.BLACK)
    frame.pixel(x + 2, y + 2, C.BLACK)
    frame.pixel(x + 1, y + 1, C.WHITE if color != C.WHITE else C.CYAN)


def slot_y(level):
    return FLOOR - 2 - level * 3


def draw(frame, tubes, flash=False, skip_top=None):
    for i, tube in enumerate(tubes):
        done = len(tube) == CAPACITY and len(set(tube)) == 1
        wall = BALL_COLORS[tube[0]] if done else C.BLUE
        if flash:
            wall = C.WHITE
        x = TUBE_X[i]
        frame.vline(x - 1, 3, 13, wall)
        frame.vline(x + 3, 3, 13, wall)
        frame.hline(x, 15, 3, wall)
        for level, k in enumerate(tube):
            if skip_top == i and level == len(tube) - 1:
                continue
            ball(frame, x, slot_y(level), BALL_COLORS[k])


def build():
    tubes = deal()
    moves = solve(tubes)
    anim = Animation(delay=DELAY)
    for _ in range(HOLD_START):
        draw(anim.frame(), tubes)
    for src, dst in moves:
        color = BALL_COLORS[tubes[src][-1]]
        x0, x1 = TUBE_X[src], TUBE_X[dst]
        path = [(x0, 0), ((x0 + x1) // 2, 0)]
        for x, y in path:
            frame = anim.frame()
            draw(frame, tubes, skip_top=src)
            ball(frame, x, y, color)
        tubes[dst].append(tubes[src].pop())
        draw(anim.frame(), tubes)
    while len(anim) < FRAMES:
        n = len(anim)
        draw(anim.frame(), tubes, flash=(n - HOLD_START - len(moves) * MOVE_FRAMES) % 2 == 1 and n < FRAMES - 2)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/ball_sort.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
