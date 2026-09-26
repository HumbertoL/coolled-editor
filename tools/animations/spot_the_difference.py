#!/usr/bin/env python3
"""
Spot the Difference -- two little house scenes, three changes, one timer.

A title card says SPOT THE / 3 DIFFERENCES, then the panel splits into two
copies of the same pixel scene either side of a divider: a YELLOW sun with
flickering rays, a WHITE cottage under a RED roof with a chimney, a BLUE
door and a CYAN window, a YELLOW cat on the lawn flicking its tail, a WHITE
picket fence, and a GREEN tree with one RED apple, all on a strip of grass.
The divider is a timer bar that drains GREEN -> YELLOW -> RED while you look.

The right-hand copy differs three ways: its window is lit YELLOW (a colour
change), its chimney is gone (a missing item), and a little WHITE bird
flaps between the sun and the roof (an extra item). When the timer runs
out, each difference is picked out in turn on both halves with flashing
MAGENTA corner brackets, the divider counting 1, 2, 3, and the brackets stay
up for the last beat before the loop resets.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
W, H = 96, 16
SCENE_W = 45
CAT_X = 5
LEFT_X, RIGHT_X = 0, W - SCENE_W  # 0 and 51; divider is columns 45..50

TITLE_END = 6  # frames 0..5: title card
COUNT_END = 36  # frames 6..35: look for them
PER_REVEAL = 5  # frames 36..50: one difference each

# Each difference: (x, y, w, h) box in scene coordinates.
DIFFS = [
    (22, 9, 5, 3),  # window colour
    (23, 0, 4, 5),  # chimney
    (8, 0, 7, 5),  # bird
]


BIRD = [
    ["#...#", ".#.#.", "..#.."],  # wings up
    [".....", "##.##", "..#.."],  # wings level
]


def draw_scene(f, ox, right, index):
    def px(x, y, c):
        if 0 <= x < SCENE_W:
            f.pixel(ox + x, y, c)

    # Sun, rays flicker between straight and diagonal.
    for x, y in [(3, 1), (4, 1), (2, 2), (3, 2), (4, 2), (5, 2), (2, 3), (3, 3), (4, 3), (5, 3), (3, 4), (4, 4)]:
        px(x, y, C.YELLOW)
    if (index // 3) % 2:
        rays = [(0, 2), (0, 3), (7, 2), (7, 3), (3, 6), (4, 6)]
    else:
        rays = [(1, 0), (6, 0), (1, 5), (6, 5), (0, 3), (7, 2)]
    for x, y in rays:
        px(x, y, C.YELLOW)

    # Chimney (missing on the right).
    if not right:
        for y in range(1, 5):
            px(24, y, C.RED)
            px(25, y, C.RED)

    # Roof: a triangle from apex (20, 3) to base row 7.
    for row, y in enumerate(range(3, 8)):
        half = 1 + row * 2 - (1 if row == 0 else 0)
        for x in range(20 - half, 21 + half):
            px(x, y, C.RED)

    # Walls, door, window.
    for y in range(8, 15):
        for x in range(13, 28):
            px(x, y, C.WHITE)
    for y in range(10, 15):
        for x in range(15, 18):
            px(x, y, C.BLUE)
    px(17, 12, C.YELLOW)  # door knob
    window = C.YELLOW if right else C.CYAN
    for y in range(9, 12):
        for x in range(22, 27):
            px(x, y, window)
    px(24, 9, C.WHITE)
    px(24, 10, C.WHITE)
    px(24, 11, C.WHITE)

    # Picket fence.
    for x in range(29, 37):
        px(x, 12, C.WHITE)
    for x in range(29, 37, 2):
        for y in range(10, 15):
            px(x, y, C.WHITE)

    # Tree: canopy, trunk, one apple.
    canopy = [
        "..###..",
        ".#####.",
        "#######",
        "#######",
        "#######",
        ".#####.",
        "..###..",
    ]
    for r, line in enumerate(canopy):
        for c, ch in enumerate(line):
            if ch == "#":
                px(37 + c, 2 + r, C.GREEN)
    px(39, 5, C.RED)
    for y in range(9, 15):
        px(40, y, C.RED)
        px(41, y, C.RED)

    # Cat sitting on the lawn by the house, tail flicking.
    cat = [
        "#.#..",
        "###..",
        "###..",
        ".##..",
        "####.",
        "####.",
    ]
    for r, line in enumerate(cat):
        for c, ch in enumerate(line):
            if ch == "#":
                px(CAT_X + c, 9 + r, C.YELLOW)
    if (index // 4) % 3 == 0:
        tail = [(4, 13), (5, 12), (5, 11)]  # flicked up
    else:
        tail = [(4, 14), (5, 14), (6, 13)]  # curled on the grass
    for x, y in tail:
        px(CAT_X + x, y, C.YELLOW)

    # Extra bird (right only), flapping between the sun and the roof.
    if right:
        wings = BIRD[(index // 3) % 2]
        for r, line in enumerate(wings):
            for c, ch in enumerate(line):
                if ch == "#":
                    px(9 + c, 1 + r, C.WHITE)

    # Grass.
    for x in range(SCENE_W):
        px(x, 15, C.GREEN)


def draw_box(f, ox, box, color, arm=2):
    """Viewfinder corner brackets around a box, clipped to the scene."""
    x, y, w, h = box
    x0, y0, x1, y1 = x - 1, y - 1, x + w, y + h
    for cx, cy, dx, dy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        for k in range(arm + 1):
            for px, py in ((cx + dx * k, cy), (cx, cy + dy * k)):
                if 0 <= px < SCENE_W and 0 <= py < H:
                    f.pixel(ox + px, py, color)


def timer(f, index):
    left = 1 - (index - TITLE_END) / (COUNT_END - TITLE_END)
    height = round(H * left)
    color = C.GREEN if left > 0.5 else C.YELLOW if left > 0.2 else C.RED
    for y in range(H - height, H):
        f.pixel(47, y, color)
        f.pixel(48, y, color)
    for y in range(H - height):
        f.pixel(47, y, C.BLUE if y % 2 else C.BLACK)
        f.pixel(48, y, C.BLUE if y % 2 else C.BLACK)


def main():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        f = anim.frame()
        if index < TITLE_END:
            f.small_text("SPOT THE", "center", 2, C.WHITE)
            f.small_text("3 DIFFERENCES", "center", 9, C.YELLOW if index % 2 else C.RED)
            continue
        draw_scene(f, LEFT_X, False, index)
        draw_scene(f, RIGHT_X, True, index)
        if index < COUNT_END:
            timer(f, index)
            continue
        step = min((index - COUNT_END) // PER_REVEAL, len(DIFFS) - 1)
        fresh = index - COUNT_END < PER_REVEAL * len(DIFFS) and (index - COUNT_END) % PER_REVEAL < 3
        for k in range(step + 1):
            if k == step and fresh:
                color = C.WHITE if index % 2 else C.MAGENTA
            else:
                color = C.MAGENTA
            for ox in (LEFT_X, RIGHT_X):
                draw_box(f, ox, DIFFS[k], color)
        f.small_text(str(step + 1), 47, 5, C.MAGENTA)
    out = Path(__file__).resolve().parents[2] / "src/sample/spot_the_difference.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
