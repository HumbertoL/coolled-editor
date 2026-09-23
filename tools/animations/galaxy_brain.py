#!/usr/bin/env python3
"""
Galaxy Brain (2017) -- the expanding brain, four panels of enlightenment.

A small, dim blue brain sits beside USE A 4K SCREEN. Each stage it grows and
brightens as the idea gets worse: a cyan brain for USE AN LED SIGN, a white
one throwing off short rays for ONLY 96X16 PIXELS, and finally a blazing
brain for 8 COLORS IS PLENTY, beams wheeling round it and shock-waves of
light rolling out across the panel.
The palette has no brightness levels, so the glow climbs the only ramp it has,
BLUE -> CYAN -> WHITE; the final beams are cleared from behind the caption
so they seem to burst out around it rather than through it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
CENTER = (11, 8)
TEXT_X = 26
# Side-view brains, one per stage: '#' is the brain, '.' inside the outline a
# fold, ' ' outside it.
BRAINS = [
    [
        " ### ",
        "#####",
        "#####",
        " ##  ",
    ],
    [
        "  #####  ",
        " ##.#.## ",
        "##.###.##",
        "#.##.##.#",
        "##.#.#.##",
        " ####### ",
        "    ##   ",
    ],
    [
        "   #######   ",
        " ###..#..### ",
        "##..##.##..##",
        "#.##..#..##.#",
        "##..###.#..##",
        "#.##...#.##.#",
        " ###.##.###  ",
        "   ######    ",
        "      ##     ",
    ],
    [
        "    #########    ",
        "  ###...#...###  ",
        " ##..###.###..## ",
        "##.##...#...##.##",
        "#.#..##.#.##..#.#",
        "##..#..###..#..##",
        "#.##.##...##.##.#",
        "##..#..#.#..#..##",
        " ##.##.#.#.##.## ",
        "  ###..###..###  ",
        "    #########    ",
        "         ###     ",
    ],
]
# (starts at frame, body, folds, caption lines)
STAGES = [
    (0, C.BLUE, C.BLACK, ("USE A 4K", "SCREEN")),
    (11, C.CYAN, C.BLUE, ("USE AN", "LED SIGN")),
    (22, C.WHITE, C.CYAN, ("ONLY 96X16", "PIXELS")),
    (33, C.WHITE, C.CYAN, ("8 COLORS", "IS PLENTY")),
]
TEXT_COLORS = [C.BLUE, C.CYAN, C.WHITE, C.WHITE]


def stage_at(index):
    current = 0
    for n, stage in enumerate(STAGES):
        if index >= stage[0]:
            current = n
    return current


def draw_brain(frame, n, body, folds):
    rows = BRAINS[n]
    x0 = CENTER[0] - len(rows[0]) // 2
    y0 = CENTER[1] - len(rows) // 2
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != " ":
                frame.pixel(x0 + c, y0 + r, body if ch == "#" else folds)


def haloed_text(frame, text, x, y, color):
    """Clear a 1px border around the glyphs, then draw them."""
    stamp = Canvas(frame.width, frame.height)
    stamp.text(text, x, y, C.WHITE, proportional=True)
    for px, py in stamp.lit():
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                frame.pixel(px + ox, py + oy, C.BLACK)
    frame.text(text, x, y, color, proportional=True)


def build():
    anim = Animation(delay=DELAY)
    cx, cy = CENTER
    for index in range(FRAMES):
        frame = anim.frame()
        n = stage_at(index)
        start, body, folds, lines = STAGES[n]
        k = index - start

        if n == 2:
            # Short rays, flickering between two sets.
            for a in range(8):
                angle = a * math.pi / 4 + (k % 2) * math.pi / 8
                for r in range(8, 11):
                    frame.pixel(round(cx + r * math.cos(angle)), round(cy + r * 0.75 * math.sin(angle)), C.CYAN)
        if n == 3:
            # Beams wheeling out from the brain across the whole panel; the
            # caption's box is cleared below, so they burst out from behind it.
            for a in range(16):
                angle = a * 2 * math.pi / 16 + k * 0.09
                color = C.WHITE if a % 3 == 0 else C.CYAN if a % 3 == 1 else C.BLUE
                for step in range(10, 16):
                    frame.pixel(round(cx + step * math.cos(angle)), round(cy + step * 0.8 * math.sin(angle)), color)
            # Shock-waves of light rolling outward, white edge first.
            for y in range(16):
                for x in range(96):
                    d = math.hypot(x - cx, (y - cy) * 1.6)
                    if d < 14:
                        continue
                    phase = (d - k * 2.5) % 9
                    if phase < 1:
                        frame.pixel(x, y, C.WHITE)
                    elif phase < 2.2:
                        frame.pixel(x, y, C.CYAN)
                    elif phase < 3.4:
                        frame.pixel(x, y, C.BLUE)
            box = TEXT_X + max(Canvas.text_width(t, proportional=True) for t in lines) + 1
            frame.rect(TEXT_X - 2, 0, box - TEXT_X + 3, 16, C.BLACK, fill=True)

        # A flash on the frame each new stage arrives.
        if k == 0 and n > 0:
            frame.fill(C.BLUE if n < 3 else C.CYAN)
        if n == 3 and k % 2:
            body, folds = C.WHITE, C.YELLOW
        draw_brain(frame, n, body, folds)

        color = TEXT_COLORS[n]
        if n == 3 and k % 4 == 1:
            color = C.YELLOW
        haloed_text(frame, lines[0], TEXT_X, 0, color)
        haloed_text(frame, lines[1], TEXT_X, 9, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/galaxy_brain.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
