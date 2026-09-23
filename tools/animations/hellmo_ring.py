#!/usr/bin/env python3
"""
This Is Fine, with Hellmo -- the dog at the centre of a summoning circle.

Two memes in one room. KC Green's dog sits at the middle of the panel in his
hat with his mug, and five Hellmos -- Elmo, arms raised, in the flames --
circle him like a carousel. The ring is an ellipse seen from slightly above:
a Hellmo on the far half is drawn small and high and passes *behind* the dog,
one on the near half is full size and low and passes *in front of* him, and
the switch happens at the ends of the ellipse where it is hardest to see. So
the sort order does the work of 3D. One revolution per loop, seamless.

Everything sits in rows 5-15, which leaves the top five rows for the caption:
THIS IS FINE. types out in a 3x5 mini-font, since the 5x7 font would collide
with the hat. Each Hellmo is cut out of the fire behind it by a one-pixel black
outline, since red fur on red flame would otherwise vanish. The dog blinks and
takes a sip. The fire does not stop.
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
SEED = 666
COUNT = 5
CX, RADIUS = 48, 40

# Dog from this_is_fine.py: hat (white) over a yellow body, mug in hand.
DOG = [
    ".####....",
    "..##.....",
    ".#####...",
    "#.###.#..",
    ".#####...",
    "..###....",
    ".#####.#.",
    "#.....##.",
    "#######..",
    "#.....#..",
]
DOG_X, DOG_Y = 44, 6

# r fur, W eye white, K pupil / mouth, Y nose. Two arm poses, swapped on a
# beat so the circle looks like it is chanting.
HELLMO_NEAR = [
    [
        "r.......r",
        "r.WWrWW.r",
        "r.WKrKW.r",
        ".rrrYrrr.",
        "..rKKKr..",
        "..rrrrr..",
        "...rrr...",
        "..rr.rr..",
        "..r...r..",
    ],
    [
        ".r.....r.",
        "r.WWrWW.r",
        "r.WKrKW.r",
        ".rrrYrrr.",
        "..rKKKr..",
        "..rrrrr..",
        "...rrr...",
        "..rr.rr..",
        "..r...r..",
    ],
]
HELLMO_FAR = [
    ["r...r", "rWrWr", ".rYr.", ".rKr.", "..r..", ".r.r."],
    [".r.r.", "rWrWr", ".rYr.", ".rKr.", "..r..", ".r.r."],
]
PAINT = {"r": C.RED, "W": C.WHITE, "K": C.BLACK, "Y": C.YELLOW}
NEAR_BOTTOM, FAR_BOTTOM = 15, 11

MINI = {
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["#", "#", "#", "#", "#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "F": ["###", "#..", "##.", "#..", "#.."],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "E": ["###", "#..", "##.", "#..", "###"],
    ".": [".", ".", ".", ".", "#"],
    " ": ["..", "..", "..", "..", ".."],
}
CAPTION = "THIS IS FINE."
CAPTION_AT = 8
SIP_AT = 30
BLINKS = (12, 13, 41)


def mini_width(text):
    return sum(len(MINI[ch][0]) + 1 for ch in text) - 1


def mini_text(frame, text, x, y, color):
    for ch in text:
        for r, line in enumerate(MINI[ch]):
            for c, cell in enumerate(line):
                if cell == "#":
                    frame.pixel(x + c, y + r, color)
        x += len(MINI[ch][0]) + 1


def draw_fire(frame, rng, index):
    """Floor flames, taller at the walls, flickering every frame."""
    for x in range(96):
        edge = max(0.0, 1 - min(x, 95 - x) / 16)
        wobble = math.sin(x * 0.7 + index * 1.3) + math.sin(x * 0.23 - index * 0.9)
        height = 3 + round(edge * 12 + wobble) + rng.randint(0, 1)
        top = 16 - max(1, height)
        for y in range(top, 16):
            if rng.random() < 0.15:
                continue
            heat = (y - top) / max(1, 15 - top)
            frame.pixel(x, y, C.RED if heat < 0.35 else C.YELLOW if heat < 0.8 else C.WHITE)
    # Embers drifting up, kept out of the caption rows.
    for k in range(18):
        ex = (k * 37 + index * (1 + k % 3)) % 96
        ey = 14 - ((index * 2 + k * 5) % 9)
        if ey >= 6:
            frame.pixel(ex, ey, C.YELLOW if k % 2 else C.RED)


def draw_sprite(frame, sprite, x, y):
    """Paint with a one-pixel black halo, so red fur reads against flame."""
    cells = [(x + c, y + r, PAINT[ch]) for r, line in enumerate(sprite)
             for c, ch in enumerate(line) if ch != "."]
    for px, py, _ in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                frame.pixel(px + dx, py + dy, C.BLACK)
    for px, py, color in cells:
        frame.pixel(px, py, color)


def draw_dog(frame, index):
    blink = index in BLINKS
    sip = SIP_AT <= index < SIP_AT + 6
    cells = [(DOG_X + c, DOG_Y + r) for r, line in enumerate(DOG)
             for c, ch in enumerate(line) if ch == "#" and not (r == 6 and c == 7)]
    for px, py in cells:
        for dx in (-1, 0, 1):
            frame.pixel(px + dx, py, C.BLACK)
    for px, py in cells:
        frame.pixel(px, py, C.WHITE if py - DOG_Y < 2 else C.YELLOW)
    for ex in (2, 4):
        frame.pixel(DOG_X + ex, DOG_Y + 3, C.YELLOW if blink else C.BLACK)
    mug_y = DOG_Y + 3 if sip else DOG_Y + 6
    frame.rect(DOG_X + 7, mug_y, 2, 2, C.CYAN, fill=True)
    frame.pixel(DOG_X + 9, mug_y, C.CYAN)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    caption_x = (96 - mini_width(CAPTION)) // 2
    for index in range(FRAMES):
        frame = anim.frame()
        draw_fire(frame, rng, index)

        pose = (index // 3) % 2
        ring = []
        for i in range(COUNT):
            theta = 2 * math.pi * (index / FRAMES + i / COUNT)
            depth = math.sin(theta)  # > 0: near side, in front of the dog
            near = depth > 0
            sprite = (HELLMO_NEAR if near else HELLMO_FAR)[(pose + i) % 2]
            width, height = len(sprite[0]), len(sprite)
            x = round(CX + RADIUS * math.cos(theta)) - width // 2
            bottom = NEAR_BOTTOM if near else FAR_BOTTOM
            ring.append((depth, sprite, x, bottom - height + 1))

        ring.sort(key=lambda item: item[0])
        for depth, sprite, x, y in ring:
            if depth <= 0:
                draw_sprite(frame, sprite, x, y)
        draw_dog(frame, index)
        for depth, sprite, x, y in ring:
            if depth > 0:
                draw_sprite(frame, sprite, x, y)

        if index >= CAPTION_AT:
            shown = CAPTION[: min(len(CAPTION), index - CAPTION_AT + 1)]
            mini_text(frame, shown, caption_x, 0, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hellmo_ring.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
