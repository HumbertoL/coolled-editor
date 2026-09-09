#!/usr/bin/env python3
"""
Floor collapse -- Dungeon Crawler Carl.

The countdown before a floor closes. COLLAPSE IN sits on the top line and
the timer runs the last ten seconds in real time -- 200ms frames, five per
second -- while red bars close in from both edges. At zero everything goes
white for a beat, then the loop puts the ten seconds back.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 200
SECONDS = 10
PER_SECOND = 1000 // DELAY


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        remaining = max(0, SECONDS - index // PER_SECOND)
        zero = remaining == 0

        if zero:
            if index % 2 == 0:
                frame.fill(C.RED)
                frame.text("COLLAPSE", "center", 4, C.WHITE, proportional=True)
            else:
                frame.text("COLLAPSE", "center", 4, C.RED, proportional=True)
            continue

        # Bars closing in: 1px per second gone, on both sides.
        gone = SECONDS - remaining
        bars = gone + 1
        frame.rect(0, 0, bars, anim.height, C.RED, fill=True)
        frame.rect(anim.width - bars, 0, bars, anim.height, C.RED, fill=True)

        frame.text("COLLAPSE IN", "center", 0, C.YELLOW, proportional=True)
        timer = f"00:00:{remaining:02d}"
        urgent = remaining <= 3
        blink_on = (index // PER_SECOND) % 2 == 0 if not urgent else index % 2 == 0
        color = C.WHITE if (urgent and blink_on) else C.RED if urgent else C.YELLOW
        frame.text(timer, "center", 9, color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dcc_collapse.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
