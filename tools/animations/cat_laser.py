#!/usr/bin/env python3
"""
Cat Laser -- a red dot, and one cat with no self-control.

A ginger cat sits at the left edge of the panel, head and pupils tracking a
red laser dot that darts around on quick, jittery seeded paths while its tail
twitches. The dot parks on the floor, the cat wiggles, pounces across the
panel and lands on nothing: the dot has vanished. The cat trots home and looks
around as if none of that happened.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SEED = 7

FLOOR = 15
CAT_X = 2
PARK = (34, 14)          # where the dot stops before the pounce
CHASE_END = 33
WIGGLE_END = 38
POUNCE = {38: (6, -3), 39: (14, -5), 40: (22, -2), 41: (28, 0)}  # cat dx, dy
LAND_END = 45
TROT_END = 48


def dot_path(rng):
    """One dot position per frame for the chase, in quick jittery hops."""
    pos = []
    x, y = 40.0, 6.0
    frame = 0
    while len(pos) < CHASE_END:
        tx, ty = rng.randint(26, 92), rng.randint(1, 13)
        hops = rng.randint(2, 4)
        hold = rng.randint(1, 2)
        for h in range(hops):
            x += (tx - x) / (hops - h)
            y += (ty - y) / (hops - h)
            for _ in range(hold):
                jx, jy = rng.randint(-1, 1), rng.randint(-1, 1)
                pos.append((round(x) + jx, max(0, min(FLOOR - 1, round(y) + jy))))
    pos = pos[:CHASE_END]
    # park it on the floor for the last few frames of the chase
    pos[-3:] = [(PARK[0] + 3, PARK[1] - 2), (PARK[0] + 1, PARK[1] - 1), PARK]
    return pos


def draw_cat(f, ox, oy, pose, hx, hy, pdx, pdy, tail, blink=False, question=False):
    Y, W = C.YELLOW, C.WHITE
    x0, y0 = CAT_X + ox, oy
    if pose == "air":
        # stretched out mid-pounce, facing right
        f.rect(x0 + 2, y0 + 7, 11, 4, Y, fill=True)
        f.hline(x0 + 13, y0 + 8, 3, Y)                   # front legs reaching
        f.pixel(x0 + 16, y0 + 8, W)
        f.hline(x0 + 13, y0 + 10, 2, Y)
        f.pixel(x0 + 15, y0 + 10, W)
        f.hline(x0 - 1, y0 + 9, 3, Y)                    # hind legs
        f.pixel(x0 - 2, y0 + 10, Y)
        f.pixel(x0 + 1, y0 + 6, Y)                       # tail up
        f.pixel(x0, y0 + 5, Y)
        hx0, hy0 = x0 + 12, y0 + 3
        head(f, hx0, hy0, 1, 0, blink)
        return
    if pose == "land":
        f.rect(x0 + 2, y0 + 9, 8, 4, Y, fill=True)
        f.hline(x0 + 10, y0 + 12, 4, Y)
        f.pixel(x0 + 14, y0 + 12, W)
        f.hline(x0, y0 + 11, 3, Y)
        f.pixel(x0 + 1, y0 + 8, Y)
        f.pixel(x0, y0 + 7, Y)
        hx0, hy0 = x0 + 8, y0 + 5
        head(f, hx0, hy0, pdx, pdy, blink)
        if question:
            f.text("?", x0 + 9, 0, C.WHITE, proportional=True)
        return
    crouch = 1 if pose == "crouch" else 0
    # body and haunch
    f.hline(x0 + 4, y0 + 8 + crouch, 5, Y)
    f.hline(x0 + 3, y0 + 9 + crouch, 7, Y)
    f.rect(x0 + 2, y0 + 10 + crouch, 8, 4 - crouch, Y, fill=True)
    f.hline(x0 + 2, y0 + 14, 10, Y)                      # paws
    f.pixel(x0 + 11, y0 + 14, W)
    f.pixel(x0 + 10, y0 + 11 + crouch, W)                # chest
    f.pixel(x0 + 10, y0 + 12 + crouch, W)
    f.pixel(x0 + 9, y0 + 12 + crouch, W)
    # tail
    tails = {
        0: [(1, 14), (0, 13), (0, 12), (0, 11), (0, 10)],
        1: [(1, 14), (0, 13), (0, 12), (1, 11), (1, 10)],
        2: [(1, 14), (1, 13), (0, 13), (0, 12), (-1, 11)],
    }
    for (tx, ty) in tails[tail]:
        f.pixel(x0 + tx, y0 + ty + (1 if crouch else 0) * 0, Y)
    head(f, x0 + 6 + hx, y0 + 3 + hy + crouch, pdx, pdy, blink)


def head(f, x, y, pdx, pdy, blink):
    Y, W = C.YELLOW, C.WHITE
    f.rect(x, y, 8, 6, Y, fill=True)
    f.pixel(x, y - 1, Y)          # ears
    f.pixel(x + 1, y - 1, Y)
    f.pixel(x + 6, y - 1, Y)
    f.pixel(x + 7, y - 1, Y)
    f.pixel(x + 1, y, C.MAGENTA)  # inner ear tint
    f.pixel(x + 6, y, C.MAGENTA)
    for ex in (x + 2, x + 5):
        if blink:
            f.hline(ex, y + 2, 2, C.BLACK)
            continue
        f.rect(ex, y + 1, 2, 2, C.GREEN, fill=True)
        f.pixel(ex + pdx, y + 1 + pdy, C.BLACK)
    f.pixel(x + 4, y + 4, C.MAGENTA)   # nose
    f.pixel(x + 3, y + 5, W)           # muzzle
    f.pixel(x + 5, y + 5, W)


def build():
    rng = random.Random(SEED)
    dots = dot_path(rng)
    tail_rng = random.Random(SEED + 1)
    tails = [tail_rng.choice([0, 0, 1, 2]) for _ in range(FRAMES)]
    anim = Animation(delay=DELAY)
    for t in range(FRAMES):
        f = anim.frame()
        f.hline(0, FLOOR, 96, C.BLUE)
        # a little baseboard mark so the floor reads
        for x in range(0, 96, 8):
            f.pixel(x, FLOOR, C.CYAN)

        dot = None
        ox = oy = 0
        pose = "sit"
        hx = hy = 0
        pdx = pdy = 0
        blink = False
        tail = tails[t]
        question = False

        if t < CHASE_END:
            dot = dots[t]
        elif t < WIGGLE_END:
            dot = PARK
        if t < WIGGLE_END:
            # head and pupils follow the dot
            d = dot
            if t < 2:
                d = dots[2]
            pdx = 1 if d[0] > 46 else 0
            pdy = 0 if d[1] < 5 else 1
            if d[1] < 5:
                hy = -1
            elif d[1] > 10:
                hy = 1
            if d[0] > 70:
                hx = 1
            if t % 12 == 7:
                blink = True
        if CHASE_END <= t < WIGGLE_END:
            pose = "crouch"
            pdx, pdy = 1, 1
            hy = 0
            tail = 2 if t % 2 else 1
            ox = (t % 2)
        if t in POUNCE:
            pose = "air"
            ox, oy = POUNCE[t]
        elif t == 42 or t == 43:
            pose = "land"
            ox, oy = 28, 1
            pdx, pdy = 0, 1
            question = t == 43
        elif t == 44 or t == 45:
            pose = "land"
            ox, oy = 28, 1
            pdx, pdy = (-1, 0) if t == 44 else (0, -1)
            question = True
        if 46 <= t < TROT_END + 3:
            # trot home, tail-first innocence
            k = t - 46
            ox = (28, 18, 8, 0, 0)[min(k, 4)] if k < 5 else 0
            pose = "sit"
            pdx, pdy = 0, 0
        if t >= TROT_END + 3:
            k = t - (TROT_END + 3)      # 0..
            pose = "sit"
            look = [(0, -1), (0, -1), (1, -1), (0, 0), (-1, 0), (-1, 0), (0, 0)]
            pdx, pdy = look[min(k, len(look) - 1)]
            hy = -1 if pdy < 0 else 0
            tail = 0 if k % 3 else 1

        # dot vanishes with a pop at the moment the cat lands
        if t == 41:
            dot = PARK
        if t == 42:
            f.pixel(PARK[0], PARK[1], C.WHITE)   # last flash
            f.pixel(PARK[0] + 1, PARK[1] - 1, C.RED)

        draw_cat(f, ox, oy, pose, hx, hy, pdx, pdy, tail, blink, question)
        if dot and t < 42:
            f.pixel(dot[0], dot[1], C.RED)
            if t >= 1 and t < CHASE_END:
                px, py = dots[t - 1]
                if abs(px - dot[0]) + abs(py - dot[1]) > 3:
                    f.pixel((px + dot[0]) // 2, (py + dot[1]) // 2, C.MAGENTA)
        # dot reappears (out of reach) at the very end to make the loop
        if t == FRAMES - 1:
            f.pixel(dots[0][0], dots[0][1], C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cat_laser.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
