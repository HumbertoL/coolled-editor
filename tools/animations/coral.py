#!/usr/bin/env python3
"""
Diffusion-Limited Aggregation -- coral/crystal growth simulation.

Seeds line the bottom row.  Random walkers drift in and stick when they touch
the growing structure, building branching coral-like or frost-like patterns.
Color by age: newest WHITE, older CYAN, oldest BLUE -- so the growth front
glows.

53 frames, DELAY=100.  SEED=23 for reproducibility.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
WIDTH = 96
HEIGHT = 16
SEED = 23

# Eight-connected neighbors: cardinal + diagonal.  Diagonal adjacency
# produces more delicate branching than 4-connected.
NEIGHBORS = [(-1, -1), (0, -1), (1, -1),
             (-1,  0),          (1,  0),
             (-1,  1), (0,  1), (1,  1)]

# Cardinal directions for the random walk itself.
WALK_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def simulate_dla(rng, target_cells):
    """
    Run a DLA simulation.  Returns a list of (x, y) in the order they were
    deposited (seeds first, then walkers that stuck).
    """
    occupied = set()
    deposit_order = []

    # Seeds along the bottom row, every other pixel.
    for x in range(0, WIDTH, 2):
        occupied.add((x, HEIGHT - 1))
        deposit_order.append((x, HEIGHT - 1))

    # Also a few seeds along the sides to encourage upward and inward growth.
    for y in range(HEIGHT - 1, HEIGHT // 2, -3):
        occupied.add((0, y))
        deposit_order.append((0, y))
        occupied.add((WIDTH - 1, y))
        deposit_order.append((WIDTH - 1, y))

    max_walkers = target_cells * 300
    launched = 0

    while len(deposit_order) < target_cells and launched < max_walkers:
        launched += 1

        # Spawn walker from a random position along the top or random edge.
        # Biased toward the top so the structure grows upward.
        side = rng.random()
        if side < 0.6:
            # Top edge
            wx, wy = rng.randint(0, WIDTH - 1), 0
        elif side < 0.8:
            # Left edge
            wx, wy = 0, rng.randint(0, HEIGHT - 1)
        else:
            # Right edge
            wx, wy = WIDTH - 1, rng.randint(0, HEIGHT - 1)

        if (wx, wy) in occupied:
            continue

        # Random walk.
        steps = 0
        max_steps = WIDTH * HEIGHT * 3
        stuck = False
        while steps < max_steps:
            steps += 1

            # Check 8-connected adjacency to an occupied cell.
            for dx, dy in NEIGHBORS:
                nx, ny = wx + dx, wy + dy
                if (nx, ny) in occupied:
                    occupied.add((wx, wy))
                    deposit_order.append((wx, wy))
                    stuck = True
                    break

            if stuck:
                break

            # Move randomly (4 cardinal directions).
            dx, dy = rng.choice(WALK_DIRS)
            nx, ny = wx + dx, wy + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and (nx, ny) not in occupied:
                wx, wy = nx, ny
            # else: stay put

    return deposit_order


def build():
    rng = random.Random(SEED)

    # Target ~40% of the display filled.
    target_cells = int(WIDTH * HEIGHT * 0.40)

    deposit_order = simulate_dla(rng, target_cells)
    total_deposits = len(deposit_order)

    anim = Animation(delay=DELAY)

    for f in range(FRAMES):
        frame = anim.frame()

        # Linear reveal: spread deposits evenly across frames.
        t = (f + 1) / FRAMES
        show_count = max(1, int(t * total_deposits))
        show_count = min(show_count, total_deposits)

        # Draw all cells up to the threshold, colored by age relative to
        # the current frame's frontier.
        for i in range(show_count):
            x, y = deposit_order[i]
            # Age: 0.0 = newest (just deposited), 1.0 = oldest (seeds).
            age = (show_count - 1 - i) / max(1, show_count - 1)

            if age < 0.12:
                color = C.WHITE   # newest growth front
            elif age < 0.35:
                color = C.CYAN    # recent
            else:
                color = C.BLUE    # oldest established structure

            frame.pixel(x, y, color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/coral.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
