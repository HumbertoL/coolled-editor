#!/usr/bin/env python3
"""
Pong -- one rally, looping forever.

The ball crosses the panel and back in exactly the frame count, and its
vertical bounce is tuned so it lands at the same height at both ends, which is
what makes the loop seamless. Each paddle tracks the ball while it is on its
side and drifts back to the middle otherwise, so they look like they are
playing rather than glued to the ball.

The ball leaves a one-frame blue ghost behind it, which is the cheapest motion
blur there is on a 3-bit palette.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 90

LEFT_X, RIGHT_X = 3, 92          # ball x at each end of the rally
PADDLE_HEIGHT = 5
Y_SPEED = 28.0 / 12.0            # two full up-and-down cycles per loop
Y_PHASE = 9.0


def ball_at(index):
    half = FRAMES // 2
    t = index / half if index < half else (FRAMES - index) / half
    x = round(LEFT_X + (RIGHT_X - LEFT_X) * t)
    phase = (index * Y_SPEED + Y_PHASE) % 28
    y = round(phase if phase <= 14 else 28 - phase)
    return x, y


def paddle_y(target, resting=6):
    return max(0, min(16 - PADDLE_HEIGHT, target - PADDLE_HEIGHT // 2 if target is not None else resting))


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        bx, by = ball_at(index)
        px, py = ball_at((index - 1) % FRAMES)

        # Net and score.
        for y in range(0, anim.height, 4):
            frame.vline(47, y, 2, C.BLUE)
        frame.text("3", 39, 1, C.CYAN)
        frame.text("2", 51, 1, C.YELLOW)

        # Paddles: follow the ball on their own half, idle otherwise.
        left = paddle_y(by if bx < 48 else None)
        right = paddle_y(by if bx >= 48 else None)
        frame.rect(0, left, 2, PADDLE_HEIGHT, C.CYAN, fill=True)
        frame.rect(94, right, 2, PADDLE_HEIGHT, C.YELLOW, fill=True)

        # Ghost, then ball.
        frame.rect(px, py, 2, 2, C.BLUE, fill=True)
        frame.rect(bx, by, 2, 2, C.WHITE, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pong.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
