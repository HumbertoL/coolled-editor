#!/usr/bin/env python3
"""
Neural net -- a forward pass, five times.

Four layers of nodes across the panel: 4 in, two hidden layers of 6, 3 out.
An input pattern lights up on the left, activation pours along the edges into
the next layer, the nodes that cross threshold light, and so on to the right
until one output wins. Then a new input. The weights are random but fixed,
so the same input always gives the same answer -- as it should.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 7
SIZES = [4, 6, 6, 3]
LAYER_X = [6, 34, 62, 90]
PER_PASS = 10
LAYER_COLORS = [C.YELLOW, C.CYAN, C.CYAN, C.GREEN]


def node_y(layer, i):
    n = SIZES[layer]
    return round(1.5 + (13.0 * i / (n - 1) if n > 1 else 6.5))


def build():
    rng = random.Random(SEED)
    weights = [
        [[rng.uniform(-1, 1) for _ in range(SIZES[l + 1])] for _ in range(SIZES[l])]
        for l in range(len(SIZES) - 1)
    ]
    inputs = [[1, 0, 1, 0], [0, 1, 1, 0], [1, 1, 0, 1], [0, 0, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1]]
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()
        p, k = divmod(index, PER_PASS)
        x_in = inputs[p % len(inputs)]
        acts = [x_in]
        for l in range(len(SIZES) - 1):
            scores = [sum(acts[l][i] * weights[l][i][j] for i in range(SIZES[l])) for j in range(SIZES[l + 1])]
            # Winner-take-most: the top few of each layer fire, one output wins.
            keep = 1 if l == len(SIZES) - 2 else 3
            top = sorted(range(len(scores)), key=lambda j: -scores[j])[:keep]
            acts.append([1 if j in top else 0 for j in range(SIZES[l + 1])])

        # Which layer is "live" at this moment of the pass.
        live_layer = min(3, k // 2)
        edge_phase = k % 2 == 1 and live_layer < 3

        for l in range(len(SIZES) - 1):
            for i in range(SIZES[l]):
                for j in range(SIZES[l + 1]):
                    if l < live_layer or (l == live_layer and edge_phase):
                        if acts[l][i] and acts[l + 1][j]:
                            frame.line(LAYER_X[l], node_y(l, i), LAYER_X[l + 1], node_y(l + 1, j),
                                       C.WHITE if l == live_layer else C.BLUE)
        for l in range(len(SIZES)):
            for i in range(SIZES[l]):
                lit = acts[l][i] and l <= live_layer
                color = LAYER_COLORS[l] if lit else C.BLUE
                frame.rect(LAYER_X[l] - 1, node_y(l, i) - 1, 3, 3, color, fill=True)
                if lit and l == live_layer:
                    frame.pixel(LAYER_X[l], node_y(l, i), C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/neural_net.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
