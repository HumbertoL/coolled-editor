#!/usr/bin/env python3
"""
Pool gator -- Florida-man energy, which GTA 6's Leonida has in spades (its
first trailer pulled an alligator out of a backyard pool).

A magenta flamingo floatie bobs in a suburban pool. Two eyes and a snout
glide in from the left with a cyan wake, then sink. Jaws burst up under the
floatie, CHOMP, and POP! -- it's gone. A beat later the gator surfaces on its
back, belly up and lounging, wearing the flamingo's head as a hat, under
ONLY IN LEONIDA.
"""

from __future__ import annotations

import math

from gta6_art import palm, save, stamp
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 110
SURFACE = 10
POOL = (12, 84)
FLOAT_X = 56
FLAMINGO = [
    "....mm.",
    "....mmy",
    "....m..",
    "....m..",
    "mmmmmm.",
    ".mmmm..",
]
HAT = ["mm.", "mmy", "m..", "m.."]


def pool(f, i):
    f.hline(0, SURFACE - 1, POOL[0], C.WHITE)  # deck
    f.hline(POOL[1] + 1, SURFACE - 1, 96 - POOL[1], C.WHITE)
    f.vline(POOL[0], SURFACE - 1, 7, C.WHITE)
    f.vline(POOL[1], SURFACE - 1, 7, C.WHITE)
    for y in range(SURFACE, 16):
        f.hline(POOL[0] + 1, y, POOL[1] - POOL[0] - 1, C.BLUE)
    for x in range(POOL[0] + 1, POOL[1]):
        if math.sin(x * 0.6 + i * 0.7) > 0.85:
            f.pixel(x, SURFACE, C.CYAN)
        if math.sin(x * 0.4 - i * 0.5 + 1) > 0.9:
            f.pixel(x, SURFACE + 3, C.CYAN)
    palm(f, 90, 15, 13, C.GREEN, sway=math.sin(i * 0.3), frond=C.GREEN)
    palm(f, 4, 15, 10, C.GREEN, sway=math.sin(i * 0.3 + 1), frond=C.GREEN)


def eyes(f, x):
    """Eyes and snout breaking the surface, heading right."""
    f.hline(x, SURFACE, 10, C.GREEN)
    f.pixel(x + 1, SURFACE - 1, C.GREEN)
    f.pixel(x + 2, SURFACE - 1, C.YELLOW)
    f.pixel(x + 4, SURFACE - 1, C.GREEN)
    f.pixel(x + 5, SURFACE - 1, C.YELLOW)
    f.pixel(x + 9, SURFACE - 1, C.GREEN)  # nostrils
    for k in range(1, 7):  # V-shaped wake
        f.pixel(x - k * 2, SURFACE + (k + 1) // 3, C.CYAN)


def jaws(f, hinge_x, hinge_y, open_):
    """A snout pointing up out of the water, jaws apart when open_."""
    if open_:
        f.line(hinge_x, hinge_y, hinge_x - 4, hinge_y - 8, C.GREEN)
        f.line(hinge_x + 1, hinge_y, hinge_x - 3, hinge_y - 8, C.GREEN)
        f.line(hinge_x + 2, hinge_y, hinge_x + 7, hinge_y - 7, C.GREEN)
        f.line(hinge_x + 3, hinge_y, hinge_x + 8, hinge_y - 7, C.GREEN)
        for k in range(2, 8, 2):
            f.pixel(hinge_x - k // 2 + 1, hinge_y - k, C.WHITE)
            f.pixel(hinge_x + 2 + k * 5 // 8, hinge_y - k, C.WHITE)
        f.pixel(hinge_x - 2, hinge_y - 5, C.YELLOW)  # eye
    else:
        f.rect(hinge_x, hinge_y - 8, 3, 8, C.GREEN, fill=True)
        f.pixel(hinge_x + 1, hinge_y - 8, C.GREEN)
        for k in range(2, 8, 2):
            f.pixel(hinge_x + 3, hinge_y - k, C.WHITE)
        f.pixel(hinge_x - 1, hinge_y - 5, C.YELLOW)


def lounging(f, x, i):
    """Belly up: yellow belly on top, green back below, legs in the air."""
    f.hline(x, SURFACE - 2, 17, C.YELLOW)
    f.hline(x - 1, SURFACE - 1, 19, C.YELLOW)
    for k in range(x + 1, x + 17, 3):  # belly scales
        f.pixel(k, SURFACE - 2, C.GREEN)
    f.hline(x - 10, SURFACE, 37, C.GREEN)  # tail to snout
    f.hline(x - 5, SURFACE - 1, 4, C.GREEN)
    f.rect(x + 18, SURFACE - 2, 9, 2, C.GREEN, fill=True)  # head and snout
    f.pixel(x + 19, SURFACE - 3, C.GREEN)
    f.pixel(x + 20, SURFACE - 3, C.YELLOW)  # eye
    for k in range(x + 21, x + 27, 2):
        f.pixel(k, SURFACE - 1, C.WHITE)  # teeth
    wave = i % 4 < 2
    for lx in (x + 2, x + 13):
        f.vline(lx, SURFACE - 4, 2, C.GREEN)
        f.pixel(lx + (1 if wave else -1), SURFACE - 5, C.GREEN)
    stamp(f, HAT, x + 19, SURFACE - 7)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        pool(f, i)
        bob = 1 if (i // 3) % 2 else 0
        if i < 23:
            stamp(f, FLAMINGO, FLOAT_X, SURFACE - 5 + bob)
        if i < 16:
            eyes(f, 14 + i * 2)
        elif i < 20:  # submerging: bubbles
            for k in range(3):
                f.pixel(46 + k * 2 + i % 2, SURFACE - (i + k) % 3, C.CYAN)
        if 20 <= i < 23:
            f.small_text("...", 44, 2, C.WHITE)
        if 23 <= i < 26:  # jaws burst up, floatie on the tip
            rise = (i - 22) * 3
            jaws(f, FLOAT_X + 1, SURFACE + 9 - rise, True)
            stamp(f, FLAMINGO, FLOAT_X, SURFACE - 5 - rise + 2)
        elif 26 <= i < 29:
            jaws(f, FLOAT_X + 1, SURFACE, False)
            f.small_text("CHOMP", 30, 1, C.WHITE)
        elif 29 <= i < 34:
            if i < 31:
                jaws(f, FLOAT_X + 1, SURFACE + (i - 28) * 3, False)
            f.small_text("POP!", 52, 1, C.YELLOW if i % 2 else C.WHITE)
            spread = (i - 28) * 3
            for dx, dy in ((-1, -1), (1, -1), (-1, 0), (1, 0), (0, -1)):
                f.pixel(FLOAT_X + 3 + dx * spread, SURFACE - 4 + dy * spread // 2 + (i - 28), C.MAGENTA)
        elif 34 <= i < 40:
            f.hline(FLOAT_X, SURFACE, 4, C.MAGENTA)  # the deflated ring
        if i >= 40:
            lounging(f, 34, i)
            colour = C.MAGENTA if i % 4 < 2 else C.CYAN
            f.small_text("ONLY IN", 16, 1, colour)  # split round the hat
            f.small_text("LEONIDA", 57, 1, colour)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_pool_gator")
