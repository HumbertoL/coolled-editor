#!/usr/bin/env python3
"""
Delivered -- a send completing.

A percentage counts up while a bar fills beneath it, then the count is
replaced by SENT and a tick, held for a beat. The satisfying part of running a
broadcast, which felt worth putting on a wall.

The bar fills in green and the tick lands in white, so the finish reads as a
change of state rather than just the bar reaching the end.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 24
DELAY = 110
COUNT_FRAMES = 18

BAR_Y, BAR_HEIGHT = 10, 3
TEXT_Y = 1


def build():
    anim = Animation(delay=DELAY)
    bar_x0, bar_x1 = 8, anim.width - 8
    span = bar_x1 - bar_x0

    for index in range(FRAMES):
        frame = anim.frame()
        counting = index < COUNT_FRAMES
        progress = (index + 1) / COUNT_FRAMES if counting else 1.0

        if counting:
            label = f"{round(progress * 100)}%"
            width = Canvas.text_width(label, proportional=True)
            frame.text(label, (anim.width - width) // 2, TEXT_Y, C.CYAN,
                       proportional=True)
        else:
            label = "SENT"
            width = Canvas.text_width(label, proportional=True) + 7
            x = (anim.width - width) // 2
            frame.text(label, x, TEXT_Y, C.GREEN, proportional=True)
            # Tick to the right of the word, flashing once as it appears.
            tick = C.WHITE if (index - COUNT_FRAMES) % 2 == 0 else C.GREEN
            frame.glyph("+CHECK", x + width - 5, TEXT_Y, tick)

        # Track, then the filled portion over the top.
        frame.rect(bar_x0, BAR_Y, span, BAR_HEIGHT, C.BLUE, fill=True)
        filled = round(span * progress)
        frame.rect(bar_x0, BAR_Y, filled, BAR_HEIGHT,
                   C.GREEN if counting else C.WHITE, fill=True)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_delivered.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
