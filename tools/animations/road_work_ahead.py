#!/usr/bin/env python3
"""
Road Work Ahead (2014) -- the vine.

An orange diamond sign slides past on the roadside reading ROAD WORK AHEAD,
a beat, and then the reply: UH YEAH, I SURE HOPE IT DOES. Six seconds, like
the original.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SIGN_AT, REPLY_AT = 0, 26


def diamond(frame, cx, cy, r, color):
    for dy in range(-r, r + 1):
        w = r - abs(dy)
        frame.hline(cx - w, cy + dy, 2 * w + 1, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Road: dashed centre line moving to give the driving feel.
        frame.hline(0, 15, 96, C.BLUE)
        for dash in range(-(index * 2) % 12, 96, 12):
            frame.hline(dash, 14, 6, C.YELLOW)
        if index < REPLY_AT:
            x = 8
            diamond(frame, x, 7, 7, C.YELLOW)
            diamond(frame, x, 7, 5, C.RED)
            frame.vline(x, 14, 1, C.WHITE)
            k = index
            shown = min(3, k // 3 + 1)
            frame.text("ROAD WORK"[:4 if shown == 1 else 9], 20, 0, C.YELLOW if shown < 3 else C.WHITE, proportional=True)
            if shown == 3:
                frame.text("AHEAD" + ("?" if index % 4 < 2 else ""), 20, 9, C.WHITE, proportional=True)
        else:
            k = index - REPLY_AT
            frame.text("UH YEAH, I SURE"[:8 if k < 4 else 15], 2, 0, C.WHITE, proportional=True)
            if k >= 6:
                frame.text("HOPE IT DOES", 2, 9, C.CYAN if k % 4 < 2 else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/road_work_ahead.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
