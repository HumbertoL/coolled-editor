#!/usr/bin/env python3
"""
TEXT-EM-ALL -- the name, with a shine passing over it.

Eleven characters at 6px each is 65 pixels, so the wordmark fits comfortably
on one line with room to breathe. The letters sit steady in cyan while a white
highlight glides across them, then everything holds still for a beat before
the loop.

Restrained on purpose: a name is the one thing on a sign that should not be
hard to read.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, highlight  # noqa: E402

WORD = "TEXT-EM-ALL"
FRAMES = 24
DELAY = 130
SWEEP_FRAMES = 16
TEXT_Y = 4
HIGHLIGHT_HALF_WIDTH = 2


def build():
    anim = Animation(delay=DELAY)
    width = Canvas.text_width(WORD, proportional=True)
    x0 = (anim.width - width) // 2
    right = x0 + width

    for index in range(FRAMES):
        frame = anim.frame()
        if index < SWEEP_FRAMES:
            span = (right + 5) - (x0 - 5)
            head = (x0 - 5) + span * index / (SWEEP_FRAMES - 1)
            color = highlight(C.CYAN, C.WHITE, head, HIGHLIGHT_HALF_WIDTH)
        else:
            color = C.CYAN
        frame.text(WORD, x0, TEXT_Y, color, proportional=True)

        # Understated rule beneath the word, brightening with the sweep.
        for x in range(x0, right):
            lit = index < SWEEP_FRAMES and abs(x - head) < 8
            frame.pixel(x, TEXT_Y + 8, C.CYAN if lit else C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_wordmark.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
