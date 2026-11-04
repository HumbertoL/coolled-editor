#!/usr/bin/env python3
"""
Blue wave ocean -- a calm night sea, made to be left running.

Beats, all at once and all looping:

- A white moon hangs top right in a black sky dotted with blue, cyan and
  white stars that twinkle on their own slow cycles.
- Three parallax bands of swell roll across the dark water as thin
  outlines: a slow BLUE far band, a CYAN middle band flecked with blue, and
  a CYAN near band with a blue undertow whose crests break into WHITE foam.
  Each surface is a sum of sines whose spatial periods divide the panel width
  and whose temporal speeds are whole cycles per loop, so the last frame
  flows straight into the first.
- Under the moon a streak of cyan and white glints shimmers across the
  water, each glint flickering on a whole-number cycle.
- A small sailboat with a white sail rides the middle swell, rising and
  falling with the water beneath it and drifting gently to and fro, its white-and-blue hull under
  a white mainsail and jib.

Seamless: every moving thing is a function of 2*pi*frame/FRAMES with an
integer multiplier.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 110
W, H = 96, 16

MOON_X, MOON_Y, MOON_R = 80, 2, 2.3

# Each band: (base row, color, [(spatial cycles across 96px, temporal cycles
# per loop, amplitude, phase offset)]).  Positive temporal cycles move right.
BANDS = [
    ("far", 7.0, C.BLUE, [(4, 1, 0.5, 0.0), (7, 2, 0.3, 1.3)]),
    ("mid", 10.0, C.CYAN, [(3, 1, 1.0, 0.7), (5, 2, 0.6, 2.1), (11, 3, 0.25, 0.4)]),
    ("near", 13.4, C.CYAN, [(2, 1, 1.4, 2.5), (5, 3, 0.7, 0.2), (9, 4, 0.3, 1.7)]),
]

STARS = [  # (x, y, color, twinkle cycles per loop, phase)
    (5, 1, C.WHITE, 2, 0.0), (13, 4, C.BLUE, 1, 1.0), (21, 0, C.CYAN, 3, 2.0),
    (30, 2, C.WHITE, 1, 4.0), (38, 5, C.BLUE, 2, 0.5), (46, 1, C.CYAN, 1, 3.1),
    (55, 3, C.WHITE, 3, 1.7), (63, 0, C.BLUE, 2, 5.0), (69, 4, C.CYAN, 1, 2.6),
    (90, 5, C.WHITE, 2, 3.9), (93, 1, C.BLUE, 1, 0.9),
]

NEAR_FOAM = 12.4
STREAK_HALF = {"far": 1, "mid": 2, "near": 3}

BOAT_X, BOAT_DRIFT = 26.0, 3.0


def surface(band, x, t):
    _, base, _, waves = band
    y = base
    for k, m, amp, ph in waves:
        y += amp * math.sin(2 * math.pi * (k * x / W) - m * t + ph)
    return y


def glint(x, y, t):
    """Deterministic, looping flicker for the moon streak."""
    seed = (x * 37 + y * 101) % 97
    return math.sin(((seed % 3) + 1) * t + seed)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for sx, sy, col, cyc, ph in STARS:
            if math.sin(cyc * t + ph) > -0.4:
                frame.pixel(sx, sy, col)

        for x in range(W):
            for y in range(6):
                if (x - MOON_X) ** 2 + (y - MOON_Y) ** 2 <= MOON_R ** 2:
                    frame.pixel(x, y, C.WHITE)

        # Bands back to front; each blanks what is below its surface.
        for bi, band in enumerate(BANDS):
            name, _, color, _ = band
            for x in range(W):
                s = surface(band, x, t)
                top = round(s)
                for y in range(max(top, 0), H):
                    frame.pixel(x, y, C.BLACK)
                if name == "far":
                    frame.pixel(x, top, C.BLUE)
                elif name == "mid":
                    frame.pixel(x, top, C.CYAN)
                    if (x + 2 * top) % 4 == 0:
                        frame.pixel(x, top + 2, C.BLUE)
                else:
                    crest = s < NEAR_FOAM
                    frame.pixel(x, top, C.WHITE if crest else C.CYAN)
                    frame.pixel(x, top + 1, C.BLUE)

                # Moon streak: glints in the dark water below each surface.
                half = STREAK_HALF[name]
                if abs(x - MOON_X) <= half:
                    for y in range(top, H):
                        if abs(x - MOON_X) > half - (y % 2):
                            continue
                        g = glint(x, y, t)
                        if g > 0.55:
                            frame.pixel(x, y, C.WHITE)
                        elif g > -0.1:
                            frame.pixel(x, y, C.CYAN)

            if name == "mid":
                draw_boat(frame, t, band)

    return anim


def draw_boat(frame, t, band):
    bx = BOAT_X + BOAT_DRIFT * math.sin(t)
    x0 = round(bx)
    by = round(surface(band, bx, t))
    # Hull: 6 wide, tapering, sitting on the water.
    for dx in range(-4, 5):
        frame.pixel(x0 + dx, by - 2, C.BLACK)
    for dx in range(-3, 4):
        frame.pixel(x0 + dx, by - 1, C.WHITE)
    for dx in range(-2, 3):
        frame.pixel(x0 + dx, by, C.BLUE)
    # Mast and triangular sail.
    for dy in range(2, 7):
        frame.pixel(x0, by - dy, C.WHITE)
    for row, width in enumerate([1, 2, 3]):
        for dx in range(1, width + 1):
            frame.pixel(x0 + dx, by - 5 + row, C.WHITE)
    frame.pixel(x0 - 1, by - 2, C.WHITE)
    frame.pixel(x0 - 2, by - 2, C.WHITE)
    frame.pixel(x0 - 1, by - 3, C.WHITE)


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/blue_wave_ocean.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
