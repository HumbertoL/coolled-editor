#!/usr/bin/env python3
"""
Loss (2008) -- the four panels, as abstract as they get.

The comic strip that became a meme purely through its layout: one figure
standing; two figures; two figures, one seated; and one figure standing at a
bed. It is recognisable reduced to lines -- | || ||- |_ -- and that is what
this draws, one panel at a time, then the strokes fade to blue and hold.
If you know, you know.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
PANEL_W = 22
GAP = 2
X0 = 2
EVERY = 9
# Each panel: list of strokes as (x, y, w, h) inside a 22x14 panel.
PANELS = [
    [(9, 3, 2, 9)],
    [(6, 3, 2, 9), (12, 3, 2, 9)],
    [(6, 3, 2, 9), (12, 5, 2, 7)],
    [(5, 3, 2, 9), (9, 10, 9, 2)],
]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shown = min(len(PANELS), index // EVERY + 1)
        settled = index >= EVERY * len(PANELS) + 4
        for i in range(len(PANELS)):
            px = X0 + i * (PANEL_W + GAP)
            frame.rect(px, 1, PANEL_W, 14, C.BLUE if i < shown else C.BLACK)
            if i >= shown:
                continue
            fresh = i == shown - 1 and not settled
            for x, y, w, h in PANELS[i]:
                frame.rect(px + x, 1 + y, w, h, C.WHITE if fresh else C.CYAN, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/loss.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
