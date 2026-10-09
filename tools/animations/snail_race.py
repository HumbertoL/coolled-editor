#!/usr/bin/env python3
"""
Snail race -- live coverage of the slowest sport on earth.

Three snails (red, magenta and cyan shells on white bodies) sit on a
three-lane track divided by blue dotted lines, a checkered finish line far
off on the right. A red starter flag drops; AND THEY'RE OFF! while a crowd
of coloured dots jumps and camera flashes pop. Nobody moves. The commentary
keeps going regardless: WHAT A START!, NECK AND NECK, then a day counter
racing from DAY 1 to DAY 47 as a sun and moon trade places. The magenta
snail edges forward one pixel -- HE'S MAKING HIS MOVE! -- and the network
cuts to a slow-motion REPLAY with a yellow telestrator ring around the
single pixel of progress. It ends on LAP 1 OF 500.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
LANES = (5, 9, 13)                       # top row of each snail
SHELLS = (C.RED, C.MAGENTA, C.CYAN)
START_X = 4
FINISH_X = 91
DAYS = (1, 2, 3, 6, 12, 23, 47, 47)

SNAIL = [  # facing right, 11 wide, 3 tall
    "..SSS...E.E",
    ".SSKSS..BB.",
    "BBSSSBBBBB.",
]
SNAIL_PERK = [  # eye stalks up and forward
    "..SSS....EE",
    ".SSKSS..BB.",
    "BBSSSBBBBB.",
]


def snail(frame, x, y, shell, perk=False):
    for r, row in enumerate(SNAIL_PERK if perk else SNAIL):
        for c, ch in enumerate(row):
            if ch == "S":
                frame.pixel(x + c, y + r, shell)
            elif ch == "B":
                frame.pixel(x + c, y + r, C.WHITE)
            elif ch == "E":
                frame.pixel(x + c, y + r, C.YELLOW)
            elif ch == "K":
                frame.pixel(x + c, y + r, C.BLACK)    # the shell's spiral


def track(frame):
    for y in (8, 12):
        for x in range(0, FINISH_X, 3):
            frame.pixel(x, y, C.BLUE)
    # Start line and checkered finish.
    for y in range(5, 16):
        if y % 2:
            frame.pixel(START_X - 2, y, C.WHITE)
        frame.pixel(FINISH_X + (y % 2), y, C.WHITE)
        frame.pixel(FINISH_X + 2 + (y % 2), y, C.WHITE)


def crowd(frame, rng, x0, x1, cheering):
    palette = (C.RED, C.YELLOW, C.GREEN, C.MAGENTA, C.CYAN, C.WHITE)
    for x in range(x0, x1, 2):
        hop = rng.random() < 0.5 if cheering else False
        y = 2 - hop if cheering else 3
        frame.pixel(x, y, palette[(x * 7) % len(palette)])
        if cheering and rng.random() < 0.3:
            frame.pixel(x, y - 1 - hop, C.WHITE)        # arms up
    if cheering and rng.random() < 0.7:
        fx = rng.randrange(x0, x1)
        frame.pixel(fx, 0, C.WHITE)                     # camera flash
        frame.pixel(fx - 1, 1, C.WHITE)
        frame.pixel(fx + 1, 1, C.WHITE)


def build():
    rng = random.Random(500)
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        track(f)
        # Positions: the magenta snail gains one pixel at frame 33.
        moved = i >= 33 and not (38 <= i < 44)       # replay rewinds it
        xs = [START_X, START_X + (1 if moved else 0), START_X]
        if i >= 49:
            xs[0] += 1                                # red answers, at last
        for lane, (y, shell, x) in enumerate(zip(LANES, SHELLS, xs)):
            perk = (i + lane * 2) % 6 < 2
            snail(f, x, y, shell, perk)

        if i <= 5:
            # Starter flag up, then drops.
            f.vline(1, 0, 5, C.WHITE)
            if i <= 3:
                f.rect(2, 0, 4, 3, C.RED, fill=True)
                f.small_text("READY...", 9, 0, C.WHITE)
                crowd(f, rng, 64, 96, cheering=False)
            else:
                f.vline(2, 1, 4, C.RED)
                f.vline(3, 1 + (i - 4), 3, C.RED)
                f.small_text("GO!", 9, 0, C.YELLOW)
                crowd(f, rng, 64, 96, cheering=True)
        elif i <= 12:
            f.small_text("AND THEY'RE OFF!", 0, 0, C.YELLOW if i % 2 else C.WHITE)
            crowd(f, rng, 62, 96, cheering=True)
        elif i <= 18:
            f.small_text("WHAT A START!", 0, 0, C.WHITE)
            # Dust puffs behind them, for drama. They are not moving.
            if i % 2:
                for y in LANES:
                    f.pixel(START_X - 1, y + 2, C.YELLOW)
                    f.pixel(START_X - 3, y + 1, C.YELLOW)
            crowd(f, rng, 54, 96, cheering=i % 3 == 0)
        elif i <= 23:
            f.small_text("NECK AND NECK", 0, 0, C.WHITE)
            f.small_text("LIVE", 81, 0, C.RED if i % 2 else C.BLACK)
        elif i <= 31:
            day = DAYS[i - 24]
            f.small_text(f"DAY {day}", 0, 0, C.CYAN)
            # Sun and moon trading places overhead, fast.
            if i % 2:
                f.rect(60, 0, 3, 3, C.YELLOW, fill=True)
                f.pixel(59, 1, C.YELLOW)
                f.pixel(63, 1, C.YELLOW)
                f.pixel(61, 3, C.YELLOW)
            else:
                f.rect(76, 0, 3, 3, C.WHITE, fill=True)
                f.pixel(77, 0, C.BLACK)
                f.pixel(78, 1, C.BLACK)
                for sx in (30, 44, 88):
                    f.pixel(sx, (sx // 7) % 3, C.WHITE)
        elif i <= 37:
            f.small_text("HE'S MAKING HIS MOVE!", 0, 0,
                         C.YELLOW if i % 2 else C.MAGENTA)
            if i >= 34:
                f.pixel(START_X, LANES[1] + 2, C.GREEN)        # slime trail
        elif i <= 45:
            # Slow-motion replay: the same one pixel, ringed.
            if i % 2 == 0:
                f.pixel(1, 2, C.RED)
                f.pixel(2, 2, C.RED)
                f.pixel(1, 1, C.RED)
                f.pixel(2, 1, C.RED)
            f.small_text("REPLAY", 5, 0, C.WHITE)
            f.small_text("1/10 SPEED", 56, 0, C.CYAN)
            if i >= 41:
                nose = START_X + 10 + (1 if i >= 44 else 0)
                ny = LANES[1] + 1
                for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2),
                               (2, -2), (-2, 2), (2, 2), (-3, -1), (-3, 1),
                               (3, -1), (3, 1), (-1, -3), (1, -3), (-1, 3),
                               (1, 3)):
                    f.pixel(nose + dx, ny + dy, C.YELLOW)
                if i >= 44:
                    f.small_text("+1PX", 24, 9, C.YELLOW)
        else:
            colour = C.WHITE if i < 49 or i % 2 else C.YELLOW
            f.small_text("LAP 1 OF 500", "center", 0, colour)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/snail_race.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
