#!/usr/bin/env python3
"""
Coin flip -- a coin is tossed, spins four times in the air, and lands heads.

The coin is a disc of YELLOW with a WHITE rim, drawn with its width scaled by
the cosine of its spin angle, so it narrows edge-on and fills out face-on. It
rises and falls on a parabola over 29 frames and then rests. HEADS appears
once it has landed. The coin starts and ends flat on the ground, so the loop
returns to the first frame.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
FLIGHT = 29
RADIUS = 5.0
GROUND = 10
COIN_X = 22
TEXT_X = 46
SPINS = 4


def coin_state(index):
    if index >= FLIGHT:
        return GROUND, 0.0
    t = index / FLIGHT
    y = GROUND - 5 * math.sin(math.pi * t)
    angle = 2 * math.pi * SPINS * t
    return y, angle


def draw_coin(frame, cy, angle):
    squash = max(0.2, abs(math.cos(angle)))
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            sx = dx / squash
            value = sx * sx + dy * dy
            if value <= RADIUS * RADIUS:
                colour = C.WHITE if value > (RADIUS - 1.2) ** 2 else C.YELLOW
                frame.pixel(COIN_X + dx, round(cy) + dy, colour)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        cy, angle = coin_state(index)
        draw_coin(frame, cy, angle)
        if index > FLIGHT + 1:
            frame.text("HEADS", x=TEXT_X, y=2, color=C.YELLOW)
            frame.text("4 SPINS", x=TEXT_X, y=9, color=C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/coin_flip.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
