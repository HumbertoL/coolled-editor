#!/usr/bin/env python3
"""
Thanos Snap (2018) -- perfectly balanced, as all things should be.

The Infinity Gauntlet waits at the left, six stones glinting in turn, facing
a line of eight little heroes in their own colours. Fingers snap: a burst at
the fingertips and the whole panel whites out for a frame. Then four of the
eight -- only half, chosen as cold as the original -- come apart. Each pixel
lets go on its own schedule, left side first, and drifts up and to the right
as ash that cools as it goes, yellow to red to magenta to blue to nothing.
The survivors stand in the gaps. The verdict: PERFECTLY, then BALANCED.
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
SEED = 2018

# Glove pixels: '#' gold, letters are stones.
GAUNTLET_UP = [
    "....#.#....",
    "..#.#.#.#..",
    "..#.#.#.#..",
    "..#.#.#.#..",
    ".#R#B#M#G#.",
    "##########.",
    ".####W####.",
    "..##SS####.",
    "..#######..",
    "...#####...",
    "...#####...",
    "..#######..",
    "..#.#.#.#..",
    "..#######..",
]
# Fingers curled down, thumb up -- the instant after the snap.
GAUNTLET_SNAP = [
    "...........",
    "...........",
    ".#.........",
    ".##........",
    ".#R#B#M#G#.",
    "##########.",
    ".####W####.",
    "..##SS####.",
    "..#######..",
    "...#####...",
    "...#####...",
    "..#######..",
    "..#.#.#.#..",
    "..#######..",
]
STONES = {"R": C.RED, "B": C.BLUE, "M": C.MAGENTA, "G": C.GREEN, "W": C.WHITE, "S": C.CYAN}
GX, GY = 1, 2

HERO = [
    ".###.",
    ".###.",
    "..#..",
    "#####",
    "..#..",
    ".#.#.",
    "#...#",
]
HERO_COLORS = [C.RED, C.BLUE, C.GREEN, C.YELLOW, C.MAGENTA, C.CYAN, C.WHITE, C.RED]
HERO_X0, HERO_PITCH, HERO_Y = 17, 10, 9
DOOMED = {1: 11, 2: 17, 4: 14, 7: 20}   # hero index -> frame their dusting begins
PEEL_SPAN = 9                            # frames over which a hero comes apart

SNAP_AT, FLASH_AT = 7, 8
WORDS = [(34, "PERFECTLY"), (44, "BALANCED.")]
# Ash cools as it drifts. The first two frames keep the hero's own colour.
ASH = [None, None, C.YELLOW, C.YELLOW, C.RED, C.RED, C.MAGENTA, C.MAGENTA, C.BLUE, C.BLUE]


def hero_pixels(index):
    x0 = HERO_X0 + index * HERO_PITCH
    return [
        (x0 + c, HERO_Y + r)
        for r, line in enumerate(HERO)
        for c, ch in enumerate(line)
        if ch == "#"
    ]


def make_dust(rng):
    """Every doomed pixel's release time, drift and lifetime, fixed up front."""
    dust = []
    for index, start in DOOMED.items():
        x0 = HERO_X0 + index * HERO_PITCH
        for x, y in hero_pixels(index):
            # Left side lets go first, top a touch before bottom, with noise.
            bias = (x - x0) / 4 * 0.7 + (y - HERO_Y) / 6 * 0.3
            release = start + round(bias * (PEEL_SPAN - 3) + rng.uniform(0, 3))
            dust.append({
                "hero": index,
                "home": (x, y),
                "release": release,
                "vx": rng.uniform(0.7, 1.7),
                "vy": rng.uniform(-0.35, -0.05),
                "lift": rng.uniform(0.01, 0.03),
                "phase": rng.uniform(0, math.tau),
                "life": rng.randint(12, 18),
            })
    return dust


def draw_sprite(frame, rows, x0, y0, color_of):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                frame.pixel(x0 + c, y0 + r, color_of(ch))


def build():
    rng = random.Random(SEED)
    dust = make_dust(rng)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index == FLASH_AT:
            frame.fill(C.WHITE)
            draw_sprite(frame, GAUNTLET_SNAP, GX, GY, lambda ch: C.YELLOW)
            continue

        # The gauntlet, stones taking turns to glint before the snap.
        pose = GAUNTLET_SNAP if index >= SNAP_AT else GAUNTLET_UP
        glint = "RBMGWS"[index % 6] if index < SNAP_AT else None

        def glove(ch):
            if ch == "#":
                return C.YELLOW
            return C.WHITE if ch == glint else STONES[ch]

        draw_sprite(frame, pose, GX, GY, glove)
        if index == SNAP_AT:
            cx, cy = GX + 1, GY + 1
            for dx, dy in ((-1, -1), (1, -1), (2, 0), (0, -2), (3, -1), (-1, 1)):
                frame.pixel(cx + dx, cy + dy, C.WHITE)
        wave = index - FLASH_AT - 1
        if 0 <= wave < 3:
            # The snap ripples out across the line of heroes.
            front = 16 + wave * 28
            for y in range(16):
                bend = round(abs(y - 8) ** 2 / 16)
                frame.pixel(front - bend, y, C.CYAN)
                frame.pixel(front - bend - 2, y, C.BLUE if y % 2 else C.BLACK)

        # The doomed: whole until each pixel's release, then ash.
        for grain in dust:
            age = index - grain["release"]
            if age < 0:
                x, y = grain["home"]
                # Just before letting go, a pixel flickers pale.
                near = age >= -1 and index >= DOOMED[grain["hero"]]
                frame.pixel(x, y, C.WHITE if near else HERO_COLORS[grain["hero"]])
                continue
            if age >= grain["life"]:
                continue
            hx, hy = grain["home"]
            x = hx + grain["vx"] * age + 0.8 * math.sin(grain["phase"] + age * 0.7)
            y = hy + grain["vy"] * age - grain["lift"] * age * age + 0.5 * math.cos(grain["phase"] + age * 0.9)
            shade = ASH[min(len(ASH) - 1, age * len(ASH) // grain["life"])] or HERO_COLORS[grain["hero"]]
            frame.pixel(round(x), round(y), shade)
        # Survivors drawn last, so the ash of the fallen passes behind them.
        for hero, color in enumerate(HERO_COLORS):
            if hero not in DOOMED:
                for x, y in hero_pixels(hero):
                    frame.pixel(x, y, color)

        for at, word in WORDS:
            if at <= index < at + 10:
                k = index - at
                color = C.WHITE if k == 0 else C.MAGENTA
                frame.text(word, 14 + (82 - frame.text_width(word, proportional=True)) // 2, 0, color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/thanos_snap.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
