#!/usr/bin/env python3
"""
Breakout -- brick-breaker on a 96x16 panel.

Rows of coloured bricks along the top, a paddle skating along the bottom that
tracks the ball, and a ball that ricochets off walls, paddle and bricks. The
physics runs at several sub-steps per displayed frame so the ball moves at a
readable speed without tunnelling through bricks. Not seamless -- it is a short
rally that knocks a hole through the wall.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70

W, H = 96, 16
BRICK_ROWS = [(1, C.RED), (2, C.YELLOW), (3, C.GREEN), (4, C.CYAN)]
BRICK_W = 8
PADDLE_W = 11
PADDLE_Y = 15
SUBSTEPS = 3


def build():
    anim = Animation(delay=DELAY)

    # Brick grid: bricks[(col, row)] = color, col in units of BRICK_W.
    bricks = {}
    for row, color in BRICK_ROWS:
        for col in range(W // BRICK_W):
            bricks[(col, row)] = color

    bx, by = 20.0, 11.0
    vx, vy = 1.6, -1.5
    paddle_x = 40.0

    for _ in range(FRAMES):
        for _ in range(SUBSTEPS):
            # Paddle eases toward the ball.
            target = bx - PADDLE_W / 2
            paddle_x += max(-2.2, min(2.2, target - paddle_x))
            paddle_x = max(0, min(W - PADDLE_W, paddle_x))

            bx += vx
            by += vy

            if bx <= 0:
                bx = 0
                vx = abs(vx)
            elif bx >= W - 1:
                bx = W - 1
                vx = -abs(vx)
            if by <= 0:
                by = 0
                vy = abs(vy)

            # Paddle bounce, with angle off the paddle centre.
            if vy > 0 and by >= PADDLE_Y - 1:
                if paddle_x - 1 <= bx <= paddle_x + PADDLE_W:
                    vy = -abs(vy)
                    offset = (bx - (paddle_x + PADDLE_W / 2)) / (PADDLE_W / 2)
                    vx = max(-2.0, min(2.0, vx + offset * 0.9))
                    by = PADDLE_Y - 1
                elif by > H:
                    # Missed: relaunch from the paddle.
                    bx, by = paddle_x + PADDLE_W / 2, PADDLE_Y - 2
                    vx, vy = 1.4, -1.6

            # Brick collision.
            col = int(bx) // BRICK_W
            row = int(round(by))
            if (col, row) in bricks:
                del bricks[(col, row)]
                vy = -vy

        frame = anim.frame()
        for (col, row), color in bricks.items():
            frame.hline(col * BRICK_W, row, BRICK_W - 1, color)
        frame.hline(int(paddle_x), PADDLE_Y, PADDLE_W, C.WHITE)
        frame.pixel(int(bx), int(by), C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/breakout.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
