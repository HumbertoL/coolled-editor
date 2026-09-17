#!/usr/bin/env python3
"""
Hello there (2005) -- and the only correct answer to it.

Obi-Wan strolls in from the left and raises a hand: HELLO THERE. Then the
reply arrives at speed -- Grievous slides in from the right, four arms
unfolding, four blades igniting one at a time and winding up into the
windmill -- and the panel answers GENERAL KENOBI! Obi-Wan lights his own
blade last, which is when the greeting stops being a greeting.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
WALK_UNTIL = 7          # Obi-Wan is still arriving
GREETING_AT = 7         # HELLO THERE starts typing
ARRIVAL_AT = 18         # Grievous enters
IGNITE_AT = 25          # one blade per frame from here
REPLY_AT = 33           # GENERAL KENOBI!
OBI_SABRE_AT = 45

OBI_Y = 9
GRIEVOUS_X, GRIEVOUS_Y = 72, 8
PIVOT = (GRIEVOUS_X + 2, GRIEVOUS_Y + 3)
BLADE_COLORS = [C.BLUE, C.GREEN, C.BLUE, C.GREEN]

OBI_WAN = [
    ".#.",
    "###",
    "###",
    ".#.",
    "#.#",
    "#.#",
]
GRIEVOUS = [
    "#####",
    "#.#.#",
    "..#..",
    ".###.",
    "..#..",
    ".#.#.",
    ".#.#.",
]


def sprite(frame, rows, x, y, color):
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, y + row, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, 15, 96, C.BLUE)

        # Obi-Wan: walks in, then stands there being pleased with himself.
        obi_x = min(12, index * 2)
        sprite(frame, OBI_WAN, obi_x, OBI_Y, C.CYAN)
        if index >= WALK_UNTIL:
            # The raised hand, with a small idle bob so he is not a statue.
            wave = 1 if index % 4 < 2 else 0
            frame.pixel(obi_x + 3, OBI_Y + 1 - wave, C.WHITE)
            frame.pixel(obi_x + 4, OBI_Y - wave, C.WHITE)
        if index >= OBI_SABRE_AT:
            reach = min(4, (index - OBI_SABRE_AT) * 2 + 2)
            frame.line(obi_x + 3, OBI_Y + 2, obi_x + 3, OBI_Y + 2 - reach, C.CYAN)

        # Grievous slides in and unfurls.
        if index >= ARRIVAL_AT:
            slide = max(0, 24 - (index - ARRIVAL_AT) * 8)
            lit = 0 if index < IGNITE_AT else min(4, index - IGNITE_AT + 1)
            spin = (index - IGNITE_AT) * 0.8
            for arm in range(lit):
                angle = spin + arm * math.pi / 2
                # Start the blade clear of the body so the spin stays legible;
                # the panel is wider than it is tall, hence the flat ellipse.
                dx, dy = math.cos(angle), math.sin(angle)
                frame.line(
                    PIVOT[0] + slide + round(3 * dx),
                    PIVOT[1] + round(2 * dy),
                    PIVOT[0] + slide + round(10 * dx),
                    PIVOT[1] + round(6 * dy),
                    BLADE_COLORS[arm],
                )
            # Body last, so a blade sweeping past never eats him.
            sprite(frame, GRIEVOUS, GRIEVOUS_X + slide, GRIEVOUS_Y, C.WHITE)

        if REPLY_AT <= index:
            shown = "GENERAL KENOBI!"[: max(1, (index - REPLY_AT) * 4)]
            flash = C.WHITE if (index - REPLY_AT) % 4 < 2 else C.YELLOW
            frame.text(shown, 2, 0, flash, proportional=True)
        elif index >= GREETING_AT:
            frame.text(
                "HELLO THERE"[: max(1, (index - GREETING_AT) * 2)],
                2, 0, C.CYAN, proportional=True,
            )
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hello_there.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
