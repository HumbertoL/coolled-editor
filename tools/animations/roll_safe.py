#!/usr/bin/env python3
"""
Roll Safe (2017) -- the man tapping his temple, "can't be broke".

A grinning, half-lidded man on the left taps his temple with one finger, the
hand darting away and back on a steady beat. On the right the thinking is
revealed in steps by a left-to-right wipe: YOU CAN'T BE BROKE, then IF YOU
DON'T, then CHECK YOUR ACCOUNT, each line sliding up as the next arrives. The
last line blinks once, smugly, before the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import wipe  # noqa: E402

FRAMES = 48
DELAY = 120

PAL = {
    "B": C.BLUE, "F": C.YELLOW, "W": C.WHITE, "K": C.BLACK, "R": C.RED,
    "C": C.CYAN, "M": C.MAGENTA, "G": C.GREEN,
}

HEAD = [
    "..BBBBBB..",
    ".BBBBBBBB.",
    ".BFFFFFFF.",
    ".BBBBBBBF.",
    ".FWKFWKFF.",
    ".FFFFFFFF.",
    ".FRRRRRFF.",
    "..FWWWWF..",
    "...FFFF...",
]
BODY = [
    "..CCCCCC..",
    ".CCCCCCCC.",
    "CCCCCCCCCC",
    "CCCCCCCCCC",
    "CCCCCCCCCC",
    "CCCCCCCCCC",
    "CCCCCCCCCC",
]


def spr(frame, rows, x, y):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                frame.pixel(x + c, y + r, PAL[ch])


def build():
    anim = Animation(delay=DELAY)
    tx = 22
    for i in range(FRAMES):
        f = anim.frame()
        beat = i % 8
        touch = beat in (0, 1, 2, 3)
        bob = 1 if beat in (1, 2) else 0
        spr(f, BODY, 1, 9)
        spr(f, HEAD, 1, 0 + bob)
        # the hand: a fist with the index finger up at the temple
        hx = 11 if touch else 14
        hy = 3 + bob if touch else 5
        f.rect(hx, hy + 2, 3, 3, C.YELLOW, fill=True)
        f.vline(hx + 1 - 1 + (0 if touch else 0), hy - 1 if touch else hy, 3, C.YELLOW)
        f.rect(hx, hy + 5, 3, 16 - (hy + 5), C.CYAN, fill=True)
        if touch:
            f.pixel(11, 2 + bob, C.WHITE)          # the tap flash
        # the eyes glance to the text side after the first page
        # text pages
        page = 0 if i < 5 else 1 if i < 17 else 2 if i < 30 else 3
        def reveal(k0):
            return tx - 2 + (i - k0) * 15
        if page == 1:
            f.small_text("YOU CAN'T BE BROKE", tx, 5, wipe(C.WHITE, C.BLACK, reveal(5)))
        elif page == 2:
            if i < 22:
                f.small_text("YOU CAN'T BE BROKE", tx, 2, C.WHITE)
                f.small_text("IF YOU DON'T", tx, 9, wipe(C.YELLOW, C.BLACK, reveal(17)))
            else:
                f.small_text("YOU CAN'T BE BROKE", tx, 2, C.WHITE)
                f.small_text("IF YOU DON'T", tx, 9, C.YELLOW)
        elif page == 3:
            f.small_text("IF YOU DON'T", tx, 2, C.YELLOW)
            if i < 35:
                f.small_text("CHECK YOUR ACCOUNT", tx, 9, wipe(C.GREEN, C.BLACK, reveal(30)))
            else:
                blink = i in (41, 42, 45, 46)
                f.small_text("CHECK YOUR ACCOUNT", tx, 9, C.WHITE if blink else C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/roll_safe.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
