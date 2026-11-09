#!/usr/bin/env python3
"""
Assembly line -- a three-station factory that turns lumps into presents.

A conveyor carries items a station's width at a time. While the belt is
stopped, all three machines work at once, each on a different item:

* the press drops a mould over a raw cyan lump and lifts off a white box;
* the sprayer paints the box red from the top down;
* the arm comes down and ties a yellow ribbon round it.

Then the belt runs again: the finished present leaves on the right, each
item moves up one station, and a new lump arrives from the left. Because
every item ends the cycle exactly where the one ahead of it began, in the
state that one began in, the 53 frames loop seamlessly -- the factory never
stops, and it is always the same instant of the same shift.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
PITCH = 32                 # distance between stations
STATIONS = (16, 48, 80)    # x of each station's centre line
TRAVEL = 16                # frames the belt runs; the rest is work
BELT_Y = 13
RAW, BOX, PAINTED, WRAPPED = range(4)

LUMP = [
    "..####..",
    ".######.",
    "########",
    "########",
]
# Top row of the mould for each work frame: down, hold, back up.
MOULD = [-4, -4, -2, 0, 2, 4, 6, 6, 6, 6, 4, 2, 0, -2]
SPRAY_START, SPRAY_ROW_FRAMES = 8, 4
ARM = {20: 1, 21: 2, 22: 3, 23: 4, 24: 4, 25: 4, 26: 4, 27: 4, 28: 3, 29: 2, 30: 1}
TIED = 24                  # work frame the ribbon goes on


def draw_item(frame, cx, state, painted_rows=0):
    left = cx - 4
    if state == RAW:
        for r, row in enumerate(LUMP):
            for col, cell in enumerate(row):
                if cell == "#":
                    frame.pixel(left + col, BELT_Y - 4 + r, C.CYAN)
        return
    frame.rect(left, BELT_Y - 6, 8, 6, C.WHITE)
    rows = 4 if state >= PAINTED else painted_rows
    frame.rect(left + 1, BELT_Y - 5, 6, rows, C.RED, fill=True)
    if state == WRAPPED:
        frame.rect(cx - 1, BELT_Y - 6, 2, 6, C.YELLOW, fill=True)
        frame.hline(cx - 2, BELT_Y - 7, 4, C.YELLOW)
        frame.pixel(cx - 3, BELT_Y - 8, C.YELLOW)
        frame.pixel(cx + 2, BELT_Y - 8, C.YELLOW)


def draw_belt(frame, shift):
    frame.hline(0, BELT_Y, 96, C.BLUE)
    frame.hline(0, 15, 96, C.BLUE)
    for x in range(96):
        if (x - shift) % 4 == 0:
            frame.pixel(x, 14, C.CYAN)


def draw_press(frame, top):
    x = STATIONS[0]
    frame.rect(x - 1, 0, 2, max(top, 0), C.YELLOW, fill=True)
    frame.rect(x - 5, top, 10, 7, C.MAGENTA, fill=True)


def draw_sprayer(frame, spraying, work):
    x = STATIONS[1]
    frame.rect(x - 2, 0, 4, 2, C.GREEN, fill=True)
    frame.rect(x - 1, 2, 2, 1, C.GREEN, fill=True)
    if spraying:
        for y in range(3, BELT_Y - 6):
            for dx in range(-3, 3):
                if (dx * 7 + y * 13 + work * 5) % 3 == 0 and abs(dx + 0.5) <= y - 1.5:
                    frame.pixel(x + dx, y, C.RED)


def draw_arm(frame, reach):
    x = STATIONS[2]
    frame.rect(x - 1, 0, 2, reach, C.GREEN, fill=True)
    frame.hline(x - 3, reach, 6, C.GREEN)
    frame.pixel(x - 3, reach + 1, C.GREEN)
    frame.pixel(x + 2, reach + 1, C.GREEN)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        moving = index < TRAVEL
        shift = PITCH * index // TRAVEL if moving else PITCH
        work = index - TRAVEL          # negative while the belt runs
        draw_belt(frame, shift)

        mould_top = MOULD[work] if 0 <= work < len(MOULD) else MOULD[0]
        pressed = work >= MOULD.index(6)
        painted_rows = max(0, min(4, (work - SPRAY_START) // SPRAY_ROW_FRAMES + 1)) if work >= SPRAY_START else 0
        spraying = SPRAY_START <= work < SPRAY_START + 4 * SPRAY_ROW_FRAMES
        tied = work >= TIED

        # Items by the station they are heading for (or sitting at).
        x0 = STATIONS[0] - PITCH + shift
        draw_item(frame, x0, BOX if pressed else RAW)
        draw_item(frame, x0 + PITCH, PAINTED if painted_rows == 4 else BOX, painted_rows)
        draw_item(frame, x0 + 2 * PITCH, WRAPPED if tied else PAINTED)
        if moving:
            draw_item(frame, x0 + 3 * PITCH, WRAPPED)

        draw_press(frame, mould_top)
        draw_sprayer(frame, spraying, work)
        draw_arm(frame, ARM.get(work, 1))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/assembly_line.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
