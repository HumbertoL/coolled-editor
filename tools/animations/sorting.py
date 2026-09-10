#!/usr/bin/env python3
"""
Sorting -- bubble sort, watched.

Twenty-four bars of shuffled heights sort themselves. Every swap the
algorithm makes is recorded, the sequence is sampled evenly to fit the
frames, and the pair being swapped is drawn red against the cyan rest. Once
the order is right a green sweep runs left to right, the traditional "done"
pass from every sorting visualiser ever made.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 17
BARS = 24
SWEEP_FRAMES = 8
BASE_Y = 15


def bubble_sort_states(values):
    states = [(list(values), None)]
    values = list(values)
    for end in range(len(values) - 1, 0, -1):
        for i in range(end):
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
                states.append((list(values), (i, i + 1)))
    return states


def build():
    rng = random.Random(SEED)
    heights = list(range(1, BARS + 1))
    rng.shuffle(heights)
    states = bubble_sort_states([h * 15 // BARS + 1 for h in heights])
    sort_frames = FRAMES - SWEEP_FRAMES
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()
        if index < sort_frames:
            pick = round((len(states) - 1) * index / (sort_frames - 1))
            values, active = states[pick]
            for i, h in enumerate(values):
                color = C.RED if active and i in active else C.CYAN
                frame.rect(2 + i * 4, BASE_Y - h + 1, 3, h, color, fill=True)
        else:
            values = states[-1][0]
            edge = (index - sort_frames + 1) * BARS / SWEEP_FRAMES
            for i, h in enumerate(values):
                color = C.GREEN if i < edge else C.CYAN
                if abs(i - edge) < 1:
                    color = C.WHITE
                frame.rect(2 + i * 4, BASE_Y - h + 1, 3, h, color, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sorting.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
