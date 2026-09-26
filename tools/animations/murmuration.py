#!/usr/bin/env python3
"""
Murmuration -- starlings flocking at dusk, and the hawk that scatters them.

Sixty boids follow Craig Reynolds' three rules -- keep apart, match your
neighbours' heading, drift toward their centre -- and nothing else: the
flock's swirling, stretching shape is not drawn, it emerges. They fly as
black specks against a sunset (blue sky, a magenta band, red at the horizon,
a yellow sun sinking into a treeline), the one way to show a bird in 3 bits
that still reads as a silhouette.

Halfway through, a hawk -- a larger black chevron -- cuts across. Boids
within sight of it add a fourth rule, flee, so a hole tears open in the flock
and seals behind the hawk as it passes.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
W, H = 96, 16
BIRDS = 60
SUBSTEPS = 3
SEED = 11

# Vertical distances count double: the sky is only 16 rows tall, so the
# flock needs to feel squeezed less than it is.
YS = 2.0


def sky(x, y):
    if y >= 12:
        return C.RED
    if y >= 9:
        return C.MAGENTA
    return C.BLUE


def treeline():
    rnd = random.Random(4)
    tops = []
    h = 15.0
    for x in range(W):
        h += rnd.uniform(-0.7, 0.7)
        h = max(14.0, min(15.6, h))
        tops.append(int(h))
    return tops


TREES = treeline()
SUN = (70, 12.5, 3.6)


def hawk_at(step):
    """The hawk's position, or None, at a sim step."""
    start, end = 22 * SUBSTEPS, 44 * SUBSTEPS
    if not start <= step <= end:
        return None
    f = (step - start) / (end - start)
    return (-8 + f * (W + 16), 3 + 6 * math.sin(f * math.pi * 1.3))


def simulate():
    rnd = random.Random(SEED)
    boids = []
    for _ in range(BIRDS):
        a = rnd.uniform(-0.4, 0.4)
        boids.append(
            [rnd.uniform(20, 60), rnd.uniform(3, 10), math.cos(a), math.sin(a) * 0.3]
        )
    frames = []
    total = (FRAMES + 20) * SUBSTEPS
    for step in range(total):
        hawk = hawk_at(step - 20 * SUBSTEPS)
        new = []
        for i, (x, y, vx, vy) in enumerate(boids):
            cx = cy = ax = ay = sx = sy = 0.0
            n = 0
            for j, (x2, y2, vx2, vy2) in enumerate(boids):
                if i == j:
                    continue
                dx = (x2 - x + W / 2) % W - W / 2
                dy = (y2 - y) * YS
                d2 = dx * dx + dy * dy
                if d2 < 100:
                    n += 1
                    cx += dx
                    cy += dy / YS
                    ax += vx2
                    ay += vy2
                    if d2 < 9:
                        sx -= dx / (d2 + 0.1)
                        sy -= dy / YS / (d2 + 0.1)
            if n:
                vx += 0.004 * cx / n + 0.06 * (ax / n - vx)
                vy += 0.012 * cy / n + 0.06 * (ay / n - vy)
            vx += 0.08 * sx
            vy += 0.08 * sy
            if hawk:
                dx = (x - hawk[0] + W / 2) % W - W / 2
                dy = (y - hawk[1]) * YS
                d = math.hypot(dx, dy)
                if d < 12:
                    push = 0.35 * (12 - d) / 12
                    vx += push * dx / (d + 0.1)
                    vy += push * dy / (d + 0.1)
            # Stay inside the sky, above the trees.
            if y < 1.5:
                vy += 0.08
            if y > 8:
                vy -= 0.1 * (y - 8)
            vy += 0.02 * math.sin(step * 0.05 + x * 0.1)  # gusts
            speed = math.hypot(vx, vy)
            lo, hi = 0.35, 0.9
            if speed > hi:
                vx, vy = vx * hi / speed, vy * hi / speed
            elif speed < lo:
                vx, vy = vx * lo / (speed + 1e-6), vy * lo / (speed + 1e-6)
            new.append([(x + vx / SUBSTEPS * 2) % W, y + vy / SUBSTEPS * 2, vx, vy])
        boids = new
        if step >= 20 * SUBSTEPS and step % SUBSTEPS == 0:
            frames.append(([(b[0], b[1]) for b in boids], hawk))
    return frames[:FRAMES]


def main():
    anim = Animation(delay=DELAY)
    for birds, hawk in simulate():
        frame = anim.frame()
        sx, sy, sr = SUN
        for x in range(W):
            for y in range(H):
                if y >= TREES[x]:
                    continue
                if (x - sx) ** 2 + ((y - sy) * 1.0) ** 2 < sr * sr:
                    frame.pixel(x, y, C.YELLOW)
                else:
                    frame.pixel(x, y, sky(x, y))
        for x, y in birds:
            frame.pixel(round(x) % W, round(y), C.BLACK)
        if hawk:
            hx, hy = round(hawk[0]), round(hawk[1])
            for dx, dy in ((0, 0), (-1, -1), (1, -1), (-2, -2), (2, -2), (0, 1)):
                frame.pixel(hx + dx, hy + dy, C.BLACK)
    out = Path(__file__).resolve().parents[2] / "src/sample/murmuration.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
