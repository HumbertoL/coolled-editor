#!/usr/bin/env python3
"""
Fireball -- 8d6, the spell everybody takes.

FIREBALL! flares across the top while eight little d6 tumble along the
bottom, showing a new face each frame. They settle left to right, then the
total counts up beside them and the whole row flashes through red and
yellow. The dice are 5x5 with real pip layouts, which is the smallest a d6
can be and still read.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 14           # chosen so the total is worth the spell slot
DICE = 8
SETTLE_START, SETTLE_EVERY = 14, 3
DIE_Y, DIE_X0, DIE_PITCH = 10, 3, 7

PIPS = {
    1: [(2, 2)],
    2: [(1, 1), (3, 3)],
    3: [(1, 1), (2, 2), (3, 3)],
    4: [(1, 1), (3, 1), (1, 3), (3, 3)],
    5: [(1, 1), (3, 1), (2, 2), (1, 3), (3, 3)],
    6: [(1, 1), (3, 1), (1, 2), (3, 2), (1, 3), (3, 3)],
}


def die(frame, x, y, value, body, pip):
    frame.rect(x, y, 5, 5, body, fill=True)
    for px, py in PIPS[value]:
        frame.pixel(x + px, y + py, pip)


def build():
    rng = random.Random(SEED)
    results = [rng.randint(1, 6) for _ in range(DICE)]
    total = sum(results)
    anim = Animation(delay=DELAY)
    all_settled = SETTLE_START + SETTLE_EVERY * (DICE - 1)

    for index in range(FRAMES):
        frame = anim.frame()
        hot = index >= all_settled

        title_color = C.YELLOW if index % 4 < 2 else C.RED
        frame.text("FIREBALL!", 3, 1, title_color, proportional=True)
        if index >= 4:
            frame.text("8D6", 68, 1, C.WHITE if hot else C.RED, proportional=True)

        shown = 0
        for i in range(DICE):
            settled_at = SETTLE_START + SETTLE_EVERY * i
            x = DIE_X0 + i * DIE_PITCH
            if index < settled_at:
                value = rng.randint(1, 6)
                die(frame, x, DIE_Y, value, C.RED, C.BLACK)
            else:
                shown += results[i]
                body = C.YELLOW if hot and (index + i) % 4 < 2 else C.WHITE
                die(frame, x, DIE_Y, results[i], body, C.BLACK)

        if index >= SETTLE_START:
            counted = shown if not hot else min(total, shown + (index - all_settled) * 3)
            counted = min(counted, total)
            label = f"={counted}"
            color = C.WHITE if counted < total else (C.YELLOW if index % 2 else C.RED)
            frame.text(label, 62, 9, color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dnd_fireball.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
