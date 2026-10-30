#!/usr/bin/env python3
"""
Jack-o'-lantern -- carved, lit, and winking.

A plain red pumpkin with magenta rib lines and a curly green stem sits
on the left of a dark panel. A knife -- white blade, yellow handle -- slides
in and carves it in real time: the blade's tip traces a triangle eye, then
the other, then a little nose, then a long jagged grin, every cut opening
as a black hole the moment the blade passes.

The knife leaves. A match appears beside the pumpkin, strikes with a white
spark, catches yellow, and dips into the corner of the grin. The candle
takes: the mouth lights first, then the eyes, and from then on every carved
pixel flickers in yellow and white, guttering red now and then.

On the right, HAPPY lights letter by letter like wicks catching, then
HALLOWEEN beneath it, and the words flicker in sympathy with the candle --
when the flame gutters red, so does the text. To finish, the pumpkin gives
the room a slow wink: one eye squeezes down to a glowing slit and opens
again.
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

# Pumpkin body: an ellipse sitting on the bottom row.
CX, CY = 14.0, 9.4
RX, RY = 13.6, 6.6
RIBS = (-0.8, -0.42, 0.42, 0.8)      # rib positions as a fraction of half-width

# Face, drawn as ASCII art over the pumpkin's columns (x 0..28).
FACE = {
    5:  "........#...........#........",
    6:  ".......###.........###.......",
    7:  "......#####.......#####......",
    8:  ".....#######.....#######.....",
    9:  "..............#..............",
    10: ".............###.............",
    11: "....##.................##....",
    12: ".....####..#######..####.....",
    13: "......########.########......",
    14: ".........#####.#####.........",
}


def face_cells(rows, xs):
    return [(x, y) for y in rows for x in xs if FACE[y][x] == "#"]


def by_angle(cells):
    """Order a cut around its centroid, as a blade traces an outline."""
    mx = sum(x for x, _ in cells) / len(cells)
    my = sum(y for _, y in cells) / len(cells)
    return sorted(cells, key=lambda p: math.atan2(p[1] - my, p[0] - mx))


LEFT_EYE = by_angle(face_cells(range(5, 9), range(0, 14)))
RIGHT_EYE = by_angle(face_cells(range(5, 9), range(15, 29)))
NOSE = face_cells(range(9, 11), range(29))
# the grin is sliced left to right in one long stroke
MOUTH = sorted(face_cells(range(11, 15), range(29)), key=lambda p: (p[0], p[1]))
CUTS = [("eye", LEFT_EYE, 3), ("eye", RIGHT_EYE, 3), ("nose", NOSE, 2), ("mouth", MOUTH, 5)]

TEXT1, TEXT2 = "HAPPY", "HALLOWEEN"
TEXT_LEFT = 31
T2_X = TEXT_LEFT + (W - TEXT_LEFT - Canvas.text_width(TEXT2)) // 2
T1_X = T2_X + (Canvas.text_width(TEXT2) - Canvas.text_width(TEXT1)) // 2
T1_Y, T2_Y = 0, 9

# Beat sheet (frame indexes).
KNIFE_IN = 3          # 0-2 the pumpkin just sits
CARVE_START = 4       # 4-16 carving (13 frames)
KNIFE_OUT = 17
MATCH_START = 18      # 18 match appears, 19 spark, 20-21 flame, 22 into the grin
LIGHT_START = 23      # 23 the grin catches, 24 the eyes, then flicker
HAPPY_START = 26      # one letter per frame
HALLOWEEN_START = 31
WINK = {43: 1, 44: 2, 45: 2, 46: 2, 47: 2, 48: 1}   # frame -> lid stage
STEADY = range(41, 50)  # no guttering while it winks

# Candle level per frame once lit: 0 guttering, 1 steady, 2 flaring.
rnd_level = random.Random(31)
LEVELS = [rnd_level.choice((1, 1, 1, 2, 2, 0)) for _ in range(FRAMES)]


def pumpkin_mask():
    pts = set()
    for y in range(3, H):
        for x in range(0, 30):
            if ((x - CX) / RX) ** 2 + ((y - CY) / RY) ** 2 <= 1.0:
                pts.add((x, y))
    # the dimple where the stem goes in
    pts.discard((int(CX) - 3, 3))
    pts.discard((int(CX) + 3, 3))
    return pts


BODY = pumpkin_mask()


def rib_pixels():
    out = set()
    for y in range(4, H):
        span = math.sqrt(max(0.0, 1 - ((y - CY) / RY) ** 2))
        for k in RIBS:
            x = round(CX + k * RX * span)
            if abs(k) < 0.5 and 5 <= y <= 14:
                continue          # inner ribs would run through the face
            if (x, y) in BODY:
                out.add((x, y))
    return out


RIB = rib_pixels()


def carve_order():
    """Flatten the cuts into (frame, pixel) -- when each pixel opens."""
    schedule = []
    f = CARVE_START
    for _name, path, frames in CUTS:
        per = len(path) / frames
        for i, p in enumerate(path):
            schedule.append((f + int(i / per), p))
        f += frames
    return schedule


SCHEDULE = carve_order()
HOLES = [p for _f, p in SCHEDULE]
RIGHT_EYE_SET = set(RIGHT_EYE)
assert max(f for f, _ in SCHEDULE) < KNIFE_OUT


def draw_pumpkin(c):
    for (x, y) in BODY:
        c.pixel(x, y, C.MAGENTA if (x, y) in RIB else C.RED)
    # stem, curling right
    for (x, y) in [(14, 0), (15, 0), (16, 0), (13, 1), (14, 1), (13, 2), (14, 2), (13, 3), (14, 3)]:
        c.pixel(x, y, C.GREEN)


def draw_knife(c, tip, f):
    """Blade runs up-right from the tip, handle beyond it."""
    tx, ty = tip
    for i in range(5):
        c.pixel(tx + i, ty - i, C.WHITE if i else C.CYAN)
    for i in range(5, 8):
        c.pixel(tx + i, ty - i, C.YELLOW)


def flame_color(rnd, level):
    r = rnd.random()
    if level == 0:
        return C.RED if r < 0.45 else C.YELLOW
    if level == 2:
        return C.WHITE if r < 0.45 else C.YELLOW
    return C.YELLOW if r < 0.75 else C.WHITE if r < 0.95 else C.RED


def draw_text(c, f, rnd, level):
    n1 = min(len(TEXT1), max(0, f - HAPPY_START + 1))
    n2 = min(len(TEXT2), max(0, (f - HALLOWEEN_START + 1) * 2))
    base = {0: C.RED, 1: C.YELLOW, 2: C.YELLOW}[level]
    for row, text, x0, y0, n, start in (
        (0, TEXT1, T1_X, T1_Y, n1, HAPPY_START),
        (1, TEXT2, T2_X, T2_Y, n2, HALLOWEEN_START),
    ):
        for i in range(n):
            # a letter that has just caught glows red for a frame first
            just = (start + (i if row == 0 else i // 2)) == f
            col = C.RED if just else base
            x = x0 + 6 * i
            if level == 2 and not just:
                # a white shimmer running through the brightest frames
                hot = (f * 7 + i * 3 + row) % 9 == 0
                col = C.WHITE if hot else col
            c.text(text[i], x, y0, col)


def main():
    rnd = random.Random(1031)
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        draw_pumpkin(c)

        opened = [p for fo, p in SCHEDULE if fo <= f]
        lit = f >= LIGHT_START
        level = LEVELS[f] if f >= LIGHT_START + 2 and f not in STEADY else 1
        winking = f in WINK

        for p in opened:
            if not lit:
                col = C.BLACK
            elif f == LIGHT_START:
                # the grin catches first; the eyes are still dark
                if p[1] < 11:
                    col = C.BLACK
                else:
                    col = C.YELLOW if rnd.random() < 0.55 else C.RED
            elif f == LIGHT_START + 1:
                col = C.YELLOW if rnd.random() < 0.6 else C.RED
            else:
                col = flame_color(rnd, level)
            if winking and p in RIGHT_EYE_SET:
                # lid shut: flesh over the eye, a glowing slit along the bottom
                stage = WINK[f]
                if stage == 2 and p[1] < 8:
                    col = C.RED
                elif stage == 1 and p[1] < 7:
                    col = C.RED
                elif stage == 2:
                    col = C.YELLOW
            c.pixel(*p, col)

        # the knife
        if f == KNIFE_IN:
            draw_knife(c, (24, 2), f)
        elif CARVE_START <= f < KNIFE_OUT:
            tip = [p for fo, p in SCHEDULE if fo == f][-1]
            draw_knife(c, tip, f)
        elif f == KNIFE_OUT:
            draw_knife(c, (27, 1), f)

        # the match
        if MATCH_START <= f < LIGHT_START:
            mx, my = {18: (32, 9), 19: (32, 9), 20: (32, 8), 21: (28, 9)}.get(f, (22, 12))
            c.vline(mx, my + 1, 5, C.YELLOW)          # stick
            c.pixel(mx, my, C.RED)                    # head
            if f == 19:
                for dx, dy in ((-2, -2), (2, -2), (0, -3), (-2, 1), (2, 1), (3, -1), (-3, -1)):
                    c.pixel(mx + dx, my + dy, C.WHITE)
                c.pixel(mx, my, C.WHITE)
            elif f >= 20:
                c.pixel(mx, my - 1, C.YELLOW)
                c.pixel(mx, my - 2, C.WHITE if f % 2 else C.YELLOW)
                c.pixel(mx - 1 + (f % 2), my - 1, C.RED)
                c.pixel(mx, my, C.YELLOW)

        if f >= HAPPY_START:
            draw_text(c, f, rnd, level)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/jack_o_lantern.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
