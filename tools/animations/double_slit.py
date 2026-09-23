#!/usr/bin/env python3
"""
double_slit -- the pattern builds up one photon at a time.

A red emitter on the left fires single yellow photons at a barrier with two
slits. Nothing is drawn going *through* the slits -- past the barrier only
faint blue wavefronts spread from both openings -- and each photon turns up
as a flash somewhere on the detector at the right edge. Its row is drawn
from the two-slit intensity, a cos^2 fringe under a sinc^2 envelope, with a
seeded RNG. The hits stack into a histogram growing leftward from the
screen; any row with a hit shows at least one pixel, so the first few land
visibly and look random. The rate climbs from one every other frame to
sixteen a frame, and by the end three bright bands and their dark gaps
stand out of the noise. Holds, then clears for the loop.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 1801  # Young, 1801

EMIT_X = 6
BARRIER_X = 28
SLITS = (5, 10)
SCREEN_X = 94
BAR_MAX = 40
PHOTON_SPEED = 6     # px per frame, emitter to barrier
FLIGHT = 3           # frames from barrier to screen
FRINGE = 5.0         # rows per fringe: dark rows land on 0, 5, 10, 15
ENVELOPE = 12.0


def intensity(row):
    u = row - 7.5
    fringe = math.cos(math.pi * u / FRINGE) ** 2
    s = math.pi * u / ENVELOPE
    envelope = (math.sin(s) / s) ** 2 if s else 1.0
    return fringe * envelope


def emissions(index):
    if index < 12:
        return 1 if index % 2 == 0 else 0
    if index < 20:
        return 1
    if index < 29:
        return 3
    if index < 37:
        return 8
    if index < 43:
        return 16
    return 0


def build():
    rng = random.Random(SEED)
    weights = [intensity(r) for r in range(16)]
    top = max(weights)

    def sample_row():
        while True:
            row = rng.randrange(16)
            if rng.random() * top < weights[row]:
                return row

    # Pre-roll every photon so the bar scale can be fixed from the final
    # counts and the bars only ever grow.
    to_barrier = math.ceil((BARRIER_X - EMIT_X) / PHOTON_SPEED)
    photons = []  # (emitted frame, sub-offset, row it lands on)
    for index in range(FRAMES):
        for k in range(emissions(index)):
            photons.append((index, rng.randrange(PHOTON_SPEED), sample_row(), rng.randint(-1, 1)))
    final = [0] * 16
    for _, _, row, _ in photons:
        final[row] += 1
    scale = BAR_MAX / max(final)

    anim = Animation(delay=DELAY)
    counts = [0] * 16
    for index in range(FRAMES):
        frame = anim.frame()
        # Plane waves before the barrier: dotted vertical lines moving right.
        for x in range(EMIT_X + 1, BARRIER_X):
            if (x - index * 2) % 6 == 0:
                for y in range(3, 13, 2):
                    frame.pixel(x, y + (x // 6) % 2, C.BLUE)
        # Circular wavefronts spreading from both slits.
        for x in range(BARRIER_X + 1, SCREEN_X):
            for y in range(16):
                for sy in SLITS:
                    d = math.hypot(x - BARRIER_X, y - sy)
                    if (d - index * 2) % 8 < 0.9:
                        frame.pixel(x, y, C.BLUE)

        # Emitter and barrier.
        frame.rect(0, 6, 5, 4, C.RED, fill=True)
        frame.pixel(5, 7, C.YELLOW)
        frame.pixel(5, 8, C.YELLOW)
        for y in range(16):
            if y not in SLITS:
                frame.pixel(BARRIER_X, y, C.WHITE)

        # Photons in flight to the barrier, and arrivals at the screen.
        landed = set()
        for emitted, offset, row, wobble in photons:
            age = index - emitted
            x = EMIT_X + offset + age * PHOTON_SPEED
            if 0 <= age and x < BARRIER_X:
                frame.pixel(x, 7 + (wobble > 0), C.YELLOW)
            if age == to_barrier + FLIGHT:
                counts[row] += 1
                landed.add(row)

        # Histogram growing leftward from the screen.
        for row in range(16):
            if not counts[row]:
                continue
            length = max(1, math.ceil(counts[row] * scale))
            frame.hline(SCREEN_X - length, row, length, C.CYAN)
            if row in landed:
                frame.pixel(SCREEN_X - length, row, C.WHITE)
        frame.vline(SCREEN_X, 0, 16, C.WHITE)
        for row in landed:
            frame.pixel(SCREEN_X + 1, row, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/double_slit.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
