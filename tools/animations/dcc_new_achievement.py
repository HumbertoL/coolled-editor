#!/usr/bin/env python3
"""
"Neeewwww achievement" -- narrator voice. Dungeon Crawler Carl.

Two beats. A highlight sweeps across the top line while the bottom waits,
then the bottom lights up left-to-right in the direction the sweep just
travelled, so it reads as cause and effect. Then a hold with the corner
sparks lit, then it falls back to the waiting state for the loop.

Red and yellow, after the book covers: NEEEWWW in red with a yellow glint
sweeping through it, ACHIEVEMENT! wiping in yellow with a white leading edge.
53 frames at 100ms rather than 24 at 230ms, which is the difference between a
glide and a stutter.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, highlight  # noqa: E402

TOP = "NEEEWWW"
BOTTOM = "ACHIEVEMENT!"

FRAMES = 53
DELAY = 100
SWEEP, WIPE, HOLD, FADE = 22, 12, 13, 6
assert SWEEP + WIPE + HOLD + FADE == FRAMES

SPARKS = [(4, 3), (91, 3), (4, 12), (91, 12)]
TOP_Y, BOTTOM_Y = 0, 9


def spark(canvas, cx, cy, color, big=False):
    arms = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    if big:
        arms += [(-2, 0), (2, 0), (0, -2), (0, 2)]
    for dx, dy in arms:
        canvas.pixel(cx + dx, cy + dy, color)


def build():
    anim = Animation(delay=DELAY)
    top_width = Canvas.text_width(TOP, proportional=True)
    bottom_width = Canvas.text_width(BOTTOM, proportional=True)
    top_x = (anim.width - top_width) // 2
    bottom_x = (anim.width - bottom_width) // 2

    for index in range(FRAMES):
        frame = anim.frame()

        if index < SWEEP:
            head = (top_x - 4) + (top_width + 8) * index / (SWEEP - 1)
            top_color = highlight(C.RED, C.YELLOW, head, 2)
            bottom_color = None
            spark_color, big = C.RED, False
        elif index < SWEEP + WIPE:
            step = index - SWEEP
            edge = bottom_x + (bottom_width + 2) * (step + 1) / WIPE
            top_color = C.RED

            def bottom_color(x, _y, edge=edge):
                if x >= edge:
                    return C.BLACK
                return C.WHITE if x >= edge - 3 else C.YELLOW

            spark_color, big = C.YELLOW, step % 4 < 2
        elif index < SWEEP + WIPE + HOLD:
            step = index - SWEEP - WIPE
            top_color = C.RED
            bottom_color = C.YELLOW
            spark_color, big = (C.WHITE if step % 6 < 3 else C.YELLOW), step % 6 < 3
        else:
            step = index - SWEEP - WIPE - HOLD
            top_color = C.RED
            # Ease out: yellow, then the bottom line thins to a red glow, then off.
            bottom_color = [C.YELLOW, C.YELLOW, C.RED, C.RED, None, None][step]
            spark_color, big = C.RED, False

        frame.text(TOP, top_x, TOP_Y, top_color, proportional=True)
        if bottom_color is not None:
            frame.text(BOTTOM, bottom_x, BOTTOM_Y, bottom_color, proportional=True)
        for cx, cy in SPARKS:
            spark(frame, cx, cy, spark_color, big)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_new_achievement.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
