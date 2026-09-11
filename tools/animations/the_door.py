#!/usr/bin/env python3
"""
The door -- something on the other side.

Darkness, then the faint outline of a door frame. It opens slowly, warm light
spilling through the widening gap onto the floor, and a figure stands in it,
black against the light. It looks in for a while. Then the door shuts in two
frames, and in the dark that follows, two red eyes open where the figure was,
and blink out.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
DOOR_X, DOOR_W = 40, 14
FRAME_AT, OPEN_AT, OPEN_END, SLAM_AT, EYES_AT, EYES_END = 4, 8, 22, 36, 42, 50

FIGURE = [
    "..##..",
    ".####.",
    "..##..",
    ".####.",
    "######",
    "######",
    ".####.",
    ".####.",
    ".#..#.",
    ".#..#.",
]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if FRAME_AT <= index < SLAM_AT + 2:
            frame.rect(DOOR_X - 1, 0, DOOR_W + 2, 16, C.BLUE)
        if OPEN_AT <= index < SLAM_AT:
            gap = min(DOOR_W, index - OPEN_AT + 1) if index < SLAM_AT - 1 else 3
            if index >= OPEN_END:
                gap = DOOR_W
            frame.rect(DOOR_X, 1, gap, 14, C.YELLOW, fill=True)
            # Light spilling onto the floor, widening with the gap.
            spill = gap * 2
            frame.hline(DOOR_X - spill // 2 + DOOR_W // 2 - gap // 2, 15, spill, C.YELLOW)
            if gap >= 6:
                fx = DOOR_X + gap // 2 - 3
                for r, line in enumerate(FIGURE):
                    for c, ch in enumerate(line):
                        if ch == "#" and DOOR_X <= fx + c < DOOR_X + gap:
                            frame.pixel(fx + c, 4 + r, C.BLACK)
            # The edge of the swinging door itself.
            frame.vline(DOOR_X + gap, 1, 14, C.WHITE)
        if EYES_AT <= index < EYES_END and not (EYES_END - 2 <= index):
            ex = DOOR_X + DOOR_W // 2
            frame.pixel(ex - 2, 6, C.RED)
            frame.pixel(ex + 1, 6, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/the_door.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
