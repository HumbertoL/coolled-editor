#!/usr/bin/env python3
"""
Bongo Cat (2018) -- the round white cat, going to town on the bongos.

The cat leans over the desk behind a pair of bongos, paws alternating left,
right, left, right: each slap lands flat on a drum, the drum rim flashes and
little impact marks fly off it, while the lifted paw leaves a motion streak
under it. Every hit sends a musical note rising and drifting out to the edge
of the panel. Midway it pauses with both paws up -- then slams both at once.
Notes are simulated modulo the loop length, so the ones still rising at the
last frame are the ones already in the air at the first, and the loop has no
seam.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
HEAD = [
    ".#.........#.",
    ".##.......##.",
    ".###########.",
    "#############",
    "#############",
    "#############",
    "#############",
    "#############",
    ".###########.",
    "..#########..",
]
HEAD_X, HEAD_Y = 42, 1
EYES = [(3, 5), (9, 5)]
MOUTH = [(5, 7), (7, 7), (6, 8)]
PAW = [".##.", "####"]
# Paw x positions (left, right), and their y when raised or down.
PAW_X = (36, 57)
PAW_UP_Y, PAW_DOWN_Y = 3, 9
DRUMS = [(34, 8), (55, 8)]      # x, width
DRUM_TOP = 11
TABLE_Y = 14
NOTE = [".##.", ".#.#", ".#..", "##..", "##.."]
NOTE_COLORS = [C.CYAN, C.YELLOW, C.MAGENTA, C.GREEN]
NOTE_LIFE = 12


def hits_at(index):
    """Which paws are down this frame: a set of 0 (left) and 1 (right)."""
    if 24 <= index < 30:
        return set()                      # the dramatic pause, both paws up
    if 30 <= index < 34:
        return {0, 1}                     # SLAM
    beat = index // 2
    return {beat % 2}


def build():
    anim = Animation(delay=DELAY)
    # Every frame on which a paw comes down spawns a note from that drum.
    spawns = []
    for index in range(FRAMES):
        before = hits_at((index - 1) % FRAMES)
        for paw in hits_at(index) - before:
            spawns.append((index, paw))

    for index in range(FRAMES):
        frame = anim.frame()
        down = hits_at(index)
        slam = down == {0, 1}

        # Notes first, so the cat sits in front of them.
        for n, (born, paw) in enumerate(spawns):
            age = (index - born) % FRAMES
            if age >= NOTE_LIFE:
                continue
            direction = -1 if paw == 0 else 1
            start_x = PAW_X[paw] + (-4 if paw == 0 else 4)
            x = start_x + direction * (2 * age + 2)
            y = 8 - age + (n % 3 == 0)
            color = NOTE_COLORS[n % len(NOTE_COLORS)]
            for r, line in enumerate(NOTE):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(x + c, y + r, color)

        # Head.
        for r, line in enumerate(HEAD):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(HEAD_X + c, HEAD_Y + r, C.WHITE)
        frame.pixel(HEAD_X + 1, HEAD_Y + 1, C.MAGENTA)
        frame.pixel(HEAD_X + 11, HEAD_Y + 1, C.MAGENTA)
        blink = index in (5, 44)
        for ex, ey in EYES:
            frame.pixel(HEAD_X + ex, HEAD_Y + ey, C.WHITE if blink else C.BLACK)
            if slam:
                # Happy ^ ^ eyes for the big hit.
                frame.pixel(HEAD_X + ex, HEAD_Y + ey, C.WHITE)
                frame.pixel(HEAD_X + ex, HEAD_Y + ey - 1, C.BLACK)
                frame.pixel(HEAD_X + ex - 1, HEAD_Y + ey, C.BLACK)
                frame.pixel(HEAD_X + ex + 1, HEAD_Y + ey, C.BLACK)
        for mx, my in MOUTH:
            frame.pixel(HEAD_X + mx, HEAD_Y + my, C.BLACK)

        # Bongos and the desk.
        for paw, (dx, width) in enumerate(DRUMS):
            hit = paw in down
            frame.hline(dx, DRUM_TOP, width, C.WHITE if hit else C.YELLOW)
            frame.rect(dx + 1, DRUM_TOP + 1, width - 2, 2, C.RED, fill=True)
            frame.hline(dx + 1, DRUM_TOP + 1, width - 2, C.YELLOW)
        frame.hline(0, TABLE_Y, 96, C.BLUE)
        frame.hline(0, TABLE_Y + 1, 96, C.BLUE)

        # Paws.
        for paw in (0, 1):
            px = PAW_X[paw]
            py = PAW_DOWN_Y if paw in down else PAW_UP_Y
            for r, line in enumerate(PAW):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(px + c, py + r, C.WHITE)
            if paw in down:
                # Impact marks flying off the drum.
                dx, width = DRUMS[paw]
                spread = 2 if slam else 1
                for s in range(spread):
                    frame.pixel(dx - 1 - s * 2, DRUM_TOP - 1 - s, C.WHITE)
                    frame.pixel(dx + width + s * 2, DRUM_TOP - 1 - s, C.WHITE)
            elif index % 2 == 0 and hits_at(index - 1) & {paw}:
                # Just lifted: a motion streak under the rising paw.
                frame.vline(px, py + 3, 2, C.CYAN)
                frame.vline(px + 3, py + 3, 2, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bongo_cat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
