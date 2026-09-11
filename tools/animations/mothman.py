#!/usr/bin/env python3
"""
Mothman -- Point Pleasant, and the bridge that is the whole point.

The Silver Bridge is drawn first: towers, a sagging catenary, hangers down to
the deck. Two red eyes open above it and hold, because the eyes are what
every account starts with. Then the wings unfold either side of them, take
the thing up off the span, and turn it toward you -- the span doubling every
few frames until the wings run off both edges of the panel and there is
nothing left but the eyes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

# Scene beats, by frame index.
EYES_AT = 5         # they open over the bridge
WINGS_AT = 13       # and something unfolds either side of them
RISE_AT = 21        # up off the deck
SWOOP_AT = 38       # toward the lens
DARK_AT = 50        # wings past both edges; only the eyes are left

DECK_Y = 14
TOWER_X = (20, 76)
CENTER_X = 48


def draw_bridge(frame):
    frame.hline(0, DECK_Y, 96, C.BLUE)
    frame.hline(0, DECK_Y + 1, 96, C.BLUE)
    for x in TOWER_X:
        frame.vline(x, 4, DECK_Y - 4, C.BLUE)
    frame.line(0, 9, TOWER_X[0], 4, C.BLUE)
    frame.line(TOWER_X[1], 4, 95, 9, C.BLUE)
    span = TOWER_X[1] - TOWER_X[0]
    for x in range(TOWER_X[0], TOWER_X[1] + 1):
        sag = 4 + round(6 * math.sin(math.pi * (x - TOWER_X[0]) / span))
        frame.pixel(x, sag, C.BLUE)
        if (x - TOWER_X[0]) % 7 == 0:
            frame.vline(x, sag, DECK_Y - sag, C.BLUE)


def draw_wings(frame, cx, cy, span, flap):
    """
    One filled wing each side. ``flap`` in [-1, 1] drives both the arch of
    the leading edge and how deep the web hangs behind it.
    """
    for side in (-1, 1):
        for step in range(1, span + 1):
            u = step / span
            lead = cy - round(5 * flap * math.sin(math.pi * u)) - round(3 * u)
            depth = max(1, round(5 * (1 - u) + 2 * flap))
            frame.vline(cx + side * step, lead, depth, C.MAGENTA)
            frame.pixel(cx + side * step, lead, C.WHITE if flap > 0.4 else C.MAGENTA)


def draw_body(frame, cx, cy, eye_size, eye=C.RED):
    """Body under a pair of eyes that keep a one-pixel gap at any size."""
    frame.vline(cx, cy, 5, C.MAGENTA)
    if eye_size > 1:
        frame.vline(cx - 1, cy + 1, 3, C.MAGENTA)
        frame.vline(cx + 1, cy + 1, 3, C.MAGENTA)
    for side in (-1, 1):
        left = cx - eye_size if side < 0 else cx + 1
        frame.rect(left, cy - eye_size, eye_size, eye_size, eye, fill=True)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < DARK_AT:
            draw_bridge(frame)

        if index < EYES_AT:
            continue

        flap = math.sin(2 * math.pi * index / 6)
        if index < WINGS_AT:
            cy = 8
            span = 0
            eye_size = 1
        elif index < RISE_AT:
            grown = (index - WINGS_AT) / (RISE_AT - WINGS_AT)
            cy = 8
            span = round(18 * grown)
            eye_size = 1
        elif index < SWOOP_AT:
            rise = (index - RISE_AT) / (SWOOP_AT - RISE_AT)
            cy = round(8 - 3 * math.sin(math.pi * rise))
            span = 18 + round(4 * rise)
            eye_size = 1
        else:
            close = (index - SWOOP_AT) / (FRAMES - SWOOP_AT)
            cy = 8
            span = round(22 + 40 * close * close)
            eye_size = 1 + round(2 * close)

        if index >= DARK_AT:
            # Past the edges of the panel: eyes only, and then not even those.
            draw_body(frame, CENTER_X, 8, 3 if index < FRAMES - 1 else 2)
            continue

        if span:
            draw_wings(frame, CENTER_X, cy, span, flap)
        draw_body(frame, CENTER_X, cy, eye_size)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/mothman.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
