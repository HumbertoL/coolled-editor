#!/usr/bin/env python3
"""
Thirteen years -- the wait from GTA V (2013) to GTA VI (Nov 19 2026).

A fan holding a controller watches the year tick from 2013 while a loading bar
creeps to 99% and sticks there, and his white beard grows a pixel at a time.
Then the delays: FALL 2025 is struck out in red, then MAY 2026. Finally
NOV 19 lands in green, IT'S OUT! flashes, confetti falls, and the fan --
beard down to his knees -- jumps for joy.
"""

from __future__ import annotations

import random

from gta6_art import save
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 120
CONFETTI = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA, C.WHITE]


def fan(f, beard, hop):
    y = 3 - hop
    f.rect(3, y - 1, 6, 2, C.RED, fill=True)  # hair
    f.rect(3, y + 1, 6, 4, C.YELLOW, fill=True)  # face
    f.pixel(4, y + 2, C.BLACK)
    f.pixel(7, y + 2, C.BLACK)
    f.rect(2, y + 5, 8, 16, C.BLUE, fill=True)  # body, runs off the bottom
    if hop:
        f.pixel(1, y + 4, C.YELLOW)  # arms up
        f.pixel(10, y + 4, C.YELLOW)
        f.pixel(1, y + 3, C.YELLOW)
        f.pixel(10, y + 3, C.YELLOW)
    else:
        f.hline(3, y + 9, 6, C.WHITE)  # controller in his lap
        f.pixel(4, y + 8, C.RED)
        f.pixel(7, y + 8, C.GREEN)
    # Beard: from the chin, narrowing as it grows.
    for k in range(beard):
        row = y + 4 + k
        width = 4 if k < 3 else 2 if k < 7 else 1
        f.hline(6 - width // 2 - (width > 1), row, width, C.WHITE)


def build():
    rng = random.Random(19)
    confetti = [(rng.randrange(14, 96), rng.randrange(-16, 0), rng.choice(CONFETTI)) for _ in range(40)]
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        beard = min(12, i // 2)
        year = min(2026, 2013 + i // 2) if i < 30 else 2026
        hop = 1 if i >= 42 and i % 2 == 0 else 0
        fan(f, beard, hop)

        if i < 26:
            f.text(str(year), 15, 1, C.WHITE)
            f.small_text("STILL WAITING" + "." * (i % 4), 15, 10, C.CYAN)
            fill = min(40, round(i * 42 / 22))
            f.rect(48, 1, 44, 5, C.WHITE)
            f.hline(49, 2, fill, C.GREEN)
            f.hline(49, 3, fill, C.GREEN)
            f.hline(49, 4, fill, C.GREEN)
            pct = min(99, round(i * 99 / 22))
            f.small_text(f"{pct}%", 80 - 4 * (pct > 9), 9, C.YELLOW if pct == 99 else C.WHITE)
        elif i < 40:
            f.text(str(year if i < 32 else 2026), 15, 1, C.WHITE)
            f.small_text("DELAYED", 15, 10, C.RED if i % 2 else C.MAGENTA)
            f.small_text("FALL 2025", 52, 2, C.WHITE)
            if i >= 29:
                f.hline(50, 4, min(38, (i - 28) * 12), C.RED)
            if i >= 32:
                f.small_text("MAY 2026", 52, 9, C.WHITE)
            if i >= 35:
                f.hline(50, 11, min(36, (i - 34) * 12), C.RED)
        else:
            f.small_text("NOV 19", 15, 2, C.GREEN)
            f.small_text("2026", 15, 9, C.GREEN)
            if i >= 41:
                f.text("IT'S OUT!", 40, 5 if i % 4 < 2 else 4, C.YELLOW if i % 2 else C.WHITE)
                for cx, cy, col in confetti:
                    y = cy + (i - 42) * 2
                    x = cx + ((i + cx) % 3) - 1
                    if 0 <= y < 16 and f.get(x, y) == C.BLACK:
                        f.pixel(x, y, col)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_thirteen_years")
