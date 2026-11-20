#!/usr/bin/env python3
"""
Turkey escape -- a Thanksgiving gag.

A red turkey with a fanned tail (yellow, magenta and green bands) pecks at
a few grains in the middle of the panel. A chef -- tall white hat, white
coat, cleaver raised -- marches in from the left. The turkey looks up, a red
! pops over its head, and it vanishes in a puff of smoke.

When the smoke clears there is a wooden sign reading EAT MORE / HAM! and,
beside it, a "different" bird: same turkey, now in cyan glasses and a blue
moustache. The chef walks right up, reads the sign (a yellow ? blinks), stares
at the bird -- who breaks into a cyan sweat -- shrugs twice with his arms up,
turns round and walks off.

The turkey wipes its brow, flicks the sweat away, and does a victory hop with
its tail colours cycling while PHEW! lights up where the chef stood.

Beat sheet (frame indexes):
  0-11   turkey pecks; chef walks in (2-11)
  10-11  turkey looks up, red !
  12-14  smoke puff; sign and disguised turkey appear under it
  15-22  chef walks up to the sign
  23-30  chef reads, ? blinks, turkey sweats
  31-35  shrug, shrug
  36-44  chef turns and walks off left
  45-46  brow wipe
  47-52  victory hop, PHEW!
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

PAL = {
    "R": C.RED, "Y": C.YELLOW, "M": C.MAGENTA, "G": C.GREEN,
    "W": C.WHITE, "B": C.BLUE, "C": C.CYAN, "K": C.BLACK,
}

# Turkey body and tail, facing left. Origin is the sprite's top-left.
TURKEY_BODY = [
    "........GYMYG...",
    ".......GYMRMYG..",
    "......GYMRRRMYG.",
    "......GYMRRRMYG.",
    "......GYMRRRMYG.",
    ".......YMRRRMY..",
    "......RRRRRRRR..",
    ".....RRRRRRRRRR.",
    "....RRRRRRRRRRR.",
    "....RRRRRRRRRR..",
    ".....RRRRRRRR...",
    "......Y...Y.....",
    "......Y...Y.....",
    ".....YY..YY.....",
]
# Head, 5x5, beak on the left.
HEAD = [
    ".WWW.",
    "WWWWW",
    "YWKWW",
    "YWWWW",
    ".WWW.",
]
# The same head in disguise: glasses across the eye, moustache under the beak.
HEAD_DISGUISED = [
    ".WWW.",
    "CCCCW",
    "YCKCW",
    "BBBWW",
    ".WWW.",
]
TURKEY_H = len(TURKEY_BODY)

# Chef, facing right, 16 rows tall.
CHEF = [
    ".WWWW.",
    "WWWWWW",
    ".WWWW.",
    ".WWWW.",
    ".YYYY.",
    ".YYKY.",
    ".YYYY.",
    "..WW..",
    ".WWWW.",
    ".WWWW.",
    ".WWWW.",
    ".WWWW.",
]
CHEF_LEGS = [
    [".B..B.", ".B..B.", ".B..B.", "KK.KK."],   # standing
    [".B.B..", "B...B.", "B...B.", "K...K."],   # stride
    ["..BB..", "..B.B.", ".B..B.", ".K..K."],   # passing
]

TX0 = 56        # turkey's pecking spot
TX1 = 80        # where it stands in disguise
TY = H - TURKEY_H

SIGN_TOP = ("EAT", "MORE")
SIGN_X0, SIGN_X1 = 43, 77


def sprite(c, rows, x0, y0, flip=False, recolor=None):
    w = len(rows[0])
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            col = PAL[ch]
            if recolor:
                col = recolor.get(ch, col)
            xx = x0 + (w - 1 - dx if flip else dx)
            c.pixel(xx, y0 + dy, col)


def draw_turkey(c, x, y, pose="stand", disguised=False, tail_shift=0, wing_up=False):
    recolor = None
    if tail_shift:
        cyc = ["Y", "M", "G"]
        recolor = {k: PAL[cyc[(cyc.index(k) + tail_shift) % 3]] for k in cyc}
    sprite(c, TURKEY_BODY, x, y, recolor=recolor)
    head = HEAD_DISGUISED if disguised else HEAD
    if pose == "peck":
        hx, hy = x - 2, y + 7
        # neck sloping down to the ground
        c.pixel(x + 3, y + 8, C.WHITE)
        c.pixel(x + 4, y + 7, C.WHITE)
        sprite(c, head, hx, hy)
        c.pixel(hx + 1, hy + 5, C.RED)        # wattle
    else:
        hx, hy = x - 1, y + 1
        c.pixel(x + 3, y + 6, C.WHITE)        # neck
        c.pixel(x + 4, y + 7, C.WHITE)
        sprite(c, head, hx, hy)
        c.pixel(hx, hy + 5, C.RED)            # wattle
        c.pixel(hx, hy + 6, C.RED)
    if wing_up:
        # a wing raised to the forehead
        for p in ((x + 5, y + 6), (x + 4, y + 5), (x + 4, y + 4), (x + 3, y + 3)):
            c.pixel(*p, C.RED)
    return hx, hy


def draw_chef(c, x, step, flip=False, arms="cleaver", bob=0):
    y = 0 + bob
    body = CHEF + CHEF_LEGS[step % 3 if step >= 0 else 0]
    sprite(c, body, x, y, flip=flip)
    front = x + 6 if not flip else x - 1
    back = x - 1 if not flip else x + 6
    d = 1 if not flip else -1
    if arms == "cleaver":
        c.pixel(front, y + 8, C.WHITE)           # arm
        c.pixel(front, y + 7, C.YELLOW)          # handle
        c.pixel(front + d, y + 6, C.YELLOW)
        for bx in range(3):
            for by in range(3):
                c.pixel(front + d * (bx + 1), y + 3 + by, C.CYAN)
    elif arms == "shrug_up":
        for (ax, ay) in ((0, 8), (1, 7), (1, 6)):
            c.pixel(front + d * ax, y + ay, C.WHITE)
            c.pixel(back - d * ax, y + ay, C.WHITE)
        c.pixel(front + d, y + 7, C.CYAN)        # cleaver hanging limp
        c.pixel(front + d * 2, y + 7, C.CYAN)
        c.pixel(front + d * 2, y + 8, C.CYAN)
    elif arms == "shrug_mid":
        for (ax, ay) in ((0, 9), (1, 9), (2, 8)):
            c.pixel(front + d * ax, y + ay, C.WHITE)
            c.pixel(back - d * ax, y + ay, C.WHITE)
        c.pixel(front + d * 2, y + 9, C.CYAN)
        c.pixel(front + d * 3, y + 9, C.CYAN)
        c.pixel(front + d * 3, y + 10, C.CYAN)
    elif arms == "down":
        c.pixel(front, y + 9, C.WHITE)
        c.pixel(front, y + 10, C.YELLOW)
        c.pixel(front + d, y + 10, C.CYAN)
        c.pixel(front + d, y + 11, C.CYAN)
        c.pixel(front + d * 2, y + 11, C.CYAN)


def draw_sign(c):
    # wooden board (yellow frame), white letters, post down to the ground
    c.rect(SIGN_X0, 0, SIGN_X1 - SIGN_X0 + 1, 14, C.YELLOW)
    w1 = Canvas.small_text_width("EAT MORE")
    c.small_text("EAT MORE", (SIGN_X0 + SIGN_X1 + 1 - w1) // 2, 2, C.WHITE)
    w2 = Canvas.small_text_width("HAM!")
    c.small_text("HAM!", (SIGN_X0 + SIGN_X1 + 1 - w2) // 2, 8, C.RED)
    mid = (SIGN_X0 + SIGN_X1) // 2
    c.vline(mid, 14, 2, C.YELLOW)


def draw_puff(c, f, cx, cy, rnd):
    age = f - 12
    r = 3 + age * 3
    n = 60 - age * 12
    for _ in range(n):
        a = rnd.random() * math.tau
        d = r * math.sqrt(rnd.random())
        x = round(cx + d * math.cos(a) * 1.6)
        y = round(cy + d * math.sin(a))
        c.pixel(x, y, rnd.choice((C.WHITE, C.WHITE, C.CYAN, C.BLUE)))


def lerp_x(f, f0, f1, x0, x1):
    t = (f - f0) / (f1 - f0)
    return round(x0 + (x1 - x0) * t)


def main():
    rnd = random.Random(1127)
    grains = [(TX0 - 4, 15), (TX0 - 7, 15), (TX0 - 1, 15), (TX0 - 10, 15)]
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()

        # --- the turkey -------------------------------------------------
        if f < 12:
            for i, g in enumerate(grains):
                if f < 3 * (i + 1) + 2:     # grains get eaten one by one
                    c.pixel(*g, C.YELLOW)
            pose = "peck" if (f < 10 and f % 3 == 1) else "stand"
            draw_turkey(c, TX0, TY, pose)
            if f in (10, 11):
                c.text("!", TX0 - 8, 0, C.RED)
        elif f >= 14:
            draw_sign(c)
            hop = 0
            tail = 0
            wing = f in (45, 46)
            if f >= 47:
                hop = -1 if f % 2 else 0
                tail = (f - 47) % 3 + 1
            hx, hy = draw_turkey(c, TX1, TY + hop, "stand", disguised=True,
                                 tail_shift=tail, wing_up=wing)
            # sweat: a bead forms at 25 and slides down
            if 25 <= f <= 44:
                k = (f - 25) % 6
                c.pixel(hx + 3, hy - 1 + min(k, 3) if k < 4 else hy - 1, C.CYAN)
            if f == 46:
                for p in ((hx + 6, hy - 2), (hx + 8, hy - 3), (hx + 10, hy - 2)):
                    c.pixel(*p, C.CYAN)
            if f >= 47 and f % 2 == 0:
                # little sparkles of glee
                c.pixel(TX1 + 15, TY - 1 + (f % 4), C.YELLOW)
                c.pixel(TX1 - 3, TY + 1, C.WHITE)

        # --- the chef ---------------------------------------------------
        if 2 <= f <= 11:
            draw_chef(c, lerp_x(f, 2, 11, -8, 14), f, arms="cleaver")
        elif 12 <= f <= 14:
            draw_chef(c, 14, -1, arms="cleaver")
        elif 15 <= f <= 22:
            draw_chef(c, lerp_x(f, 15, 22, 15, 29), f, arms="cleaver")
        elif 23 <= f <= 30:
            draw_chef(c, 29, -1, arms="down")
            if f % 4 != 3:
                c.text("?", 36, 0, C.YELLOW)
        elif 31 <= f <= 35:
            arms = "shrug_up" if f in (31, 32, 34) else "shrug_mid"
            draw_chef(c, 29, -1, arms=arms)
            c.text("?", 36, 0, C.YELLOW)
        elif 36 <= f <= 44:
            draw_chef(c, lerp_x(f, 36, 44, 29, -8), f, flip=True, arms="down")

        # --- the puff on top of everything ------------------------------
        if 12 <= f <= 15:
            draw_puff(c, f, TX0 + 7, 9, rnd)
            if f >= 13:
                draw_puff(c, f, TX1 + 6, 9, rnd)

        if f >= 45:
            n = min(5, f - 44)
            c.text("PHEW!"[:n], 4, 4, C.YELLOW if f % 2 else C.WHITE)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/turkey_escape.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
