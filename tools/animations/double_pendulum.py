#!/usr/bin/env python3
"""
Double Pendulum -- three of them, released a thousandth of a radian apart.

A pendulum hung from a pendulum is the textbook chaotic system: perfectly
deterministic, yet any difference in where it starts grows exponentially.
Here three share one pivot -- red, green and blue -- started with their upper
arms 0.001 rad apart. For the first seconds they overlap exactly and read as
a single white pendulum (red + green + blue light adds to white on the
panel), then colour fringes appear as they peel apart, and soon each is
flailing on its own. Each lower bob leaves a short trail.

On the left, a strip chart records each lower arm's angle over time, the
three traces drawn on top of one another until they fork. On the right, the
spread between them in degrees climbs from a fraction of a
degree, green, through yellow, to red and over a hundred.

Integrated with RK4 at 40 steps a frame; equal masses and arm lengths.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
W, H = 96, 16
PIVOT = (48.0, 7.5)
ARM = 3.6  # pixels per arm on screen
G = 9.81
L = 1.0
DT = 0.1  # simulated seconds per frame
SUBSTEPS = 40
START = (math.radians(150), math.radians(170))
EPS = 0.001
CHANNELS = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
CHART = (0, 38)  # strip chart columns
READOUT_X = 60
TRAIL = 6
WARMUP = 0  # frames simulated before the loop starts


def deriv(state):
    t1, t2, w1, w2 = state
    d = t1 - t2
    den = 3 - math.cos(2 * d)
    a1 = (
        -G / L * (3 * math.sin(t1) + math.sin(t1 - 2 * t2))
        - 2 * math.sin(d) * (w2 * w2 + w1 * w1 * math.cos(d))
    ) / den
    a2 = (
        2 * math.sin(d) * (2 * w1 * w1 + 2 * G / L * math.cos(t1) + w2 * w2 * math.cos(d))
    ) / den
    return (w1, w2, a1, a2)


def rk4(state, h):
    def add(s, k, f):
        return tuple(a + b * f for a, b in zip(s, k))

    k1 = deriv(state)
    k2 = deriv(add(state, k1, h / 2))
    k3 = deriv(add(state, k2, h / 2))
    k4 = deriv(add(state, k3, h))
    return tuple(
        s + h / 6 * (a + 2 * b + 2 * c + d) for s, a, b, c, d in zip(state, k1, k2, k3, k4)
    )


def bobs(state):
    t1, t2 = state[0], state[1]
    x1 = PIVOT[0] + ARM * math.sin(t1)
    y1 = PIVOT[1] + ARM * math.cos(t1)
    return (x1, y1), (x1 + ARM * math.sin(t2), y1 + ARM * math.cos(t2))


def add_light(frame, x, y, channel):
    x, y = int(round(x)), int(round(y))
    if not frame.in_bounds(x, y):
        return
    old = frame.get(x, y)
    frame.pixel(x, y, tuple(max(a, b) for a, b in zip(old, channel)))


def line(frame, a, b, channel):
    steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
    seen = set()
    for i in range(steps + 1):
        t = i / steps
        p = (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t))
        if p not in seen:
            seen.add(p)
            add_light(frame, p[0], p[1], channel)


MINI = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    ".": ["...", "...", "...", "...", ".#."],
}


def mini_text(frame, text, x, y, color):
    for ch in text:
        glyph = MINI[ch]
        width = 1 if ch == "." else 3
        for r, row in enumerate(glyph):
            for c, cell in enumerate(row[:width] if ch != "." else row[1:2]):
                if cell == "#":
                    frame.pixel(x + c, y + r, color)
        x += width + 1


def main():
    states = [
        (START[0] + i * EPS, START[1], 0.0, 0.0) for i in range(3)
    ]
    history = []  # per frame: [theta2 per pendulum]
    trails = [[] for _ in range(3)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES + WARMUP):
        for _ in range(SUBSTEPS):
            states = [rk4(s, DT / SUBSTEPS) for s in states]
        history.append([s[1] for s in states])
        for i, s in enumerate(states):
            trails[i] = (trails[i] + [bobs(s)[1]])[-TRAIL:]
        if index < WARMUP:
            continue
        frame = anim.frame()
        # Strip chart: newest sample at the right edge of the chart.
        x0, x1 = CHART
        span = x1 - x0
        recent = history[-span:]
        for k in range(1, len(recent)):
            x = x1 - len(recent) + k
            for i in range(3):
                ya = 7.5 + 7 * math.sin(recent[k - 1][i])
                yb = 7.5 + 7 * math.sin(recent[k][i])
                line(frame, (x - 1, ya), (x, yb), CHANNELS[i])
        frame.vline(x1 + 1, 0, H, C.BLUE)
        # Pendulums.
        for i, s in enumerate(states):
            (b1, b2) = bobs(s)
            line(frame, PIVOT, b1, CHANNELS[i])
            line(frame, b1, b2, CHANNELS[i])
            for p in trails[i][:-1]:
                add_light(frame, p[0], p[1], CHANNELS[i])
        frame.pixel(int(PIVOT[0]), int(PIVOT[1]), C.WHITE)
        # Spread readout.
        angles = [math.degrees(s[0]) for s in states]
        a2 = [math.degrees(s[1]) for s in states]
        spread = max(
            abs((a - b + 180) % 360 - 180)
            for vals in (angles, a2)
            for a in vals
            for b in vals
        )
        frame.vline(READOUT_X - 3, 0, H, C.BLUE)
        frame.text("DIFF", x=READOUT_X, y=0, color=C.CYAN)
        text = f"{spread:.2f}" if spread < 10 else f"{spread:.0f}"
        colour = C.GREEN if spread < 1 else C.YELLOW if spread < 30 else C.RED
        frame.text(text, x=READOUT_X, y=9, color=colour)
    out = Path(__file__).resolve().parents[2] / "src/sample/double_pendulum.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
