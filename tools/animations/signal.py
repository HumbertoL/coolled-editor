#!/usr/bin/env python3
"""
Signal -- something in the noise.

Static: blue and cyan specks scattered at random. Then a trace forms across
the middle and pulses emerge from it in groups -- two, three, five, seven,
eleven -- the way a deliberate signal would announce itself. The noise fades
as the pulses sharpen to white. The numbers appear beneath them. Then the
static swallows it again.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 2357
PRIMES = [2, 3, 5, 7, 11]
EMERGE, CLEAR, FADE = 10, 24, 44
TRACE_Y = 6


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < EMERGE:
            clarity = 0.0
        elif index < CLEAR:
            clarity = (index - EMERGE) / (CLEAR - EMERGE)
        elif index < FADE:
            clarity = 1.0
        else:
            clarity = max(0.0, 1 - (index - FADE) / (FRAMES - FADE))

        noise = int(120 * (1 - clarity) + 6)
        for _ in range(noise):
            frame.pixel(rng.randrange(96), rng.randrange(16), C.BLUE if rng.random() < 0.7 else C.CYAN)

        if clarity > 0:
            trace = C.CYAN if clarity < 1 else C.BLUE
            frame.hline(4, TRACE_Y, 88, trace)
            x = 6
            for group, p in enumerate(PRIMES):
                for k in range(p):
                    height = round(4 * clarity)
                    color = C.WHITE if clarity >= 1 else C.CYAN
                    frame.vline(x, TRACE_Y - height, height + 1, color)
                    x += 2
                if clarity >= 1 and index >= CLEAR + 4:
                    label = str(p)
                    frame.text(label, x - 2 * p, 9, C.YELLOW if index % 6 else C.WHITE, proportional=True)
                x += 5
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/signal.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
