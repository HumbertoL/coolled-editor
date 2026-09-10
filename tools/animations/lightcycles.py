#!/usr/bin/env python3
"""
Lightcycles -- the Tron derby, ending in a wall.

Two bikes, cyan and yellow, carve the grid at right angles, leaving solid light
walls behind them. Their turns are scripted so the walls interleave into a tight
spiral; then the yellow rider gets boxed in and crashes, flashing white where it
hits. Not seamless -- it plays once and holds on the crash.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 80
W, H = 96, 16

# Scripted turn points: at frame N, set heading (dx, dy).
# Cyan starts left going right; yellow starts right going left.
CYAN_TURNS = {0: (1, 0), 10: (0, 1), 14: (1, 0), 24: (0, -1), 28: (1, 0),
              38: (0, 1), 42: (1, 0)}
YELLOW_TURNS = {0: (-1, 0), 12: (0, -1), 15: (-1, 0), 26: (0, 1), 30: (-1, 0),
                40: (0, -1)}
FRAMES = 53


def build():
    anim = Animation(delay=DELAY)

    walls = {}                    # (x, y) -> color, the trails
    cx, cy = 4, 11
    yx, yy = 91, 4
    cd = (1, 0)
    yd = (-1, 0)
    crashed_at = None

    for index in range(FRAMES):
        if index in CYAN_TURNS:
            cd = CYAN_TURNS[index]
        if index in YELLOW_TURNS:
            yd = YELLOW_TURNS[index]

        if crashed_at is None:
            # Lay current heads as walls, then advance two pixels each.
            for _ in range(2):
                walls[(cx, cy)] = C.CYAN
                walls[(yx, yy)] = C.YELLOW
                ncx, ncy = cx + cd[0], cy + cd[1]
                nyx, nyy = yx + yd[0], yy + yd[1]
                # Yellow crashes into a wall or the border.
                if (not (0 <= nyx < W and 1 <= nyy < H)) or (nyx, nyy) in walls:
                    crashed_at = (yx, yy)
                    break
                cx, cy = ncx % W, max(1, min(H - 1, ncy))
                yx, yy = nyx, nyy

        frame = anim.frame()
        for (x, y), color in walls.items():
            frame.pixel(x, y, color)
        if crashed_at is None:
            frame.pixel(cx, cy, C.WHITE)
            frame.pixel(yx, yy, C.WHITE)
        else:
            # Explosion flash around the crash site.
            for r in range(1, 4):
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if abs(dx) + abs(dy) == r:
                            frame.pixel(crashed_at[0] + dx, crashed_at[1] + dy,
                                        C.RED if r > 1 else C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lightcycles.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
