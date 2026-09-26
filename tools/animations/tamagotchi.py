#!/usr/bin/env python3
"""
Tamagotchi -- a whole day of a virtual pet, in five seconds.

The LCD sits in the middle of the panel inside a blue bezel, with the toy's
icon bays either side: a fork and knife and a bath duck on the left, a heart
meter and the attention call on the right. Idle icons are dim blue; the one
in use lights up.

A spotted egg wobbles, cracks, and pops: the top of the shell flies off and a
round cyan blob blinks up at you, then bounces around the screen. Its tummy
rumbles -- the attention icon flashes red and the food icon blinks -- until a
burger drops in and it chomps it down in three bites. Satisfied, it... makes
a little yellow pile, with green stink lines, and squints at it. The duck
icon lights, a yellow duck rides a cyan wave across the screen and washes the
mess away, and the pet bounces for joy as red hearts float up and the heart
meter fills.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16
LCD_X0, LCD_X1 = 18, 77       # bezel columns; the scene lives between them
FLOOR = 14                    # sprites stand on this row
PET_X = 43                    # the pet's home column (left edge of sprite)

PALETTE = {
    "#": C.CYAN,      # pet body
    "k": C.BLACK,
    "w": C.WHITE,
    "e": C.WHITE,     # egg shell
    "s": C.MAGENTA,   # egg spots
    "y": C.YELLOW,
    "g": C.GREEN,
    "r": C.RED,
    "b": C.BLUE,
    "c": C.CYAN,
}

# -- the pet, 10x8 ---------------------------------------------------------
PET = {
    "normal": [
        "...####...",
        ".########.",
        "##########",
        "##k####k##",
        "##k####k##",
        "###k##k###",
        ".###kk###.",
        "..##..##..",
    ],
    "blink": [
        "...####...",
        ".########.",
        "##########",
        "##########",
        "#kk####kk#",
        "###k##k###",
        ".###kk###.",
        "..##..##..",
    ],
    "happy": [
        "...####...",
        ".########.",
        "##k####k##",
        "#k#k##k#k#",
        "##########",
        "##kkkkkk##",
        ".##kkkk##.",
        "..##..##..",
    ],
    "sad": [
        "...####...",
        ".########.",
        "#k######k#",
        "##k####k##",
        "##k####k##",
        "##########",
        ".##kkkk##.",
        "..##..##..",
    ],
    "open": [
        "...####...",
        ".########.",
        "##k####k##",
        "##########",
        "##kkkkkk##",
        "##kkkkkk##",
        ".#kkkkkk#.",
        "..##..##..",
    ],
    "shut": [
        "...####...",
        ".########.",
        "##k####k##",
        "##########",
        "##########",
        "##kkkkkk##",
        ".########.",
        "..##..##..",
    ],
    "squint": [
        "...####...",
        ".########.",
        "#k######k#",
        "##k####k##",
        "#k######k#",
        "##########",
        ".#k#kk#k#.",
        "..##..##..",
    ],
}

EGG = [
    "...ee...",
    "..eeee..",
    ".eesees.",
    ".eeeeee.",
    "eseeeese",
    "eeeesee.",
    "eeseeeee",
    "eeeeesee",
    ".eeeeee.",
    "..eeee..",
]
EGG = [row if len(row) == 8 else row + "." for row in EGG]
CRACK = [(0, 5), (1, 4), (2, 5), (3, 4), (4, 5), (5, 4), (6, 5), (7, 4)]

BURGER = [
    ".yyyyy.",
    "yywyyyy",
    "ggggggg",
    "rrrrrrr",
    "yyyyyyy",
]

POOP = [
    "..y...",
    ".yyy..",
    ".yyyy.",
    "yyyyyy",
]
CUP = [
    "e.ee.ee.ee.e",
    "eeseeeeeseee",
    ".eeeeseeeee.",
]

DUCK = [
    "..yy..",
    ".ykyr.",
    "..yyrr",
    "yyyyy.",
    ".yyyy.",
]

HEART = [
    "rr.rr",
    "rrrrr",
    ".rrr.",
    "..r..",
]

# -- icons, 7x7, drawn in whichever colour their state calls for -----------
ICONS = {
    "food": [
        "#.#.#..",
        "#.#.#.#",
        "#####.#",
        ".###.##",
        "..#..##",
        "..#...#",
        "..#...#",
    ],
    "duck": [
        "..##...",
        ".#.##..",
        ".######",
        "#.##...",
        "######.",
        "######.",
        ".####..",
    ],
    "heart": [
        ".##.##.",
        "#######",
        "#######",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    "call": [
        "..###..",
        "..###..",
        "..###..",
        "..###..",
        "..###..",
        ".......",
        "..###..",
    ],
}
ICON_POS = {"food": (5, 0), "duck": (5, 9), "heart": (84, 0), "call": (84, 9)}


def sprite(frame, rows, x, y, palette=None, shift=None):
    """Blit ASCII art; ``shift(row) -> dx`` bends it (the egg's wobble)."""
    palette = palette or PALETTE
    for r, row in enumerate(rows):
        dx = shift(r) if shift else 0
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c + dx, y + r, palette[ch])


def pet(frame, face, x, lift=0):
    sprite(frame, PET[face], x, FLOOR - 8 - lift + 1)


def bezel(frame):
    frame.vline(LCD_X0, 0, H, C.BLUE)
    frame.vline(LCD_X1, 0, H, C.BLUE)
    frame.hline(LCD_X0 + 1, 15, LCD_X1 - LCD_X0 - 1, C.BLUE)


def icons(frame, lit, happiness):
    """``lit`` maps icon name -> colour for this frame; the rest are dim.
    The heart icon doubles as the happiness meter: red fills it from the
    bottom, ``happiness`` rows of its seven."""
    for name, rows in ICONS.items():
        x, y = ICON_POS[name]
        color = lit.get(name, C.BLUE)
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch == "#":
                    here = color
                    if name == "heart" and r >= 7 - happiness:
                        here = C.RED
                    frame.pixel(x + c, y + r, here)


def stink(frame, x, k):
    """Two wavy green stink lines rising off the pile."""
    for i, sx in enumerate((x, x + 4)):
        for dy in range(4):
            wob = (dy + k + i) % 2
            frame.pixel(sx + wob, FLOOR - 5 - dy, C.GREEN)


BOUNCE = [0, 2, 3, 2, 0]


def main():
    anim = Animation(delay=DELAY)

    for f in range(FRAMES):
        frame = anim.frame()
        bezel(frame)
        lit = {}
        hearts_full = 3

        if f < 10:
            # Egg wobbles, harder as it goes, and cracks.
            lean = [0, 1, 0, -1][f % 4] if f >= 2 else 0
            if f >= 6:
                lean = [1, -1][f % 2]
            ex, ey = 44, FLOOR - 10 + 1
            sprite(frame, EGG, ex, ey,
                   shift=lambda r, lean=lean: lean if r < 5 else 0)
            if f >= 6:
                cut = CRACK if f >= 8 else CRACK[:5]
                for cx, cy in cut:
                    frame.pixel(ex + cx + (lean if cy < 5 else 0), ey + cy, C.BLACK)
            if f >= 8:
                lit["call"] = C.YELLOW
        elif f < 14:
            # Hatch: the top of the shell flies off, the pet blinks up.
            k = f - 10
            face = "blink" if k == 1 else "normal"
            pet(frame, face, PET_X)
            sprite(frame, EGG[:5], 44 - k * 3, FLOOR - 9 - k * 2)
            sprite(frame, CUP, PET_X - 1, FLOOR - 2)
            for sx, sy in ((38, 3), (56, 4), (40, 10), (58, 9)):
                if (sx + k) % 2 == 0:
                    frame.pixel(sx, sy, C.WHITE)
        elif f < 21:
            # Bounce around: left, right, back home.
            k = f - 14
            xs = [PET_X, 38, 33, 38, PET_X, 49, PET_X]
            lift = [0, 2, 0, 2, 0, 2, 0][k]
            pet(frame, "happy" if lift else "normal", xs[k], lift)
        elif f < 26:
            # Hungry: sad face, attention icon flashes, food icon blinks.
            pet(frame, "sad", PET_X)
            if f % 2:
                lit["call"] = C.RED
                lit["food"] = C.WHITE
            # A rumble: the pet shivers.
            hearts_full = 1
            if f % 2 == 0:
                frame.pixel(PET_X - 2, FLOOR - 4, C.WHITE)
                frame.pixel(PET_X + 11, FLOOR - 4, C.WHITE)
        elif f < 34:
            # The burger drops in, then three bites.
            lit["food"] = C.YELLOW
            k = f - 26
            bx = PET_X + 13
            if k < 2:
                pet(frame, "sad", PET_X)
                sprite(frame, BURGER, bx, [1, 9][k])
            else:
                chomp = (k - 2) % 2 == 0
                bites = (k - 1) // 2   # 0..3
                pet(frame, "open" if chomp else "shut", PET_X + 2)
                rows = [row[bites * 2:] for row in BURGER]
                if bites < 4:
                    sprite(frame, rows, bx + bites * 2, 9)
                if not chomp and bites:
                    frame.pixel(PET_X + 13, 7, C.YELLOW)
                    frame.pixel(PET_X + 14, 5, C.YELLOW)
        elif f < 41:
            # Full... then a little pile appears.
            k = f - 34
            hearts_full = 5
            if k < 2:
                pet(frame, "happy", PET_X)
            else:
                pet(frame, "squint", PET_X - 4)
                sprite(frame, POOP, PET_X + 12, FLOOR - 3)
                if k >= 3:
                    stink(frame, PET_X + 12, k)
                if k >= 3 and f % 2:
                    lit["call"] = C.RED
                    lit["duck"] = C.WHITE
        elif f < 46:
            # Flush: a wave with a duck riding it sweeps left to right.
            k = f - 41
            lit["duck"] = C.YELLOW
            hearts_full = 5
            front = LCD_X0 + 1 + k * 13
            if front < PET_X + 12:
                sprite(frame, POOP, PET_X + 12, FLOOR - 3)
                stink(frame, PET_X + 12, k)
            # Water behind the front: clear the scene, draw waves.
            for x in range(LCD_X0 + 1, min(front, LCD_X1)):
                for y in range(0, 15):
                    frame.pixel(x, y, C.BLACK)
                if (x + f) % 4 < 2:
                    frame.pixel(x, 13, C.CYAN)
                else:
                    frame.pixel(x, 12, C.CYAN)
                frame.pixel(x, 14, C.BLUE)
            pet(frame, "squint" if front < PET_X else "happy", PET_X - 4)
            if front < LCD_X1:
                frame.vline(front, 9, 6, C.CYAN)
                sprite(frame, DUCK, front - 5, 6)
        else:
            # Joy: hearts float up, the meter fills, the pet bounces.
            k = f - 46
            lit["heart"] = C.RED
            hearts_full = min(7, 5 + k // 2)
            lift = BOUNCE[k % len(BOUNCE)]
            pet(frame, "happy", PET_X, lift)
            for hx, start in ((PET_X - 9, 0), (PET_X + 13, 2), (PET_X - 16, 3), (PET_X + 20, 1)):
                t = k - start
                if 0 <= t <= 6:
                    sprite(frame, HEART, hx + (t % 2), 10 - t * 2)

        icons(frame, lit, hearts_full)

    out = Path(__file__).resolve().parents[2] / "src/sample/tamagotchi.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
