#!/usr/bin/env python3
"""
Parade balloon -- a giant turkey floats down the avenue.

A Thanksgiving parade seen from the curb, with the camera walking alongside.
Across the middle of the panel a huge inflated turkey balloon -- red body
with a white shine, a fanned tail in yellow, magenta and green bands, white
head, yellow beak, red wattle -- bobs and sways on white tethers held by four
tiny handlers in blue. Ahead of it a marching band in red coats with white
plumes keeps step: a yellow tuba, a white bass drum, a trumpet, with music
notes drifting up. Behind it two banner carriers hold a magenta banner that
reads THANKS.

Behind the parade a blue-outlined skyline with cyan and white windows slides slowly
left, and the street's lane dashes slide faster, so the parade seems to
advance while staying centred. Confetti in every colour drifts down.

Everything repeats on a 48-frame period: the skyline tiles every 48px and
scrolls 1px a frame, the lane dashes every 12px at 2px a frame, the bob and
the march are 24 and 4 frames, and each confetti fleck falls exactly one
panel height per loop. Seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 48
DELAY = 110
W, H = 96, 16
TAU = math.tau

# --- skyline: one 48px tile, repeated ------------------------------------
TILE = 48
SKY_BOTTOM = 10          # buildings stop above the street
rnd_city = random.Random(1126)
BUILDINGS = []          # (x, width, top)
x = 0
while x < TILE:
    w = rnd_city.choice((5, 6, 7, 8))
    w = min(w, TILE - x)
    top = rnd_city.choice((2, 3, 4, 5, 6, 7))
    BUILDINGS.append((x, w, top))
    x += w + rnd_city.choice((0, 1))
WINDOWS = set()
for bx, bw, top in BUILDINGS:
    for wx in range(bx + 1, bx + bw - 1, 2):
        for wy in range(top + 2, SKY_BOTTOM - 1, 2):
            if rnd_city.random() < 0.35:
                WINDOWS.add((wx, wy))

# --- confetti --------------------------------------------------------------
rnd_conf = random.Random(2511)
CONFETTI = [
    (rnd_conf.uniform(0, W), rnd_conf.uniform(0, H), rnd_conf.uniform(0, TAU),
     rnd_conf.choice((C.RED, C.YELLOW, C.GREEN, C.MAGENTA, C.CYAN, C.WHITE)))
    for _ in range(14)
]

BALLOON_X = 33           # left edge of the balloon's bounding box


def draw_city(c, f):
    """Building outlines only, so the parade in front stays readable."""
    off = f % TILE
    for rep in range(-1, W // TILE + 2):
        base = rep * TILE - off
        for bx, bw, top in BUILDINGS:
            x0, x1 = base + bx, base + bx + bw - 1
            c.hline(x0, top, bw, C.BLUE)
            c.vline(x0, top, SKY_BOTTOM - top, C.BLUE)
            c.vline(x1, top, SKY_BOTTOM - top, C.BLUE)
        for wx, wy in WINDOWS:
            # windows wink on and off, on the 48-frame period
            if (wx * 7 + wy * 3 + f // 8) % 11:
                c.pixel(base + wx, wy, C.CYAN if (wx + wy) % 3 else C.WHITE)


def draw_street(c, f):
    off = (2 * f) % 12
    for x0 in range(-12, W + 12, 12):
        c.hline(x0 - off, 15, 4, C.YELLOW)


def balloon_pixels(bob, sway):
    """The balloon, as {(x, y): color}."""
    px = {}
    ox = BALLOON_X + sway
    oy = bob
    # tail fan: a half-disc behind the body, in radial bands
    fcx, fcy = ox + 8, oy + 9
    for y in range(oy - 1, fcy + 1):
        for x in range(ox - 2, ox + 19):
            d = math.hypot((x - fcx) / 1.15, y - fcy)
            if d <= 9.3:
                ang = math.atan2(fcy - y, fcx - x)          # 0 = pointing left
                band = min(8, int(ang / (math.pi / 9)))
                col = (C.YELLOW, C.MAGENTA, C.GREEN)[band % 3]
                if d > 8.3:
                    col = C.WHITE if band % 2 else C.RED     # feather tips
                px[(x, y)] = col
    # body: a fat ellipse in front of the fan
    bcx, bcy = ox + 16, oy + 8
    for y in range(oy + 3, oy + 14):
        for x in range(ox + 6, ox + 27):
            if ((x - bcx) / 8.6) ** 2 + ((y - bcy) / 4.4) ** 2 <= 1:
                px[(x, y)] = C.RED
    # a white shine and a magenta wing
    for p in ((bcx + 2, bcy - 3), (bcx + 3, bcy - 3), (bcx + 4, bcy - 2)):
        px[p] = C.WHITE
    for dx, dy in ((-3, 0), (-2, 0), (-1, 0), (0, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (0, 2), (2, 2)):
        px[(bcx + dx, bcy + dy)] = C.MAGENTA
    # neck and head, facing right
    for p in ((ox + 24, oy + 5), (ox + 25, oy + 4), (ox + 25, oy + 5)):
        px[p] = C.WHITE
    hx, hy = ox + 25, oy + 1
    for dy, row in enumerate((".WW.", "WWWW", "WWKW", ".WWW")):
        for dx, ch in enumerate(row):
            if ch != ".":
                px[(hx + dx, hy + dy)] = C.WHITE if ch == "W" else C.BLACK
    px[(hx + 4, hy + 2)] = C.YELLOW
    px[(hx + 5, hy + 2)] = C.YELLOW
    px[(hx + 3, hy + 4)] = C.RED
    px[(hx + 3, hy + 5)] = C.RED
    return px


HANDLERS = [35, 43, 51, 59]
# where each tether meets the balloon, relative to the balloon origin
ANCHORS = [(5, 9), (11, 11), (18, 12), (24, 10)]


def draw_handler(c, x, f, i):
    step = (f + i) % 4 < 2
    c.pixel(x, 12, C.WHITE)                      # head
    c.pixel(x, 13, C.BLUE)
    c.pixel(x, 14, C.BLUE)
    c.pixel(x - 1 if step else x + 1, 15, C.BLUE)
    c.pixel(x + 1 if step else x - 1, 15, C.BLUE)
    return (x, 12)


def draw_band(c, f):
    # three marchers, in step, every other frame pair
    for i, x in enumerate((74, 82, 90)):
        up = (f // 2) % 2 == 0
        y0 = 8 if up else 9
        c.pixel(x, y0, C.WHITE)                  # plume
        c.pixel(x, y0 + 1, C.RED)                # shako
        c.pixel(x, y0 + 2, C.YELLOW)             # face
        c.vline(x, y0 + 3, 3, C.RED)             # coat
        legs = ((x - 1, 15), (x + 1, 15)) if up else ((x, 15), (x, 14))
        for p in legs:
            c.pixel(*p, C.WHITE)
        if i == 0:
            # tuba: a yellow coil and bell over the shoulder
            for p in ((x + 1, y0 + 3), (x + 2, y0 + 3), (x + 2, y0 + 2),
                      (x + 2, y0 + 1), (x + 3, y0 + 1), (x + 3, y0), (x + 4, y0)):
                c.pixel(*p, C.YELLOW)
        elif i == 1:
            # bass drum, beaten on the off step
            c.rect(x + 1, y0 + 3, 3, 3, C.WHITE, fill=True)
            c.pixel(x + 2, y0 + 4, C.RED)
            if not up:
                c.pixel(x + 4, y0 + 2, C.YELLOW)
        else:
            # trumpet held level
            c.hline(x + 1, y0 + 3, 3, C.YELLOW)
            c.pixel(x + 4, y0 + 2, C.YELLOW)
            c.pixel(x + 4, y0 + 4, C.YELLOW)


def draw_notes(c, f):
    # two notes, each rising one 12-frame climb, four climbs a loop
    for k, (x0, phase) in enumerate(((78, 0), (90, 6))):
        t = (f + phase) % 12
        y = 7 - t // 2
        x = x0 + (1 if (t // 3) % 2 else 0)
        if y >= 0 and t < 10:
            col = (C.CYAN, C.GREEN)[k]
            c.pixel(x, y, col)
            c.pixel(x, y - 1, col)
            c.pixel(x - 1, y, col)
            c.pixel(x + 1, y - 1, col)


def draw_banner(c, f):
    up = (f // 2) % 2 == 0
    for x, pole in ((1, 2), (28, 27)):
        y0 = 11 if up else 12
        c.pixel(x, y0, C.YELLOW)                  # head
        c.vline(x, y0 + 1, 15 - y0 - 1, C.GREEN)  # body
        c.pixel(x - 1 if up else x + 1, 15, C.GREEN)
        c.vline(pole, 2, 10, C.WHITE)             # pole
    sag = 0 if up else 1
    c.rect(3, 2 + sag, 24, 9, C.BLACK, fill=True)
    c.rect(3, 2 + sag, 24, 9, C.MAGENTA)
    tw = Canvas.small_text_width("THANKS")
    c.small_text("THANKS", 3 + (24 - tw) // 2, 4 + sag, C.YELLOW)


def draw_confetti(c, f):
    for x0, y0, ph, col in CONFETTI:
        y = (y0 + f * H / FRAMES) % H
        x = x0 + 1.5 * math.sin(TAU * f / 24 + ph)
        c.pixel(round(x) % W, int(y), col)


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        draw_city(c, f)
        draw_street(c, f)
        draw_banner(c, f)
        draw_band(c, f)
        draw_notes(c, f)

        bob = round(math.sin(TAU * f / 24))
        sway = round(0.6 * math.sin(TAU * f / 48))
        balloon = balloon_pixels(bob, sway)
        # tethers first, so the balloon sits over their ends
        for i, hxp in enumerate(HANDLERS):
            hx, hy = draw_handler(c, hxp, f, i)
            ax = BALLOON_X + sway + ANCHORS[i][0]
            ay = bob + ANCHORS[i][1]
            c.line(ax, ay, hx, hy - 1, C.WHITE)
        for (x, y), col in balloon.items():
            c.pixel(x, y, col)

        draw_confetti(c, f)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/parade_balloon.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
