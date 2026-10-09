#!/usr/bin/env python3
"""
Sieve -- Eratosthenes finding the primes up to 384.

The numbers 1 to 384 sit as dots in eight rows of 48, reading left to right,
top to bottom. Each prime up to 19 blinks yellow and sweeps out its multiples
in its own colour: 2 red, 3 green, 5 magenta, 7 cyan, the rest yellow, while unsieved numbers wait in blue. Because a
row is 48 wide, multiples of 2 and 3 fall in straight columns and 5 and 7 run
in diagonals. Past the square root nothing is left to strike, so the
survivors light white and the struck numbers clear away, leaving the primes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
COLS, ROWS = 48, 8
LIMIT = COLS * ROWS
COLOUR = {2: C.RED, 3: C.GREEN, 5: C.MAGENTA, 7: C.CYAN}
SWEEP = {2: 6, 3: 5, 5: 4, 7: 4}   # frames to sweep each prime; others take 3


def spot(n):
    i = n - 1
    return 2 * (i % COLS), 2 * (i // COLS)


def schedule():
    """(prime, frame its sweep starts, sweep length) for each sieving prime."""
    plan, frame = [], 1
    for p in (2, 3, 5, 7, 11, 13, 17, 19):
        length = SWEEP.get(p, 3)
        plan.append((p, frame, length))
        frame += length + 1
    return plan, frame


def build():
    plan, end = schedule()
    reveal = end           # survivors light up
    clear = end + 3        # struck numbers clear, one prime's colour a frame
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        struck = {}
        active = None
        confirmed = 1
        for p, start, length in plan:
            if index < start:
                break
            confirmed = p
            multiples = list(range(p * p, LIMIT + 1, p))
            if index < start + length:
                active = p
                multiples = multiples[: round(len(multiples) * (index - start + 1) / length)]
            for m in multiples:
                struck.setdefault(m, p)
        for n in range(2, LIMIT + 1):
            x, y = spot(n)
            if n in struck:
                p = struck[n]
                order = [q for q, _, _ in plan].index(p)
                if index >= clear + order:
                    continue
                frame.pixel(x, y, COLOUR.get(p, C.YELLOW))
            else:
                frame.pixel(x, y, C.WHITE if index >= reveal or n <= confirmed else C.BLUE)
        if active:
            x, y = spot(active)
            frame.rect(x - 1 if x else x, y - 1 if y else y, 3, 3, C.YELLOW if index % 2 == 0 else C.WHITE)
            frame.pixel(x, y, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sieve.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
