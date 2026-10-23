#!/usr/bin/env python3
"""
Pace car.

Three joggers in mismatched shirts run in place while the ground scrolls
under them. A white golf cart rolls in from the left, its driver holding a
megaphone, and as it draws level a big line appears above: BRISK JOG! The
joggers' eyes follow it as it goes. It rolls off the right edge; the joggers
pick up speed, blur, and start sweating. The cart comes round again, slower
this time, with LOVE THE ENERGY, and the joggers go red in the face. Button:
the joggers stop dead, bent double with hands on knees, and the cart pulls
up beside them, megaphone wagging: BRISK JOG!, blinking.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

JOGGERS = [(6, C.GREEN), (20, C.MAGENTA), (34, C.CYAN)]   # x and shirt colour
CART_W = 15

# Each pass: (first frame, speed in px/frame, line). The cart starts off the
# left edge and the line shows while any of it is on the panel.
PASSES = [
    (1, 5, "BRISK JOG!"),
    (21, 4, "LOVE THE ENERGY"),
]
STOP = 42             # the joggers quit; the cart parks beside them

RUN = [
    ["..HH...", "..HH...", "A.SS.A.", ".SSSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", ".ASS...", "..SSA..", "..SS...", "..LL...", ".L.L..."],
    ["..HH...", "..HH...", ".ASS.A.", "..SSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", "..SSA..", ".ASS...", "..SS...", "..LL...", "..L.L.."],
]
BLUR = ["..HH...", "..HH...", "AASSAA.", ".SSSS..", "..SS...", "LLLLLL.", "LLLLLL."]
BENT = [".......", ".......", "..SSHH.", ".SSSSHH", ".A.SS..", ".A.LL..", "...LL.."]
CART = [
    ".WWWWWWWWWWWW..",
    ".W..........W..",
    ".W..........W..",
    ".W...YY.....W..",
    ".W...YYMM...W..",
    "RRRRRRRRRRRRRRR",
    "RRRRRRRRRRRRRRR",
    "..BB.......BB..",
]
CART_PALETTE = {"W": C.WHITE, "Y": C.YELLOW, "M": C.MAGENTA, "R": C.RED, "B": C.BLUE}


def sprite(frame, art, x, y, palette):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, palette[ch])


def cart_at(i):
    """Where the cart is this frame, and which line it is shouting."""
    for start, speed, line in PASSES:
        if i >= start:
            x = -CART_W + (i - start) * speed
            if i >= STOP:
                return -CART_W + (STOP - start) * speed, "BRISK JOG!"
            if x < 96:
                return x, line
    return None, None


def build():
    anim = Animation(delay=DELAY)
    scroll = 0
    for i in range(FRAMES):
        f = anim.frame()
        pace = 0 if i < 10 else 1 if i < 26 else 2
        if i >= STOP:
            pace = 3
        scroll += 2 + pace
        for x in range(96):
            if (x + scroll) % 5 == 0:
                f.pixel(x, 15, C.BLUE)

        cart_x, line = cart_at(i)
        if cart_x is not None and i >= STOP:
            # Parked: the megaphone wags as it idles.
            sprite(f, CART, cart_x, 8, CART_PALETTE)
            if i % 2:
                f.pixel(cart_x + 8, 12, C.MAGENTA)
                f.pixel(cart_x + 8, 10, C.MAGENTA)
        elif cart_x is not None:
            sprite(f, CART, cart_x, 8, CART_PALETTE)
            f.pixel(cart_x + 8, 12 - (i % 2), C.MAGENTA)
        if line and (i < STOP or i % 4 < 3):
            f.text(line, "center", 0, C.YELLOW if "BRISK" in line else C.CYAN,
                   proportional=True)

        for x, shirt in JOGGERS:
            head = C.YELLOW if pace < 2 else C.RED
            palette = {"H": head, "S": shirt, "A": C.WHITE, "L": C.WHITE}
            # Cut the jogger out of the cart when it passes behind.
            if cart_x is not None and cart_x - 8 < x < cart_x + CART_W + 1:
                f.rect(x - 1, 8, 9, 7, C.BLACK, fill=True)
            if i >= STOP:
                sprite(f, BENT, x, 8, palette)
                f.pixel(x - 1 - (i % 2), 10, C.CYAN)
                continue
            phase = ((i * (1 + pace)) // 2 + x) % 4
            art = BLUR if pace == 2 and i % 2 else RUN[phase]
            sprite(f, art, x, 8, palette)
            # Eyes follow the cart when it is near.
            if cart_x is not None and cart_x - 10 < x < cart_x + CART_W + 10:
                f.pixel(x + 3, 9, C.BLACK)
            if pace >= 1:
                for k in range(pace):
                    f.pixel(x - 1 - k * 2, 8 + (i + k * 2) % 4, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/brisk_cart.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
