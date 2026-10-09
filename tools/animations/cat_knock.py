#!/usr/bin/env python3
"""
Cat knock -- eye contact, then the mug goes over the edge.

A ginger cat sits on a red table beside a white mug of coffee, steam curling
up from it. It eyes the mug, then turns and stares straight out of the panel
with huge green eyes, and without once looking away pushes the mug toward
the edge with one paw, a pixel at a time. A long beat with the mug on the
very lip of the table. One more nudge: it tips, tumbles, and smashes on the
floor -- CRASH!, shards skittering, coffee spreading. Zero remorse: the cat
keeps staring, blinks slowly, glances at the pen that has been lying at the
other end of the table all along, looks back at you, and starts pushing that
toward the edge too.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 7

CAT = [
    ".#.......#.",
    ".##.....##.",
    ".#########.",
    "###########",
    "###########",
    ".#########.",
    "..#######..",
    ".#########.",
    ".#########.",
]
FUR = C.YELLOW
TABLE_X0, TABLE_X1, TABLE_Y = 30, 62, 9
MUG_W = 4

# Mug x by frame during the push: a pixel at a time, with little pauses.
PUSH_START = 11
PUSH = [54, 54, 55, 55, 55, 56, 56, 57, 57, 57, 58, 58, 59, 59]
HOLD_END = 31            # first frame after the held beat at the edge
IMPACT = 35
BLINK = {43: "half", 44: "shut", 45: "shut", 46: "half"}
GLANCE = 47              # eyes flick to the pen, then back to you
# The pen at the left end of the table: x by frame (its left end), and where
# the reaching paw ends. It sits at PEN_X until the cat goes for it.
PEN_X = 32
PEN_PUSH = {48: (32, 36), 49: (31, 35), 50: (31, 35), 51: (30, 34), 52: (29, 33)}
SHIFT = -14              # scene is drawn at x 27..90, then slid left


def draw_cat(frame, cx, eyes, paw_to=None, paw_left=None, tail=0):
    for r, line in enumerate(CAT):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(cx + c, r, FUR)
    # Tail curling up the left side; the tip flicks.
    for x, y in ((cx, 8), (cx - 1, 8), (cx - 2, 7), (cx - 2, 6)):
        frame.pixel(x, y, FUR)
    frame.pixel(cx - 2 + tail, 5, FUR)
    frame.pixel(cx + 5, 5, C.MAGENTA)                       # nose
    # Eyes: (cells, pupils) relative to the head.
    left, right = (1, 2, 3), (7, 8, 9)
    if eyes == "side":
        for cols in (left, right):
            for c in cols:
                for r in (3, 4):
                    frame.pixel(cx + c, r, C.GREEN)
            frame.pixel(cx + cols[2], 3, C.BLACK)
            frame.pixel(cx + cols[2], 4, C.BLACK)
    elif eyes == "front":
        for cols in (left, right):
            for c in cols:
                for r in (3, 4):
                    frame.pixel(cx + c, r, C.GREEN)
            frame.pixel(cx + cols[1], 3, C.BLACK)
            frame.pixel(cx + cols[1], 4, C.BLACK)
    elif eyes == "big":
        for cols in (left, right):
            for c in cols:
                for r in (2, 3, 4):
                    frame.pixel(cx + c, r, C.GREEN)
            frame.pixel(cx + cols[1], 3, C.BLACK)
    elif eyes == "half":
        for cols in (left, right):
            for c in cols:
                frame.pixel(cx + c, 4, C.GREEN)
            frame.pixel(cx + cols[1], 4, C.BLACK)
    elif eyes == "left":
        for cols in (left, right):
            for c in cols:
                for r in (2, 3, 4):
                    frame.pixel(cx + c, r, C.GREEN)
            frame.pixel(cx + cols[0], 3, C.BLACK)
            frame.pixel(cx + cols[0], 4, C.BLACK)
    elif eyes == "shut":
        for cols in (left, right):
            for c in cols:
                frame.pixel(cx + c, 4, C.BLACK)
    if paw_to is not None:
        # One leg stretched along the table top toward the mug.
        start = cx + 10
        if paw_to >= start:
            frame.hline(start, 8, paw_to - start + 1, FUR)
            frame.pixel(paw_to, 8, C.WHITE)
    if paw_left is not None:
        # The other way: a leg along the table toward the pen.
        frame.hline(paw_left, 8, cx - paw_left, FUR)
        frame.pixel(paw_left, 8, C.WHITE)


def draw_pen(frame, x):
    # Lying on the table, cap to the right; past the edge it starts to tip.
    if x < TABLE_X0:
        frame.pixel(x, 9, C.MAGENTA)
        frame.hline(x + 1, 8, 2, C.MAGENTA)
        frame.pixel(x + 3, 8, C.WHITE)
    else:
        frame.hline(x, 8, 3, C.MAGENTA)
        frame.pixel(x + 3, 8, C.WHITE)


def draw_table(frame):
    frame.hline(TABLE_X0, TABLE_Y, TABLE_X1 - TABLE_X0 + 1, C.RED)
    for x in (TABLE_X0 + 1, TABLE_X1 - 1):
        frame.vline(x, TABLE_Y + 1, 15 - TABLE_Y, C.RED)


def draw_mug(frame, x, y, handle="right"):
    frame.rect(x, y, MUG_W, 4, C.WHITE, fill=True)
    if handle == "right":
        frame.pixel(x + MUG_W, y + 1, C.WHITE)
        frame.pixel(x + MUG_W, y + 2, C.WHITE)
        frame.hline(x + 1, y, 2, C.BLUE)                    # coffee
    elif handle == "down":
        frame.pixel(x + 1, y + 4, C.WHITE)
        frame.pixel(x + 2, y + 4, C.WHITE)
        frame.vline(x + MUG_W - 1, y + 1, 2, C.BLUE)
    elif handle == "left":
        frame.pixel(x - 1, y + 1, C.WHITE)
        frame.pixel(x - 1, y + 2, C.WHITE)


def draw_steam(frame, x, index):
    for k in range(3):
        y = 4 - ((index + k * 2) % 5)
        wobble = (index // 2 + k) % 2
        if 0 <= y <= 4:
            frame.pixel(x + 1 + wobble, y, C.WHITE if y > 2 else C.BLUE)


def build():
    rng = random.Random(SEED)
    # Shards: (vx, vy, color), launched from the impact point.
    shards = [
        (rng.uniform(-2.2, -0.6), rng.uniform(-2.6, -1.2), C.WHITE) for _ in range(4)
    ] + [
        (rng.uniform(0.6, 3.0), rng.uniform(-2.8, -1.0), C.WHITE) for _ in range(5)
    ] + [
        (rng.uniform(-1.5, 2.0), rng.uniform(-3.0, -1.8), C.BLUE) for _ in range(5)
    ]
    impact_x, impact_y = 67, 14

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        text_layer = frame
        frame = Canvas(anim.width, anim.height)
        draw_table(frame)

        # Where the mug is and where the cat sits.
        if index < PUSH_START:
            mx = PUSH[0]
        elif index < PUSH_START + len(PUSH):
            mx = PUSH[index - PUSH_START]
        else:
            mx = PUSH[-1]
        cx = 41 if mx < 56 else 42 if mx < 58 else 43

        eyes = "side" if index < 6 else "front" if index == 6 else "big"
        if index in BLINK:
            eyes = BLINK[index]
        if index == GLANCE:
            eyes = "left"
        paw = None
        if PUSH_START <= index <= HOLD_END:
            paw = mx - 1 if index < HOLD_END else mx
        pen_x, paw_left = PEN_PUSH.get(index, (PEN_X, None))
        tail = 1 if (index // 3) % 4 == 0 else 0
        draw_pen(frame, pen_x)
        draw_cat(frame, cx, eyes, paw, paw_left, tail)

        # The mug.
        if index < HOLD_END:
            draw_mug(frame, mx, 5)
            draw_steam(frame, mx, index)
        elif index < IMPACT:
            k = index - HOLD_END                     # 0..3
            path = [(60, 5, "right"), (62, 7, "down"), (64, 9, "left"), (66, 11, "down")]
            x, y, handle = path[k]
            draw_mug(frame, x, y, handle)
            if k == 0:
                frame.pixel(60, 3, C.WHITE)          # coffee sloshing out
        else:
            t = index - IMPACT
            if t == 0:
                # The smash: a white starburst on the floor.
                for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (-2, -1), (2, -1),
                               (-3, 0), (3, 0), (0, -2), (-2, -3), (2, -3)):
                    frame.pixel(impact_x + dx, impact_y + dy, C.WHITE)
                frame.pixel(impact_x, impact_y + 1, C.YELLOW)
            # Coffee puddle spreading along the floor.
            spread = min(2 + t, 9)
            frame.hline(impact_x - spread // 2, 15, spread, C.BLUE)
            # Shards on ballistic arcs, settling on the floor.
            for vx, vy, color in shards:
                tt = min(t, 6) * 0.9
                x = impact_x + vx * tt
                y = impact_y + vy * tt + 0.45 * tt * tt
                if y >= 15 or t >= 6:
                    y = 15 if color == C.BLUE else 14
                    if color == C.BLUE:
                        continue
                frame.pixel(round(x), round(y), color)
            if t <= 3:
                text_layer.text("CRASH!", 60 - (t == 0), 1 + (t == 0),
                                C.RED if t % 2 else C.YELLOW)

        text_layer.blit(frame, SHIFT)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cat_knock.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
