#!/usr/bin/env python3
"""
Loom -- a shuttle weaves nested diamonds, one pick per row.

The warp runs top to bottom: stripes of yellow and red threads, shown as bare
strands where nothing has been woven yet. The white shuttle races across
trailing a weft thread -- blue picks, then magenta -- and wherever the
weave pattern lifts a warp thread over it, the warp colour shows instead. Row
by row a pattern of nested diamonds emerges out of the bare threads. Once the cloth is
done it rolls away upwards and the bare warp is back.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70
W, H = 96, 16
PICK_FRAMES = 3


def warp_color(x):
    return C.YELLOW if (x // 16) % 2 == 0 else C.RED


def weft_color(y):
    return C.BLUE if (y // 8) % 2 == 0 else C.MAGENTA


def warp_up(x, y):
    # nested diamonds: distance from the centre of each 16x8 tile, in rings
    d = abs((x % 16) - 7.5) / 2 + abs((y % 8) - 3.5)
    return int(d) % 2 == 0


def woven(x, y):
    return warp_color(x) if warp_up(x, y) else weft_color(y)


def bare(x):
    return warp_color(x) if x % 2 == 0 else C.BLACK


def build():
    anim = Animation(delay=DELAY)
    weave_frames = H * PICK_FRAMES  # 48
    for index in range(FRAMES):
        frame = anim.frame()
        if index < weave_frames:
            row, sub = divmod(index, PICK_FRAMES)
            ltr = row % 2 == 0
            reach = (sub + 1) * W // PICK_FRAMES
            for y in range(H):
                for x in range(W):
                    if y < row:
                        frame.pixel(x, y, woven(x, y))
                    elif y == row and ((x < reach) if ltr else (x >= W - reach)):
                        frame.pixel(x, y, woven(x, y))
                    else:
                        frame.pixel(x, y, bare(x))
            head = reach - 1 if ltr else W - reach
            if sub < PICK_FRAMES - 1:
                for dx in range(-2, 3):
                    frame.pixel(head + dx, row, C.WHITE)
        else:
            # the finished cloth rolls up and off the top
            shift = (index - weave_frames + 1) * H // (FRAMES - weave_frames)
            for y in range(H):
                for x in range(W):
                    src = y + shift
                    frame.pixel(x, y, woven(x, src) if src < H else bare(x))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/loom.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
