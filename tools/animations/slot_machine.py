#!/usr/bin/env python3
"""
Slot machine -- three reels spin, decelerate, and land on 7 7 7.

Each reel picks a fresh random glyph every frame until it locks. Reels lock
one at a time (left first) to build the classic anticipation, and the last
few frames flash the jackpot with a border strobe.

The three reel windows are 20px wide with 2px gaps, framed by a rectangle
each; each glyph is drawn 5px wide centred inside its window.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 100
SEED = 7

# Reels lock at these frame indices. Everything after the last lock is jackpot
# flash. Spaced so the ear reads "cachunk... cachunk... CACHUNK!" -- the
# gap widens toward the last reel.
LOCKS = (10, 14, 18)

# Reel windows: (left x, width) -- chosen so three fit across 96 with matching
# 3px gaps and 3px side margins.
REEL_W = 26
GAP = 4
LEFT = (96 - (3 * REEL_W + 2 * GAP)) // 2
WINDOWS = [(LEFT + i * (REEL_W + GAP), REEL_W) for i in range(3)]

SPIN_SYMBOLS = ("7", "$", "+HEART", "+STAR", "*", "0", "8")
JACKPOT = "7"


def draw_frame(canvas):
    """Slot machine cabinet border and reel dividers."""
    canvas.rect(0, 0, canvas.width, canvas.height, C.YELLOW)
    for x, w in WINDOWS:
        canvas.rect(x, 1, w, canvas.height - 2, C.RED)


def draw_symbol(canvas, x, w, name, color):
    """Centre a 5-wide, 7-tall glyph inside a reel window."""
    gx = x + (w - 5) // 2
    canvas.glyph(name, gx, 4, color)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()
        jackpot = index >= LOCKS[-1]

        # Cabinet: strobing gold/red on the jackpot, plain otherwise.
        if jackpot:
            border = C.YELLOW if index % 2 == 0 else C.RED
            frame.rect(0, 0, frame.width, frame.height, border)
            for x, w in WINDOWS:
                frame.rect(x, 1, w, frame.height - 2, border)
        else:
            draw_frame(frame)

        for reel, (x, w) in enumerate(WINDOWS):
            locked = index >= LOCKS[reel]
            if locked:
                # Jackpot flashes yellow/white; the pre-jackpot lock sits red.
                if jackpot:
                    color = C.WHITE if index % 2 == 0 else C.YELLOW
                else:
                    color = C.RED
                draw_symbol(frame, x, w, JACKPOT, color)
            else:
                # Deterministic per-reel spin -- different symbols per frame.
                symbol = rng.choice(SPIN_SYMBOLS)
                draw_symbol(frame, x, w, symbol, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/slot_machine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
