#!/usr/bin/env python3
"""
Campaign sent -- a Text-Em-All broadcast counting up to 250,000 delivered.

Two-row layout. Top: a big odometer counter easing from 0 to the final
number. Bottom: a progress bar filling in step, with an animated "SENDING..."
label that flips to "SENT!" and turns green when the count settles.

The number formatting uses a comma; the font ships one, and the digits are
5x7 so seven columns of digits plus commas fit within the width.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 110
TARGET = 250_000
COUNT_FRAMES = 18   # 0..17 climbing, 18..23 settled


def format_count(n):
    return f"{n:,}"


def build():
    anim = Animation(delay=DELAY)
    bar_max = 82  # inside the 96 with 7px margins

    for index in range(FRAMES):
        frame = anim.frame()

        if index < COUNT_FRAMES:
            # Ease-out: t^0.55 accelerates fast then slows near the end so
            # the last digits are readable rather than a blur.
            t = (index + 1) / COUNT_FRAMES
            value = int(TARGET * (t ** 0.55))
            done = False
        else:
            value = TARGET
            done = True

        # Top row: counter, right-aligned so the digits fly in from the left.
        text = format_count(value)
        width = frame.text_width(text, proportional=True)
        x = frame.width - width - 3
        frame.text(text, x, 0, C.WHITE if not done else C.GREEN, proportional=True)

        # Left-column label. During counting, a rotating three-dot animation.
        if not done:
            dots = "." * (1 + index % 3)
            frame.text("SENDING" + dots, 2, 8, C.YELLOW, proportional=True)
        else:
            frame.text("SENT!", 2, 8, C.GREEN, proportional=True)
            # Little check mark to the right of "SENT!".
            frame.glyph("+CHECK", 32, 8, C.GREEN)

        # Progress bar (bottom-most row). Filled portion is coloured by state.
        fill = bar_max if done else int(bar_max * value / TARGET)
        frame.hline(7, 15, bar_max, C.BLUE)                      # track
        color = C.GREEN if done else C.CYAN
        frame.hline(7, 15, max(1, fill), color)
        # Bar end caps so the bar reads as a bar and not a stray line.
        frame.pixel(6, 15, C.BLUE)
        frame.pixel(7 + bar_max, 15, C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/campaign_sent.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
