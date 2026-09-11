#!/usr/bin/env python3
"""
Gradient descent -- a ball rolling downhill on a loss curve.

The curve has a shallow dip on the left and the real minimum on the right.
The ball starts high, takes steps proportional to the slope, and settles
into the shallow dip -- the classic local minimum. A warm restart (one kick
of velocity, a real trick from training schedules) carries it over the
ridge and down into the true one. LOSS in the corner falls as it goes;
the trail behind the ball is where it has been. This is training, in one
dimension.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
LR = 0.012
MOMENTUM = 0.78
STEPS_PER_FRAME = 1
RESTART_AT = 22      # a warm restart: one kick of velocity once it has settled
KICK = 0.16


def loss(x):
    """x in [0, 1]. A shallow dip near 0.3 and a deep one near 0.78."""
    return (0.55 * math.exp(-((x - 0.3) / 0.12) ** 2) * -1
            + 1.0 * math.exp(-((x - 0.78) / 0.10) ** 2) * -1
            + 0.9 + 0.35 * (x - 0.5) ** 2 * 4) / 1.2


def slope(x, h=1e-4):
    return (loss(x + h) - loss(x - h)) / (2 * h)


def to_px(x, y):
    return round(x * 95), round(14 - y * 12)


def build():
    anim = Animation(delay=DELAY)
    x, v = 0.04, 0.0
    trail = []
    lo = min(loss(i / 200) for i in range(201))
    hi = max(loss(i / 200) for i in range(201))

    def norm(y):
        return (y - lo) / (hi - lo)

    for index in range(FRAMES):
        frame = anim.frame()
        for px in range(96):
            frame.pixel(px, to_px(px / 95, norm(loss(px / 95)))[1], C.BLUE)
        for tx in trail:
            frame.pixel(*to_px(tx, norm(loss(tx))), C.CYAN)
        bx, by = to_px(x, norm(loss(x)))
        frame.rect(bx - 1, by - 2, 3, 2, C.YELLOW if index % 2 else C.WHITE, fill=True)
        frame.text(f"LOSS {norm(loss(x)):.2f}", 52, 0, C.WHITE, proportional=True)

        if RESTART_AT <= index < RESTART_AT + 4:
            frame.text("RESTART", 2, 0, C.YELLOW if index % 2 else C.WHITE, proportional=True)

        trail.append(x)
        if index == RESTART_AT:
            v = KICK
        for _ in range(STEPS_PER_FRAME):
            v = MOMENTUM * v - LR * slope(x)
            x = min(0.99, max(0.01, x + v))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/gradient_descent.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
