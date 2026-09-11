#!/usr/bin/env python3
"""
Can it run Doom? -- the question asked of every device with a screen.

The question, then a first-person corridor: perspective edges to a vanishing
point and wall rings that grow toward the viewer, so it feels like walking.
An imp comes down the hall, doubling in size as it closes, and a shotgun at
the bottom of the frame fires: muzzle flash, the imp goes white and is gone.
Then the answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
ASK_END, HALL_END = 9, 43
GROW_AT, FIRE_AT = 24, 36

IMP = [
    "#.....#",
    ".#...#.",
    "..###..",
    ".#####.",
    "#.###.#",
    "..#.#..",
    "..#.#..",
]
GUN = ["..#..", ".###.", "#####"]
VP = (47.5, 7.5)
RINGS = 5


def sprite(frame, rows, x, y, color, scale=1):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.rect(x + c * scale, y + r * scale, scale, scale, color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < ASK_END:
            frame.text("CAN IT RUN DOOM" + ("?" if index % 4 < 3 else ""), "center", 4, C.WHITE, proportional=True)
            continue
        if index >= HALL_END:
            k = index - HALL_END
            frame.text("YES.", "center", 0, C.GREEN if k % 4 < 2 else C.WHITE, proportional=True)
            if k >= 2:
                frame.text("IT RUNS DOOM", "center", 9, C.YELLOW, proportional=True)
            continue

        step = index - ASK_END
        for cx, cy in ((0, 0), (95, 0), (0, 15), (95, 15)):
            frame.line(cx, cy, VP[0], VP[1], C.BLUE)
        for k in range(RINGS):
            s = ((k + step * 0.25) % RINGS) / RINGS
            s = s * s
            hw, hh = 47.5 * s, 7.5 * s
            if hw < 1:
                continue
            frame.rect(round(VP[0] - hw), round(VP[1] - hh), round(2 * hw) + 1, round(2 * hh) + 1,
                       C.CYAN if s > 0.5 else C.BLUE)

        if index < FIRE_AT + 2:
            scale = 1 if index < GROW_AT else 2
            hit = index >= FIRE_AT
            imp_w, imp_h = 7 * scale, 7 * scale
            sprite(frame, IMP, round(VP[0] - imp_w / 2), round(VP[1] - imp_h / 2) + (0 if scale == 1 else 0),
                   C.WHITE if hit else C.RED, scale)
        if FIRE_AT <= index < FIRE_AT + 2:
            for dx, dy in ((-2, -1), (0, -2), (2, -1), (-1, -3), (1, -3), (0, -4)):
                frame.pixel(48 + dx, 12 + dy, C.YELLOW if index == FIRE_AT else C.RED)
        sprite(frame, GUN, 46, 13 if index < FIRE_AT else 14, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/can_it_run_doom.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
