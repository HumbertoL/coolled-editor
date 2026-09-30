#!/usr/bin/env python3
"""
Rubber Duck -- bath time, with a swell.

A yellow rubber duck bobs on cyan and blue waves, tilting nose-up and nose-down
as each swell passes under it. Bubbles rise through the water and pop above it,
a little foam pile sits on the right, the duck blinks and gives a SQUEAK, and
in the last stretch the bubbles multiply into a proper bubble bath.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100
SEED = 33
SWELLS = 2            # wave cycles that pass per loop
PERIOD = 26           # pixels per wave
BASE = 11.0
AMP = 1.2
DUCK_CX = 45

DUCK = [
    "......YYY..",
    ".....YYYYY.",
    ".....YKYYRR",
    ".....YYYYR.",
    "Y...YYYYY..",
    "YYYYYYYYYY.",
    ".YYYYYYYYY.",
    "..YYYYYYY..",
]


def surface(x, t):
    return BASE + AMP * math.sin(2 * math.pi * (x / PERIOD - SWELLS * t / FRAMES))


def draw_duck(f, t, blink):
    cy = surface(DUCK_CX, t)
    slope = (surface(DUCK_CX + 4, t) - surface(DUCK_CX - 4, t)) / 8
    top = round(cy) - 6
    left = DUCK_CX - 5
    for r, row in enumerate(DUCK):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            shear = -round(slope * (c - 5) * 0.9)
            color = {"Y": C.YELLOW, "R": C.RED, "K": C.BLACK}[ch]
            if ch == "K" and blink:
                color = C.YELLOW
            f.pixel(left + c, top + r + shear, color)
    # a bright highlight on the back
    f.pixel(left + 5, top + 4, C.WHITE)


def draw_water(f, t):
    for x in range(96):
        s = surface(x, t)
        top = round(s)
        f.pixel(x, top, C.CYAN)
        for y in range(top + 1, 16):
            f.pixel(x, y, C.BLUE)
        # sparkle of cyan lines drifting through the deep water
        if (x + 2 * (t // 2) + (top % 3)) % 9 == 0:
            f.pixel(x, min(15, top + 2), C.CYAN)
        # foam on the crests
        if s < BASE - AMP + 0.35:
            f.pixel(x, top, C.WHITE)


def make_bubbles(rng):
    bubbles = []
    # (birth frame, x, rise speed, size) -- births cluster late for the bath
    births = [3, 9, 15, 20, 26, 29, 31, 33, 35, 36, 38, 39, 40, 42, 43, 44, 45, 46]
    for b in births:
        x = rng.choice([rng.randint(6, 34), rng.randint(56, 78), rng.randint(36, 56)])
        bubbles.append((b, x, rng.choice([0.5, 0.6, 0.7]), rng.choice([1, 1, 2])))
    return bubbles


def draw_bubbles(f, t, bubbles):
    for (birth, x, speed, size) in bubbles:
        age = (t - birth) % FRAMES
        y = 15 - speed * age
        sx = x + round(math.sin(age * 0.7 + x) * 1.0)
        surf = surface(sx, t)
        if y > surf + 1:
            f.pixel(sx, round(y), C.WHITE if age % 4 else C.CYAN)
        elif y > surf - 5:
            ay = round(y)
            if size == 2:
                f.pixel(sx, ay, C.CYAN)
                f.pixel(sx + 1, ay, C.WHITE)
                f.pixel(sx, ay + 1, C.WHITE)
                f.pixel(sx + 1, ay + 1, C.CYAN)
            else:
                f.pixel(sx, ay, C.WHITE)
        elif y > surf - 6.2:
            ay = round(y)
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                f.pixel(sx + dx, ay + dy, C.WHITE)


def draw_foam(f, t):
    grow = 0
    if t >= 28:
        grow = min(2, (t - 28) // 6)
    cx = 88
    s = surface(cx, t)
    base = round(s) + 1
    blobs = [(-2, 0, 2), (2, 0, 2), (0, -1, 2)]
    if grow >= 1:
        blobs += [(0, -3, 2), (-4, 0, 1)]
    if grow >= 2:
        blobs += [(3, -3, 1), (-3, -3, 2), (5, 0, 1)]
    for (dx, dy, r) in blobs:
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + 1:
                    px, py = cx + dx + x, base + dy + y
                    if py <= base:
                        f.pixel(px, py, C.WHITE if (x + y) % 3 else C.CYAN)


def build():
    rng = random.Random(SEED)
    bubbles = make_bubbles(rng)
    anim = Animation(delay=DELAY)
    for t in range(FRAMES):
        f = anim.frame()
        blink = t in (20, 21, 22)
        draw_duck(f, t, blink)
        draw_water(f, t)
        draw_foam(f, t)
        draw_bubbles(f, t, bubbles)
        if 21 <= t <= 26:
            rise = (t - 21) // 3
            f.small_text("SQUEAK", 14, 3 - rise, C.YELLOW if t % 2 else C.WHITE)
            f.pixel(36, 4 - rise, C.YELLOW)
            f.pixel(37, 2 - rise, C.YELLOW)
        if blink and 21 <= t:
            pass
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rubber_duck.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
