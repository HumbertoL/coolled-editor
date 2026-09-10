#!/usr/bin/env python3
"""
Clawd -- the Claude Code mascot, out for a walk.

The little terracotta blob from the terminal splash, redrawn as an 18x11 sprite
with four stubby legs and two dark eyes. He trots in from the left with a
two-frame walk cycle and a one-pixel bob, stops in the middle, blinks, and a
terminal prompt appears beside him with a blinking cursor -- the moment right
before you type. Then he trots off the right edge, and the loop brings him
back round.

Red is as close as the panel gets to Claude's orange. The eyes are black
gaps in the body, so they read against the red without a third colour.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

BODY = [
    "....##########....",
    "..##############..",
    ".################.",
    "##################",
    "####..######..####",
    "####..######..####",
    "##################",
    "##################",
    ".################.",
    "..##############..",
]
BODY_BLINK = [row.replace(".", "#") if i in (4, 5) else row for i, row in enumerate(BODY)]
LEGS = [
    "..##..##....##..##",     # standing
    ".##....##..##....##",    # stride
]
WIDTH = len(BODY[0])

WALK_IN_END, WALK_OUT_START = 18, 36
STOP_X = 28
GROUND = 13


def clawd_x(index):
    if index < WALK_IN_END:
        return round(-WIDTH + (STOP_X + WIDTH) * index / WALK_IN_END)
    if index < WALK_OUT_START:
        return STOP_X
    return STOP_X + round((96 - STOP_X + 2) * (index - WALK_OUT_START + 1) / (FRAMES - WALK_OUT_START))


def draw_clawd(frame, x, walking, phase, blink):
    body = BODY_BLINK if blink else BODY
    bob = 1 if walking and phase else 0
    top = GROUND - len(BODY) - bob
    for r, line in enumerate(body):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, top + r, C.RED)
    legs = LEGS[phase if walking else 0]
    for c, ch in enumerate(legs):
        if ch == "#":
            frame.pixel(x + c, GROUND, C.RED)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        walking = index < WALK_IN_END or index >= WALK_OUT_START
        x = clawd_x(index)
        blink = index in (24, 25, 31)
        draw_clawd(frame, x, walking, index % 2, blink)

        if WALK_IN_END + 2 <= index < WALK_OUT_START:
            k = index - WALK_IN_END - 2
            frame.text(">", STOP_X + WIDTH + 4, 5, C.WHITE, proportional=True)
            if (k // 3) % 2 == 0:
                frame.rect(STOP_X + WIDTH + 9, 4, 4, 8, C.WHITE, fill=True)
        frame.hline(0, GROUND + 1, anim.width, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/clawd.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
