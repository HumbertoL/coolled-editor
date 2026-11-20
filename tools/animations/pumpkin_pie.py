#!/usr/bin/env python3
"""
Pumpkin pie -- one slice at a time, until there is no pie.

A whole pumpkin pie seen from above sits in a blue tin on the left: a
yellow crust ring, red filling (there is no orange in the palette) and a
white dollop of whipped cream in the middle, with wavy cyan and white
steam curling up over it. PIE / TIME! lights up beside it.

A knife comes in and cuts it into eight, one diameter per frame, each cut
showing white as the blade passes and black once it has. Then a fork
starts taking slices, clockwise from the top: it reaches in, the slice
lifts clear and slides out of the tin, leaving the blue tin floor and a
yellow crumb or two. Each slice gets a running excuse on the right --
JUST A / SLIVER, FOR / GRANDMA, FOR ME / AGAIN, ONE MORE / SLICE...,
OK LAST / ONE,
REALLY / LAST ONE, WHO'S / COUNTING, WELL / NOW...

When the eighth is gone the tin is empty but for crumbs, the fork scrapes
at it, and MORE / PIE? blinks.

Beat sheet (frame indexes):
     0-7   whole pie steaming, PIE / TIME!
     8-13  knife: in, four cuts, out
    14-45  eight slices, four frames each (reach, lift, slide, gone)
    46-52  empty tin, scraping fork, MORE / PIE?
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16

# The pie, seen from above.
CX, CY = 11, 8
R_TIN, R_CRUST, R_FILL, R_CREAM = 7.6, 6.6, 4.9, 1.5

CUT_FRAMES = {9: 90, 10: 0, 11: 45, 12: 135}   # frame -> cut angle (deg)
KNIFE_IN, KNIFE_OUT = 8, 13
SLICE_START = 14
SLICE_LEN = 4
END_START = SLICE_START + 8 * SLICE_LEN        # 46

QUIPS = [
    ("JUST A", "SLIVER"),
    ("FOR", "GRANDMA"),
    ("FOR ME", "AGAIN"),
    ("ONE MORE", "SLICE..."),
    ("OK LAST", "ONE"),
    ("REALLY", "LAST ONE"),
    ("WHO'S", "COUNTING"),
    ("WELL", "NOW..."),
]

TEXT_LEFT = 23


def pie_pixels():
    """Map (x, y) -> (radius, angle-in-degrees, clockwise from 12 o'clock)."""
    out = {}
    for y in range(H):
        for x in range(0, 24):
            dx, dy = x - CX, y - CY
            r = math.hypot(dx, dy)
            if r <= R_TIN:
                ang = math.degrees(math.atan2(dx, -dy)) % 360
                out[(x, y)] = (r, ang)
    return out


PIE = pie_pixels()


def base_color(r):
    if r > R_CRUST:
        return C.BLUE
    if r > R_FILL:
        return C.YELLOW
    if r > R_CREAM:
        return C.RED
    return C.WHITE


def wedge_of(ang):
    return int(ang // 45) % 8


def on_cut(x, y, cut_deg):
    """Is (x, y) within half a pixel of the diameter at ``cut_deg``?"""
    t = math.radians(cut_deg)
    ux, uy = math.sin(t), -math.cos(t)
    dx, dy = x - CX, y - CY
    return abs(dx * uy - dy * ux) < 0.55


def wedge_dir(k):
    a = math.radians(k * 45 + 22.5)
    return math.sin(a), -math.cos(a)


rnd_crumbs = random.Random(1124)
CRUMBS = {}
for k in range(8):
    cells = [p for p, (r, a) in PIE.items() if r <= R_CRUST and wedge_of(a) == k and r > 2]
    CRUMBS[k] = rnd_crumbs.sample(cells, 2)


def draw_steam(c, f, wisps):
    """Wavy wisps of steam rising over the pie, each four pixels long."""
    for i, (x0, phase) in enumerate(((8, 0), (14, 6), (11, 11))[:wisps]):
        head = 13 - (f * 2 + phase) % 15
        for j in range(4):
            y = head + j
            x = x0 + round(1.2 * math.sin((y + f) * 0.8 + i))
            if 1 <= y <= 14:
                c.pixel(x, y, C.WHITE if j == 0 else C.CYAN)


def draw_fork(c, tip_x, tip_y, scrape=False):
    """A fork coming in from the right: tines to the left, handle trailing."""
    for i in range(3):
        c.pixel(tip_x + i, tip_y - 1, C.WHITE)
        c.pixel(tip_x + i, tip_y + 1, C.WHITE)
        c.pixel(tip_x + i, tip_y, C.WHITE if not scrape else C.CYAN)
    c.pixel(tip_x + 3, tip_y, C.WHITE)
    c.pixel(tip_x + 3, tip_y - 1, C.WHITE)
    c.pixel(tip_x + 3, tip_y + 1, C.WHITE)
    for i in range(4, 10):
        c.pixel(tip_x + i, tip_y + (1 if i > 6 else 0), C.WHITE)


def draw_knife(c, cut_deg):
    t = math.radians(cut_deg)
    ux, uy = math.sin(t), -math.cos(t)
    for s in range(-8, 9):
        c.pixel(round(CX + ux * s), round(CY + uy * s), C.WHITE)
    # handle beyond the rim
    for s in range(9, 13):
        c.pixel(round(CX + ux * s), round(CY + uy * s), C.YELLOW)


def right_text(c, top, bottom, color, color2=None):
    region = W - TEXT_LEFT
    for row, (txt, col) in enumerate(((top, color), (bottom, color2 or color))):
        if not txt:
            continue
        x = TEXT_LEFT + (region - Canvas.text_width(txt)) // 2
        c.text(txt, x, 0 if row == 0 else 9, col)


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()

        cuts = [a for fr, a in CUT_FRAMES.items() if fr < f] if f >= KNIFE_IN else []
        gone = set()
        moving = None          # (wedge, offset)
        if f >= SLICE_START:
            n = min(8, (f - SLICE_START) // SLICE_LEN + 1)
            stage = (f - SLICE_START) % SLICE_LEN if f < END_START else 4
            cur = n - 1
            gone = set(range(cur))
            if stage in (1, 2):
                moving = (cur, 2 if stage == 1 else 6)
            elif stage == 3 or f >= END_START:
                gone.add(cur)
            elif stage == 0:
                moving = (cur, 0)

        # the pie
        for (x, y), (r, a) in PIE.items():
            k = wedge_of(a)
            if r > R_CRUST:
                c.pixel(x, y, C.BLUE)
                continue
            if k in gone or (moving and k == moving[0]):
                col = C.YELLOW if (x, y) in CRUMBS[k] else C.BLUE
                c.pixel(x, y, col)
                continue
            col = base_color(r)
            if r > R_CREAM and any(on_cut(x, y, cd) for cd in cuts):
                col = C.BLACK
            c.pixel(x, y, col)

        # fork
        if SLICE_START <= f < END_START:
            k = (f - SLICE_START) // SLICE_LEN
            stage = (f - SLICE_START) % SLICE_LEN
            ux, uy = wedge_dir(k)
            off = {0: 0, 1: 2, 2: 6}.get(stage)
            if off is not None:
                # the fork reaches in from outside, along the slice's own line
                for s_ in range(0, 9):
                    rr = 3.5 + off + s_
                    c.pixel(round(CX + ux * rr), round(CY + uy * rr),
                            C.WHITE if s_ < 6 else C.CYAN)
        elif f >= END_START:
            # scraping the empty tin
            sx = 9 + (f % 2) * 4
            draw_fork(c, sx, 9 + (f % 3 == 0), scrape=True)

        # the slice in flight
        if moving:
            k, off = moving
            ux, uy = wedge_dir(k)
            for (x, y), (r, a) in PIE.items():
                if r <= R_CRUST and wedge_of(a) == k:
                    if any(on_cut(x, y, cd) for cd in cuts):
                        continue
                    c.pixel(round(x + ux * off), round(y + uy * off), base_color(r))

        if f < KNIFE_IN + 4:
            draw_steam(c, f, 3 if f < KNIFE_IN else 1)

        if f in CUT_FRAMES:
            draw_knife(c, CUT_FRAMES[f])
        elif f == KNIFE_IN:
            draw_knife(c, 60)
        elif f == KNIFE_OUT:
            draw_knife(c, 135)

        # words
        if f < KNIFE_IN:
            if f >= 1:
                right_text(c, "PIE", "TIME!" if f >= 3 else "", C.YELLOW,
                           C.WHITE if f % 2 else C.YELLOW)
        elif f < SLICE_START:
            right_text(c, "CUT IT", "FAIR..." if f >= 10 else "", C.CYAN, C.WHITE)
        elif f < END_START:
            k = (f - SLICE_START) // SLICE_LEN
            top, bottom = QUIPS[k]
            right_text(c, top, bottom, C.YELLOW, C.RED if k >= 5 else C.WHITE)
        else:
            blink = (f - END_START) % 2 == 0
            right_text(c, "MORE", "PIE?", C.WHITE if blink else C.YELLOW,
                       C.YELLOW if blink else C.RED)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/pumpkin_pie.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
