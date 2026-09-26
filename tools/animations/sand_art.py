#!/usr/bin/env python3
"""
Sand art -- a spout sweeps over the panel, pouring coloured sand into strata.

A falling-sand cellular automaton: every grain drops if it can, otherwise
slides down one diagonal, otherwise rests. The spout visits a string of spots,
pouring a new colour at each while drifting a little, so every pour heaps up
into a mound and avalanches down over the mounds before it -- the way a
bottle of layered sand builds up. The stream is visible below the spout.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SUBSTEPS = 5
GRAINS_PER_STEP = 4
POUR_FRAMES = 7
TRAVEL_FRAMES = 1
SPOTS = [34, 60, 20, 47, 76, 30, 62]
LAYERS = [C.YELLOW, C.RED, C.MAGENTA, C.BLUE, C.CYAN, C.GREEN, C.WHITE]
W, H = 96, 16
SEED = 3


def step(grid, rng):
    for y in range(H - 2, -1, -1):
        xs = list(range(W))
        rng.shuffle(xs)
        for x in xs:
            color = grid[y][x]
            if color is None:
                continue
            if grid[y + 1][x] is None:
                grid[y + 1][x], grid[y][x] = color, None
                continue
            sides = [-1, 1]
            rng.shuffle(sides)
            for side in sides:
                nx = x + side
                if 0 <= nx < W and grid[y + 1][nx] is None and grid[y][nx] is None:
                    grid[y + 1][nx], grid[y][x] = color, None
                    break


def spout_x(time):
    """Pour position at a (fractional) frame: drift at a spot, then glide on."""
    period = POUR_FRAMES + TRAVEL_FRAMES
    spot, local = divmod(time, period)
    spot = int(spot)
    here = SPOTS[spot % len(SPOTS)]
    there = SPOTS[(spot + 1) % len(SPOTS)]
    if local < POUR_FRAMES:
        return here + 3 * math.sin(math.pi * local / POUR_FRAMES)
    u = (local - POUR_FRAMES) / TRAVEL_FRAMES
    return here + (there - here) * u


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    grid = [[None] * W for _ in range(H)]
    for index in range(FRAMES):
        spot, local = divmod(index, POUR_FRAMES + TRAVEL_FRAMES)
        spot %= len(SPOTS)
        color = LAYERS[spot % len(LAYERS)]
        pouring = local < POUR_FRAMES
        for sub in range(SUBSTEPS):
            spout = spout_x(index + sub / SUBSTEPS)
            for _ in range(GRAINS_PER_STEP if pouring else 0):
                x = min(W - 1, max(0, round(spout + rng.uniform(-1.2, 1.2))))
                if grid[1][x] is None:
                    grid[1][x] = color
            step(grid, rng)
        frame = anim.frame()
        for y in range(H):
            for x in range(W):
                if grid[y][x] is not None:
                    frame.pixel(x, y, grid[y][x])
        nozzle = round(spout_x(index + 1))
        frame.hline(nozzle - 1, 0, 3, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sand_art.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
