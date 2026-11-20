#!/usr/bin/env python3
"""
Hand turkey -- the one every kid draws in November.

A white crayon traces round a spread hand on the left of the panel: up the
thumb, over each of the four fingers, down the side of the palm. Then the
colouring-in starts. Each finger becomes a tail feather, scribbled in a
few frames apiece in red, yellow, green and magenta, the crayon tip
changing colour to match. The thumb becomes the head: coloured in blue with a white dot of an eye, a
yellow beak, a red wattle hanging under it. Two yellow stick legs go on
underneath.

Then the crayon moves right and writes HAPPY, one letter a frame, and
THANKSGIVING under it, every letter a different crayon. To finish, the
turkey gobbles -- its beak opens and shuts -- and blinks, while the
letters take turns jumping a pixel like a kid bouncing in their seat.

Beat sheet (frame indexes):
  0-1    blank paper
  2-17   outline traced (16 frames)
  18-29  feathers coloured, 3 frames a finger
  30-33  blue head and eye, beak, wattle, legs
  34-44  HAPPY, then THANKSGIVING, a letter a frame (two a frame on line 2)
  44-52  gobble, blink, bouncing letters
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16

# The hand, traced as ASCII art (x 1..25 once shifted). Four fingers fan up
# and become feathers; the thumb, up and to the left, becomes the head.
HAND = [
    "............##...........",
    ".......##..####..##......",
    "......####.####.####.....",
    "..##..####.####.####..##.",
    ".####.####.####.####.####",
    ".####.####.####.####.####",
    "..####.###.####.####.####",
    "...######################",
    "....####################.",
    ".....##################..",
    "......################...",
    ".......##############....",
    "........############.....",
    "..........########.......",
]
SHIFT = 1                                       # room for the beak at x 0
FINGER_BANDS = [(6, 9), (11, 14), (16, 19), (21, 24)]   # unshifted columns
FEATHER_COLORS = [C.RED, C.YELLOW, C.GREEN, C.MAGENTA]

MASK = {}
for y, row in enumerate(HAND):
    for x, ch in enumerate(row):
        if ch == "#":
            MASK[(x + SHIFT, y)] = None

OUTLINE = {
    p for p in MASK
    if any((p[0] + dx, p[1] + dy) not in MASK for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
}


def region(p):
    x, y = p[0] - SHIFT, p[1]
    if x <= 5 and y <= 7:
        return "thumb"
    if y <= 7:
        for i, (lo, hi) in enumerate(FINGER_BANDS):
            if lo <= x <= hi:
                return i
    return "palm"


INTERIOR = {p: region(p) for p in MASK if p not in OUTLINE}


def trace_order():
    """Walk the outline greedily, nearest unvisited pixel next, from the wrist."""
    left = set(OUTLINE)
    cur = min(left, key=lambda p: (-p[1], p[0]))       # bottom-left of the palm
    path = [cur]
    left.remove(cur)
    while left:
        cur = min(left, key=lambda p: ((p[0] - cur[0]) ** 2 + (p[1] - cur[1]) ** 2, p[1], p[0]))
        path.append(cur)
        left.remove(cur)
    return path


TRACE = trace_order()
TRACE_START, TRACE_FRAMES = 2, 16
COLOR_START, PER_FINGER = 18, 3
FACE_START = 30
TEXT_START = 34
GOBBLE_START = 44

# The head: the thumb's tip.
EYE = (2 + SHIFT, 4)
BEAK = [(0, 4), (1, 4)]
BEAK_OPEN = [(0, 3), (1, 3), (0, 5), (1, 5)]
WATTLE = [(1 + SHIFT, 6), (1 + SHIFT, 7), (2 + SHIFT, 8)]
assert EYE in INTERIOR and not any(p in MASK for p in BEAK + BEAK_OPEN + WATTLE)
LEGS = [(13, 14), (13, 15), (12, 15), (14, 15), (17, 14), (17, 15), (16, 15), (18, 15)]

LINE1, LINE2 = "HAPPY", "THANKSGIVING"
TEXT_X = 25
L2_X = TEXT_X
L1_X = L2_X + (Canvas.text_width(LINE2) - Canvas.text_width(LINE1)) // 2
assert L2_X + Canvas.text_width(LINE2) <= W
CRAYONS = [C.RED, C.YELLOW, C.GREEN, C.MAGENTA, C.CYAN]

# when each letter is written: HAPPY one a frame, then THANKSGIVING two a frame
LETTERS = []
for i, ch in enumerate(LINE1):
    LETTERS.append((TEXT_START + i, ch, L1_X + 6 * i, 0, CRAYONS[i % 5]))
for i, ch in enumerate(LINE2):
    LETTERS.append((TEXT_START + len(LINE1) + i // 2, ch, L2_X + 6 * i, 9, CRAYONS[(i + 2) % 5]))
assert LETTERS[-1][0] < GOBBLE_START + 2


def draw_crayon(c, x, y, tip):
    """A crayon held at a slant: tip at (x, y), body up and to the right."""
    c.pixel(x, y, tip)
    for i in range(1, 4):
        c.pixel(x + i, y - i, tip if i == 1 else C.WHITE)
    c.pixel(x + 4, y - 4, C.BLUE)


def main():
    rnd = random.Random(1126)
    # scribble order inside each feather
    fills = {}
    for i in range(4):
        pts = [p for p, r in INTERIOR.items() if r == i]
        rnd.shuffle(pts)
        fills[i] = pts

    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        crayon = None

        # outline
        if f >= TRACE_START:
            n = len(TRACE) if f >= TRACE_START + TRACE_FRAMES else \
                round(len(TRACE) * (f - TRACE_START + 1) / TRACE_FRAMES)
            for p in TRACE[:n]:
                c.pixel(*p, C.WHITE)
            if f < TRACE_START + TRACE_FRAMES:
                crayon = (TRACE[n - 1], C.WHITE)

        # feathers
        for i in range(4):
            start = COLOR_START + i * PER_FINGER
            if f < start:
                continue
            k = min(1.0, (f - start + 1) / PER_FINGER)
            pts = fills[i][: round(len(fills[i]) * k)]
            for p in pts:
                c.pixel(*p, FEATHER_COLORS[i])
            if f < start + PER_FINGER:
                crayon = (pts[-1], FEATHER_COLORS[i])

        # face and legs
        gobbling = f >= GOBBLE_START and (f - GOBBLE_START) % 4 in (1, 2)
        blinking = f in (49, 50)
        if f >= FACE_START:
            for p, r in INTERIOR.items():
                if r == "thumb":
                    c.pixel(*p, C.BLUE)
            if not blinking:
                c.pixel(*EYE, C.WHITE)
        if f == FACE_START:
            crayon = (EYE, C.BLUE)
        if f >= FACE_START + 1:
            for p in (BEAK_OPEN if gobbling else BEAK):
                c.pixel(*p, C.YELLOW)
            if f == FACE_START + 1:
                crayon = (BEAK[-1], C.YELLOW)
        if f >= FACE_START + 2:
            for p in WATTLE:
                c.pixel(*p, C.RED)
            if f == FACE_START + 2:
                crayon = (WATTLE[-1], C.RED)
        if f >= FACE_START + 3:
            for p in LEGS:
                c.pixel(*p, C.YELLOW)
            if f == FACE_START + 3:
                crayon = (LEGS[-1], C.YELLOW)

        # writing
        written = [L for L in LETTERS if L[0] <= f]
        for j, (fw, ch, x, y, col) in enumerate(written):
            dy = 0
            if f >= GOBBLE_START and (f + j) % 7 == 0:
                dy = -1
            c.text(ch, x, y + dy, col)
        if written and f <= LETTERS[-1][0]:
            last = written[-1]
            crayon = ((last[2] + 4, last[3] + 6), last[4])

        if crayon:
            (x, y), tip = crayon
            draw_crayon(c, x, y, tip)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/hand_turkey.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
