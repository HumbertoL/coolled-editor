#!/usr/bin/env python3
"""
Fireworks -- three shells, staggered so one is always doing something.

Each shell rises as a single yellow spark with a fading tail, bursts at its
apex into a ring of particles, and the particles fall under gravity while
cooling: the shell's bright colour for a few frames, then its dim partner,
then blue embers, then gone. The launches are timed so the last ember of the
third shell dies on the final frame.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 110
SEED = 7

GRAVITY = 0.32
PARTICLES = 14
LIFE = 9

# (launch frame, x, rise frames, apex y, bright colour, dim colour)
SHELLS = [
    (0, 22, 6, 4, C.YELLOW, C.RED),
    (5, 66, 6, 3, C.WHITE, C.CYAN),
    (10, 46, 5, 5, C.GREEN, C.YELLOW),
]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    bursts = []
    for launch, x, rise, apex, bright, dim in SHELLS:
        particles = []
        for i in range(PARTICLES):
            angle = 2 * math.pi * i / PARTICLES + rng.uniform(-0.15, 0.15)
            speed = rng.uniform(0.8, 1.15)
            particles.append((math.cos(angle) * 3.0 * speed, math.sin(angle) * 1.3 * speed))
        bursts.append((launch + rise, x, apex, bright, dim, particles))

    for index in range(FRAMES):
        frame = anim.frame()

        for launch, x, rise, apex, bright, dim in SHELLS:
            age = index - launch
            if 0 <= age < rise:
                y = 15 - (15 - apex) * age / rise
                frame.pixel(x, round(y) + 2, C.RED)
                frame.pixel(x, round(y) + 1, C.YELLOW)
                frame.pixel(x, round(y), C.WHITE)

        for burst_frame, x, apex, bright, dim, particles in bursts:
            age = index - burst_frame
            if not 0 <= age < LIFE:
                continue
            color = bright if age < 3 else dim if age < 6 else C.BLUE
            for vx, vy in particles:
                px = x + vx * age
                py = apex + vy * age + 0.5 * GRAVITY * age * age
                frame.pixel(round(px), round(py), color)
            if age == 0:
                frame.rect(x - 1, apex - 1, 3, 3, C.WHITE, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fireworks.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
