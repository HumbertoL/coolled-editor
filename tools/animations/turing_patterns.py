#!/usr/bin/env python3
"""
Turing Patterns -- the word TURING dissolving into the patterns he predicted.

In 1952 Alan Turing showed that two chemicals which react and diffuse at
different rates can break a uniform soup into spots and stripes -- his
guess at how a leopard gets its spots. This is the Gray-Scott version of that
system, run on the wrapping 96x16 panel. The inhibitor-rich soup is black;
the activator is seeded in the shape of the word, and the rest is chemistry:
the letters swell, then bud and branch into worms that crawl outward and
fold against each other until a fingerprint-like labyrinth packs the panel.

Colour is activator concentration through the GLOW ramp, BLUE at the fringe,
CYAN, then WHITE at the cores, with a MAGENTA rim where the activator is
advancing into fresh soup. The simulation runs faster as it goes -- a few
steps a frame at first, so the letters are readable, then hundreds.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16
# Diffusion is scaled down from the usual 1.0 / 0.5 so the pattern's
# wavelength is ~6px: at full strength one blob would fill all 16 rows.
DU, DV = 0.35, 0.175
FEED, KILL = 0.029, 0.057  # the labyrinth regime: worms that branch
HOLD = 5  # frames the plain word shows before it starts to react


def steps_for(frame):
    if frame < HOLD:
        return 0
    k = frame - HOLD
    return int(2 + 0.6 * k + 0.035 * k * k)


def seed():
    word = Canvas(W, H)
    word.text("TURING", x="center", y=4, color=C.WHITE, tracking=5)
    rnd = random.Random(3)
    u = [[1.0] * W for _ in range(H)]
    v = [[0.0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if word.get(x, y) != C.BLACK:
                # Strong seeds: 1px strokes of a weak seed just starve.
                u[y][x] = 0.2
                v[y][x] = 0.6 + rnd.uniform(-0.05, 0.05)
    return u, v


def step(u, v):
    nu = [[0.0] * W for _ in range(H)]
    nv = [[0.0] * W for _ in range(H)]
    for y in range(H):
        up, dn = u[(y - 1) % H], u[(y + 1) % H]
        vup, vdn = v[(y - 1) % H], v[(y + 1) % H]
        ur, vr = u[y], v[y]
        for x in range(W):
            xl, xr = (x - 1) % W, (x + 1) % W
            a, b = ur[x], vr[x]
            lap_u = (
                0.2 * (ur[xl] + ur[xr] + up[x] + dn[x])
                + 0.05 * (up[xl] + up[xr] + dn[xl] + dn[xr])
                - a
            )
            lap_v = (
                0.2 * (vr[xl] + vr[xr] + vup[x] + vdn[x])
                + 0.05 * (vup[xl] + vup[xr] + vdn[xl] + vdn[xr])
                - b
            )
            r = a * b * b
            nu[y][x] = a + (DU * lap_u - r + FEED * (1 - a))
            nv[y][x] = b + (DV * lap_v + r - (FEED + KILL) * b)
    return nu, nv


def colour(a, b):
    if b > 0.28:
        return C.WHITE
    if b > 0.20:
        return C.CYAN
    if b > 0.10:
        return C.BLUE
    if b > 0.05 and a < 0.6:
        return C.MAGENTA
    return C.BLACK


def main():
    u, v = seed()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        for _ in range(steps_for(index)):
            u, v = step(u, v)
        frame = anim.frame()
        if index < HOLD:
            frame.text("TURING", x="center", y=4, color=C.WHITE, tracking=5)
            continue
        for y in range(H):
            for x in range(W):
                frame.pixel(x, y, colour(u[y][x], v[y][x]))
    out = Path(__file__).resolve().parents[2] / "src/sample/turing_patterns.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
