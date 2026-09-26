#!/usr/bin/env python3
"""
Bubble wrap -- a sheet of it, popped by a front that wanders left to right.

Each bubble is a cyan dome with a white glint. It pops in a one-frame yellow
burst, then lies flat as a crinkled blue scrap. The pop order follows the
columns but with seeded jitter per bubble, so a few run ahead and a few hold
out -- the way nobody pops bubble wrap in a neat line. The last frames reinflate
the sheet from the left, so the loop starts over with a fresh one.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
PITCH_X = 5
PITCH_Y = 4
POP_START = 3
POP_END = 42
REFILL_START = 45
SEED = 7

DOME = ["_##_", "#o##", "_##_"]
FLAT = ["____", "#_##", "____"]
BURST = [(-1, 1), (4, 1), (1, -1), (2, 3), (-1, -1), (4, -1), (-1, 3), (4, 3)]


def bubbles():
    rng = random.Random(SEED)
    out = []
    for row in range(PITCH_Y):
        offset = 2 if row % 2 else 0
        for col in range(20):
            x = 1 + col * PITCH_X + offset
            if x + 3 >= 96:
                continue
            y = row * PITCH_Y
            base = POP_START + (POP_END - POP_START) * x / 92
            pop = round(base + rng.uniform(-4, 4))
            pop = max(POP_START, min(POP_END, pop))
            refill = REFILL_START + round(x / 96 * 6)
            out.append((x, y, pop, refill))
    return out


def stamp(frame, x, y, sprite, colors):
    for dy, line in enumerate(sprite):
        for dx, ch in enumerate(line):
            if ch in colors:
                frame.pixel(x + dx, y + dy, colors[ch])


def build():
    anim = Animation(delay=DELAY)
    sheet = bubbles()
    for index in range(FRAMES):
        frame = anim.frame()
        for x, y, pop, refill in sheet:
            if index < pop or index >= refill:
                stamp(frame, x, y, DOME, {"#": C.CYAN, "o": C.WHITE})
            elif index == pop:
                stamp(frame, x, y, FLAT, {"#": C.WHITE})
                for dx, dy in BURST:
                    frame.pixel(x + dx, y + dy, C.YELLOW)
            else:
                stamp(frame, x, y, FLAT, {"#": C.BLUE})
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bubble_wrap.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
