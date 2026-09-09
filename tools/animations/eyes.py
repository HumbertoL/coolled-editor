#!/usr/bin/env python3
"""
Eyes -- a pair of them, watching the room.

Two white ellipses with cyan irises and black pupils. They glance left, glance
right, blink, look up as if thinking, look down, double-blink, and squint
sideways at whoever is in the room -- because a face that never blinks is
unsettling, and a sign that side-eyes you is funny.

Blinking is done by shrinking the ellipse's vertical radius, so the lids close
from both edges toward the middle, the way a cartoon blink does.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53          # device maximum: a whole routine instead of one glance each way
DELAY = 120

EYES = [34, 61]
CY = 7.5
RX, RY = 7.0, 6.0

# Per frame: (pupil dx, pupil dy, openness 0..1)
SCRIPT = (
    [(0, 0, 1.0)] * 6
    + [(-3, 0, 1.0)] * 5
    + [(0, 0, 1.0)] * 3
    + [(3, 1, 1.0)] * 5
    + [(0, 0, 0.4), (0, 0, 0.0), (0, 0, 0.5)]           # blink
    + [(0, 0, 1.0)] * 4
    + [(-2, -2, 1.0)] * 4                                 # up and left, thinking
    + [(0, 2, 1.0)] * 4                                   # down
    + [(0, 0, 0.4), (0, 0, 0.0), (0, 0, 0.5), (0, 0, 0.0), (0, 0, 0.5)]   # double blink
    + [(0, 0, 1.0)] * 6
    + [(2, 0, 0.5)] * 4                                   # sideways squint
    + [(0, 0, 1.0)] * 4
)
assert len(SCRIPT) == FRAMES


def draw_eye(frame, cx, dx, dy, openness):
    ry = RY * openness
    if ry < 0.5:
        frame.hline(round(cx - RX) + 1, round(CY), round(2 * RX) - 1, C.CYAN)
        return
    for y in range(16):
        for x in range(round(cx - RX) - 1, round(cx + RX) + 2):
            if ((x - cx) / RX) ** 2 + ((y - CY) / ry) ** 2 <= 1.0:
                frame.pixel(x, y, C.WHITE)
    px, py = round(cx + dx), round(CY + dy)
    for y in range(py - 2, py + 3):
        for x in range(px - 2, px + 3):
            inside_eye = ((x - cx) / RX) ** 2 + ((y - CY) / ry) ** 2 <= 1.0
            if not inside_eye or abs(x - px) + abs(y - py) > 3:
                continue
            frame.pixel(x, y, C.BLACK if abs(x - px) <= 1 and abs(y - py) <= 1 else C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    for dx, dy, openness in SCRIPT:
        frame = anim.frame()
        for cx in EYES:
            draw_eye(frame, cx, dx, dy, openness)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/eyes.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
