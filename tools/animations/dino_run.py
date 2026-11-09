#!/usr/bin/env python3
"""
Dino run -- the offline-page runner, on a loop that never ends in GAME OVER.

The dinosaur stays put while the desert scrolls past at 3 pixels a frame.
The world is 144 pixels long -- 48 frames' worth -- and holds a cactus, a
low-flying pterodactyl and a pair of cacti. The dinosaur jumps the cacti on
a nine-frame parabola and simply keeps its head down for the bird, which
clears it by a row. Clouds drift at a third of the speed and the ground
texture repeats with the world, so everything but the score is seamless.
build() asserts that no obstacle pixel ever touches the dinosaur.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 48
DELAY = 80
SPEED = 3
WORLD = FRAMES * SPEED
DINO_X = 10
FEET_Y = 14
GROUND_Y = 15
JUMP_HALF = 4
JUMP_HEIGHT = 6

DINO = [
    "....####",
    "....#.##",
    "....####",
    "....##..",
    "#..####.",
    "##.###.#",
    ".#####..",
    "..####..",
]
LEGS = ["..#..#..", "..##.#..", "..#..##."]

CACTUS = [
    "..#..",
    "#.#.#",
    "###.#",
    "..###",
    "..#..",
]
BIRD = [
    [
        "..#.....",
        ".###....",
        "########",
        "...###..",
    ],
    [
        "........",
        ".###....",
        "########",
        "..####..",
    ],
]

# (kind, world x of the left edge). Cacti stand on the ground; the bird flies.
OBSTACLES = [("cactus", 46), ("bird", 88), ("cactus", 124), ("cactus", 130)]
JUMPS = [46 + 2, 127 + 2]  # world x the dinosaur's middle should be over at the peak


def stamp(canvas, rows, x, y, colour):
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell == "#":
                canvas.pixel(x + col, y + row, colour)


def jump_height(index):
    """Pixels off the ground at this frame."""
    middle = DINO_X + 4
    best = 0
    for peak_x in JUMPS:
        # Frames from the peak, measured round the loop.
        offset = (index * SPEED + middle - peak_x + WORLD / 2) % WORLD - WORLD / 2
        k = offset / SPEED
        if abs(k) < JUMP_HALF:
            best = max(best, round(JUMP_HEIGHT * (1 - (k / JUMP_HALF) ** 2)))
    return best


def build():
    rng = random.Random(52)
    pebbles = {rng.randrange(WORLD) for _ in range(34)}
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        scroll = index * SPEED

        hazards = Canvas()
        for kind, world_x in OBSTACLES:
            for lap in (-WORLD, 0, WORLD):
                x = world_x - scroll + lap
                if kind == "cactus":
                    stamp(hazards, CACTUS, x, FEET_Y - 4, C.GREEN)
                else:
                    stamp(hazards, BIRD[(index // 2) % 2], x, 1, C.MAGENTA)

        height = jump_height(index)
        dino = Canvas()
        legs = LEGS[0] if height else LEGS[1 + (index // 2) % 2]
        stamp(dino, DINO + [legs], DINO_X, FEET_Y - 8 - height, C.WHITE)
        clash = set(dino.lit()) & set(hazards.lit())
        assert not clash, f"frame {index}: dinosaur hits an obstacle at {sorted(clash)}"

        frame = anim.frame()
        for base in (20, 68):  # clouds, a third of the ground speed
            x = (base - scroll // 3) % 96
            for dx, dy in [(1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1)]:
                frame.pixel((x + dx) % 96, 3 + dy + (base % 3), C.BLUE)
        for x in range(96):
            if (x + scroll) % WORLD not in pebbles:
                frame.pixel(x, GROUND_Y, C.YELLOW)
        frame.blit(hazards)
        frame.blit(dino)
        # The score is opaque, so the bird flies in from behind it.
        frame.rect(74, 0, 22, 6, C.BLACK, fill=True)
        frame.small_text(f"{index * 7:05d}", 76, 0, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dino_run.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
