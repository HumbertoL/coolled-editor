#!/usr/bin/env python3
"""
Campfire -- a night camp with one good fire.

Flames of red, yellow and a white-hot core lick up from a stack of crossed
logs, their heights a sum of seeded sine waves so the flicker never repeats
inside the loop yet wraps perfectly. Sparks drift up and out. A crescent moon
hangs over a tent silhouette, stars twinkle, and on the right a marshmallow
on a stick slowly turns from white to gold as it roasts.
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
SEED = 7
FIRE_X = 50
GROUND = 15


def build():
    rng = random.Random(SEED)
    # flame columns: each gets three seeded sines with integer cycles per loop
    waves = {
        dx: [(rng.randint(1, 4), rng.uniform(0, 6.28), rng.uniform(0.5, 1.1)) for _ in range(3)]
        for dx in range(-5, 6)
    }
    stars = [(rng.randint(0, 95), rng.randint(0, 6)) for _ in range(16)]
    stars = [(x, y) for x, y in stars if not (x < 30 and y > 5) and not (38 <= x <= 46 and y < 9)]
    star_phase = [rng.randrange(FRAMES) for _ in stars]
    sparks = []
    for _ in range(9):
        sparks.append({
            "start": rng.randrange(FRAMES),
            "life": rng.randint(18, 30),
            "x": FIRE_X + rng.randint(-3, 3),
            "drift": rng.uniform(-0.25, 0.3),
            "wob": rng.uniform(0, 6.28),
        })

    def flame_height(dx, t):
        base = 11.5 - abs(dx) * 2.0
        n = sum(a * math.sin(2 * math.pi * (k * t / FRAMES) + ph) for k, ph, a in waves[dx])
        return max(0, base + n * 1.9)

    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        # stars
        for (x, y), ph in zip(stars, star_phase):
            v = (i + ph) % 12
            f.pixel(x, y, C.WHITE if v < 2 else (C.CYAN if v < 6 else C.BLUE))
        # moon (crescent), facing left
        mx, my = 41, 1
        for r, row in enumerate([".WWW.", "WWW..", "WW...", "WW...", "WWW..", ".WWW."]):
            for c, ch in enumerate(row):
                if ch == "W":
                    f.pixel(mx + c, my + r, C.YELLOW)
        # tent: a magenta-edged triangle with a dark doorway
        for r in range(9):
            y = 6 + r
            half = 1 + r
            f.hline(14 - half, y, 2 * half + 1, C.BLUE)
            f.pixel(14 - half, y, C.MAGENTA)
            f.pixel(14 + half, y, C.MAGENTA)
        f.vline(14, 6, 1, C.WHITE)
        f.hline(10, GROUND, 9, C.BLUE)
        for r in range(4):
            f.hline(14 - r // 2 - 1 + 0, 12 + r - 1, 2 + r // 2 * 0 + 1, C.BLACK)
        f.rect(13, 11, 3, 5, C.BLACK, fill=True)
        # ground
        f.hline(0, GROUND, 96, C.GREEN)
        # flames, back to front: red outside, yellow mid, white core
        for dx in range(-5, 6):
            h = int(round(flame_height(dx, i)))
            for layer, color, cut in ((0, C.RED, 0), (1, C.YELLOW, 3), (2, C.WHITE, 6)):
                lh = h - cut - abs(dx) // (3 - layer if layer < 2 else 1) * 0
                if layer == 1 and abs(dx) > 3:
                    continue
                if layer == 2 and abs(dx) > 1:
                    continue
                for k in range(max(0, lh)):
                    f.pixel(FIRE_X + dx, 13 - k, color)
        # logs
        f.line(FIRE_X - 7, 14, FIRE_X + 5, 12, C.RED)
        f.line(FIRE_X - 7, 12, FIRE_X + 7, 14, C.RED)
        f.pixel(FIRE_X - 7, 14, C.YELLOW)
        f.pixel(FIRE_X + 7, 14, C.YELLOW)
        f.pixel(FIRE_X - 7, 12, C.YELLOW)
        f.pixel(FIRE_X + 5, 12, C.YELLOW)
        # sparks
        for s in sparks:
            age = (i - s["start"]) % FRAMES
            if age < s["life"]:
                y = 8 - age * 0.45
                x = s["x"] + s["drift"] * age + math.sin(age * 0.6 + s["wob"])
                col = C.YELLOW if age < s["life"] * 0.5 else C.RED
                f.pixel(round(x), round(y), col)
        # marshmallow on a stick
        sway = round(math.sin(2 * math.pi * i / FRAMES))
        tipx, tipy = 60 + sway, 10
        f.line(tipx + 2, tipy + 1, 84, 15, C.RED)
        toast = 0.5 + 0.5 * math.sin(2 * math.pi * i / FRAMES - 1.2)
        mm = C.WHITE if toast < 0.5 else C.YELLOW
        f.rect(tipx - 1, tipy - 1, 3, 3, mm, fill=True)
        if toast > 0.9:
            f.pixel(tipx - 1, tipy, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/campfire.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
