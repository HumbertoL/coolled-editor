#!/usr/bin/env python3
"""
Pigeon post -- message delivery, the original way.

A pigeon flaps across the panel with an envelope in its feet, bobbing on a
slow sine. Over the mailbox it lets go: the envelope falls, lands in the
slot, and the mailbox flag pops up red. The pigeon carries on off the edge,
and the loop sends it round with the next letter.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

PIGEON = [
    [
        "....##....",
        "..######.#",
        "#########.",
        ".#######..",
        "...##.....",
    ],
    [
        "..........",
        "..######.#",
        "#########.",
        ".#######..",
        "..##.##...",
    ],
]
ENVELOPE = ["#####", "#.#.#", "##.##", "#####"]
MAILBOX_X = 62
DROP_AT = 26


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES
        px = round(-12 + 116 * t)
        py = 2 + round(1.5 * math.sin(2 * math.pi * 3 * t))

        # Mailbox on a post, slot on top, flag on the side.
        frame.rect(MAILBOX_X, 8, 9, 5, C.BLUE, fill=True)
        frame.rect(MAILBOX_X + 1, 7, 7, 1, C.BLUE, fill=True)
        frame.hline(MAILBOX_X + 2, 8, 5, C.BLACK)
        frame.rect(MAILBOX_X + 4, 13, 2, 3, C.BLUE, fill=True)
        delivered = index >= DROP_AT + 5
        if delivered:
            frame.vline(MAILBOX_X + 9, 5, 4, C.RED)
            frame.hline(MAILBOX_X + 9, 5, 2, C.RED)
        else:
            frame.hline(MAILBOX_X + 9, 12, 3, C.RED)

        for r, line in enumerate(PIGEON[index % 2]):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(px + c, py + r, C.WHITE)
        frame.pixel(px + 9, py + 1, C.YELLOW)          # beak

        if index < DROP_AT:
            ex, ey = px + 3, py + 5
        elif index < DROP_AT + 5:
            k = index - DROP_AT
            ex = MAILBOX_X + 2
            ey = (2 + 5) + k * k // 2 + k
        else:
            ex = ey = None
        if ex is not None and ey < 9:
            for r, line in enumerate(ENVELOPE):
                for c, ch in enumerate(line):
                    frame.pixel(ex + c, ey + r, C.WHITE if ch == "#" else C.RED if (r, c) == (1, 2) else C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pigeon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
