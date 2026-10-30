#!/usr/bin/env python3
"""
Witch flyby -- a witch on a broomstick loops-the-loop across the full moon.

A classic Halloween silhouette scene. A huge yellow full moon, pocked with
red craters, fills the middle of the sky among twinkling stars. Along the
bottom runs a hill: a crooked haunted house with a leaning spire and lit
yellow windows (one flickers) on the left, a bare, gnarled tree whose
branches claw across the moon, and a little graveyard of tombstones and a
cross on the right. The scenery is blue in the sky and pure black where it
crosses the moon.

A witch flies in from the left: pointy hat, green face, cape flapping, with
a black cat with a green eye riding the back of the broom. She is magenta
against the night and a black silhouette against the moon. A trail of
sparkles falls from the broom bristles, white turning yellow, cyan, then
blue as it fades. In front of the moon she pulls up into a full
loop-the-loop -- the whole sprite rotates, upside down at the top -- then
carries on and out to the right. The loop is seamless: she leaves the
right edge, her last sparkles finish falling, and she enters from the left.
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
W, H = 96, 16

MOON_X, MOON_Y, MOON_R = 48, 7.5, 8.2

# Flight beat sheet (frames). x is the broom pivot's position.
ENTER_X = -7           # f=0: the broom tip is just poking in
LOOP_START, LOOP_END = 18, 26   # eight 45-degree steps
LOOP_X0 = 45           # pivot x where she pulls up
LOOP_R = 3.0
LOOP_DRIFT = 6         # forward travel during the loop
EXIT_F, EXIT_X = 49, 105
CRUISE_Y = 11          # broom row while flying level

# Two cape frames. H hat, W witch, F face, C cape, K cat, E cat eye,
# S broom stick, B bristles. The pivot is the broom at (PIVOT_COL, PIVOT_ROW).
# 16x10, so a quarter-turned witch still fits the panel's 16 rows.
WITCH = [
    [
        "......H.........",
        ".......H........",
        ".......HH.......",
        "......HHHH......",
        ".....HHHHHHH....",
        "........WFF.....",
        "..K.K.CWWW......",
        "B.KEK.CWWWWWWW..",
        "BBKKK.CWW....W..",
        "BBSSSSSSSSSSSSSS",
    ],
    [
        "......H.........",
        ".......H........",
        ".......HH.......",
        "......HHHH......",
        ".....HHHHHHH....",
        "....CC..WFF.....",
        "..K.K..WWW......",
        "B.KEK..WWWWWWW..",
        "BBKKK..WW....W..",
        "BBSSSSSSSSSSSSSS",
    ],
]
PIVOT_COL, PIVOT_ROW = 8, 9
SKY_INK = {
    "H": C.MAGENTA, "W": C.MAGENTA, "C": C.MAGENTA, "F": C.GREEN,
    "K": C.BLUE, "E": C.GREEN, "S": C.RED, "B": C.YELLOW,
}
# Against the moon everything is black -- except the cat's eye.
MOON_INK = {k: (C.GREEN if k == "E" else C.BLACK) for k in SKY_INK}

HOUSE = [
    ".....#............",
    "....#.............",
    "..###.............",
    "..###.............",
    ".#####.....##.....",
    ".#Y#Y#....####....",
    ".#####...######...",
    ".#####..########..",
    ".#####.##########.",
    ".#####..#Y###Y##..",
    ".##Y##..########..",
    ".#####..####Y###..",
    "#######.##YY####..",
]
HOUSE_X = 4

TREE = [
    "#...#.....#....",
    ".#...#...#...#.",
    "..#..#..#...#..",
    "...#.#.#...#...",
    "....###...#....",
    ".....##.##.....",
    "......###......",
    "......##.......",
    "......##.......",
    "......##.......",
    ".....###.......",
    "....####.......",
]
TREE_X = 52

GRAVES = [  # (x, art)
    (74, [".#.", "###", "###", "###"]),
    (80, [".#.", "###", ".#.", ".#.", ".#."]),
    (85, ["##", "##", "##"]),
    (90, [".##.", "####", "####", "####"]),
]

CRATERS = [(44, 2), (45, 2), (42, 6), (51, 10), (52, 10), (53, 3)]


def ground(x):
    """Top row of the hill at column x."""
    left = 11.5 + 0.004 * (x - 12) ** 2
    right = 12.2 + 0.006 * (x - 84) ** 2
    return int(round(max(11, min(14, left, right))))


def in_moon(x, y):
    return (x - MOON_X) ** 2 + (y - MOON_Y) ** 2 <= MOON_R ** 2


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def flight(f):
    """Pivot position (x, y) and pitch angle at time f (may be fractional)."""
    if f < LOOP_START:
        t = f / LOOP_START
        x = ENTER_X + (LOOP_X0 - ENTER_X) * t
        return x, CRUISE_Y + 0.6 * math.sin(f * 0.9), 0.0
    if f < LOOP_END:
        t = (f - LOOP_START) / (LOOP_END - LOOP_START)
        th = 2 * math.pi * t
        x = LOOP_X0 + LOOP_R * math.sin(th) + LOOP_DRIFT * t
        y = CRUISE_Y - LOOP_R * (1 - math.cos(th))
        return x, y, th
    t = (f - LOOP_END) / (EXIT_F - LOOP_END)
    x = LOOP_X0 + LOOP_DRIFT + (EXIT_X - LOOP_X0 - LOOP_DRIFT) * t
    return x, CRUISE_Y + 0.6 * math.sin(f * 0.9), 0.0


def witch_pixels(px, py, th, cape):
    """Rasterize the (possibly rotated) witch: {(x, y): code}."""
    art = WITCH[cape]
    px, py = int(round(px)), int(round(py))
    out = {}
    c, s = math.cos(th), math.sin(th)
    rows, cols = len(art), len(art[0])
    reach = math.hypot(cols, rows)
    for y in range(int(py - reach), int(py + reach) + 1):
        for x in range(int(px - reach), int(px + reach) + 1):
            dx, dy = x - px, y - py
            # inverse of the nose-up rotation (y points down)
            sx = c * dx - s * dy
            sy = s * dx + c * dy
            col, row = int(round(sx + PIVOT_COL)), int(round(sy + PIVOT_ROW))
            if 0 <= row < rows and 0 <= col < cols and art[row][col] != ".":
                out[(x, y)] = art[row][col]
    return out


def draw_art(c, art, x0, y0, sky, extra=None):
    for r, line in enumerate(art):
        for k, ch in enumerate(line):
            if ch == ".":
                continue
            x, y = x0 + k, y0 + r
            if extra and ch in extra:
                c.pixel(x, y, extra[ch])
            else:
                c.pixel(x, y, C.BLACK if in_moon(x, y) else sky)


def main():
    rnd = random.Random(1692)
    stars = []
    while len(stars) < 22:
        x, y = rnd.randrange(W), rnd.randrange(10)
        if (x - MOON_X) ** 2 + (y - MOON_Y) ** 2 > (MOON_R + 2) ** 2 and y < ground(x) - 3:
            if not (HOUSE_X - 1 <= x <= HOUSE_X + 18 and y >= 0):
                stars.append((x, y, rnd.random() * 2 * math.pi, rnd.choice((2, 3, 4))))

    # sparkles: spawned every frame at the bristles, fall and fade
    LIFE = 7
    spawn = {}
    for f in range(FRAMES):
        if f >= EXIT_F:
            continue
        x, y, th = flight(f)
        bx = x + math.cos(th) * -(PIVOT_COL - 1)
        by = y - math.sin(th) * -(PIVOT_COL - 1)
        spawn[f] = [(bx + rnd.uniform(-1.5, 1.5), by + 1 + rnd.uniform(0, 1), rnd.uniform(-0.3, 0.3))
                    for _ in range(2)]
    fade = [C.WHITE, C.WHITE, C.YELLOW, C.YELLOW, C.CYAN, C.BLUE, C.BLUE]

    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        # stars: integer cycles per loop so the twinkle wraps cleanly
        for (x, y, ph, k) in stars:
            v = math.sin(2 * math.pi * k * f / FRAMES + ph)
            if v > -0.6:
                c.pixel(x, y, C.WHITE if v > 0.3 else C.BLUE)
        # moon and craters
        for y in range(H):
            for x in range(int(MOON_X - MOON_R) - 1, int(MOON_X + MOON_R) + 2):
                if in_moon(x, y):
                    c.pixel(x, y, C.YELLOW)
        for (x, y) in CRATERS:
            c.pixel(x, y, C.RED)
        # scenery
        draw_art(c, TREE, TREE_X, ground(TREE_X + 6) - len(TREE) + 1, C.BLUE)
        for gx, art in GRAVES:
            draw_art(c, art, gx, ground(gx + 1) - len(art) + 1, C.BLUE)
        flicker = C.YELLOW if (f % 9) not in (3, 5) else C.RED
        draw_art(c, HOUSE, HOUSE_X, ground(HOUSE_X + 6) - len(HOUSE) + 1, C.BLUE,
                 extra={"Y": C.YELLOW})
        c.pixel(HOUSE_X + 3, ground(HOUSE_X + 6) - len(HOUSE) + 11, flicker)
        for x in range(W):
            for y in range(ground(x), H):
                c.pixel(x, y, C.BLACK if in_moon(x, y) else C.BLUE)
        # sparkles (modular age, so trails from the last pass wrap into f=0)
        for s0, parts in spawn.items():
            age = (f - s0) % FRAMES
            if age >= LIFE:
                continue
            for (sx, sy, vx) in parts:
                x = sx + vx * age - 0.5 * age
                y = sy + 0.5 * age + 0.12 * age * age
                if (int(age) + int(sx)) % 3 == 2 and age > 2:
                    continue  # twinkle off
                col = fade[age]
                if in_moon(int(round(x)), int(round(y))) and col == C.YELLOW:
                    col = C.WHITE
                c.pixel(round(x), round(y), col)
        # the witch
        if f < EXIT_F:
            x, y, th = flight(f)
            for (wx, wy), code in witch_pixels(x, y, th, (f // 2) % 2).items():
                ink = MOON_INK if in_moon(wx, wy) else SKY_INK
                c.pixel(wx, wy, ink[code])

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/witch_flyby.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
