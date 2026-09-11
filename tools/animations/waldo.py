#!/usr/bin/env python3
"""
Where's Waldo -- a crowd, a magnifying glass, and one striped jumper.

Two rows of little people in random colours fill the panel. A magnifying
ring wanders over the crowd, pausing on likely suspects, and finally settles
on the one in red and white stripes with the bobble hat, who waves. The ring
flashes gold. Seeded, so he is always in the same place -- which is how the
books work too.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 1987
COLORS = [C.BLUE, C.GREEN, C.CYAN, C.MAGENTA, C.YELLOW]
ROWS = [(2, 0), (9, 2)]         # (top y of the row, x stagger)
PITCH = 5
FOUND_AT = 38
WALDO_INDEX = 23


def person(frame, x, y, color, waldo=False, wave=False):
    frame.pixel(x + 1, y, C.WHITE if not waldo else C.RED)          # head / hat
    if waldo:
        frame.pixel(x + 1, y - 1, C.WHITE)
    for r in range(1, 4):
        c = color if not waldo else (C.RED if r % 2 else C.WHITE)
        frame.hline(x, y + r, 3, c)
    frame.pixel(x, y + 4, color if not waldo else C.BLUE)
    frame.pixel(x + 2, y + 4, color if not waldo else C.BLUE)
    if wave:
        frame.pixel(x + 3, y, C.RED if waldo else color)
    if waldo:
        frame.pixel(x, y + 1, C.RED)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    people = []
    for row, (y, stagger) in enumerate(ROWS):
        for i in range(18):
            x = 1 + stagger + i * PITCH + rng.randint(0, 1)
            people.append((x, y + rng.randint(0, 1), rng.choice(COLORS)))
    waldo = people[WALDO_INDEX]
    suspects = [people[5], people[30], people[12], people[27]]
    stops = suspects + [waldo]

    def ring_at(index):
        seg = min(len(stops) - 1, index // 8) if index < FOUND_AT else len(stops) - 1
        if index >= FOUND_AT:
            return stops[-1][0] + 1, stops[-1][1] + 2
        a = stops[seg]
        b = stops[min(len(stops) - 1, seg + 1)]
        k = (index % 8) / 8
        # Pause on each suspect for half the segment, then move.
        move = max(0.0, (k - 0.5) * 2)
        return round(a[0] + 1 + (b[0] - a[0]) * move), round(a[1] + 2 + (b[1] - a[1]) * move)

    for index in range(FRAMES):
        frame = anim.frame()
        found = index >= FOUND_AT
        for i, (x, y, color) in enumerate(people):
            is_waldo = i == WALDO_INDEX
            person(frame, x, y, color, waldo=is_waldo, wave=is_waldo and found and index % 2 == 0)
        rx, ry = ring_at(index)
        ring = (C.YELLOW if index % 2 else C.WHITE) if found else C.WHITE
        for dx, dy in ((-3, -1), (-3, 0), (-3, 1), (3, -1), (3, 0), (3, 1), (-2, -2), (-1, -3), (0, -3), (1, -3),
                       (2, -2), (-2, 2), (-1, 3), (0, 3), (1, 3), (2, 2)):
            frame.pixel(rx + dx, ry + dy, ring)
        frame.line(rx + 3, ry + 3, rx + 5, ry + 5, ring)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/waldo.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
