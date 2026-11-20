#!/usr/bin/env python3
"""
Five stars -- and the oldest trick in the series.

A magenta car tears down the road while the wanted meter fills one star at a
time and police cruisers with flashing red and blue bars pull in behind. A
spray shop rolls in from the right; the car ducks inside, the shutter drops,
paint mist leaks out and the stars blink. The shutter rolls up on a green
car, the stars are gone, and the cops' lights go dark under three puzzled ?s.
"""

from __future__ import annotations

import random

from gta6_art import sedan, save, stamp
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 100
STAR = ["..#..", ".###.", "#####", ".###.", ".#.#."]
STAR_AT = [2, 7, 12, 17, 22]
COP_X = [30, 14, -2]
STOP = 30  # the road stops scrolling and the car heads for the shop
GARAGE = 75


def build():
    rng = random.Random(6)
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        stars = sum(i >= t for t in STAR_AT)
        lost = i >= 45
        scroll = min(i, STOP) * 3

        # Road: lane dashes stop when the chase does.
        for x in range(-scroll % 8 - 8, 96, 8):
            f.hline(x, 15, 4, C.WHITE)

        # Spray shop rolls in from the right.
        gx = max(GARAGE, 96 + 3 * (22 - i)) if i >= 22 else None
        if gx is not None:
            f.small_text("SPRAY", gx + 1, 0, C.CYAN if i % 4 < 2 or i < STOP else C.GREEN)
            f.hline(gx, 6, 21, C.WHITE)
            f.vline(gx, 6, 9, C.WHITE)
            f.vline(gx + 20, 6, 9, C.WHITE)

        # The player's car.
        car_x = 46 if i < STOP else min(78, 46 + (i - STOP) * 5)
        body = C.GREEN if lost else C.MAGENTA
        if i < STOP or car_x < (gx or 96) + 1 or lost:
            sedan(f, car_x, 10, body)
        elif i < 36:
            sedan(f, car_x, 10, body)

        # The shutter: down at 36-38, up again at 45-47.
        if gx is not None:
            if 36 <= i < 45:
                door = min(8, (i - 35) * 3)
            elif 45 <= i < 48:
                door = max(0, 8 - (i - 44) * 3)
            else:
                door = 0
            for row in range(door):
                f.hline(gx + 1, 7 + row, 19, C.YELLOW if row % 2 == 0 else C.RED)
            if 38 <= i < 45:  # paint mist leaking out round the door
                for _ in range(10):
                    side = rng.choice((gx - 1 - rng.randrange(3), gx + 1 + rng.randrange(19)))
                    y = rng.randrange(1, 6) if side > gx else rng.randrange(7, 15)
                    f.pixel(side, y, rng.choice((C.CYAN, C.GREEN, C.WHITE)))
                f.small_text("PSST", gx - 18, 1, C.WHITE if i % 2 else C.CYAN)

        # The cops: one more per star, sliding in from the left.
        for k, target in enumerate(COP_X[: min(3, stars)]):
            arrived = STAR_AT[k]
            x = min(target, target - 20 + (i - arrived) * 6)
            if lost:
                sedan(f, x, 10, C.WHITE, lights=(C.BLUE, C.BLUE))
                if i >= 47:
                    f.small_text("?", x + 5, 2 + (k % 2), C.YELLOW)
            else:
                flip = (i + k) % 2
                sedan(f, x, 10, C.WHITE, lights=(C.RED, C.BLUE) if flip else (C.BLUE, C.RED))

        # Wanted meter.
        if not lost:
            blink = 38 <= i < 45 and i % 2 == 0
            for k in range(5):
                lit = k < stars and not blink
                stamp(f, STAR, 2 + 6 * k, 0, {"#": C.WHITE if lit else C.BLUE})
        elif i >= 48:
            f.small_text("LOST 'EM", 42, 3, C.YELLOW if i % 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_wanted")
