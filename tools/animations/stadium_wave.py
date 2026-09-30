#!/usr/bin/env python3
"""
Stadium Wave -- the crowd stands up, one section at a time.

A row of little fans in mismatched shirts fills the bottom of the panel. A
wave rolls left to right: each fan rises from a slump to full height with both
arms up, then sits back down as the crest passes. A beach ball rides the crest
and a foam finger waves from one lucky seat. Up top, a scoreboard keeps the
score, the ball passing behind it. The wave enters and leaves the panel
entirely, so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
PITCH = 5
FANS = 19
X0 = 1
WIDTH_FANS = 5.0                       # wave width, in fans
SHIRTS = [C.RED, C.CYAN, C.GREEN, C.MAGENTA, C.BLUE, C.YELLOW, C.WHITE]
FINGER_FAN = 13


def rise(phase):
    """0 seated .. 1 standing, for a fan `phase` fans behind the crest."""
    if phase < 0 or phase > WIDTH_FANS:
        return 0.0
    return math.sin(math.pi * phase / WIDTH_FANS) ** 0.8


def fan(f, x, s, shirt, finger=False):
    head_y = 12 - round(3 * s)
    # torso
    f.rect(x, head_y + 2, 4, 16 - head_y - 2, shirt, fill=True)
    # head
    f.rect(x + 1, head_y, 2, 2, C.WHITE if shirt != C.WHITE else C.YELLOW, fill=True)
    # arms
    if s > 0.75:                       # both arms up
        f.vline(x, head_y - 2, 3, shirt)
        f.vline(x + 3, head_y - 2, 3, shirt)
        f.pixel(x, head_y - 3, C.WHITE)
        f.pixel(x + 3, head_y - 3, C.WHITE)
        if finger:
            f.rect(x + 3, head_y - 5, 2, 3, C.RED, fill=True)
            f.pixel(x + 4, head_y - 6, C.RED)
            f.pixel(x + 3, head_y - 5, C.WHITE)
    elif s > 0.3:                      # arms out, halfway
        f.pixel(x - 1, head_y + 2, shirt)
        f.pixel(x + 4, head_y + 2, shirt)
        f.pixel(x, head_y + 1, shirt)
        f.pixel(x + 3, head_y + 1, shirt)


def build():
    anim = Animation(delay=DELAY)
    span = FANS + WIDTH_FANS
    for i in range(FRAMES):
        f = anim.frame()
        crest = i / FRAMES * span           # fan index at the wave's front edge
        # beach ball rides the middle of the wave
        mid = crest - WIDTH_FANS / 2
        bx = round(X0 + mid * PITCH + 1)
        by = 2
        if -3 < bx < 96:
            f.rect(bx, by + 1, 3, 3, C.WHITE, fill=True)
            f.pixel(bx + 1, by + 1, C.RED)
            f.pixel(bx, by + 3, C.BLUE)
            f.pixel(bx + 2, by + 2, C.GREEN)
        # the crowd
        for n in range(FANS):
            s = rise(crest - n)
            fan(f, X0 + n * PITCH, s, SHIRTS[(n * 3) % len(SHIRTS)], finger=(n == FINGER_FAN))
        # scoreboard on top (drawn last: the ball goes behind it)
        label = [("HOME", C.RED), ("3", C.YELLOW), ("-", C.WHITE), ("2", C.YELLOW), ("AWAY", C.CYAN)]
        total = sum(f.small_text_width(t) + 2 for t, _ in label) - 2
        left = (96 - total) // 2
        f.rect(left - 2, 0, total + 4, 7, C.BLACK, fill=True)
        f.rect(left - 2, 0, total + 4, 7, C.BLUE)
        x = left
        for text, color in label:
            if text == "3" or text.strip() == "3":
                color = C.YELLOW if i % 16 < 12 else C.WHITE
            x = f.small_text(text.strip() if text.strip() else text, x, 1, color) + 2
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/stadium_wave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
