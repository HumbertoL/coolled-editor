#!/usr/bin/env python3
"""
Ride or die -- Jason and Lucia, GTA 6's two leads, on the Leonida highway.

A pink convertible cruises right at night while blue palms, stars and
the lane dashes stream past. A label over the driver reads JASON, then the
game's character switch flashes the car white and the label jumps to LUCIA,
her long hair whipping in the wind. Then little hearts float up between
them, and RIDE OR DIE glows above. 48 frames, so the scenery loops cleanly.
"""

from __future__ import annotations

import math

from gta6_art import palm, save
from jtkit import Animation, colors as C

FRAMES = 48
DELAY = 110
CAR_X = 34
JASON_X = CAR_X + 16
LUCIA_X = CAR_X + 9


STARS = [(5, 2), (19, 6), (27, 1), (44, 3), (63, 5), (71, 1), (86, 4), (92, 7)]


def scenery(f, i):
    for sx, sy in STARS:
        if (sx + i // 3) % 9:
            f.pixel(sx, sy, C.WHITE)
    # palms in dim blue: one every 24 px, moving 2 px a frame
    for p in range(5):
        x = p * 24 - (i * 2) % 24
        palm(f, x, 13, 9 + p % 2 * 2, C.BLUE, sway=0.5)
    f.hline(0, 14, 96, C.BLACK)
    for x in range(-(i * 4) % 8 - 8, 96, 8):
        f.hline(x, 15, 4, C.YELLOW)


def car(f, flash):
    body = C.WHITE if flash else C.MAGENTA
    f.rect(CAR_X, 10, 28, 3, body, fill=True)
    f.hline(CAR_X + 2, 9, 7, body)  # rear deck
    f.hline(CAR_X + 21, 9, 6, body)  # hood
    f.line(CAR_X + 20, 9, CAR_X + 18, 6, C.CYAN)  # windshield
    f.pixel(CAR_X + 27, 10, C.YELLOW)  # headlight
    f.pixel(CAR_X, 10, C.RED)
    for wx in (CAR_X + 3, CAR_X + 20):
        f.rect(wx, 12, 4, 3, C.WHITE, fill=True)
        f.pixel(wx + 1, 13, C.BLACK)
        f.pixel(wx + 2, 13, C.BLACK)


def jason(f):
    f.rect(JASON_X - 2, 6, 3, 3, C.YELLOW, fill=True)
    f.hline(JASON_X - 2, 5, 3, C.RED)  # short hair
    f.pixel(JASON_X - 2, 6, C.RED)
    f.pixel(JASON_X, 7, C.BLACK)


def lucia(f, i):
    f.rect(LUCIA_X - 1, 6, 3, 3, C.YELLOW, fill=True)
    f.hline(LUCIA_X - 1, 5, 3, C.RED)
    # long hair streaming back in the wind
    for k in range(1, 6):
        y = 5 + k // 2 + round(math.sin(i * 1.3 + k) * 0.7)
        f.pixel(LUCIA_X - 1 - k, y, C.RED)
        f.pixel(LUCIA_X - 1 - k, y + 1, C.RED if k < 3 else C.BLACK)
    f.pixel(LUCIA_X + 1, 7, C.BLACK)


def backed_text(f, text, x, y, colour):
    """Small text on a black backing so the scenery doesn't run through it."""
    w = f.small_text_width(text)
    f.rect(x - 1, y - 1, w + 2, 7, C.BLACK, fill=True)
    f.small_text(text, x, y, colour)


def label(f, name, x, colour):
    backed_text(f, name, x - f.small_text_width(name) // 2, 0, colour)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        scenery(f, i)
        flash = i in (16, 17)
        car(f, flash)
        lucia(f, i)
        jason(f)
        if i < 16:
            label(f, "JASON", JASON_X - 1, C.WHITE)
        elif i < 30:
            label(f, "LUCIA", LUCIA_X, C.WHITE if i > 17 else C.CYAN)
        else:
            backed_text(f, "RIDE OR DIE", 53, 0, C.YELLOW if i % 4 < 2 else C.RED)
            for k in range(3):
                age = (i - 30 - k * 5) % 15
                if 0 <= age < 9:
                    hx = LUCIA_X + 3 + (age // 3 + k) % 2
                    hy = 4 - age // 2
                    if hy >= -1:
                        f.pixel(hx, hy + 1, C.RED)
                        f.pixel(hx + 2, hy + 1, C.RED)
                        f.hline(hx, hy + 2, 3, C.RED)
                        f.pixel(hx + 1, hy + 3, C.RED)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_road_trip")
