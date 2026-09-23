#!/usr/bin/env python3
"""
Moo Deng (2024) -- Khao Kheow's baby pygmy hippo, the bounciest pork.

A pink-and-grey baby hippo wallows in her pool, face on: a grey head with
a wet shine, little ears, eyes set high, and the much wider pink muzzle with
its two nostrils and blushing cheeks. She bounces four times,
each landing throwing up a splash, while MOO DENG bobs beside her letter by
letter. Then she rears up and opens wide and chomps -- the famous tiny-jaw bite -- three
times, to CHOMP!. Last, one big hop and a belly flop that sends spray
flying: BOUNCY PIG, which is what her name means.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 2024
SKIN, BACK, SHINE = C.MAGENTA, C.BLUE, C.WHITE
WATER_Y = 14
HIPPO_X, HIPPO_Y = 3, 2
TEXT_X0, TEXT_X1 = 26, 96

HOP = [0, 1, 2, 2, 2, 1]                 # one bounce, six frames
BOUNCE_END, CHOMP_END = 24, 42
BIG_HOP = [0, 1, 2, 2, 2, 2, 1, 0]       # the finale, from frame 42
CHOMP_LIFT = 2                           # she rears up out of the water to bite


FACE = [
    "...BB........BB...",
    "...BRB......BRB...",
    "....BBBBBBBBBB....",
    "...BBBBBWWBBBBB...",
    "...BWKBBBBBBWKB...",
    "...BKKBBBBBBKKB...",
    "..BBBBBBBBBBBBBB..",
    ".################.",
    "##################",
    "###KK########KK###",
    "##R############R##",
    "#####KKKKKKKK#####",
    ".################.",
]
PAINT = {"B": BACK, "#": SKIN, "W": SHINE, "K": C.BLACK, "R": C.RED}


def inside(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def hippo_pixels(open_mouth):
    """Her face, front on, in local coordinates, as {(x, y): color}.

    Front on reads as a hippo far better than a profile at this size: a
    narrow grey head over a much wider pink muzzle, and the two nostrils.
    """
    px = {}
    for y, line in enumerate(FACE):
        for x, ch in enumerate(line):
            if ch != ".":
                px[(x, y)] = PAINT[ch]
    if not open_mouth:
        return px

    # Open wide: the lower jaw drops, the gape shows red, and the little
    # tusks show white at the corners -- the bite that made her famous.
    opened = {}
    for (x, y), color in px.items():
        if y >= 11:
            opened[(x, y + 3)] = color if color != C.BLACK else SKIN
        else:
            opened[(x, y)] = color
    for x in range(1, 17):
        for y in (11, 12, 13):
            opened[(x, y)] = C.RED
    for x, y in ((2, 11), (15, 11), (3, 13), (14, 13)):
        opened[(x, y)] = C.WHITE
    return opened


def lift_at(index):
    if index < BOUNCE_END:
        return HOP[index % len(HOP)]
    if index < CHOMP_END:
        return CHOMP_LIFT
    k = index - CHOMP_END
    return BIG_HOP[k] if k < len(BIG_HOP) else 0


def build():
    rng = random.Random(SEED)
    closed, opened = hippo_pixels(False), hippo_pixels(True)
    anim = Animation(delay=DELAY)

    # Splashes: each landing throws droplets that arc out and fall back.
    landings = [i for i in range(1, FRAMES) if lift_at(i) == 0 and lift_at(i - 1) > 0]
    drops = []
    for at in landings:
        big = at >= CHOMP_END
        for _ in range(14 if big else 6):
            side = rng.choice((-1, 1))
            drops.append({
                "at": at,
                "x": HIPPO_X + (0 if side < 0 else 17) + rng.uniform(-1, 1),
                "vx": side * rng.uniform(0.6, 2.2 if big else 1.4),
                "vy": -rng.uniform(1.2, 2.4 if big else 1.8),
            })

    for index in range(FRAMES):
        frame = anim.frame()
        lift = lift_at(index)
        chomping = BOUNCE_END <= index < CHOMP_END and (index - BOUNCE_END) % 6 in (1, 2, 3)
        # A slight squash on the frame she lands.
        squash = lift == 0 and index > 0 and lift_at(index - 1) > 0
        for (x, y), color in (opened if chomping else closed).items():
            yy = HIPPO_Y - lift + y + (1 if squash and y < 6 else 0)
            frame.pixel(HIPPO_X + x, yy, color)

        # The pool: a wavy surface over solid blue, drawn over her legs.
        for x in range(96):
            crest = math.sin(x * 0.45 - index * 0.8) > 0.55
            frame.pixel(x, WATER_Y, C.CYAN if crest else C.BLACK if x % 2 else C.BLUE)
            frame.pixel(x, WATER_Y + 1, C.BLUE if (x + index) % 5 else C.CYAN)
        for x in range(HIPPO_X - 1, HIPPO_X + 19):
            if lift == 0:
                frame.pixel(x, WATER_Y, C.CYAN if (x + index) % 3 == 0 else C.BLUE)

        for d in drops:
            t = index - d["at"]
            if t < 0:
                continue
            x = d["x"] + d["vx"] * t
            y = WATER_Y - 1 + d["vy"] * t + 0.35 * t * t
            if y < WATER_Y:
                frame.pixel(round(x), round(y), C.WHITE if t == 0 else C.CYAN)

        # Captions, each bobbing a letter at a time.
        if index < BOUNCE_END:
            caption, color = "MOO DENG", C.MAGENTA
        elif index < CHOMP_END:
            caption, color = "CHOMP!", C.WHITE if chomping else C.RED
        else:
            caption, color = "BOUNCY PIG", C.MAGENTA if index % 4 < 2 else C.WHITE
        width = frame.text_width(caption, proportional=True)
        x = TEXT_X0 + (TEXT_X1 - TEXT_X0 - width) // 2
        cursor = x
        for n, ch in enumerate(caption):
            # One letter at a time hops, a wave passing along the word.
            bob = 1 if n == index % (len(caption) + 4) and caption != "CHOMP!" else 0
            if caption == "CHOMP!" and chomping:
                bob = rng.choice((0, 1))
            frame.text(ch, cursor, 3 - bob, color, proportional=True)
            cursor += frame.text_width(ch, proportional=True) + 1
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/moo_deng.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
