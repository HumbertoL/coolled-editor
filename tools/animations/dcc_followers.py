#!/usr/bin/env python3
"""
Followers -- Dungeon Crawler Carl.

The crawl is a show, and the number that matters is the audience. A follower
count ticks upward in uneven jumps, the way a live counter does, with a heart
that beats every time a big batch lands. Red heart, yellow digits, a little
white flash on each surge.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 21
START = 1_204_331


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    count = START
    surge_frames = set()
    last_surge = 0
    for index in range(FRAMES):
        frame = anim.frame()
        jump = rng.choice((0, 0, 1, 1, 2, 3, 5, 8, 13, 0, 0, 0, 0, 0, 40, 120))
        if jump >= 40:
            surge_frames.add(index)
            last_surge = jump
        count += jump
        surging = any(index - s < 3 for s in surge_frames if s <= index)

        frame.text("FOLLOWERS", 4, 0, C.RED, proportional=True)
        label = f"{count:,}"
        frame.text(label, 4, 9, C.WHITE if surging else C.YELLOW, proportional=True)

        beat = surging or index % 10 < 2
        heart = C.WHITE if surging else C.RED
        frame.glyph("+HEART", 84, 4 if beat else 5, heart)
        if beat:
            for dx, dy in ((-2, 2), (7, 2), (2, -1), (2, 8)):
                frame.pixel(84 + dx, 4 + dy, C.RED)
        if surging:
            frame.text(f"+{last_surge}", 60, 0, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_followers.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
