#!/usr/bin/env python3
"""
Captcha -- I'm not a robot, says the robot.

A checkbox and the familiar line. A mouse cursor glides in from the right,
hovers, clicks; the box spins for a moment the way they do; a green tick
appears. Then the text changes its mind: BEEP BOOP. This animation was
written by a language model, which is the joke.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
BOX_X, BOX_Y = 4, 4
CURSOR = [
    "#....",
    "##...",
    "###..",
    "####.",
    "#####",
    "#.##.",
    "...#.",
]
ARRIVE, CLICK, SPIN_END, TICK, BEEP = 12, 16, 26, 28, 40
SPIN = [(1, 0), (2, 1), (1, 2), (0, 1)]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.rect(BOX_X, BOX_Y, 8, 8, C.WHITE if index != CLICK else C.CYAN)
        if index >= BEEP:
            frame.text("BEEP BOOP.", 18, 4, C.GREEN if index % 4 < 2 else C.WHITE, proportional=True)
        else:
            frame.text("I'M NOT A ROBOT", 18, 4, C.WHITE, proportional=True)

        if CLICK < index < SPIN_END:
            # A little spinner inside the box.
            k = index - CLICK
            for i, (dx, dy) in enumerate(SPIN):
                on = (i + k) % 4
                frame.rect(BOX_X + 2 + dx * 2 - (1 if dx == 1 else 0), BOX_Y + 2 + dy * 2 - (1 if dy == 1 else 0), 2, 2,
                           C.CYAN if on == 0 else C.BLUE if on == 1 else C.BLACK, fill=True)
        if index >= TICK:
            frame.glyph("+CHECK", BOX_X + 2, BOX_Y + 1, C.GREEN)

        # The cursor: in from the right, over the box, click, then away.
        if index < ARRIVE:
            cx = 90 - (90 - BOX_X - 3) * index / ARRIVE
            cy = 12 - (12 - BOX_Y - 3) * index / ARRIVE
        elif index <= CLICK + 3:
            cx, cy = BOX_X + 3, BOX_Y + 3 + (1 if index == CLICK else 0)
        else:
            cx = BOX_X + 3 + (index - CLICK - 3) * 6
            cy = BOX_Y + 3 + (index - CLICK - 3) * 0.6
        for r, line in enumerate(CURSOR):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(round(cx) + c, round(cy) + r, C.YELLOW if index == CLICK else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/captcha.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
