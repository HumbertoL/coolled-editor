#!/usr/bin/env python3
"""
Zoomies -- a dog, suddenly and for no reason, at full speed.

A yellow dog stands wagging in the middle of the panel. A "!" pops over its
head, and it is gone: dashing to the edge, skidding round in a spray of dust,
and back the other way, a little faster every lap. The ears flap, then stream
straight back; by the fourth lap it trails blue-and-cyan ghosts of itself and
ZOOMIES! strobes across the top. Then, as abruptly as it started, it skids
to a stop and flops flat on its belly, panting, tongue out, tail still going,
while little hearts float up off the top.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 2024
PALETTE = {"Y": C.YELLOW, "E": C.RED, "T": C.RED, "W": C.WHITE}

# Facing right. E is ear, T is tongue.
HEAD_AND_BODY = [
    "..........YYY..",
    "..........Y.YY.",
    "..........YYYYY",
    ".YYYYYYYYYYYT..",
    ".YYYYYYYYYY.T..",
    ".YYYYYYYYY.....",
]
LEGS = {
    "stride": ["Y........Y.....", "Y..........Y..."],
    "tuck": ["..Y.Y..Y.Y.....", "...Y....Y......"],
    "brace": [".Y.Y....Y.Y....", "Y...Y..Y...Y..."],
    "stand": [".Y.Y....Y.Y....", ".Y.Y....Y.Y...."],
}
EARS = {"down": [(9, 1), (9, 2), (9, 3)], "up": [(9, 0), (8, 0), (7, 0)]}
TAILS = {"up": [(0, 2), (0, 1)], "down": [(0, 4), (0, 5)], "back": [(0, 3), (-1, 3)]}
LYING = [
    "..........YYY..",
    "..........Y.YY.",
    ".YYYYYYYYYYYYYY",
    "YYYYYYYYYYYY.T.",
    "YYYYYYYYYYYYYY.",
]
DOG_W = 15
DOG_Y = 8
START_X = 40
BURST_AT = 5  # the "!" shows before this
STOP_AT = 41  # zoomies end here: last skid, then the flop
LAPS = [7, 10, 14, 18, 23]  # px per frame, one per lap
SKID_FRAMES = 2
X_MIN, X_MAX = 0, 96 - DOG_W
DUST = [C.WHITE, C.CYAN, C.WHITE, C.BLUE]
STROBE = [C.MAGENTA, C.CYAN, C.YELLOW, C.WHITE]


def dog_art(legs, ears, tail, tongue=True):
    grid = [list(row) for row in HEAD_AND_BODY + LEGS[legs]]
    if not tongue:
        for row in grid:
            for i, ch in enumerate(row):
                if ch == "T":
                    row[i] = "."
    for x, y in EARS[ears]:
        grid[y][x] = "E"
    pixels = {}
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in PALETTE:
                pixels[(x, y)] = PALETTE[ch]
    for x, y in TAILS[tail]:
        pixels[(x, y)] = C.YELLOW
    return pixels


def lying_art(tail, tongue):
    pixels = {}
    for y, row in enumerate(LYING):
        for x, ch in enumerate(row):
            if ch == "T" and not tongue:
                continue
            if ch in PALETTE:
                pixels[(x, y)] = PALETTE[ch]
    pixels[(9, 1)] = C.RED  # ear flopped down
    pixels[(9, 2)] = C.RED
    pixels[(-1, 2 if tail else 4)] = C.YELLOW
    pixels[(-2, 1 if tail else 4)] = C.YELLOW
    return pixels


def stamp(canvas, pixels, x, y, facing, color=None):
    for (px, py), c in pixels.items():
        sx = x + px if facing > 0 else x + DOG_W - 1 - px
        canvas.pixel(sx, y + py, color or c)


def plan():
    """Per frame: (x, facing, speed, state) for the zoomies stretch."""
    frames = []
    x, facing, lap = START_X, 1, 0
    index = BURST_AT
    while index < STOP_AT:
        speed = LAPS[min(lap, len(LAPS) - 1)]
        target = X_MAX if facing > 0 else X_MIN
        x = max(X_MIN, min(X_MAX, x + facing * speed))
        frames.append((x, facing, speed, "run"))
        index += 1
        if x == target:
            for _ in range(SKID_FRAMES):
                if index >= STOP_AT:
                    break
                frames.append((x, facing, speed, "skid"))
                index += 1
            facing = -facing
            lap += 1
    return frames


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    route = plan()
    dust = []  # [x, y, vx, vy, life]
    last = (START_X, 1)
    for index in range(FRAMES):
        frame = anim.frame()
        scene = Canvas()
        dx = dy = 0

        if index < BURST_AT:
            # Standing, wagging -- then the idea arrives.
            wag = "up" if index % 2 else "down"
            stamp(scene, dog_art("stand", "down", wag), START_X, DOG_Y, 1)
            if index >= 2:
                scene.text("!", START_X + 11, 0, C.WHITE, proportional=True)
        elif index < BURST_AT + len(route):
            x, facing, speed, state = route[index - BURST_AT]
            fast = speed >= 14
            if state == "run":
                if speed >= 10:
                    # Motion-blur ghosts where it just was.
                    for back, color in ((speed, C.BLUE), (speed // 2, C.CYAN)):
                        ghost = dog_art("stride", "up", "back")
                        stamp(scene, ghost, x - facing * back, DOG_Y, facing, color)
                legs = "stride" if index % 2 else "tuck"
                ears = "up" if fast or index % 2 else "down"
                stamp(scene, dog_art(legs, ears, "back"), x, DOG_Y, facing)
            else:
                # Skid at the wall: braced legs, dust kicked back the way it
                # came (ahead would be off the panel), and a jolt.
                stamp(scene, dog_art("brace", "down", "up"), x, DOG_Y, facing)
                feet = x + DOG_W // 2
                for _ in range(8 + speed // 2):
                    dust.append([feet + rng.randint(-6, 6), 15, -facing * rng.uniform(0.5, 3.0), -rng.uniform(0.5, 1.8), rng.randint(2, 5)])
                if speed >= 10:
                    dx, dy = rng.randint(-1, 1), rng.randint(0, 1)
            if fast:
                scene.text("ZOOMIES!", "center", 0, STROBE[index % len(STROBE)], proportional=True)
            last = (x, facing)
        else:
            # Flopped. Panting, tail going, a heart floats up.
            since = index - BURST_AT - len(route)
            x, facing = last
            x = max(4, min(X_MAX - 4, x))
            if since == 0:
                stamp(scene, dog_art("brace", "down", "up"), x, DOG_Y, facing)
                for _ in range(14):
                    dust.append([x + DOG_W // 2 + rng.randint(-7, 7), 15, rng.uniform(-1.5, 1.5), -rng.uniform(0.4, 1.4), rng.randint(2, 4)])
            else:
                pant = since % 2 == 0
                stamp(scene, lying_art(tail=since % 2 == 1, tongue=pant), x, 10 if pant else 11, facing)
                if since >= 2:
                    # Hearts float up off the top, one after another.
                    rise = (since - 2) % 5
                    hx = x + (11 if facing > 0 else -1) + (rise % 2)
                    scene.glyph("+HEART", hx, 3 - rise, C.RED if rise < 3 else C.MAGENTA)

        # Dust drifts and fades, behind the dog.
        haze = Canvas()
        for mote in dust:
            mote[0] += mote[2]
            mote[1] += mote[3]
            mote[3] += 0.25
            mote[4] -= 1
            haze.pixel(round(mote[0]), min(15, round(mote[1])), DUST[mote[4] % len(DUST)])
        dust = [m for m in dust if m[4] > 0]

        frame.blit(haze, dx, dy)
        frame.blit(scene, dx, dy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zoomies.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
