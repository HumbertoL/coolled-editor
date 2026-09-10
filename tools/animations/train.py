#!/usr/bin/env python3
"""
Train -- a steam locomotive chuffing along.

The locomotive holds the middle of the panel while the world scrolls past:
telegraph poles slide left exactly one panel width over the loop, the drive
wheels turn a whole number of times, and the chimney puffs smoke on a cycle
that divides the frame count. All three periods line up, so it loops
seamlessly.

Smoke fades white -> cyan -> blue as it rises and drifts behind the train,
since the palette has no brightness to spend on a real fade.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90

RAIL_Y = 15
POLE_SPACING = 32  # divides 96, so the scroll wraps cleanly
WHEEL_TURNS = 6  # whole turns over the loop
PUFFS = 6  # concurrent smoke puffs; FRAMES / PUFFS frames apart


def draw_background(frame, t):
    # Rail plus sleepers.
    frame.hline(0, RAIL_Y, 96, C.BLUE)
    scroll = int(t * 96)
    for base in range(-POLE_SPACING, 96 + POLE_SPACING, 8):
        x = (base - scroll) % 96
        frame.pixel(x, RAIL_Y, C.CYAN)
    # Telegraph poles.
    for base in range(0, 96 + POLE_SPACING, POLE_SPACING):
        x = (base - scroll) % 96
        frame.vline(x, 6, 8, C.BLUE)
        frame.hline(x - 1, 7, 3, C.BLUE)


def draw_wheel(frame, cx, cy, radius, angle):
    steps = int(2 * math.pi * radius * 2)
    for i in range(steps):
        a = 2 * math.pi * i / steps
        frame.pixel(
            round(cx + radius * math.cos(a)),
            round(cy + radius * math.sin(a)),
            C.YELLOW,
        )
    # One spoke straight through, so the turn reads.
    for rr in (-radius + 1, 0, radius - 1):
        frame.pixel(
            round(cx + rr * math.cos(angle)),
            round(cy + rr * math.sin(angle)),
            C.WHITE,
        )


def draw_locomotive(frame, t):
    # Boiler, facing left.
    frame.rect(32, 8, 22, 5, C.RED, fill=True)
    frame.hline(32, 8, 22, C.YELLOW)
    # Chimney with a flared top.
    frame.rect(35, 5, 3, 3, C.RED, fill=True)
    frame.hline(34, 5, 5, C.YELLOW)
    # Cab.
    frame.rect(54, 4, 9, 9, C.RED, fill=True)
    frame.hline(53, 4, 11, C.YELLOW)
    frame.rect(56, 6, 4, 4, C.CYAN, fill=True)
    # Cowcatcher.
    frame.line(31, 9, 28, 13, C.YELLOW)
    frame.line(31, 13, 28, 13, C.YELLOW)
    # Tender behind the cab.
    frame.rect(65, 7, 10, 6, C.RED, fill=True)
    frame.hline(65, 7, 10, C.YELLOW)
    # Headlamp.
    frame.pixel(31, 8, C.WHITE)

    angle = 2 * math.pi * WHEEL_TURNS * t
    draw_wheel(frame, 38, 13, 2.2, angle)
    draw_wheel(frame, 47, 13, 2.2, angle)
    frame.pixel(58, 14, C.YELLOW)
    frame.pixel(61, 14, C.YELLOW)
    frame.pixel(68, 14, C.YELLOW)
    frame.pixel(72, 14, C.YELLOW)


def draw_smoke(frame, t):
    for k in range(PUFFS):
        age = (t - k / PUFFS) % 1.0
        # Rises from the chimney, drifting back over the train.
        x = 36 + age * 14
        y = 4 - age * 12
        if y < -1:
            continue
        if age < 0.3:
            color = C.WHITE
        elif age < 0.65:
            color = C.CYAN
        else:
            color = C.BLUE
        frame.pixel(round(x), round(y), color)
        if age > 0.25:
            frame.pixel(round(x) + 1, round(y), color)
            frame.pixel(round(x), round(y) - 1, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        draw_background(frame, t)
        draw_smoke(frame, t)
        draw_locomotive(frame, t)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/train.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
