#!/usr/bin/env python3
"""
Unlimited power (2005).

Palpatine throws his hands up on the left and the lightning goes out: forked
paths redrawn every frame, white at the source and cooling to blue as they
branch, with the Jedi on the right lifted off his feet and thrown back
through the window. UNLIMITED lands first; POWER! arrives with the panel
already crackling, and the last few frames flash the whole sky.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 66
BUILD_AT = 6            # first sparks
UNLIMITED_AT = 12
POWER_AT = 26
STORM_AT = 44           # the sky itself starts flashing
SOURCE = (14, 10)
SKY_TOP = 8             # the words own everything above this
FLOOR = 15


def bolt(frame, rng, to_x, to_y, color):
    """A jagged path from the hands to the target, with the odd branch."""
    x, y = SOURCE
    while x < to_x - 2:
        next_x = min(to_x, x + rng.randint(3, 6))
        next_y = y + rng.randint(-3, 3) + (1 if y < to_y else -1)
        next_y = max(SKY_TOP, min(14, next_y))
        frame.line(x, y, next_x, next_y, color)
        if rng.random() < 0.15:
            fork_y = max(SKY_TOP, min(14, next_y + rng.choice((-3, 3))))
            frame.line(next_x, next_y, next_x + rng.randint(2, 5), fork_y, C.BLUE)
        x, y = next_x, next_y


def figure(frame, x, top, color):
    for row, line in enumerate(("###", ".#.", ".#.", "#.#")):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, top + row, color)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, FLOOR, 96, C.BLUE)

        # Palpatine, arms up. They go higher as the charge builds.
        lift = 0 if index < BUILD_AT else (1 if index < POWER_AT else 2)
        frame.vline(SOURCE[0], SOURCE[1], FLOOR - SOURCE[1], C.WHITE)
        for side in (-3, 3):
            frame.line(SOURCE[0], SOURCE[1] + 1, SOURCE[0] + side,
                       SOURCE[1] - lift, C.WHITE)
        frame.pixel(SOURCE[0], SOURCE[1] - 1, C.WHITE)

        # The Jedi: on his feet, then off them and going backwards.
        if index < POWER_AT:
            target_x, target_top = 80, FLOOR - 4
        else:
            thrown = index - POWER_AT
            target_x = min(90, 80 + thrown // 2)
            target_top = max(SKY_TOP, FLOOR - 4 - thrown // 2)
        if index >= BUILD_AT:
            strands = 1 if index < POWER_AT else 2
            for strand in range(strands):
                color = C.WHITE if strand == 0 else (C.CYAN if strand < 3 else C.BLUE)
                bolt(frame, rng, target_x, target_top + 2, color)

        figure(frame, target_x, target_top, C.CYAN if index < POWER_AT else C.YELLOW)

        # Late on, the room itself is lit by it -- but only below the words.
        if index >= STORM_AT and index % 2 == 0:
            for x in range(0, 96, 3):
                frame.pixel(x, rng.randrange(SKY_TOP, 16), C.BLUE)

        if index >= POWER_AT:
            shown = "POWER!"[: max(1, (index - POWER_AT) * 2)]
            frame.text(shown, "center", 0, C.WHITE if index % 4 < 2 else C.YELLOW,
                       proportional=True)
        elif index >= UNLIMITED_AT:
            frame.text("UNLIMITED"[: max(1, (index - UNLIMITED_AT) * 2)], "center", 0,
                       C.CYAN, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/unlimited_power.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
