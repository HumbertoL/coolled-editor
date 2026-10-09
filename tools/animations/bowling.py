#!/usr/bin/env python3
"""
Bowling -- a hook into the pocket, a strike, seen from above.

A magenta ball rolls down a lane between blue gutters, past the yellow aiming
arrows, and hooks into the pocket between the head pin and the 3 pin. Each pin
starts moving when the shock from the impact reaches it and tumbles away along
its own line, some into the gutters and some into the pit. A cyan sweep bar
clears the deck and STRIKE! flashes on the empty lane.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
IMPACT = 19                     # frame the ball meets the head pin
SWEEP = (31, 35)                # sweep bar crosses the deck in these frames
TEXT_FROM = 36
POCKET = (77.0, 9.0)
BALL_SHAPE = [(1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3)]


def pin_spots():
    spots = []
    for col, rows in enumerate(([7], [5, 9], [3, 7, 11], [1, 5, 9, 13])):
        for row in rows:
            spots.append((78 + 4 * col, row))
    return spots


def ball_at(index):
    """Top-left of the 4x4 ball. Speed 4px a frame, hooking up the lane."""
    x = -4 + 4 * index
    if index <= IMPACT:
        u = index / IMPACT
        cy = 11.5 - 3.0 * u ** 2          # the hook bites late
    else:
        cy = POCKET[1] - 0.6 * (index - IMPACT)
        x = POCKET[0] - 2 + 3 * (index - IMPACT)
    return x, round(cy - 1.5)


def pin_tracks():
    """Each pin's position per frame after impact: a delayed, damped slide."""
    tracks = []
    for px, py in pin_spots():
        cx, cy = px + 0.5, py + 0.5
        dx, dy = cx - POCKET[0], cy - POCKET[1]
        dist = math.hypot(dx, dy) or 1.0
        delay = dist / 5.0
        vx = 1.5 * dx / dist + 1.0
        vy = 1.8 * dy / dist
        positions = {}
        x, y = float(px), float(py)
        t = IMPACT + delay
        for index in range(FRAMES):
            if index >= t:
                x += vx
                y += vy
                vx *= 0.9
                vy *= 0.9
                if y < 0 or y > 14:      # into a gutter: stays there, sliding on
                    y = 0 if y < 0 else 14
                    vy = 0
            positions[index] = (x, y, abs(vx) + abs(vy) > 0.5 and index >= t)
        tracks.append(positions)
    return tracks


def draw_lane(frame):
    frame.hline(0, 0, 96, C.BLUE)
    frame.hline(0, 15, 96, C.BLUE)
    for x, y in ((24, 4), (28, 6), (32, 8), (28, 10), (24, 12)):
        frame.pixel(x, y, C.YELLOW)
        frame.pixel(x + 1, y, C.YELLOW)
    frame.vline(8, 1, 14, C.RED)      # the foul line


def build():
    tracks = pin_tracks()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_lane(frame)
        sweep_x = None
        if SWEEP[0] <= index <= SWEEP[1]:
            sweep_x = 60 + (index - SWEEP[0]) * 9
        if index < SWEEP[0] + 1 or sweep_x is not None:
            for positions in tracks:
                x, y, tumbling = positions[index]
                x, y = round(x), round(y)
                if x > 95 or (sweep_x is not None and x < sweep_x):
                    continue
                if tumbling:
                    # Alternate lying across and along as it spins.
                    if index % 2:
                        frame.hline(x, y, 2, C.WHITE)
                    else:
                        frame.vline(x, y, 2, C.WHITE)
                    frame.pixel(x, y, C.RED)
                else:
                    frame.rect(x, y, 2, 2, C.WHITE, fill=True)
                    if index < IMPACT:
                        frame.pixel(x, y, C.RED)
        if sweep_x is not None:
            frame.vline(sweep_x, 1, 14, C.CYAN)
            frame.vline(sweep_x + 1, 1, 14, C.CYAN)
        bx, by = ball_at(index)
        if bx < 96:
            for dx, dy in BALL_SHAPE:
                frame.pixel(bx + dx, by + dy, C.MAGENTA)
            frame.pixel(bx + 1, by + 1, C.BLACK)
            frame.pixel(bx + 2, by + 1, C.BLACK)
        if IMPACT <= index <= IMPACT + 1:
            for dx, dy in ((-2, -3), (0, -4), (2, -3), (-2, 3), (0, 4), (2, 3)):
                frame.pixel(POCKET[0] + 1 + dx, POCKET[1] + dy, C.YELLOW)
        if index >= TEXT_FROM:
            colour = (C.YELLOW, C.RED, C.WHITE)[(index - TEXT_FROM) // 2 % 3]
            frame.text("STRIKE!", "center", 4, colour)
            for i, (sx, sy) in enumerate(((14, 3), (78, 11), (20, 12), (74, 2))):
                if (index + i) % 3 == 0:
                    frame.pixel(sx, sy, C.WHITE)
                    for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        frame.pixel(sx + ddx, sy + ddy, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bowling.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
