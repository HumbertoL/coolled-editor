#!/usr/bin/env python3
"""
Bigfoot -- frame 352, more or less.

The Patterson-Gimlin film as a 96x16 loop: a treeline, a handheld camera that
will not hold still, and something big walking right to left across the
clearing. Halfway through it does the thing the film is famous for and looks
back at the lens -- two white eyes for four frames -- then carries on and
goes behind the trees. The whole scene is offset by a per-frame jitter and
speckled with grain, because the wobble is as much a part of the artefact as
the subject is.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 1967
GROUND = 14

# Scene beats, by frame index.
ENTER_AT = 3        # it comes out from behind the left-hand trees
GLANCE_FROM = 22    # the look back at the camera
GLANCE_TO = 26
EXIT_AT = 48        # behind the near fir, and gone

START_X, END_X = 4, 82
#: The foreground fir it walks behind, and never comes out the far side of.
SCREEN_X = 80
BODY = [
    "..###..",
    ".#####.",
    "#######",
    "#######",
    ".#####.",
    ".#####.",
    "..###..",
]


def canopy_profile(rng):
    """A stable jagged treeline: firs of a few heights, spiked at the tips."""
    heights = []
    x = 0
    while x < 96:
        width = rng.randint(3, 6)
        height = rng.randint(2, 5)
        for offset in range(width):
            edge = min(offset, width - 1 - offset)
            heights.append(max(1, height - (1 if edge == 0 else 0)))
            x += 1
    return heights[:96]


def draw_canopy(frame, heights, dx, dy):
    for x, height in enumerate(heights):
        frame.vline(x + dx, dy, height, C.GREEN)


def draw_screen_tree(frame, dx, dy):
    """The near fir, drawn last so the subject can walk behind it."""
    for row in range(16):
        half = 1 + row // 4
        frame.hline(SCREEN_X - half + dx, row + dy, half * 2 + 1, C.GREEN)


def draw_subject(frame, x, y, stride, glancing):
    for row, line in enumerate(BODY):
        for column, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + column, y + row, C.RED)
    # Arms, counter-swinging with the legs.
    frame.line(x, y + 2, x - 1, y + 5 + stride, C.RED)
    frame.line(x + 6, y + 2, x + 7, y + 5 - stride, C.RED)
    # Legs, from the hips down to the ground.
    hip = y + len(BODY) - 1
    frame.line(x + 2, hip, x + 2 - stride, GROUND, C.RED)
    frame.line(x + 4, hip, x + 4 + stride, GROUND, C.RED)
    if glancing:
        # The head turns and catches the light -- the frame everyone argues
        # about -- so it is drawn brighter, not just given eyes.
        for row, line in enumerate(BODY[:2]):
            for column, cell in enumerate(line):
                if cell == "#":
                    frame.pixel(x + column, y + row, C.YELLOW)
        frame.pixel(x + 2, y + 1, C.WHITE)
        frame.pixel(x + 4, y + 1, C.WHITE)


def build():
    rng = random.Random(SEED)
    heights = canopy_profile(rng)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # The camera operator is running. Nothing sits still.
        dx, dy = rng.randint(-1, 1), rng.randint(-1, 0)

        draw_canopy(frame, heights, dx, dy)
        frame.hline(0, GROUND + dy, 96, C.GREEN)
        frame.hline(0, GROUND + 1 + dy, 96, C.GREEN)

        if ENTER_AT <= index < EXIT_AT:
            t = (index - ENTER_AT) / (EXIT_AT - ENTER_AT)
            x = round(START_X + (END_X - START_X) * t) + dx
            stride = (0, 1, 2, 1, 0, -1, -2, -1)[index % 8]
            bob = 1 if index % 4 in (1, 2) else 0
            draw_subject(
                frame,
                x,
                GROUND - 10 + bob + dy,
                stride,
                GLANCE_FROM <= index <= GLANCE_TO,
            )

        # The near fir last: it occludes, which is how the subject gets away.
        draw_screen_tree(frame, dx, dy)

        for _ in range(5):
            frame.pixel(rng.randrange(96), rng.randrange(16), C.WHITE)
        if rng.random() < 0.25:
            scratch = rng.randrange(96)
            frame.vline(scratch, 0, 16, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bigfoot.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
