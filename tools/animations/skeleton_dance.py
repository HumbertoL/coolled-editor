#!/usr/bin/env python3
"""
Skeleton dance -- five skeletons, one routine, no rhythm problems.

Five white skeletons stand in a row across the panel, full height, each with
a round skull, black eye sockets, a striped ribcage down a spine, a pelvis
and bony arms and legs. Off to the right a small yellow crescent moon hangs
among a few twinkling stars, and little music notes -- cyan, magenta, green,
yellow -- drift up past it, wobbling as they rise.

The routine is 24 frames, danced twice, all five in step and all five jaws
rattling the whole time:

  1. Arm pumps: both arms shoot up, drop, then one up and one down, swapping,
     while the dancers squat on every other beat so their skulls bob.
  2. Hip sway: hands on hips, the ribcage and skull swing side to side over
     planted feet.
  3. Kick line: arms straight out, and a chorus-line kick ripples down the row
     one skeleton per frame -- knee up, leg out, high kick -- right legs, then
     left.

The routine divides the frame count and the notes rise on a 24-frame cycle,
so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

CYCLE = 24
FRAMES = 2 * CYCLE        # 48: a whole number of routines, so it loops cleanly
DELAY = 130
W, H = 96, 16

BONE = C.WHITE
CENTERS = [8, 23, 38, 53, 68]          # skeleton x-centres, 15px apart

# Skull and torso, 5 wide; x 0..4 relative to the skeleton's left edge.
SKULL = [".###.", "#####", "#.#.#"]
JAWS = [".###.", ".#.#."]              # rattling: closed, chattering
TORSO = [
    "..#..",   # 4 neck
    "#####",   # 5 collarbone
    ".###.",   # 6 rib
    "..#..",   # 7 spine
    ".###.",   # 8 rib
    "..#..",   # 9 spine
]
PELVIS = ".###."                       # 10

# Arms: (elbow, hand) for the LEFT arm, from the shoulder at (0, 5).
# The right arm mirrors them about x = 2.
ARMS = {
    "down": ((-1, 7), (-2, 9)),
    "up": ((-2, 3), (-3, 1)),
    "out": ((-2, 5), (-4, 5)),
    "hip": ((-2, 7), (0, 9)),
}

MOON = [
    "..###.",
    ".##...",
    "##....",
    "##....",
    ".##...",
    "..###.",
]
MOON_X, MOON_Y = 89, 1
STARS = [(80, 1), (94, 9), (84, 7), (77, 4), (92, 13)]

NOTES = [
    ["..#.", "..##", "..#.", "###.", "##.."],          # eighth note
    [".####", ".#..#", ".#..#", "##.##", "##.##"],     # beamed pair
]
NOTE_COLORS = [C.CYAN, C.MAGENTA, C.GREEN, C.YELLOW]
# (x, phase, sprite): each rises from below the panel to above it in CYCLE frames
NOTE_SPAWNS = [(76, 0, 0), (82, 6, 1), (77, 12, 0), (83, 18, 1)]


def sprite(c, rows, x, y, color):
    for r, line in enumerate(rows):
        for k, ch in enumerate(line):
            if ch == "#":
                c.pixel(x + k, y + r, color)


def pose(t):
    """The routine: what every skeleton does on beat t (0..CYCLE-1)."""
    p = dict(arms=("down", "down"), squat=False, sway=0, kick=None)
    if t < 8:                                   # arm pumps with a bob
        p["arms"] = [("up", "up"), ("down", "down"),
                     ("up", "down"), ("down", "up")][t // 2]
        p["squat"] = t % 2 == 1
    elif t < 16:                                # hip sway
        p["arms"] = ("hip", "hip")
        p["sway"] = [0, -1, -1, 0, 0, 1, 1, 0][t - 8]
    else:                                       # kick line
        p["arms"] = ("out", "out")
    return p


def kick_for(t, i):
    """Kick-line ripple: skeleton i runs one frame behind skeleton i-1."""
    if t < 16:
        return None
    k = (t - 16 - i) % 8
    height = [1, 2, 3, 1][k % 4]
    side = "R" if k < 4 else "L"
    return side, height


def draw_leg(c, hip, height, sign, foot_x=None):
    """sign is -1 for the left leg, +1 for the right; height 0 is standing,
    with the foot planted at foot_x (the leg leans if the hip has moved)."""
    hx, hy = hip
    if height == 0:
        fx = hx if foot_x is None else foot_x
        c.line(hx, hy, fx, 14, BONE)
        c.pixel(fx, 15, BONE)
        c.pixel(fx + sign, 15, BONE)
    elif height == 1:                     # knee up
        c.line(hx, hy, hx + 2 * sign, hy + 1, BONE)
        c.line(hx + 2 * sign, hy + 1, hx + 2 * sign, hy + 3, BONE)
        c.pixel(hx + 3 * sign, hy + 3, BONE)
    elif height == 2:                     # leg out
        c.line(hx, hy, hx + 4 * sign, hy + 2, BONE)
        c.pixel(hx + 4 * sign, hy + 1, BONE)
    else:                                 # high kick
        c.line(hx, hy, hx + 4 * sign, hy - 3, BONE)
        c.pixel(hx + 5 * sign, hy - 3, BONE)


def draw_squat_leg(c, hip, sign):
    hx, hy = hip
    c.pixel(hx, hy, BONE)
    c.pixel(hx + sign, hy + 1, BONE)      # knees bow out
    c.pixel(hx + sign, hy + 2, BONE)
    c.pixel(hx, hy + 3, BONE)
    c.pixel(hx, 15, BONE)
    c.pixel(hx + sign, 15, BONE)


def draw_skeleton(c, cx, p, kick, jaw):
    x0 = cx - 2
    dy = 1 if p["squat"] else 0
    ux = p["sway"]                        # torso swings one way...
    px = -ux                              # ...hips the other, feet stay put

    sprite(c, SKULL + [JAWS[jaw]], x0 + ux, dy, BONE)
    sprite(c, TORSO, x0 + ux, 4 + dy, BONE)
    sprite(c, [PELVIS], x0 + px, 10 + dy, BONE)

    for sign, name in ((-1, p["arms"][0]), (1, p["arms"][1])):
        (ex, ey), (hx, hy) = ARMS[name]
        if name == "hip":
            hx += 2 * ux * sign           # hands ride the hips, not the torso
        sx = 0 if sign < 0 else 4
        mx = (lambda v: x0 + ux + v) if sign < 0 else (lambda v: x0 + ux + 4 - v)
        c.line(x0 + ux + sx, 5 + dy, mx(ex), ey + dy, BONE)
        c.line(mx(ex), ey + dy, mx(hx), hy + dy, BONE)

    hips = {-1: (x0 + 1 + px, 11 + dy), 1: (x0 + 3 + px, 11 + dy)}
    feet = {-1: x0 + 1, 1: x0 + 3}
    for sign in (-1, 1):
        if p["squat"]:
            draw_squat_leg(c, hips[sign], sign)
        elif kick and (kick[0] == "R") == (sign > 0):
            draw_leg(c, hips[sign], kick[1], sign)
        else:
            draw_leg(c, hips[sign], 0, sign, feet[sign])


def draw_backdrop(c, f):
    sprite(c, MOON, MOON_X, MOON_Y, C.YELLOW)
    for k, (sx, sy) in enumerate(STARS):
        if (f // 3 + k) % 4:
            c.pixel(sx, sy, C.WHITE if (f // 3 + k) % 4 == 1 else C.BLUE)


def draw_notes(c, f):
    for n, (nx, phase, kind) in enumerate(NOTE_SPAWNS):
        t = (f + phase) % CYCLE
        y = 16 - round(t * 22 / CYCLE)
        x = nx + round(math.sin(2 * math.pi * t / 8))
        sprite(c, NOTES[kind], x, y, NOTE_COLORS[n])


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        t = f % CYCLE
        draw_backdrop(c, f)
        draw_notes(c, f)
        p = pose(t)
        for i, cx in enumerate(CENTERS):
            draw_skeleton(c, cx, p, kick_for(t, i), jaw=f % 2)

    assert len(anim) == FRAMES and FRAMES % CYCLE == 0
    out = Path(__file__).resolve().parents[2] / "src/sample/skeleton_dance.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
