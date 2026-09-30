#!/usr/bin/env python3
"""
Sushi Conveyor -- a kaiten belt that never runs out of plates.

Plates of nigiri, maki rolls and tamago scroll left along a ticking belt, each
on a differently coloured rim. A pair of chopsticks drops in, pinches a piece
of tuna off one plate and whisks it away, leaving an empty plate to sail on.
The belt is a whole number of plate-widths per loop, so the loop is seamless.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
SPEED = 2                     # px per frame; 48 * 2 = 96 = one pattern
SLOT = 16
ITEMS = ["shrimp", "maki", "tamago", "salmon", "tuna", "maki"]
RIMS = [C.RED, C.CYAN, C.YELLOW, C.MAGENTA, C.GREEN, C.WHITE]
PLATE_Y = 12
GRAB_INDEX = 4                # which plate loses its tuna
GRAB_T = 15                   # frame the chopsticks pinch it
GRAB_X = 52                   # where the belt carries it at that moment


def nigiri(f, x, fish, marble):
    """10 wide, 6 tall, top-left at (x, y=6)."""
    y = 6
    f.hline(x + 2, y, 6, fish)
    f.hline(x + 1, y + 1, 8, fish)
    f.hline(x, y + 2, 10, fish)
    if marble:
        f.pixel(x + 3, y + 1, C.WHITE)
        f.pixel(x + 6, y + 1, C.WHITE)
        f.pixel(x + 4, y + 2, C.WHITE)
        f.pixel(x + 7, y + 2, C.WHITE)
    f.hline(x + 1, y + 3, 8, C.WHITE)
    f.hline(x + 1, y + 4, 8, C.WHITE)
    f.hline(x + 2, y + 5, 6, C.WHITE)


def maki(f, x):
    """One fat roll, 7x7, seen end-on: nori, rice, filling."""
    x += 2
    y = 5
    f.hline(x + 1, y, 5, C.GREEN)
    f.hline(x + 1, y + 6, 5, C.GREEN)
    f.vline(x, y + 1, 5, C.GREEN)
    f.vline(x + 6, y + 1, 5, C.GREEN)
    f.rect(x + 1, y + 1, 5, 5, C.WHITE, fill=True)
    f.rect(x + 2, y + 2, 3, 3, C.RED, fill=True)
    f.pixel(x + 3, y + 3, C.YELLOW)


def tamago(f, x):
    y = 6
    f.rect(x, y + 3, 10, 3, C.WHITE, fill=True)
    f.rect(x + 1, y, 8, 4, C.YELLOW, fill=True)
    f.vline(x + 4, y - 1, 5, C.GREEN)
    f.vline(x + 5, y - 1, 5, C.GREEN)


def item(f, kind, x, taken=False):
    if kind == "tuna":
        nigiri(f, x, C.RED, True) if not taken else nigiri(f, x, C.BLACK, False)
    elif kind == "salmon":
        nigiri(f, x, C.MAGENTA, True)
    elif kind == "shrimp":
        nigiri(f, x, C.RED, False)
        f.pixel(x + 1, 8, C.WHITE)
        f.pixel(x + 4, 8, C.WHITE)
        f.pixel(x + 7, 8, C.WHITE)
    elif kind == "maki":
        maki(f, x)
    else:
        tamago(f, x)


def plate(f, x, rim):
    f.hline(x + 1, PLATE_Y, 12, rim)
    f.hline(x, PLATE_Y + 1, 14, rim)
    f.hline(x + 2, PLATE_Y + 1, 10, C.WHITE if rim != C.WHITE else C.BLUE)


def chopsticks(f, cx, ty, gap):
    """Two slanted sticks whose tips sit at row ty, ``gap`` apart, centred on cx."""
    left = cx - gap // 2
    right = left + gap
    f.line(left, ty, left + 9, ty - 9, C.YELLOW)
    f.line(right, ty, right + 9, ty - 9, C.WHITE)
    f.line(left + 1, ty, left + 10, ty - 9, C.YELLOW)
    f.line(right + 1, ty, right + 10, ty - 9, C.WHITE)


def belt(f, t):
    off = (t * SPEED) % 4
    for x in range(96):
        seg = ((x + off) // 2) % 2
        f.pixel(x, 14, C.CYAN if seg else C.BLUE)
        f.pixel(x, 15, C.BLUE)
    # rollers
    for x in range(0, 96, 8):
        f.pixel((x - t * SPEED) % 96, 15, C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    grab_u = GRAB_INDEX * SLOT + 3           # plate x at t=0
    for t in range(FRAMES):
        f = anim.frame()
        belt(f, t)
        for i, (kind, rim) in enumerate(zip(ITEMS, RIMS)):
            u = i * SLOT + 3 - t * SPEED
            for x, primary in ((u, True), (u + 96, False)):
                if x < -14 or x > 95:
                    continue
                taken = primary and i == GRAB_INDEX and t >= GRAB_T
                plate(f, x, rim)
                item(f, kind, x + 2, taken=taken)
        cx = grab_u - min(t, GRAB_T) * SPEED + 7      # follows the fish until the pinch
        if 6 <= t < 11:
            chopsticks(f, cx, -3 + (t - 6) * 2, 6)
        elif 11 <= t < 14:
            chopsticks(f, cx, 5, 6 - (t - 11))
        elif t == 14:
            chopsticks(f, cx, 5, 2)
        elif GRAB_T <= t <= 24:
            ty = 5 - (t - GRAB_T) * 1
            cx2 = cx + (t - GRAB_T)
            chopsticks(f, cx2, ty, 2)
            f.hline(cx2 - 1, ty + 1, 4, C.RED)
            f.pixel(cx2, ty + 2, C.RED)
            f.pixel(cx2 + 1, ty + 2, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sushi_conveyor.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
