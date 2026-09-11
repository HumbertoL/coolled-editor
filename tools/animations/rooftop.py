#!/usr/bin/env python3
"""
Rooftop -- a cosy terrace at night.

String lights sag across the top in a slow twinkle, a city skyline glows
blue behind with the odd window switching on or off, and a crescent moon
hangs at the corner. On the deck: two chairs, a table with a lantern that
flickers, and potted plants that sway when the breeze comes through. Nothing
happens, deliberately. Seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
SEED = 31
DECK_Y = 14


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    buildings = []
    x = 0
    while x < 96:
        w = rng.randrange(6, 14)
        h = rng.randrange(3, 8)
        buildings.append((x, w, h))
        x += w + 1
    windows = [(bx + 1 + 2 * i, DECK_Y - 3 - 2 * j, rng.random())
               for bx, bw, bh in buildings for i in range((bw - 1) // 2) for j in range(bh // 2)]
    bulbs = list(range(4, 96, 7))

    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES

        for bx, bw, bh in buildings:
            frame.rect(bx, DECK_Y - 2 - bh, bw, bh, C.BLUE, fill=True)
        for wx, wy, seed in windows:
            if ((seed * 37 + t * 2) % 1.0) < 0.35:
                frame.pixel(wx, wy, C.YELLOW)

        # Moon, top right.
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 5 and (dx + 1) ** 2 + dy * dy > 4:
                    frame.pixel(89 + dx, 3 + dy, C.WHITE)

        # String lights: a sagging wire with bulbs that twinkle.
        for xx in range(96):
            frame.pixel(xx, 1 + round(1.2 * (1 - math.cos(2 * math.pi * xx / 32)) / 2), C.BLUE)
        for i, bx in enumerate(bulbs):
            wire_y = 1 + round(1.2 * (1 - math.cos(2 * math.pi * bx / 32)) / 2)
            on = math.sin(2 * math.pi * (2 * t) + i * 1.9) > -0.3
            frame.pixel(bx, wire_y + 1, C.YELLOW if on else C.RED)

        frame.hline(0, DECK_Y + 1, 96, C.WHITE)
        # Chairs, table, lantern.
        for cx in (34, 58):
            frame.vline(cx, DECK_Y - 4, 5, C.CYAN)
            frame.hline(cx, DECK_Y - 1, 4, C.CYAN)
            frame.pixel(cx + 3, DECK_Y, C.CYAN)
        frame.hline(43, DECK_Y - 2, 9, C.CYAN)
        frame.vline(47, DECK_Y - 1, 2, C.CYAN)
        flicker = (index * 7) % 5 == 0
        frame.rect(46, DECK_Y - 5, 3, 3, C.YELLOW if not flicker else C.WHITE, fill=True)
        frame.pixel(47, DECK_Y - 6, C.RED)

        # Plants in pots at both ends, swaying.
        for px_ in (8, 84):
            frame.rect(px_ - 1, DECK_Y - 1, 4, 2, C.RED, fill=True)
            sway = round(math.sin(2 * math.pi * t + px_) * 1.2)
            for k in range(5):
                frame.pixel(px_ + (sway if k > 2 else 0) + (k % 2) * 2 - 1, DECK_Y - 2 - k, C.GREEN)
                frame.pixel(px_ + 1 + (sway if k > 2 else 0), DECK_Y - 2 - k, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rooftop.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
