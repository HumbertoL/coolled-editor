#!/usr/bin/env python3
"""
Dino run -- the offline-page endless runner, played badly.

A small T-rex sprints across the desert, clears a cactus, clears a pair, and
then runs straight into the third. GAME OVER, and the loop is the restart.

The jumps are not hand-timed. The script knows every sprite's pixels, so for
each cactus it searches for a take-off frame on which no dino pixel ever
touches a cactus pixel, and takes the latest one that works -- the dino
leaves it as late as it dares. For the last cactus it simply does not jump,
and the crash frame is whichever frame the sprites first overlap.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SPEED = 4                 # ground pixels per frame
DINO_X = 8
GROUND_Y = 15
LIFT = [2, 4, 5, 5, 5, 4, 2]   # height above the ground through a jump

BODY = [
    "......####.",
    ".....##.###",
    ".....######",
    ".....###...",
    "#....#####.",
    "#...####...",
    "##.######..",
    ".#######.#.",
    "..#####....",
]
LEGS = {
    "a": ["..##.##....", "..#........"],
    "b": ["..##.##....", ".....#....."],
    "jump": ["..#...#....", "..##..##..."],
}
CACTUS = [
    "..#..",
    "#.#.#",
    "#####",
    "..#..",
]
CLOUD = [
    "..###..",
    ".#####.",
    "#######",
]
# (world x of the left edge, how many cacti side by side)
OBSTACLES = [(58, 1), (118, 2), (176, 1)]


def sprite_pixels(rows, x, y):
    return {
        (x + col, y + r)
        for r, row in enumerate(rows)
        for col, cell in enumerate(row)
        if cell == "#"
    }


def dino_pixels(lift, legs):
    rows = BODY + LEGS[legs]
    return sprite_pixels(rows, DINO_X, GROUND_Y - len(rows) - lift)


def cactus_pixels(scroll):
    pixels = set()
    for world_x, count in OBSTACLES:
        for k in range(count):
            pixels |= sprite_pixels(CACTUS, world_x + 5 * k - scroll, GROUND_Y - len(CACTUS))
    return pixels


def plan():
    """Lift for every frame, and the frame of the crash."""
    lift = [0] * (FRAMES + len(LIFT))

    def collisions():
        return [
            f
            for f in range(FRAMES)
            if dino_pixels(lift[f], "jump") & cactus_pixels(SPEED * f)
        ]

    for _obstacle in OBSTACLES[:-1]:
        first = collisions()[0]
        for takeoff in range(first, first - len(LIFT) - 1, -1):
            trial = list(lift)
            for k, height in enumerate(LIFT):
                trial[takeoff + k] = height
            saved, lift = lift, trial
            hits = collisions()
            if not hits or hits[0] > takeoff + len(LIFT):
                break
            lift = saved
        else:
            raise AssertionError("no take-off frame clears this cactus")
    return lift, collisions()[0]


def draw_sprite(frame, pixels, color):
    for x, y in pixels:
        frame.pixel(x, y, color)


def build():
    lift, crash = plan()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        live = min(index, crash)          # the world freezes at the crash
        dead = index >= crash
        scroll = SPEED * live

        for cloud_x, cloud_y in ((70, 1), (131, 3)):
            draw_sprite(frame, sprite_pixels(CLOUD, cloud_x - live, cloud_y), C.BLUE)
        for x in range(96):
            world = x + scroll
            if world % 17 not in (5, 6) and world % 29 != 11:
                frame.pixel(x, GROUND_Y, C.YELLOW)
        draw_sprite(frame, cactus_pixels(scroll), C.GREEN)

        legs = "jump" if lift[live] or dead else "ab"[live % 2]
        draw_sprite(frame, dino_pixels(lift[live], legs), C.WHITE)
        if dead:
            eye_y = GROUND_Y - len(BODY) - 2 - lift[live] + 1
            frame.pixel(DINO_X + 7, eye_y, C.RED)
            frame.text("GAME OVER", "center", 2, C.RED)

        score = f"{2 * live:05d}"
        frame.small_text(score, 96 - frame.small_text_width(score), 0, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dino_run.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
