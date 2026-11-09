#!/usr/bin/env python3
"""
Zelda moon -- dawn of the final day.

DAWN OF / THE FINAL DAY fades in on black, then -24 HOURS REMAIN-. Over a
little town with a clock tower, a yellow moon with a grimacing face and
bloodshot eyes sinks out of a red-starred sky while a clock in the corner
counts down from 6:00 to 0:00 and the town begins to shake. At zero a blue
and cyan spiral winds time back, the panel flashes white, and the three days
start over.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
TITLE_END = 10
HOURS_END = 15
REWIND_AT = 46
FLASH_AT = 51
MOON_X = 66
RADIUS = 9
STARS = [(24, 1), (40, 3), (49, 0), (88, 2), (93, 9), (31, 6), (82, 12), (45, 9)]

TOWER = [
    "...Y...",
    "..RRR..",
    ".RRRRR.",
    "..BBB..",
    "..BWB..",
    ".BWYWB.",
    "..BWB..",
    "..BBB..",
    "..BBB..",
    "..BCB..",
    "..BBB..",
    ".BBBBB.",
    "BBBBBBB",
]


def moon(frame, cx, cy, blink):
    for y in range(cy - RADIUS, cy + RADIUS + 1):
        for x in range(cx - RADIUS, cx + RADIUS + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= RADIUS * RADIUS + 3:
                frame.pixel(x, y, C.YELLOW)
    for x, y in ((cx - 6, cy + 5), (cx + 7, cy - 4), (cx - 2, cy - 7), (cx + 3, cy + 7)):
        frame.pixel(x, y, C.RED)
    for side in (-1, 1):
        ex = cx + side * 4
        # Brows angled down toward the nose.
        for k in range(4):
            frame.pixel(ex - side * 1 + side * k - side, cy - 5 + (1 if k == 0 else 0) - (0 if k < 2 else 1) + 1, C.BLACK)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                frame.pixel(ex + dx, cy - 2 + dy, C.WHITE)
        frame.pixel(ex, cy - 2, C.BLACK if blink else C.RED)
        frame.pixel(ex - side, cy - 2, C.RED)
    # Nose, then a wide grimace full of teeth.
    frame.pixel(cx, cy, C.RED)
    frame.pixel(cx, cy + 1, C.RED)
    frame.hline(cx - 6, cy + 3, 13, C.BLACK)
    frame.hline(cx - 6, cy + 5, 13, C.BLACK)
    for x in range(cx - 6, cx + 7):
        frame.pixel(x, cy + 4, C.WHITE if x % 2 else C.BLACK)


def town(frame, shake):
    for x in range(96):
        frame.pixel(x, 15, C.GREEN)
    for k, (hx, w, h) in enumerate(((2, 6, 4), (21, 7, 5), (30, 5, 3), (86, 8, 4))):
        for y in range(15 - h, 15):
            frame.hline(hx + shake, y, w, C.MAGENTA if k % 2 else C.RED)
        frame.pixel(hx + w // 2 + shake, 15 - h - 1, C.RED)
    for row, line in enumerate(TOWER):
        for col, cell in enumerate(line):
            if cell != ".":
                frame.pixel(11 + col + shake, 2 + row, {"Y": C.YELLOW, "R": C.RED, "B": C.BLUE,
                                                       "W": C.WHITE, "C": C.CYAN}[cell])


def build():
    anim = Animation(delay=DELAY)
    scene_frames = REWIND_AT - HOURS_END
    for index in range(FRAMES):
        frame = anim.frame()
        if index < TITLE_END:
            colour = [C.BLUE, C.CYAN][index] if index < 2 else C.WHITE
            frame.small_text("DAWN OF", "center", 2, colour)
            frame.small_text("THE FINAL DAY", "center", 9, colour)
        elif index < HOURS_END:
            frame.small_text("-24 HOURS REMAIN-", "center", 6, C.WHITE)
        elif index < REWIND_AT:
            t = (index - HOURS_END) / (scene_frames - 1)
            shake = 0 if t < 0.5 else (index % 2) * 2 - 1
            for x, y in STARS:
                if (x + index) % 5:
                    frame.pixel(x, y, C.RED if x % 3 else C.WHITE)
            cy = round(2 + 6 * t)
            moon(frame, MOON_X + shake, cy, blink=index % 9 == 0)
            town(frame, shake)
            minutes = round(360 * (1 - t))
            frame.small_text(f"{minutes // 60}:{minutes % 60:02d}", 82, 0,
                             C.RED if minutes < 60 and index % 2 else C.WHITE)
        elif index < FLASH_AT:
            # Time spirals backward: a rotating two-arm spiral, tightening.
            turn = (index - REWIND_AT) * 0.9
            for y in range(16):
                for x in range(96):
                    dx, dy = (x - 48) / 2.5, (y - 7.5)
                    r = math.hypot(dx, dy)
                    if r > 4 + (index - REWIND_AT) * 4:
                        continue
                    a = math.atan2(dy, dx) - turn - r * 0.35
                    band = (a / math.pi) % 1.0
                    if band < 0.3:
                        frame.pixel(x, y, C.CYAN if r < 6 else C.BLUE)
                    elif band < 0.38:
                        frame.pixel(x, y, C.WHITE)
        else:
            frame.fill(C.WHITE if index == FLASH_AT else C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zelda_moon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
