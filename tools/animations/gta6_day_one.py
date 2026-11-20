#!/usr/bin/env python3
"""
Day one -- Sensor Tower's estimate of GTA 6's launch day: about $2.36 billion
from 24.6 million copies, more than double GTA V's record.

A yellow counter races from $0.00B to $2.36B while green banknotes flutter
down on the right and pile up into a heap. Underneath, DAY ONE gives way to
24.6M COPIES and then 2X GTA V. Once the counter lands it flashes, and the
pile keeps growing.
"""

from __future__ import annotations

import random

from gta6_art import save
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 100
COUNT = 30
LEFT = 46  # the money falls right of here


def build():
    rng = random.Random(236)
    bills = [(rng.randrange(LEFT, 92), rng.randrange(-60, 0), rng.random() < 0.5) for _ in range(70)]
    anim = Animation(delay=DELAY)
    pile = [0] * 96
    for i in range(FRAMES):
        f = anim.frame()
        landed = []
        for k, (bx, by, phase) in enumerate(bills):
            y = by + i
            x = bx + (1 if (i // 2 + phase) % 2 else 0)
            floor = 15 - max(pile[x:x + 4])
            if y >= floor - 1:
                landed.append(k)
                continue
            if y >= -1:
                flat = (i + phase) % 4 < 2
                if flat:
                    f.hline(x, y, 4, C.GREEN)
                    f.hline(x, y + 1, 4, C.GREEN)
                    f.pixel(x + 1 + phase, y, C.WHITE)
                else:  # edge-on as it flips
                    f.hline(x + 1, y, 2, C.GREEN)
                    f.hline(x + 1, y + 1, 2, C.GREEN)
        for k in landed:  # settle into the heap
            bx = bills[k][0]
            for x in range(bx, bx + 4):
                if x < 96:
                    pile[x] = min(9, pile[x] + 1)
            bills[k] = (bx, -100, bills[k][2])
        # smooth the heap so it slumps into a mound
        for x in range(LEFT + 1, 95):
            if pile[x] > pile[x - 1] + 1:
                pile[x] -= 1
                pile[x - 1] += 1
            if pile[x] > pile[x + 1] + 1:
                pile[x] -= 1
                pile[x + 1] += 1
        for x in range(LEFT, 96):
            for h in range(pile[x]):
                y = 15 - h
                f.pixel(x, y, C.YELLOW if (x * 7 + h * 3) % 11 == 0 else C.GREEN)

        t = min(1.0, i / COUNT)
        value = 2.36 * (1 - (1 - t) ** 2)
        colour = (C.WHITE if i % 2 else C.YELLOW) if COUNT <= i < COUNT + 6 else C.YELLOW
        f.text(f"${value:.2f}B", 2, 1, colour)
        if i < 22:
            f.small_text("DAY ONE", 2, 10, C.WHITE)
        elif i < 38:
            f.small_text("24.6M COPIES", 2, 10, C.CYAN)
        else:
            f.small_text("2X GTA V", 2, 10, C.GREEN if i % 4 < 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_day_one")
