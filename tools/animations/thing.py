#!/usr/bin/env python3
"""
Thing (The Addams Family) -- the hand lets itself out of the box.

The lid of Thing's box swings open at the left, a hand climbs out and
scuttles across the panel on its fingertips, stops in the middle to drum
them one after another -- the impatient tap that is the whole character --
then bolts off the right edge. The fingers are procedural rather than a
sprite: each swings fore and aft on its own quarter-cycle phase and lifts on
the forward half, which is what makes the gait read as scuttling on so few
pixels.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
GROUND = 15
BOX_X, BOX_Y = 2, 8

# Scene beats, by frame index.
LID_OPEN = 5        # lid finishes swinging up
CLIMB_END = 11      # hand is out of the box and on the floor
WALK_END = 33       # arrives at the drumming spot
DRUM_END = 45       # done being impatient, and away
LID_SHUT = 48       # the box closes itself once Thing has gone

START_X, DRUM_X = 15.0, 56.0
PALM = [
    "..###..",
    ".#####.",
    "#######",
    ".#####.",
]
FINGER_ROOTS = [0, 2, 4, 6]


def hand_x(index):
    """Where the wrist is on frame ``index``."""
    if index <= CLIMB_END:
        return START_X
    if index <= WALK_END:
        t = (index - CLIMB_END) / (WALK_END - CLIMB_END)
        return START_X + (DRUM_X - START_X) * t
    if index <= DRUM_END:
        return DRUM_X
    t = (index - DRUM_END) / (FRAMES - DRUM_END)
    return DRUM_X + (112 - DRUM_X) * t


def lid_openness(index):
    """0 shut, 1 straight up. Shuts again at the end, so the loop wraps."""
    if index <= LID_OPEN:
        return index / LID_OPEN
    if index < LID_SHUT:
        return 1.0
    return max(0.0, 1 - (index - LID_SHUT + 1) / (FRAMES - LID_SHUT))


def draw_box(frame, index):
    """The crate, and its lid swinging up over the first few frames."""
    frame.rect(BOX_X, BOX_Y, 13, GROUND - BOX_Y + 1, C.BLUE)
    frame.vline(BOX_X + 6, BOX_Y + 2, GROUND - BOX_Y - 1, C.BLUE)
    angle = math.radians(90 * lid_openness(index))
    tip_x = BOX_X + round(12 * math.cos(angle))
    tip_y = BOX_Y - round(12 * math.sin(angle))
    frame.line(BOX_X, BOX_Y, tip_x, tip_y, C.CYAN)


def draw_hand(frame, x, y, phase, drum=None, lifted=0.0):
    """
    Palm at (x, y), fingers walking under it.

    ``phase`` drives the gait; ``drum`` names a single finger to raise
    instead, for the tapping beat. ``lifted`` tilts the whole hand up onto
    its wrist as it climbs out of the box.
    """
    for row, line in enumerate(PALM):
        for column, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + column, y + row, C.YELLOW)
    # The cuff at the wrist, and the thumb tucked behind it.
    frame.vline(x - 1, y + 1, 2, C.WHITE)
    frame.pixel(x - 1, y + 3, C.YELLOW)

    palm_bottom = y + len(PALM)
    for finger, root in enumerate(FINGER_ROOTS):
        if drum is not None:
            # Impatient tap: one finger up, the rest planted.
            tip_x = x + root
            tip_y = GROUND - (3 if finger == drum else 0)
        else:
            step = (phase + finger / len(FINGER_ROOTS)) % 1.0
            tip_x = x + root + round(2 * math.cos(2 * math.pi * step))
            tip_y = GROUND - round(2 * max(0.0, math.sin(2 * math.pi * step)))
        tip_y = min(tip_y, GROUND) - round(lifted)
        frame.line(x + root, palm_bottom - 1, tip_x, tip_y, C.YELLOW)
        frame.pixel(tip_x, tip_y, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, GROUND, 96, C.BLUE)
        draw_box(frame, index)

        x = round(hand_x(index))
        if index < LID_OPEN:
            continue
        if index <= CLIMB_END:
            # Rising out of the box: the palm lifts clear of the rim.
            t = (index - LID_OPEN) / (CLIMB_END - LID_OPEN)
            y = round(BOX_Y + 2 - 5 * t)
            draw_hand(frame, x, y, 0.0, lifted=round(3 * (1 - t)))
        elif index <= WALK_END:
            bob = 1 if index % 2 else 0
            draw_hand(frame, x, GROUND - 6 - bob, index * 0.25)
        elif index <= DRUM_END:
            beat = (index - WALK_END - 1) % (len(FINGER_ROOTS) + 1)
            draw_hand(frame, x, GROUND - 6, 0.0, drum=beat if beat < 4 else None)
        else:
            bob = 1 if index % 2 else 0
            draw_hand(frame, x, GROUND - 6 - bob, index * 0.35)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/thing.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
