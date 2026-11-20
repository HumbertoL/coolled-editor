#!/usr/bin/env python3
"""
Wrong car -- GTA 6 players found that if you try to steal a parked car with a
cat inside, the cat fights back.

A crook in a magenta hoodie strolls up to a red car with a ginger cat sitting
in the window. He reaches for the handle; the cat's ears go flat, its eyes go
red and HSSS. A flurry of paws, yellow scratch stars, the crook staggers and
then flees with his arms up. The cat settles back down, licks a paw and
blinks, while NOPE. hangs in the air.
"""

from __future__ import annotations

from gta6_art import save
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 110
CAR_X = 42
WIN_X = 50


def car(f):
    f.hline(CAR_X + 8, 5, 18, C.RED)  # roof
    for y in range(6, 9):
        f.hline(CAR_X + 6, y, 22, C.RED)
        f.hline(WIN_X, y, 8, C.BLUE)  # driver's window
        f.hline(WIN_X + 10, y, 6, C.BLUE)  # rear window
    f.rect(CAR_X, 9, 38, 4, C.RED, fill=True)
    f.pixel(CAR_X + 37, 10, C.YELLOW)
    f.pixel(CAR_X, 10, C.MAGENTA)
    f.vline(WIN_X + 9, 9, 3, C.BLACK)  # door seam
    f.hline(WIN_X + 5, 10, 2, C.WHITE)  # handle
    for wx in (CAR_X + 5, CAR_X + 29):
        f.rect(wx, 12, 4, 3, C.WHITE, fill=True)
        f.pixel(wx + 1, 13, C.BLACK)
        f.pixel(wx + 2, 13, C.BLACK)
    f.hline(0, 15, 96, C.BLUE)


def cat(f, mood, i):
    """Ginger cat in the driver's window. mood: calm, angry, lick."""
    x = WIN_X + 2
    ears = mood != "angry"
    if ears:
        f.pixel(x, 5, C.YELLOW)
        f.pixel(x + 4, 5, C.YELLOW)
    else:  # flattened back
        f.pixel(x - 1, 6, C.YELLOW)
        f.pixel(x + 5, 6, C.YELLOW)
    f.rect(x, 6, 5, 3, C.YELLOW, fill=True)
    f.pixel(x + 2, 6, C.RED)  # tabby stripe
    blink = mood != "angry" and i % 12 in (0, 1)
    eye = C.RED if mood == "angry" else C.GREEN
    if blink:
        f.hline(x + 1, 7, 3, C.BLACK)
        f.pixel(x + 2, 7, C.YELLOW)
    else:
        f.pixel(x + 1, 7, eye)
        f.pixel(x + 3, 7, eye)
    if mood == "lick":
        f.pixel(x + 2, 8, C.MAGENTA)  # tongue
        f.vline(x - 1, 7, 2, C.YELLOW)  # paw up


def crook(f, x, i, walking=True, arms_up=False, scratched=False):
    f.rect(x, 4, 3, 3, C.YELLOW, fill=True)
    f.hline(x, 3, 3, C.MAGENTA)  # hood
    f.pixel(x - 1, 4, C.MAGENTA)
    f.rect(x, 7, 3, 4, C.MAGENTA, fill=True)
    step = i % 2 if walking else 0
    f.vline(x + (0 if step else 1), 11, 4, C.BLUE)
    f.vline(x + (2 if step else 1), 11, 4, C.BLUE)
    if arms_up:
        f.vline(x - 1, 1, 3, C.YELLOW)
        f.vline(x + 3, 1, 3, C.YELLOW)
    if scratched:
        f.pixel(x + 1, 4, C.RED)
        f.pixel(x + 2, 5, C.RED)
        f.pixel(x, 6, C.RED)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        car(f)
        if i < 14:  # stroll in
            x = -4 + i * 3
            cat(f, "calm", i)
            crook(f, x, i)
        elif i < 18:  # reach for the handle
            x = 38
            cat(f, "calm" if i < 16 else "angry", i)
            crook(f, x, i, walking=False)
            f.hline(x + 3, 8, 2 + (i - 14) * 2, C.YELLOW)
            if i >= 16:
                f.small_text("HSSS", WIN_X - 2, 0, C.RED)
        elif i < 30:  # the flurry
            x = 38 + (1 if i % 2 else -1)
            cat(f, "angry", i)
            crook(f, x, i, walking=False, scratched=i >= 22)
            reach = 3 + (i * 7) % 5
            row = 6 + (i % 3)
            f.hline(WIN_X - reach, row, reach, C.YELLOW)
            f.pixel(WIN_X - reach - 1, row, C.WHITE)  # claws
            for sx, sy in ((x + 4 + i % 3, 2 + (i * 5) % 6), (x - 2 - (i % 2), 3 + (i * 3) % 5)):
                f.pixel(sx, sy, C.YELLOW)
                f.pixel(sx - 1, sy, C.WHITE)
                f.pixel(sx + 1, sy, C.WHITE)
                f.pixel(sx, sy - 1, C.WHITE)
                f.pixel(sx, sy + 1, C.WHITE)
            if i % 4 < 2:
                f.small_text("HSSS", WIN_X - 2, 0, C.RED)
        elif i < 42:  # run away
            x = 38 - (i - 29) * 4
            cat(f, "angry" if i < 34 else "calm", i)
            crook(f, x, i, arms_up=True, scratched=True)
            if x > -10:
                f.small_text("AAA!", x + 5, 0, C.WHITE)
        else:
            cat(f, "lick" if i % 6 < 4 else "calm", i)
            f.small_text("NOPE.", 6, 4, C.WHITE if i % 2 else C.CYAN)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_cat_carjack")
