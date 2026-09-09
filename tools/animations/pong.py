#!/usr/bin/env python3
"""
Pong -- a rally, and then somebody misses.

The ball crosses the panel four times, each paddle tracking it on its own
half and drifting back to the middle otherwise. On the fourth crossing the
left player is caught out of position: the ball goes past, off the edge, and
the right-hand score ticks over and flashes. The loop restarts with the
serve, so the jump back is the natural one.

The ball leaves a one-frame blue ghost behind it, which is the cheapest motion
blur there is on a 3-bit palette. 53 frames, the device maximum -- a rally
plus a point does not fit in 24.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

LEFT_X, RIGHT_X = 3, 92
CROSSING = 12                    # frames per crossing
CROSSINGS = 4
PADDLE_HEIGHT = 5
Y_SPEED = 28.0 / 12.0
Y_PHASE = 9.0
MISS_START = CROSSING * (CROSSINGS - 1)      # frame the fatal crossing begins
POINT_FRAME = CROSSING * CROSSINGS           # ball is past the paddle


def ball_at(index):
    crossing = index // CROSSING
    t = (index - crossing * CROSSING) / CROSSING
    if crossing >= CROSSINGS:
        t = 1 + (index - POINT_FRAME) / CROSSING * 2.5     # keep going, off the edge
        crossing = CROSSINGS - 1
    if crossing % 2 == 0:
        x = LEFT_X + (RIGHT_X - LEFT_X) * t
    else:
        x = RIGHT_X - (RIGHT_X - LEFT_X) * t
    phase = (index * Y_SPEED + Y_PHASE) % 28
    y = phase if phase <= 14 else 28 - phase
    return round(x), round(y)


def paddle_y(target, resting=6):
    centre = resting if target is None else target - PADDLE_HEIGHT // 2
    return max(0, min(16 - PADDLE_HEIGHT, centre))


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        bx, by = ball_at(index)
        px, py = ball_at(index - 1) if index else (None, None)
        scored = index >= POINT_FRAME

        for y in range(0, anim.height, 4):
            frame.vline(47, y, 2, C.BLUE)
        frame.text("3", 39, 1, C.CYAN)
        right_score = "3" if scored else "2"
        frame.text(right_score, 51, 1, C.WHITE if scored and index % 2 else C.YELLOW)

        # Left paddle: tracks the ball, except on the final crossing, where it
        # commits to the wrong end early and cannot get back.
        if index >= MISS_START:
            left = paddle_y(14 if by < 7 else 0)
        else:
            left = paddle_y(by if bx < 48 else None)
        right = paddle_y(by if bx >= 48 else None)
        frame.rect(0, left, 2, PADDLE_HEIGHT, C.CYAN, fill=True)
        frame.rect(94, right, 2, PADDLE_HEIGHT, C.YELLOW, fill=True)

        if px is not None:
            frame.rect(px, py, 2, 2, C.BLUE, fill=True)
        frame.rect(bx, by, 2, 2, C.WHITE, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pong.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
