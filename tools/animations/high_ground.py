#!/usr/bin/env python3
"""
The high ground (2005) -- Obi-Wan and Anakin on Mustafar.

Four dialogue beats, then the duel itself. IT'S OVER, ANAKIN / I HAVE THE
HIGH GROUND in Obi-Wan's cyan, UNDERESTIMATE MY POWER in Anakin's
yellow, DON'T TRY IT, and then he tries it: a crouch, a leap in a parabola
over the ledge, one white arc of a sabre, and the figure comes apart and
drops to the bank above the lava. Obi-Wan is left standing exactly where he
was, which is the whole joke.

The lava strip along the bottom runs under the dialogue too, so the panel
never goes to plain text.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
SEED = 2005
ACTION_AT = 28

#: (first frame, line one, line two, colour). Blank line two means one line,
#: vertically centred.
BEATS = [
    (0, "IT'S OVER,", "ANAKIN.", C.CYAN),
    (8, "I HAVE THE", "HIGH GROUND", C.CYAN),
    (17, "UNDERESTIMATE", "MY POWER!", C.YELLOW),
    (24, "DON'T TRY IT.", "", C.CYAN),
]

FIGURE = [
    ".#.",
    "###",
    ".#.",
    ".#.",
    "#.#",
]

BANK_TOP = 13          # low ground, where Anakin starts
LEDGE_TOP = 9          # high ground, where Obi-Wan stands and stays
LAVA_X0, LAVA_X1 = 45, 57
OBI_X, OBI_FEET = 72, LEDGE_TOP - 1
ANI_X, ANI_FEET = 22, BANK_TOP - 1
HAND = (OBI_X + 3, OBI_FEET - 3)   # where Obi-Wan's sabre pivots
LEAP_TO = OBI_X - 10               # where the leap gets to, and no further


def figure(frame, x, top, color):
    for row, line in enumerate(FIGURE):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, top + row, color)


def lava(frame, rng, index, wide):
    """The molten strip. `wide` opens it out for the action frames."""
    x0, x1 = (LAVA_X0, LAVA_X1) if wide else (0, 95)
    top = 12 if wide else 15
    for x in range(x0, x1 + 1):
        for y in range(top, 16):
            heat = rng.random() + 0.25 * math.sin((x + index * 2) / 4.0)
            frame.pixel(x, y, C.YELLOW if heat > 0.85 else C.RED)


def terrain(frame, rng, index):
    """Low bank on the left, the ledge on the right, lava in the gap."""
    # Lit edge, then a dither for the rock face: with no brightness levels
    # in the palette, every other pixel is the only way to read as "dimmer".
    for x0, top in ((0, BANK_TOP), (LAVA_X1 + 1, LEDGE_TOP)):
        x1 = LAVA_X0 if top == BANK_TOP else 96
        for x in range(x0, x1):
            frame.pixel(x, top, C.CYAN)
            for y in range(top + 1, 16):
                if (x + y) % 2 == 0:
                    frame.pixel(x, y, C.BLUE)
    lava(frame, rng, index, wide=True)


def sabre(frame, x0, y0, x1, y1, color):
    frame.line(x0, y0, x1, y1, color)


def guard(frame, color):
    """Obi-Wan's blade, held ready -- the pose he never leaves."""
    sabre(frame, HAND[0], HAND[1], HAND[0] + 4, HAND[1] - 4, color)


def blade(frame, angle, color):
    """His blade swung out from the hand at `angle`, y measured downward."""
    sabre(
        frame,
        HAND[0],
        HAND[1],
        HAND[0] + round(9 * math.cos(angle)),
        HAND[1] + round(9 * math.sin(angle)),
        color,
    )


def dialogue(frame, index):
    line_one, line_two, color = "", "", C.WHITE
    start = 0
    for beat_at, one, two, beat_color in BEATS:
        if index >= beat_at:
            start, line_one, line_two, color = beat_at, one, two, beat_color
    age = index - start
    # Each line types on, a couple of characters per frame.
    shown_one = line_one[: max(1, age * 5)]
    if not line_two:
        frame.text(shown_one, "center", 4, color, proportional=True)
        return
    frame.text(shown_one, 2, 0, color, proportional=True)
    if age >= 2:
        # The payoff line lands white for a frame, then settles.
        settled = color if age > 3 else C.WHITE
        frame.text(line_two[: max(1, (age - 2) * 5)], 2, 8, settled, proportional=True)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index < ACTION_AT:
            lava(frame, rng, index, wide=False)
            dialogue(frame, index)
            continue

        step = index - ACTION_AT
        terrain(frame, rng, index)
        figure(frame, OBI_X, OBI_FEET - 4, C.CYAN)

        if step < 3:
            # The crouch: Anakin gathers himself on the low ground.
            drop = 1 if step == 2 else 0
            figure(frame, ANI_X, ANI_FEET - 4 + drop, C.YELLOW)
            sabre(frame, ANI_X + 3, ANI_FEET - 2 + drop, ANI_X + 7, ANI_FEET - 5 + drop, C.BLUE)
            guard(frame, C.CYAN)
        elif step < 10:
            # The leap: a parabola from the bank to over the ledge. The
            # amplitude is picked so the apex keeps him on the panel.
            t = (step - 2) / 7.0
            x = round(ANI_X + (LEAP_TO - ANI_X) * t)
            top = round((ANI_FEET - 4) - 6 * math.sin(math.pi * t) - 4 * t)
            figure(frame, x, top, C.YELLOW)
            sabre(frame, x + 3, top + 2, x + 7, top - 1, C.BLUE)
            guard(frame, C.CYAN)
        elif step < 12:
            # The sabre comes round, trailing where it has been.
            k = step - 10
            for back in range(3):
                angle = math.radians(-45 - (k * 45 + back * 15))
                blade(frame, angle, C.WHITE if back == 0 else C.CYAN)
            figure(frame, LEAP_TO, 0 if k else 1, C.YELLOW)
        elif step == 12:
            # The cut. One white stroke through where he was.
            frame.line(LEAP_TO - 6, 6, LEAP_TO + 10, 0, C.WHITE)
            figure(frame, LEAP_TO, 0, C.WHITE)
        elif step < 18:
            # Two pieces: the top half carries on over the ledge, the rest
            # goes off the edge toward the lava.
            k = step - 13
            frame.hline(LEAP_TO, 1 + k, 3, C.YELLOW)
            frame.pixel(LEAP_TO + 1, 2 + k, C.YELLOW)
            # The other half clears the ledge edge and drops into the lava.
            fall_x, fall_y = LEAP_TO - 4 - k * 2, 3 + k * 3
            if fall_y < 13:
                frame.hline(fall_x, fall_y, 3, C.YELLOW)
                frame.pixel(fall_x + 1, fall_y + 1, C.RED)
            else:
                frame.vline(fall_x + 1, 11, 3, C.YELLOW)
            guard(frame, C.CYAN)
        else:
            # The tableau. He is left on the ledge; the lava throws light.
            k = step - 18
            frame.hline(LEAP_TO, LEDGE_TOP - 1, 3, C.YELLOW)
            frame.pixel(LEAP_TO + 3, LEDGE_TOP - 2, C.YELLOW)
            if k % 3 == 0:
                for x in range(LAVA_X0, LAVA_X1 + 1, 3):
                    frame.pixel(x, 11, C.YELLOW)
            guard(frame, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/high_ground.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
