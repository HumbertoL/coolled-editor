#!/usr/bin/env python3
"""
Snake -- a boustrophedon crawl with a growing tail.

The snake follows a fixed serpentine path rather than playing a game, because
a scripted route can be made to close on itself exactly: it sweeps left to
right along one row band, drops, sweeps back, and the loop length divides the
frame count so the head returns to the start.

The body fades back along its length -- white head, cyan neck, blue tail --
and a magenta pellet sits a fixed distance ahead on the path, so the snake is
forever about to eat it.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 100

STEP = 4            # pixels advanced per frame along the path
BODY = 26           # body length in pixels, drawn contiguously
ROWS = (3, 8, 12)   # the row bands it sweeps along
PELLET_AHEAD = 40   # pixels ahead on the route
# Start part way along a band so frame 0 shows the whole body contiguously
# rather than straddling the point where the route wraps.
START = 40


def path_points(width):
    """A serpentine route: right along one row, left along the next."""
    points = []
    for band, row in enumerate(ROWS):
        span = range(width) if band % 2 == 0 else range(width - 1, -1, -1)
        points.extend((x, row) for x in span)
    return points


def build():
    anim = Animation(delay=DELAY)
    route = path_points(anim.width)
    length = len(route)

    for index in range(FRAMES):
        frame = anim.frame()
        head = (START + index * STEP) % length

        # Pellet first, so the head draws over it when it catches up.
        px, py = route[(head + PELLET_AHEAD) % length]
        frame.pixel(px, py, C.MAGENTA)
        frame.pixel(px, py + 1, C.MAGENTA)

        # Contiguous body, two rows thick so it reads on a 16px panel.
        for segment in range(BODY):
            x, y = route[(head - segment) % length]
            if segment < 2:
                color = C.WHITE
            elif segment < 10:
                color = C.CYAN
            else:
                color = C.BLUE
            frame.pixel(x, y, color)
            frame.pixel(x, y + 1, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/snake.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
