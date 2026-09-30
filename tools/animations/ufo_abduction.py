#!/usr/bin/env python3
"""
UFO Abduction -- a saucer, a cow, and a very tidy tractor beam.

A saucer glides in over a night field, switches on a cyan beam and lifts a
white-with-black-patches cow, which turns slowly as it rises through the
sparkles. The cow slips inside, the saucer gives a happy little BURP, and it
zips off to the right, leaving a streak. The next loop starts with a fresh cow.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 100
SEED = 51

PALETTE = {"W": C.WHITE, "K": C.BLACK, "P": C.MAGENTA, "Y": C.YELLOW}

COW_SIDE = [
    "......Y.Y",
    "WWWWWWWWW",
    "WKKWWWKWW",
    "WKKWWWWWP",
    "WWWWKKWPP",
    ".W.W.W.W.",
]
COW_FRONT = [
    "Y...Y",
    "WWWWW",
    "WKWKW",
    "KKWWW",
    "WWPWW",
    ".W.W.",
]
COW_BACK = [
    ".WWW.",
    "WWKKW",
    "WKKWW",
    "WWWWW",
    "WWKWW",
    ".W.W.",
]


def mirrored(sprite):
    return [row[::-1] for row in sprite]


# Slow turn: right, three-quarter (front), left, back.
TURN = [COW_SIDE, COW_FRONT, mirrored(COW_SIDE), COW_BACK]

SAUCER_X = 32
HOVER_Y = 1
COW_X = 36
COW_GROUND_Y = 8


def draw_sprite(frame, sprite, x, y, min_y=0, flash=False):
    for r, row in enumerate(sprite):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            if y + r < min_y:
                continue
            color = PALETTE[ch]
            if ch == "K":
                color = C.BLACK
            frame.pixel(x + c, y + r, color)


def saucer(frame, x, y, lights, glow=False):
    # dome
    frame.hline(x + 5, y, 6, C.CYAN)
    frame.hline(x + 4, y + 1, 8, C.CYAN)
    frame.pixel(x + 6, y, C.WHITE)
    # disk
    frame.hline(x + 1, y + 2, 14, C.WHITE if not glow else C.YELLOW)
    frame.hline(x, y + 3, 16, C.BLUE)
    for i in range(1, 16, 3):
        on = (i // 3 + lights) % 2 == 0
        frame.pixel(x + i, y + 3, C.YELLOW if on else C.MAGENTA)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    stars = [(rng.randrange(0, 96), rng.randrange(0, 12), rng.randrange(0, 4)) for _ in range(14)]
    sparkles = {}
    for t in range(FRAMES):
        sparkles[t] = [
            (rng.randrange(-3, 4), rng.randrange(0, 10)) for _ in range(4)
        ]

    fly_in = [-16, -8, 0, 8, 16, 24, 29, 32]
    zip_x = [32, 33, 40, 56, 78, 104]
    for t in range(FRAMES):
        f = anim.frame()
        # night sky and field
        for (sx, sy, ph) in stars:
            if (t // 3 + ph) % 4:
                f.pixel(sx, sy, C.BLUE if ph % 2 else C.WHITE)
        f.pixel(88, 2, C.YELLOW)
        f.pixel(89, 2, C.YELLOW)
        f.pixel(88, 3, C.YELLOW)
        f.hline(0, 14, 96, C.GREEN)
        f.hline(0, 15, 96, C.GREEN)
        for x in range(0, 96, 5):
            f.pixel(x + (t // 24) * 0, 15, C.BLUE)

        # phases
        sx, sy = SAUCER_X, HOVER_Y
        beam = False
        beam_full = False
        cow_y = COW_GROUND_Y
        cow_visible = True
        cow_state = 0
        flash = False
        burp = False
        streak = 0
        if t < 8:
            sx = fly_in[t]
        elif t < 12:
            beam = (t % 2 == 0) or t >= 11
            beam_full = t >= 11
            sy = HOVER_Y + (t % 2)
        elif t < 34:
            beam = beam_full = True
            k = t - 12
            cow_y = COW_GROUND_Y - round(k * 10 / 21)
            cow_state = (k // 5) % 4
            sy = HOVER_Y + (t // 2) % 2
        elif t < 36:
            flash = True
            cow_visible = False
        elif t < 42:
            cow_visible = False
            burp = True
            k = t - 36
            sy = HOVER_Y + (0, 1, 1, 0, 0, 0)[k]
        else:
            cow_visible = False
            sx = zip_x[t - 42]
            streak = t - 41

        if t >= 34:
            cow_visible = False
        if t < 34 and beam:
            top_w, bot_w = 3, 8
            for y in range(sy + 4, 14):
                frac = (y - (sy + 4)) / 9
                half = round(top_w + (bot_w - top_w) * frac)
                cx = sx + 8
                if not beam_full and (t % 2):
                    half = max(1, half - 2)
                for x in range(cx - half, cx + half):
                    f.pixel(x, y, C.BLUE)
                f.pixel(cx - half, y, C.CYAN)
                f.pixel(cx + half - 1, y, C.CYAN)
                # scrolling dashes up the beam
                if (y + t) % 3 == 0:
                    f.pixel(cx - half + 2, y, C.CYAN)
                    f.pixel(cx + half - 3, y, C.CYAN)
        if cow_visible:
            sprite = TURN[cow_state]
            w = len(sprite[0])
            draw_sprite(f, sprite, sx + 8 - w // 2 if t >= 12 else COW_X, cow_y, min_y=sy + 4)
        if beam_full and t < 34:
            for (dx, dy) in sparkles[t]:
                x, y = sx + 8 + dx, 5 + dy
                f.pixel(x, y, C.WHITE)
        if flash:
            f.hline(sx + 2, sy + 4, 12, C.WHITE)
            f.pixel(sx + 8, sy + 5, C.WHITE)
        if streak:
            for i in range(3):
                y = sy + 1 + i
                length = 6 + 6 * streak
                for d in range(length):
                    if (d + i) % 2 == 0 or d < 3:
                        f.pixel(sx - 1 - d, y, C.WHITE if d < 3 else (C.CYAN if d < 10 else C.BLUE))
        saucer(f, sx, sy, t, glow=flash or burp)
        if burp:
            k = t - 36
            f.small_text("BURP", 52, 2, C.YELLOW if k % 2 == 0 else C.WHITE)
            for i in range(min(k, 3) + 1):
                f.pixel(sx + 17 + i, sy + 3 - (i % 2), C.GREEN)
            f.pixel(sx + 17, sy + 2, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/ufo_abduction.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
