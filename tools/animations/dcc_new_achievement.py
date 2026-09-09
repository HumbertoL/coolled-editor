#!/usr/bin/env python3
"""
"Neeewwww achievement" -- narrator voice.

Two beats. A highlight sweeps across the top line while the bottom waits dim,
then the bottom lights up left-to-right in the same direction the sweep just
travelled, so it reads as cause and effect. Then a hold, then an ease back
down so the loop restarts from the waiting state.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, highlight, wipe  # noqa: E402

TOP = "NEEEWWW"
BOTTOM = "ACHIEVEMENT!"

DELAY = 230
SWEEP, WIPE, HOLD, FADE = 12, 6, 4, 2

# Static corner marks, in the dimmest color available, for framing only.
STARS = [(5, 3), (90, 3), (5, 12), (90, 12)]

HIGHLIGHT_HALF_WIDTH = 2
TOP_Y, BOTTOM_Y = 0, 9


def star(canvas, cx, cy, color):
    for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        canvas.pixel(cx + dx, cy + dy, color)


def build():
    anim = Animation(delay=DELAY)

    # Proportional spacing matters here because of the trailing '!': as a
    # single column of ink in a 5-wide cell, fixed spacing left a 3px hole
    # before it and 2 dead columns after, which pushed the whole bottom line
    # 3px off centre.
    top_width = Canvas.text_width(TOP, proportional=True)
    bottom_width = Canvas.text_width(BOTTOM, proportional=True)
    top_x = (anim.width - top_width) // 2
    bottom_x = (anim.width - bottom_width) // 2
    top_right = top_x + top_width
    bottom_right = bottom_x + bottom_width

    for index in range(SWEEP + WIPE + HOLD + FADE):
        frame = anim.frame()

        if index < SWEEP:
            phase = "sweep"
            step = index
        elif index < SWEEP + WIPE:
            phase = "wipe"
            step = index - SWEEP
        elif index < SWEEP + WIPE + HOLD:
            phase = "hold"
            step = index - SWEEP - WIPE
        else:
            phase = "fade"
            step = index - SWEEP - WIPE - HOLD

        # Top line: steady yellow, with the highlight gliding in and out.
        if phase == "sweep":
            span = (top_right + 4) - (top_x - 4)
            head = (top_x - 4) + span * step / (SWEEP - 1)
            top_color = highlight(C.YELLOW, C.WHITE, head, HIGHLIGHT_HALF_WIDTH)
        else:
            top_color = C.YELLOW

        # Bottom line: dim until the sweep lands, then lit left to right.
        if phase == "sweep":
            bottom_color = C.BLUE
        elif phase == "wipe":
            # +1 so the last wipe frame clears the right edge completely.
            edge = bottom_x + (bottom_right - bottom_x + 1) * (step + 1) / WIPE
            bottom_color = wipe(C.WHITE, C.BLUE, edge)
        elif phase == "hold":
            bottom_color = C.WHITE
        else:
            bottom_color = C.CYAN if step == 0 else C.BLUE

        star_color = C.CYAN if phase in ("wipe", "hold") else C.BLUE

        frame.text(TOP, top_x, TOP_Y, top_color, proportional=True)
        frame.text(BOTTOM, bottom_x, BOTTOM_Y, bottom_color, proportional=True)
        for cx, cy in STARS:
            star(frame, cx, cy, star_color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_new_achievement.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
