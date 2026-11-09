#!/usr/bin/env python3
"""
Three-body figure eight -- three equal masses chasing one another round a
single figure-of-eight, under nothing but their mutual gravity.

The three-body problem is the textbook example of chaos, but it has a few
exact periodic solutions. This is the one found numerically by Cris Moore in
1993 and proved to exist by Chenciner and Montgomery in 2000: all three
bodies follow the same curve, a third of a period apart.

Nothing here is drawn along a precomputed curve. The script integrates
Newtonian gravity (G = m = 1) from the published initial conditions with a
fourth-order Runge-Kutta step, and the eight emerges. The orbit happens to be
about three times wider than tall, which suits the panel. One loop is one
period, so it is seamless; the script asserts the integration really does
close.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
PERIOD = 6.32591398
SUBSTEPS = 8          # recorded positions per frame, for unbroken trails
FINE = 50             # integrator steps per recorded position
TRAIL = 56            # recorded positions kept behind each body
BODY_COLORS = [C.RED, C.GREEN, C.YELLOW]

X1, Y1 = 0.97000436, -0.24308753
VX3, VY3 = -0.93240737, -0.86473146
START = [
    X1, Y1, -X1, -Y1, 0.0, 0.0,
    -VX3 / 2, -VY3 / 2, -VX3 / 2, -VY3 / 2, VX3, VY3,
]


def derivative(state):
    out = state[6:] + [0.0] * 6
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            dx = state[2 * j] - state[2 * i]
            dy = state[2 * j + 1] - state[2 * i + 1]
            inverse_cube = (dx * dx + dy * dy) ** -1.5
            out[6 + 2 * i] += dx * inverse_cube
            out[7 + 2 * i] += dy * inverse_cube
    return out


def rk4(state, dt):
    def shifted(k, scale):
        return [s + scale * d for s, d in zip(state, k)]

    k1 = derivative(state)
    k2 = derivative(shifted(k1, dt / 2))
    k3 = derivative(shifted(k2, dt / 2))
    k4 = derivative(shifted(k3, dt))
    return [
        s + dt / 6 * (a + 2 * b + 2 * c + d)
        for s, a, b, c, d in zip(state, k1, k2, k3, k4)
    ]


def orbit():
    """Positions of all three bodies at every recorded step of one period."""
    total = FRAMES * SUBSTEPS
    dt = PERIOD / (total * FINE)
    state = list(START)
    track = []
    for _ in range(total):
        track.append(state[:6])
        for _ in range(FINE):
            state = rk4(state, dt)
    drift = max(abs(a - b) for a, b in zip(state, START))
    if drift > 1e-4:
        raise AssertionError(f"orbit did not close: off by {drift:.2e}")
    return track


def to_panel(x, y):
    return round(47.5 + x * 42), round(7.5 - y * 19)


def build():
    track = orbit()
    total = len(track)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        now = index * SUBSTEPS
        # Oldest trail first, so newer segments and the bodies sit on top.
        for back in range(TRAIL, 0, -1):
            step = track[(now - back) % total]
            for body in range(3):
                color = C.BLUE if back > TRAIL // 2 else BODY_COLORS[body]
                frame.pixel(*to_panel(step[2 * body], step[2 * body + 1]), color)
        for body in range(3):
            x, y = to_panel(track[now][2 * body], track[now][2 * body + 1])
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                frame.pixel(x + dx, y + dy, BODY_COLORS[body])
            frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/three_body.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
