#!/usr/bin/env python3
"""
Stack -- slabs slide in from alternate sides and drop onto a growing tower.

Each slab sweeps across and stops over the one below. Whatever overhangs is
sliced off and tumbles away; a slab that lands dead on flashes white instead,
and a run of perfect drops is the satisfying part. The view scrolls down as
the tower climbs, so the top few slabs stay on screen, rainbow-striped.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SLAB = 2
SLIDE_FRAMES = 4
SETTLE_FRAMES = 1
SPECTRUM = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]
# where each slab stops, as an offset from the slab below; 0 is perfect
MISSES = [0, 3, 0, 0, -2, 0, 0, 0, 2, 0]
BASE_LEFT, BASE_WIDTH = 30, 36
VISIBLE_SLABS = 6


def build():
    anim = Animation(delay=DELAY)
    tower = [(BASE_LEFT, BASE_WIDTH, C.WHITE)]
    debris = []  # [x, y_world, width, color, vy]

    def world_to_screen(level, scroll):
        return 16 - SLAB * (level + 1) + scroll

    def render(moving=None, flash=None):
        frame = anim.frame()
        top = len(tower) + (1 if moving else 0)
        scroll = max(0, top - VISIBLE_SLABS) * SLAB
        for level, (left, width, color) in enumerate(tower):
            y = world_to_screen(level, scroll)
            frame.rect(left, y, width, SLAB, C.WHITE if level == flash else color, fill=True)
        if moving:
            left, width, color = moving
            frame.rect(left, world_to_screen(len(tower), scroll), width, SLAB, color, fill=True)
        for piece in debris:
            x, yw, width, color, _ = piece
            frame.rect(x, round(yw) + scroll, width, SLAB, color, fill=True)
        for piece in debris:
            piece[4] += 0.7
            piece[1] += piece[4]
        debris[:] = [p for p in debris if p[1] < 20]
        return frame

    for _ in range(2):
        render()
    for n, miss in enumerate(MISSES):
        left, width, _ = tower[-1]
        color = SPECTRUM[n % len(SPECTRUM)]
        target = left + miss
        start = -width if n % 2 == 0 else 96
        for step in range(SLIDE_FRAMES):
            u = step / SLIDE_FRAMES
            x = round(start + (target - start) * (1 - (1 - u) ** 2))
            render((x, width, color))
        # slice
        new_left = max(left, target)
        new_right = min(left + width, target + width)
        top = len(tower) + 1
        scroll = max(0, top - VISIBLE_SLABS) * SLAB
        y_world = 16 - SLAB * (len(tower) + 1)
        if target < left:
            debris.append([target, y_world, left - target, color, 0.0])
        elif target > left:
            debris.append([left + width, y_world, target - left, color, 0.0])
        tower.append((new_left, new_right - new_left, color))
        render(flash=len(tower) - 1 if miss == 0 else None)
    while len(anim) < FRAMES:
        render(flash=len(tower) - 1 if (FRAMES - len(anim)) % 2 == 0 else None)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/stack_tower.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
