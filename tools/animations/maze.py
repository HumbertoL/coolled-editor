#!/usr/bin/env python3
"""
Maze -- recursive-backtracker maze generation, animated.

A depth-first carver builds a maze on a grid where odd-coordinate pixels are
cells and even-coordinate pixels are walls.  This gives a 48x8 cell maze on
the 96x16 panel.  The full carve sequence is pre-computed, then spread evenly
across 53 frames so you watch the maze being carved.

Walls are blue, passages (carved cells and knocked-down walls) are black, the
carver head is white, and a cyan trail marks the recent path.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80

# Maze dimensions in cells (cells sit at odd pixel coordinates).
CELLS_X = 48   # columns 1, 3, 5, ... 95
CELLS_Y = 8    # rows    1, 3, 5, ... 15

# Pixel coordinates of a cell.
def cell_px(cx, cy):
    return 2 * cx + 1, 2 * cy + 1

# Pixel coordinate of the wall between two adjacent cells.
def wall_px(cx1, cy1, cx2, cy2):
    return (2 * cx1 + 1 + 2 * cx2 + 1) // 2, (2 * cy1 + 1 + 2 * cy2 + 1) // 2


def generate_carve_sequence(seed=42):
    """
    Run a recursive-backtracker and record every (cell, wall) pair carved.

    Returns a list of (cell_pixel, wall_pixel) tuples in carve order.
    """
    rng = random.Random(seed)
    visited = set()
    sequence = []

    # Neighbour offsets in cell coordinates.
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    start = (0, 0)
    visited.add(start)
    stack = [start]

    # Record the start cell itself (no wall to knock down).
    sequence.append((cell_px(*start), None))

    while stack:
        cx, cy = stack[-1]
        neighbours = []
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < CELLS_X and 0 <= ny < CELLS_Y and (nx, ny) not in visited:
                neighbours.append((nx, ny))
        if neighbours:
            nx, ny = rng.choice(neighbours)
            visited.add((nx, ny))
            stack.append((nx, ny))
            sequence.append((cell_px(nx, ny), wall_px(cx, cy, nx, ny)))
        else:
            stack.pop()

    return sequence


def build():
    sequence = generate_carve_sequence()
    total_steps = len(sequence)

    # Spread the carve steps across FRAMES.
    steps_per_frame = max(1, total_steps // FRAMES)

    anim = Animation(delay=DELAY)

    # Track which pixels have been carved so far.
    carved = set()
    step_index = 0

    # Trail: recently carved cells glow cyan, then fade.
    TRAIL_LENGTH = steps_per_frame * 3  # how many recent steps stay cyan

    for f in range(FRAMES):
        # How many steps to advance this frame.
        if f < FRAMES - 1:
            target = (f + 1) * total_steps // FRAMES
        else:
            target = total_steps
        new_this_frame = []
        while step_index < target:
            cell_pix, wall_pix = sequence[step_index]
            carved.add(cell_pix)
            new_this_frame.append(cell_pix)
            if wall_pix is not None:
                carved.add(wall_pix)
                new_this_frame.append(wall_pix)
            step_index += 1

        frame = anim.frame()

        # Draw all walls as blue.
        frame.fill(C.BLUE)

        # Clear carved passages to black.
        for px, py in carved:
            frame.pixel(px, py, C.BLACK)

        # Cyan trail for recently carved pixels.
        trail_start = max(0, step_index - TRAIL_LENGTH)
        trail_pixels = set()
        for i in range(trail_start, step_index):
            cell_pix, wall_pix = sequence[i]
            trail_pixels.add(cell_pix)
            if wall_pix is not None:
                trail_pixels.add(wall_pix)
        for px, py in trail_pixels:
            frame.pixel(px, py, C.CYAN)

        # White head at the most recently carved cell.
        if step_index > 0:
            head_cell, head_wall = sequence[min(step_index - 1, total_steps - 1)]
            hx, hy = head_cell
            frame.pixel(hx, hy, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/maze.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
