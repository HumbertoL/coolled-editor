#!/usr/bin/env python3
"""
ETA -- the progress bar that reaches 99% and stays there.

It fills fast, honestly, to 99%. Then the estimate starts to wander: 3 SEC,
8 SEC, 2 MIN, 4 HRS, 6 DAYS, 1 YEAR, and finally a shrug. The last pixel of
the bar blinks the whole time. It never finishes; the loop starts it over,
which is what you would have done anyway.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
FILL_FRAMES = 14
BAR_X, BAR_Y, BAR_W = 4, 10, 88
ETAS = ["3 SEC", "8 SEC", "2 MIN", "4 HRS", "6 DAYS", "1 YEAR", "???"]
ETA_EVERY = 6


def build():
    anim = Animation(delay=DELAY)
    inner = BAR_W - 2
    for index in range(FRAMES):
        frame = anim.frame()
        if index < FILL_FRAMES:
            pct = round(99 * (1 - (1 - (index + 1) / FILL_FRAMES) ** 2))
            eta = "3 SEC"
        else:
            pct = 99
            eta = ETAS[min(len(ETAS) - 1, (index - FILL_FRAMES) // ETA_EVERY)]
        frame.text("COPYING", 2, 0, C.WHITE, proportional=True)
        frame.text(f"{pct}%", 44, 0, C.YELLOW if pct < 99 else (C.WHITE if index % 2 else C.YELLOW), proportional=True)
        frame.text(eta, 64, 0, C.CYAN if index < FILL_FRAMES else C.RED, proportional=True)
        frame.rect(BAR_X, BAR_Y, BAR_W, 5, C.BLUE)
        filled = round(inner * pct / 100)
        frame.rect(BAR_X + 1, BAR_Y + 1, filled, 3, C.GREEN, fill=True)
        if pct == 99:
            frame.rect(BAR_X + 1 + filled, BAR_Y + 1, 1, 3, C.GREEN if index % 2 else C.BLACK, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/eta.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
