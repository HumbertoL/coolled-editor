#!/usr/bin/env python3
"""
Constellation -- the Big Dipper, joined up.

A quiet sky of twinkling background stars; the Dipper's seven stars kindle one
by one, then cyan lines trace the figure segment by segment -- around the bowl
and out along the handle. The finished asterism pulses, the lines fade back
through blue, and the sky is dark again for the wrap.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

# The seven stars, flattened onto 96x16. Bowl first, then the handle.
DIPPER = [
    (20, 4),   # Dubhe
    (22, 11),  # Merak
    (38, 12),  # Phecda
    (36, 5),   # Megrez
    (52, 7),   # Alioth
    (66, 9),   # Mizar
    (80, 4),   # Alkaid
]

# Star-index pairs, in draw order: close the bowl, then walk the handle.
SEGMENTS = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 6)]

BACKGROUND = [
    (5, 8), (10, 2), (14, 14), (30, 1), (44, 2), (48, 14),
    (60, 2), (62, 14), (72, 13), (88, 12), (92, 8), (94, 1),
]

STARS_DONE = 14      # all seven lit by here (one every 2 frames)
LINES_DONE = 35      # seven segments, 3 frames each
FADE_START = 44


def segment_progress(index):
    """How much of each segment is drawn at this frame, in [0, 1]."""
    reveal = (index - STARS_DONE) / 3.0
    return [max(0.0, min(1.0, reveal - i)) for i in range(len(SEGMENTS))]


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()

        for i, (x, y) in enumerate(BACKGROUND):
            if (index + i * 4) % 13 < 10:
                frame.pixel(x, y, C.BLUE)

        # Lines: growing, held, then fading back through blue.
        if index >= FADE_START:
            remaining = FRAMES - index
            line_color = C.BLUE if remaining > 4 else None
        elif index > LINES_DONE:
            line_color = C.CYAN
        else:
            line_color = C.CYAN
        if line_color and index > STARS_DONE:
            for (a, b), progress in zip(SEGMENTS, segment_progress(index)):
                if progress <= 0:
                    continue
                x0, y0 = DIPPER[a]
                x1, y1 = DIPPER[b]
                frame.line(
                    x0,
                    y0,
                    x0 + (x1 - x0) * progress,
                    y0 + (y1 - y0) * progress,
                    line_color,
                )

        # The Dipper stars: kindle in sequence, pulse once joined, then dim.
        for i, (x, y) in enumerate(DIPPER):
            if index < i * 2:
                continue
            if index == i * 2:
                # Kindling sparkle.
                frame.pixel(x, y, C.WHITE)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    frame.pixel(x + dx, y + dy, C.CYAN)
                continue
            if LINES_DONE < index < FADE_START and (index + i) % 6 < 2:
                color = C.YELLOW
            elif index >= FADE_START + 5:
                color = C.BLUE if FRAMES - index > 2 else C.BLACK
            else:
                color = C.WHITE
            frame.pixel(x, y, color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/constellation.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
