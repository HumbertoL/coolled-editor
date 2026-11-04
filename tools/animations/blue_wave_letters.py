#!/usr/bin/env python3
"""
Blue wave letters -- BLUE WAVE does the stadium wave.

The nine cells of BLUE WAVE, spread wide, ride a sine wave that travels left
to right, so each letter stands up in turn like a crowd doing the wave.
Colour comes from height: the letter at the crest is white, the ones on the
shoulders cyan, the ones down in the trough blue. Whichever letter is at the
crest throws off white spray: a few pixels flicked back and forward that arc
and fall for a couple of frames.

A quarter of the way in, the sea comes up underneath: a filled blue body
with a cyan surface that follows exactly the same wave as the letters, so
they surf on it, the swell flattening slightly to make room. It holds for a
while, white foam on its own crests, then ebbs back off the bottom of the
panel and the letters get their full travel back.

Seamless: the wave advances a whole number of cycles over the loop, the tide
is out at both ends, and spray is seeded by the (wrapped) frame it left from.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

FRAMES = 48
DELAY = 100
MESSAGE = "BLUE WAVE"
TRACKING = 4
CYCLES = 2  # wave cycles per loop -- must be an integer for a seamless wrap
WAVELENGTH = 52.0  # pixels

# Letter top row = centre - amp * sin(...). Dry: rows 1..9 (glyph bottom at
# row 15). Wet: rows 1..6, leaving the sea room underneath.
DRY_CENTRE, DRY_AMP = 5.0, 4.0
WET_CENTRE, WET_AMP = 3.5, 2.5

# Tide schedule (frames): rising, high, ebbing.
RISE_START, RISE_END = 10, 18
EBB_START, EBB_END = 32, 40
SUNK = 11  # how far below its high-water line the sea sits when out

SPRAY_LIFE = 3
SPRAY_PER_FRAME = 3


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def tide(t):
    """0 when the sea is out, 1 at high water."""
    if t < RISE_START or t >= EBB_END:
        return 0.0
    if t < RISE_END:
        return ease((t - RISE_START) / (RISE_END - RISE_START))
    if t < EBB_START:
        return 1.0
    return 1.0 - ease((t - EBB_START) / (EBB_END - EBB_START))


def swell(x, t):
    """Wave height in -1..1 at column x, frame t; +1 is the crest."""
    return math.sin(2 * math.pi * (x / WAVELENGTH - CYCLES * t / FRAMES))


def shape(t):
    w = tide(t)
    centre = DRY_CENTRE + (WET_CENTRE - DRY_CENTRE) * w
    amp = DRY_AMP + (WET_AMP - DRY_AMP) * w
    return w, centre, amp


def letters(width):
    positions, total = layout_text(MESSAGE, tracking=TRACKING)
    left = (width - total) // 2
    return [(ch, left + x) for ch, x in positions if ch != " "]


def letter_top(cell_x, t):
    _, centre, amp = shape(t)
    s = swell(cell_x + GLYPH_WIDTH / 2, t)
    return round(centre - amp * s), s


def height_color(s):
    if s > 0.6:
        return C.WHITE
    if s > -0.35:
        return C.CYAN
    return C.BLUE


def carve(frame, ch, x, y):
    """Black out the sea beside each stroke, so a blue letter never merges into blue water."""
    bitmap = glyph(ch)
    for row in range(GLYPH_HEIGHT):
        for col in range(GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                for dx in (-1, 1):
                    if frame.get(x + col + dx, y + row) == C.BLUE:
                        frame.pixel(x + col + dx, y + row, C.BLACK)


def draw_glyph(frame, ch, x, y, color):
    bitmap = glyph(ch)
    for row in range(GLYPH_HEIGHT):
        for col in range(GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                frame.pixel(x + col, y + row, color)


def draw_sea(frame, cast, t):
    w, centre, amp = shape(t)
    if w <= 0:
        return
    sink = (1 - w) * SUNK
    floor = {}  # columns under a letter: the surface never rises into it
    for _, cell_x in cast:
        top, _ = letter_top(cell_x, t)
        for col in range(cell_x, cell_x + GLYPH_WIDTH):
            floor[col] = top + GLYPH_HEIGHT
    for x in range(frame.width):
        s = swell(x, t)
        surface = round(centre - amp * s + GLYPH_HEIGHT + sink)
        surface = max(surface, floor.get(x, surface))
        for y in range(max(surface, 0), frame.height):
            frame.pixel(x, y, C.CYAN if y == surface else C.BLUE)
        if s > 0.93 and x not in floor:
            frame.pixel(x, surface - 1, C.WHITE)  # foam on the sea's own crests


def crest_letters(cast, t):
    """Every letter riding a crest at frame t (two can be up at once)."""
    out = []
    for i, (_, cell_x) in enumerate(cast):
        top, s = letter_top(cell_x, t)
        if s > 0.85:
            out.append((i, cell_x, top))
    return out


def draw_spray(frame, cast, t):
    for age in range(SPRAY_LIFE):
        born = (t - age) % FRAMES
        for i, cell_x, top in crest_letters(cast, born):
            rng = random.Random(born * 7919 + i * 31 + 17)
            spray_from(frame, rng, cell_x, top, age)


def spray_from(frame, rng, cell_x, top, age):
    """A few droplets flicked off both shoulders of a crest letter, arcing down."""
    for _ in range(SPRAY_PER_FRAME):
        side = rng.choice((-1, 1))
        x0 = cell_x - 1 if side < 0 else cell_x + GLYPH_WIDTH
        y0 = top + rng.randint(0, 2)
        vx = side * rng.choice((1, 2))
        vy = rng.choice((-1, -1, 0))
        x = x0 + vx * age
        y = y0 + vy * age + (age * (age + 1)) // 2  # gravity
        frame.pixel(x, y, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    cast = letters(anim.width)
    for t in range(FRAMES):
        frame = anim.frame()
        draw_sea(frame, cast, t)
        draw_spray(frame, cast, t)
        for ch, cell_x in cast:
            top, s = letter_top(cell_x, t)
            carve(frame, ch, cell_x, top)
            draw_glyph(frame, ch, cell_x, top, height_color(s))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/blue_wave_letters.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
