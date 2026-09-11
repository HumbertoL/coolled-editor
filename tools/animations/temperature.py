#!/usr/bin/env python3
"""
Temperature -- the same prompt, sampled hotter and hotter.

CAT SAT ON THE... and a completion. The temperature dial climbs from 0.0,
where the answer is always MAT, through the merely creative, to 2.0, where
the model is emitting noise and the letters change every frame. The word's
colour warms from blue to red with the dial.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
SEED = 42
STEPS = [
    (0.0, "MAT", C.BLUE),
    (0.3, "RUG", C.BLUE),
    (0.6, "SOFA", C.CYAN),
    (0.9, "ROOF", C.CYAN),
    (1.2, "MOON", C.YELLOW),
    (1.5, "TUESDAY", C.YELLOW),
    (2.0, None, C.RED),
]
PER_STEP = 7
NOISE = "#@%&?!*$~^"


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        step = min(len(STEPS) - 1, index // PER_STEP)
        temp, word, color = STEPS[step]
        frame.text("CAT SAT ON THE", 2, 0, C.WHITE, proportional=True)
        frame.text(f"T={temp:.1f}", 2, 9, color, proportional=True)
        # The dial: a bar that fills with temperature.
        frame.rect(32, 10, 22, 5, C.BLUE)
        frame.rect(33, 11, round(20 * temp / 2.0), 3, color, fill=True)
        if word is None:
            word = "".join(rng.choice(NOISE) for _ in range(rng.randint(4, 7)))
        frame.text(word, 57, 9, color if word else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/temperature.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
