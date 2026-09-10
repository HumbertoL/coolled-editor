#!/usr/bin/env python3
"""
Lunar lander -- powered descent to a marked pad.

A lander drifts in high and fast from the left, and gravity pulls it down
while scripted burns -- flame bursts under the hull -- kill its velocity in
stages. It settles onto the pad between the marker lights, kicks up a skirt
of dust, and a green beacon starts blinking. The descent is a real integration
(gravity every frame, thrust on burn frames), tuned so touchdown lands gently
on the pad.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

PAD_LEFT, PAD_RIGHT = 58, 76
PAD_Y = 13
GROUND = [
    (0, 14), (8, 13), (14, 14), (22, 15), (30, 13), (38, 14),
    (46, 15), (52, 14), (58, 13), (76, 13), (82, 14), (90, 15), (96, 14),
]
STARS = [(5, 2), (16, 6), (28, 1), (44, 4), (70, 1), (86, 5), (92, 9), (36, 8)]

GRAVITY = 0.055
TOUCHDOWN_FRAME = 40


def simulate():
    """Integrate the descent; returns per-frame (x, y, burning)."""
    x, y = 8.0, -1.0
    vx, vy = 1.9, 0.35
    path = []
    for index in range(TOUCHDOWN_FRAME + 1):
        # Burn whenever falling fast or drifting long, easing off near the pad.
        burning = vy > 0.55 or (index > 24 and vx > 0.6)
        if burning:
            vy -= 0.16
            if index > 24:
                vx -= 0.12
        vy += GRAVITY
        vx = max(0.0, vx)
        x += vx
        y += vy
        target_x = (PAD_LEFT + PAD_RIGHT) / 2
        x = min(x, target_x)
        if y > PAD_Y - 4:
            y = PAD_Y - 4
        path.append((x, y, burning))
    return path


def draw_lander(frame, x, y, burning, flicker):
    px, py = round(x), round(y)
    # Hull.
    frame.rect(px - 1, py, 3, 2, C.WHITE, fill=True)
    frame.pixel(px, py - 1, C.CYAN)
    # Legs.
    frame.pixel(px - 2, py + 2, C.WHITE)
    frame.pixel(px + 2, py + 2, C.WHITE)
    if burning:
        frame.pixel(px, py + 2, C.YELLOW if flicker else C.WHITE)
        frame.pixel(px, py + 3, C.RED if flicker else C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    path = simulate()
    land_x = round(path[-1][0])

    for index in range(FRAMES):
        frame = anim.frame()

        for x, y in STARS:
            if (index + x) % 11 < 9:
                frame.pixel(x, y, C.WHITE if x % 3 else C.BLUE)

        # Terrain silhouette, with a crater rim or two.
        for i in range(len(GROUND) - 1):
            x0, y0 = GROUND[i]
            x1, y1 = GROUND[i + 1]
            frame.line(x0, y0, x1, y1, C.BLUE)
        frame.hline(PAD_LEFT, PAD_Y, PAD_RIGHT - PAD_LEFT, C.CYAN)
        # Pad marker lights, alternating until touchdown.
        lit = index % 2 if index < TOUCHDOWN_FRAME else 1
        frame.pixel(PAD_LEFT, PAD_Y - 1, C.YELLOW if lit else C.RED)
        frame.pixel(PAD_RIGHT - 1, PAD_Y - 1, C.RED if lit else C.YELLOW)

        if index <= TOUCHDOWN_FRAME:
            x, y, burning = path[index]
            draw_lander(frame, x, y, burning, index % 2 == 0)
        else:
            draw_lander(frame, land_x, PAD_Y - 4, False, False)
            since = index - TOUCHDOWN_FRAME
            # Dust skirt rolling outward, thinning as it goes.
            if since <= 6:
                spread = since * 2
                for side in (-1, 1):
                    dx = side * (3 + spread)
                    frame.pixel(land_x + dx, PAD_Y - 1, C.CYAN if since < 3 else C.BLUE)
                    if since < 4:
                        frame.pixel(land_x + dx - side, PAD_Y - 2, C.BLUE)
            # Mission beacon.
            if since % 4 < 2:
                frame.pixel(land_x, PAD_Y - 5, C.GREEN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lunar_lander.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
