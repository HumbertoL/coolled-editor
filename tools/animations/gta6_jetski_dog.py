#!/usr/bin/env python3
"""
Jet-ski dog -- one of the first things GTA 6 players found in the water off
Leonida: a dog in sunglasses on a jet ski who rescues stranded swimmers.

A swimmer flails under a HELP!. A golden dog in black shades roars in on a
red jet ski throwing white spray, pulls up, and the swimmer is hoisted onto
the back seat. The shades glint, the dog's tail wags, and they power off to
the right as GOOD BOY lights up in yellow behind them.
"""

from __future__ import annotations

import math

from gta6_art import save, stamp
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 100
WATER = 11
SWIM_X = 66
DOG = [
    ".....ryyyy..",
    ".....kkkkkk.",
    ".....yyyyyyy",
    ".....yyyy...",
    "..yyyyyyy...",
    "..yyyyyyyy..",
]


def water(f, i):
    for y in range(WATER, 16):
        f.hline(0, y, 96, C.BLUE)
    for x in range(96):
        if math.sin(x * 0.5 - i * 0.8) > 0.8:
            f.pixel(x, WATER, C.CYAN)
        if math.sin(x * 0.33 + i * 0.5 + 2) > 0.93:
            f.pixel(x, WATER + 2, C.CYAN)


def swimmer(f, x, y, i, waving):
    f.rect(x, y, 2, 2, C.YELLOW, fill=True)  # head
    f.hline(x, y - 1, 2, C.RED)  # hair
    if waving:
        up = i % 2
        f.pixel(x - 1, y - up, C.YELLOW)
        f.pixel(x - 2, y - 1 - up, C.YELLOW)
        f.pixel(x + 2, y - 1 + up, C.YELLOW)
        f.pixel(x + 3, y - 2 + up, C.YELLOW)


def jetski(f, x, i, speed, glint):
    """Hull bottom on WATER+1; x is the stern."""
    # spray off the stern when moving
    if speed:
        for k in range(speed + 2):
            sx = x - 1 - k * 2
            f.pixel(sx, WATER - 1 - (k + i) % 3, C.WHITE)
            f.pixel(sx - 1, WATER - (k + i + 1) % 2, C.CYAN)
    f.hline(x + 1, WATER, 16, C.RED)
    f.hline(x + 2, WATER + 1, 14, C.WHITE)
    f.pixel(x + 17, WATER - 1, C.RED)  # bow
    f.pixel(x + 16, WATER, C.RED)
    f.hline(x + 3, WATER - 1, 5, C.WHITE)  # seat
    # Dog: golden, red ear, a black band of shades across the head.
    stamp(f, DOG, x + 5, WATER - 6)
    wag = (i // 2) % 2
    f.pixel(x + 6, WATER - 3 - wag, C.YELLOW)  # tail
    if glint:
        f.pixel(x + 12, WATER - 5, C.WHITE)
        f.pixel(x + 14, WATER - 5, C.CYAN)
    f.vline(x + 16, WATER - 3, 3, C.WHITE)  # handlebar


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        water(f, i)

        # Jet ski: in at speed, stops with the seat beside the swimmer, leaves.
        stop = SWIM_X - 4
        if i < 18:
            x, speed = min(stop, -24 + i * 5), 2
        elif i < 30:
            x, speed = stop, 0
        else:
            x, speed = stop + (i - 30) ** 2 // 2, 3

        if i < 22:
            swimmer(f, SWIM_X, WATER - 1, i, waving=i < 18)
            if i < 16 and i % 4 < 3:
                f.small_text("HELP!", SWIM_X - 3, 2, C.WHITE)
        if x < 96:
            jetski(f, x, i, speed, glint=26 <= i <= 28)
        if i >= 22 and x < 96:
            # passenger on the back seat, arms round the dog
            f.rect(x + 4, WATER - 5, 2, 2, C.YELLOW, fill=True)
            f.hline(x + 4, WATER - 6, 2, C.RED)
            f.rect(x + 4, WATER - 3, 3, 2, C.CYAN, fill=True)
            f.pixel(x + 7, WATER - 3, C.YELLOW)
        if 18 <= i < 22:  # hoisted out of the water onto the seat
            lift = i - 18
            f.rect(SWIM_X - lift, WATER - 1 - lift, 2, 2, C.YELLOW, fill=True)
            f.hline(SWIM_X - lift, WATER - 2 - lift, 2, C.RED)

        if 24 <= i < 30:
            f.small_text("WOOF", stop + 14, 0, C.WHITE)
        if i >= 36:
            colour = C.YELLOW if i % 4 < 2 else C.WHITE
            f.text("GOOD BOY", 6, 1, colour)
            if i >= 40:
                f.glyph("+HEART", 56, 1, C.RED if i % 2 else C.MAGENTA)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_jetski_dog")
