#!/usr/bin/env python3
"""
Crab Rave (2018) -- Noisestorm's crabs, dancing because something is gone.

Five red crabs on a strip of sand, all on the same beat: claws up, claws
down, a sidestep one way and then the other, while disco beams sweep the
dark above them and flash on the downbeat. Then the middle three burrow into
the sand and the news arrives between the two that stay, the way the meme
always frames it, crab either side: BUGS IS GONE. The two keep raving; the
three dig back up for the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120            # 4 frames a beat: ~125 BPM, near enough the track
BEAT = 4
CLAWS_UP = [
    "#.#.....#.#",
    "###.....###",
    ".#..W.W..#.",
    ".#.#####.#.",
    "..#######..",
    ".#########.",
    "..#######..",
    ".#.#...#.#.",
]
CLAWS_DOWN = [
    "...........",
    "...........",
    "....W.W....",
    "...#####...",
    "#.#######.#",
    "###########",
    "#.#######.#",
    ".#.#...#.#.",
]
CRAB_W, CRAB_H = 11, 8
CRAB_Y = 6
SAND_Y = 14
CRAB_XS = [2, 22, 42, 62, 83]
EDGE = {0, 4}
BURROW_AT, TEXT_AT, TEXT_END, RISE_AT = 20, 24, 48, 48
CAPTION = "BUGS IS GONE"
BEAMS = [(10, C.BLUE), (34, C.MAGENTA), (58, C.CYAN), (82, C.BLUE)]


def burrow_depth(index, crab):
    """How many rows of a middle crab are under the sand this frame."""
    if crab in EDGE:
        return 0
    if index < BURROW_AT:
        return 0
    if index < BURROW_AT + 4:
        return (index - BURROW_AT + 1) * 2 + 1
    if index < RISE_AT:
        return CRAB_H + 1
    return max(0, CRAB_H + 1 - (index - RISE_AT + 1) * 2)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        beat, sub = divmod(index, BEAT)
        downbeat = sub == 0

        # Disco beams swinging from the ceiling: solid on the downbeat, dotted
        # between, so the strobe pulses and the crabs stay the brightest
        # thing in the room.
        for n, (root, color) in enumerate(BEAMS):
            swing = [-1, 0, 1, 0][(beat + n) % 4]
            for y in range(1, SAND_Y):
                x = root + swing * y // 2
                if downbeat or (y + index) % 2 == 0:
                    frame.pixel(x, y, C.WHITE if downbeat and y < 4 else color)
        if downbeat:
            for x in range(0, 96, 6):
                frame.pixel(x + (beat % 2) * 3, 0, C.WHITE)
        # Glitter ball.
        frame.rect(46, 0, 4, 2, C.WHITE if downbeat else C.CYAN, fill=True)

        # Sand, with a few darker grains so it reads as ground.
        frame.hline(0, SAND_Y, 96, C.YELLOW)
        frame.hline(0, SAND_Y + 1, 96, C.YELLOW)
        for x in range(3, 96, 7):
            frame.pixel(x, SAND_Y + 1, C.RED)

        pose = CLAWS_UP if (index // 2) % 2 == 0 else CLAWS_DOWN
        step = [0, 1, 2, 1, 0, -1, -2, -1][(index // 2) % 8]
        for crab, cx in enumerate(CRAB_XS):
            depth = burrow_depth(index, crab)
            if crab in EDGE and TEXT_AT <= index < TEXT_END:
                offset = 0          # framing crabs dance on the spot
            else:
                offset = step
            y0 = CRAB_Y + depth
            for r, line in enumerate(pose):
                y = y0 + r
                if y >= SAND_Y:
                    continue
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(cx + offset + c, y, C.RED)
                    elif ch == "W":
                        frame.pixel(cx + offset + c, y, C.WHITE)
            if 0 < depth <= CRAB_H:
                # Sand kicked up where it went in.
                for dx in (1, 4, 7, 10):
                    frame.pixel(cx + offset + dx - (index % 2), SAND_Y - 1, C.YELLOW)

        if TEXT_AT <= index < TEXT_END:
            k = index - TEXT_AT
            x = (96 - frame.text_width(CAPTION, proportional=True)) // 2
            # Clear a box behind the caption so the beams don't cut the letters.
            frame.rect(x - 2, 3, frame.text_width(CAPTION, proportional=True) + 4, 9, C.BLACK, fill=True)
            color = C.WHITE if downbeat or k == 0 else [C.YELLOW, C.CYAN][beat % 2]
            frame.text(CAPTION, x, 4, color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/crab_rave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
