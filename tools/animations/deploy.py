#!/usr/bin/env python3
"""
Deploy -- a CI/CD pipeline shipping a build.

A progress bar fills across the bottom while the stage label above it advances:
BUILDING, then TESTING, then DEPLOYING, then SHIPPED with a check. An activity
pip runs ahead of the fill so it reads as working, not just full. For anyone who
lives in a terminal watching a pipeline go green.

Not seamless -- it runs one deploy to completion.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 95
W, H = 96, 16

BAR_Y = 13
BAR_X0, BAR_X1 = 3, 92

# (end_fraction, label, color)
STAGES = [
    (0.34, "BUILDING", C.CYAN),
    (0.67, "TESTING", C.YELLOW),
    (1.00, "DEPLOYING", C.GREEN),
]


def build():
    anim = Animation(delay=DELAY)
    work_frames = 44

    for index in range(FRAMES):
        frame = anim.frame()
        p = min(1.0, index / work_frames)

        # Which stage are we in?
        label, color = STAGES[-1][1], STAGES[-1][2]
        for end, lab, col in STAGES:
            if p <= end:
                label, color = lab, col
                break

        done = index >= work_frames
        if done:
            label, color = "SHIPPED", C.GREEN

        # Bar frame and fill.
        frame.rect(BAR_X0, BAR_Y, BAR_X1 - BAR_X0, 3, C.BLUE)
        fill_w = int((BAR_X1 - BAR_X0 - 2) * p)
        frame.hline(BAR_X0 + 1, BAR_Y + 1, fill_w, color)
        # Activity pip just ahead of the fill.
        if not done:
            frame.pixel(BAR_X0 + 1 + fill_w, BAR_Y + 1, C.WHITE)

        # Stage label, centred on the top rows.
        frame.text(label, x="center", y=2, color=color)
        if done and (index // 2) % 2 == 0:
            frame.glyph("+CHECK", x=frame.center_x(label) - 8, y=2,
                        color=C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/deploy.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
