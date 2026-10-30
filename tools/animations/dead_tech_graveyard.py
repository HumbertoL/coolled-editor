#!/usr/bin/env python3
"""
Dead tech graveyard -- the fax machine refuses to stay buried.

A moonlit graveyard: a yellow crescent moon top right, a strip of green
grass, and four blue tombstones with rounded tops, each carved in white
with a piece of retired technology -- FAX, IE6, ZUNE, FLASH. Cyan and white
ground fog drifts across the bottom rows. The sky reads RIP OLD TECH, which
fades out through cyan and blue as two magenta bats flap across.

Then the red mound of earth beside the FAX grave starts to shake, the
headstone rocking with it, clods hopping into the air. A green zombie hand
bursts up out of the dirt, sending a spray of red earth flying, and raises
a white sheet of paper -- a fax, lines of blue type and all. It screeches
in the sky: BEEP BOP BEEP, then a jittering EEEE-KRRRR, the page quivering.
Silence, and the payoff in yellow: YOU'VE GOT FAX, while the hand waves the
page gently above the grave.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16

STONE_TOP = 6
TEXT_Y = 8
# (name, left x); each stone is the name's width plus 2px either side.
STONES = [("FAX", 1), ("IE6", 29), ("ZUNE", 46), ("FLASH", 68)]
MOUND_X = 17              # the FAX grave's dirt, x 17..27
HAND_X = 19               # left edge of the 7px hand sprite
SKY_X = 30                # where the screeches are written

MOON = [
    "..###",
    ".##..",
    "##...",
    "##...",
    "##...",
    ".##..",
    "..###",
]

BAT = [
    ["#...#", ".###.", "..#.."],           # wings up
    ["..#..", ".###.", "#...#"],           # wings down
]

HAND = [
    "#.#.#..",
    "#.#.#..",
    "#.#.#.#",
    "######.",
    ".####..",
    "..##...",
    "..##...",
    "..##...",
    "..##...",
]

# Beat sheet: (name, frames).
SCRIPT = [
    ("still", 2),
    ("rip", 10),
    ("fade", 3),
    ("bats", 3),
    ("shake", 6),
    ("burst", 4),
    ("paper", 1),
    ("beep", 4),
    ("screech", 6),
    ("fax", 14),
]


def sprite(c, rows, x, y, color):
    for r, line in enumerate(rows):
        for k, ch in enumerate(line):
            if ch == "#":
                c.pixel(x + k, y + r, color)


def stone(c, name, x, dx=0):
    w = Canvas.small_text_width(name) + 4
    x += dx
    for y in range(STONE_TOP, H - 1):
        inset = {STONE_TOP: 2, STONE_TOP + 1: 1}.get(y, 0)
        c.hline(x + inset, y, w - 2 * inset, C.BLUE)
    c.small_text(name, x + 2, TEXT_Y, C.WHITE)


def fog(c, f, rnd_wisps):
    for (x0, y, length, color) in rnd_wisps:
        x = (x0 + f) % (W + 20) - 10
        c.hline(x, y, length, color)


def mound(c, dx=0, dy=0):
    c.hline(MOUND_X + 3 + dx, 13 + dy, 5, C.RED)
    c.hline(MOUND_X + 1 + dx, 14 + dy, 9, C.RED)
    c.hline(MOUND_X + dx, 15, 11, C.RED)


def paper(c, x, y, jiggle=0):
    """A 7x7 sheet: white, with blue lines of type and a folded corner."""
    x += jiggle
    c.rect(x, y, 7, 7, C.WHITE, fill=True)
    c.pixel(x + 6, y, C.BLACK)
    for row, length in ((1, 4), (3, 5), (5, 3)):
        c.hline(x + 1, y + row, length, C.BLUE)


def main():
    rnd = random.Random(31)
    wisps = []
    for _ in range(16):
        y = rnd.choice((13, 14, 14, 15))
        wisps.append((rnd.randrange(W + 20), y, rnd.randint(3, 8),
                      C.WHITE if rnd.random() < 0.2 else C.CYAN))
    beats = [name for name, n in SCRIPT for _ in range(n)]
    assert len(beats) == FRAMES, len(beats)

    anim = Animation(delay=DELAY)
    debris = []                     # flying clods: [x, y, vx, vy]
    for f, beat in enumerate(beats):
        c = anim.frame()
        k = beats[:f].count(beat)   # frame index within this beat

        # Sky.
        sprite(c, MOON, 89, 0, C.YELLOW)
        if beat == "rip":
            c.small_text("RIP OLD TECH", (88 - 45) // 2, 0, C.WHITE)
        elif beat == "fade":
            c.small_text("RIP OLD TECH", (88 - 45) // 2, 0,
                         [C.CYAN, C.BLUE, C.BLUE][k])
        if 12 <= f < 24:
            for bx0, by, phase in ((-8, 1, 0), (-22, 0, 1)):
                bx = bx0 + (f - 12) * 9
                sprite(c, BAT[(f + phase) % 2], bx, by, C.MAGENTA)

        # Ground and the graves.
        c.hline(0, 15, W, C.GREEN)
        shake = beat == "shake"
        for name, x in STONES:
            dx = ([1, -1][k % 2] if shake and name == "FAX" and k >= 2 else 0)
            stone(c, name, x, dx)

        hand_y = None               # top row of the hand sprite
        if beat == "burst":
            hand_y = [12, 9, 7, 6][k]
        elif beat in ("paper", "beep", "screech", "fax"):
            hand_y = 7
        sway = 0
        if beat == "fax":
            sway = [0, 1, 1, 0, -1, -1][k % 6] if k >= 2 else 0
        if hand_y is not None:
            hx = HAND_X + sway
            rows = HAND[: max(0, 15 - hand_y)]
            if beat != "burst" or k >= 2:
                jig = (k % 2) if beat == "screech" else 0
                paper(c, hx - 1 + jig, hand_y - 6, 0)
            sprite(c, rows, hx, hand_y, C.GREEN)

        # The mound: trembling, then blown apart by the hand.
        if shake:
            mound(c, dx=[0, 1, -1, 1, -1, 1][k], dy=-(k % 2) if k >= 3 else 0)
            if k >= 2:
                for _ in range(2):
                    c.pixel(MOUND_X + rnd.randrange(11), 13 - rnd.randrange(2), C.RED)
        else:
            mound(c)
        if beat == "burst" and k == 0:
            for _ in range(9):
                debris.append([MOUND_X + 2 + rnd.randrange(7), 13,
                               rnd.choice((-2, -1, 1, 2)), -rnd.randint(2, 4)])
        if debris:
            for d in debris:
                c.pixel(d[0], d[1], C.RED)
                d[0] += d[2]
                d[1] += d[3]
                d[3] += 1
            debris = [d for d in debris if d[1] < 15]

        fog(c, f, wisps)

        # The fax speaks.
        if beat == "beep":
            text = ["BEEP", "BEEP BOP", "BEEP BOP BEEP", "BEEP BOP BEEP"][k]
            c.small_text(text, SKY_X, 0, C.CYAN)
        elif beat == "screech":
            c.small_text("EEEE-KRRRR", SKY_X + (k % 2), (k % 3 == 1) * 1,
                         [C.WHITE, C.YELLOW, C.MAGENTA][k % 3])
            # static crackle around the page
            for _ in range(3):
                c.pixel(HAND_X - 3 + rnd.randrange(13), rnd.randrange(7), C.CYAN)
        elif beat == "fax":
            c.small_text("YOU'VE GOT FAX", SKY_X + 4, 0,
                         C.WHITE if k < 2 else C.YELLOW)

    out = Path(__file__).resolve().parents[2] / "src/sample/dead_tech_graveyard.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
