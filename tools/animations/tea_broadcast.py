#!/usr/bin/env python3
"""
Broadcast -- one message going out to many people at once.

Text-Em-All's whole product in six seconds: a sender on the left emits waves
that sweep right across the panel, and each recipient lights up the moment the
wave reaches it. Recipients wait in blue, turn white as the wave passes, then
settle to green -- delivered. Once the last one is reached they all pulse
together, then reset for the next send.

The arcs are ellipses squashed horizontally, so a wavefront stays visible as a
curve on a panel only sixteen pixels tall.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 100
SEED = 8

SENDER_X, SENDER_Y = 5, 8
TRAVEL_FRAMES = 17          # wave reaches the far edge
CONFIRM_FRAMES = 4          # everyone lit, pulsing
X_SQUASH = 0.34
# The squash and the radius are coupled: a wavefront of radius r reaches
# r / X_SQUASH pixels sideways, so to just clear a 96-wide panel from the
# sender the radius only needs to reach (96 - SENDER_X) * X_SQUASH ~= 31.
MAX_RADIUS = 33
WAVE_SPACING = 11
WAVES = 3
JUST_HIT = 5


def recipients(rng, width):
    """Scattered down the right two thirds, clear of the sender."""
    spots = []
    for column in range(34, width - 3, 7):
        spots.append((column + rng.randrange(-2, 3), rng.randrange(2, 14)))
    return spots


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    people = recipients(rng, anim.width)

    def distance(x, y):
        return math.hypot((x - SENDER_X) * X_SQUASH, y - SENDER_Y)

    for index in range(FRAMES):
        frame = anim.frame()
        sending = index < TRAVEL_FRAMES
        confirming = TRAVEL_FRAMES <= index < TRAVEL_FRAMES + CONFIRM_FRAMES
        lead = (index / (TRAVEL_FRAMES - 1)) * MAX_RADIUS if sending else MAX_RADIUS

        # Wavefronts, trailing behind the leading edge.
        if sending:
            for wave in range(WAVES):
                radius = lead - wave * WAVE_SPACING
                if radius <= 1:
                    continue
                color = (C.WHITE, C.CYAN, C.BLUE)[wave]
                for x in range(anim.width):
                    for y in range(anim.height):
                        if abs(distance(x, y) - radius) < 0.9:
                            frame.pixel(x, y, color)

        # Recipients.
        for x, y in people:
            reach = distance(x, y)
            if confirming:
                color = C.WHITE if index % 2 == 0 else C.GREEN
            elif not sending:
                color = C.BLUE          # reset for the next send
            elif reach > lead:
                color = C.BLUE          # not yet reached
            elif lead - reach < JUST_HIT:
                color = C.WHITE         # just hit
            else:
                color = C.GREEN         # delivered
            frame.pixel(x, y, color)
            frame.pixel(x, y - 1, color if color is C.WHITE else C.BLACK)

        # The sender: a mast that flashes while transmitting.
        for y in range(5, 12):
            frame.pixel(SENDER_X, y, C.YELLOW if sending else C.BLUE)
        frame.pixel(SENDER_X - 1, 5, C.YELLOW if sending and index % 2 == 0 else C.BLACK)
        frame.pixel(SENDER_X + 1, 5, C.YELLOW if sending and index % 2 == 0 else C.BLACK)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_broadcast.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
