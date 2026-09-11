#!/usr/bin/env python3
"""
Attention -- one head, reading a sentence about itself.

Eight tokens sit as blocks along the top and again along the bottom. The
query moves along the bottom row one token at a time, and from it lines
reach up to the tokens it attends to: white where the weight is strong, cyan
where it is moderate, blue where it barely looks. The current word is shown
in the middle. The sentence is THE SIGN IS READING ITS OWN MIND.

The weights here are hand-set to be plausible -- pronouns look back at their
nouns, verbs at their subjects -- which is roughly what real heads learn.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
TOKENS = ["THE", "SIGN", "IS", "READING", "ITS", "OWN", "MIND", "."]
# For each query token: {key index: weight 1..3}
WEIGHTS = [
    {0: 3},
    {0: 2, 1: 3},
    {1: 3, 2: 1},
    {1: 3, 2: 2, 3: 1},
    {1: 3, 3: 1, 4: 2},
    {4: 3, 1: 2, 5: 1},
    {1: 3, 4: 2, 6: 2, 3: 1},
    {6: 2, 3: 3, 1: 1},
]
PER_TOKEN = 6
TOP_Y, BOTTOM_Y = 0, 14
COLORS = {1: C.BLUE, 2: C.CYAN, 3: C.WHITE}


def token_x(i):
    return 6 + i * 12


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        q = min(len(TOKENS) - 1, index // PER_TOKEN)
        k = index % PER_TOKEN
        for i in range(len(TOKENS)):
            frame.rect(token_x(i) - 2, TOP_Y, 5, 2, C.BLUE if i > q else C.CYAN, fill=True)
            frame.rect(token_x(i) - 2, BOTTOM_Y, 5, 2, C.WHITE if i == q else C.BLUE, fill=True)
        # Lines fade in strongest first.
        for key, weight in sorted(WEIGHTS[q].items(), key=lambda kv: -kv[1]):
            if k >= (3 - weight):
                frame.line(token_x(q), BOTTOM_Y - 1, token_x(key), TOP_Y + 2, COLORS[weight])
        frame.text(TOKENS[q], "center", 5, C.YELLOW, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/attention.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
