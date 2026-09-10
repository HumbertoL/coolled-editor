#!/usr/bin/env python3
"""
Flock -- boids murmuration swooping across the panel.

~30 boids follow the classic rules: cohesion, separation, alignment.
White for dense clusters, cyan for medium, blue for sparse.
A long warmup lets the flock settle into natural patterns before recording.
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
SEED = 42

NUM_BOIDS = 30
WIDTH = 96
HEIGHT = 16
MAX_SPEED = 2.5
VISUAL_RANGE = 12.0
SEPARATION_DIST = 4.0
COHESION_WEIGHT = 0.008
SEPARATION_WEIGHT = 0.15
ALIGNMENT_WEIGHT = 0.06
WARMUP = 200


def wrap(val, limit):
    return val % limit


def dist_toroidal(x0, y0, x1, y1):
    dx = min(abs(x1 - x0), WIDTH - abs(x1 - x0))
    dy = min(abs(y1 - y0), HEIGHT - abs(y1 - y0))
    return math.sqrt(dx * dx + dy * dy)


def diff_toroidal(a, b, limit):
    d = b - a
    if d > limit / 2:
        d -= limit
    elif d < -limit / 2:
        d += limit
    return d


def clamp_speed(vx, vy):
    speed = math.sqrt(vx * vx + vy * vy)
    if speed > MAX_SPEED:
        vx = vx / speed * MAX_SPEED
        vy = vy / speed * MAX_SPEED
    return vx, vy


def step(boids):
    new_boids = []
    for i, (x, y, vx, vy) in enumerate(boids):
        cx, cy = 0.0, 0.0  # cohesion
        sx, sy = 0.0, 0.0  # separation
        ax, ay = 0.0, 0.0  # alignment
        neighbors = 0

        for j, (ox, oy, ovx, ovy) in enumerate(boids):
            if i == j:
                continue
            d = dist_toroidal(x, y, ox, oy)
            if d < VISUAL_RANGE:
                dx = diff_toroidal(x, ox, WIDTH)
                dy = diff_toroidal(y, oy, HEIGHT)
                cx += dx
                cy += dy
                ax += ovx
                ay += ovy
                neighbors += 1
                if d < SEPARATION_DIST and d > 0:
                    sx -= dx / d
                    sy -= dy / d

        if neighbors > 0:
            cx /= neighbors
            cy /= neighbors
            ax /= neighbors
            ay /= neighbors
            vx += cx * COHESION_WEIGHT
            vy += cy * COHESION_WEIGHT
            vx += ax * ALIGNMENT_WEIGHT
            vy += ay * ALIGNMENT_WEIGHT

        vx += sx * SEPARATION_WEIGHT
        vy += sy * SEPARATION_WEIGHT

        vx, vy = clamp_speed(vx, vy)
        nx = wrap(x + vx, WIDTH)
        ny = wrap(y + vy, HEIGHT)
        new_boids.append((nx, ny, vx, vy))
    return new_boids


def build():
    rng = random.Random(SEED)
    boids = []
    for _ in range(NUM_BOIDS):
        x = rng.uniform(0, WIDTH)
        y = rng.uniform(0, HEIGHT)
        angle = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(0.5, MAX_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        boids.append((x, y, vx, vy))

    # Warmup so the flock forms natural patterns
    for _ in range(WARMUP):
        boids = step(boids)

    anim = Animation(delay=DELAY)
    for _ in range(FRAMES):
        frame = anim.frame()

        # Count nearby boids for density-based coloring
        for bx, by, _, _ in boids:
            px, py = int(bx) % WIDTH, int(by) % HEIGHT
            nearby = 0
            for ox, oy, _, _ in boids:
                if dist_toroidal(bx, by, ox, oy) < 6.0:
                    nearby += 1
            if nearby >= 6:
                color = C.WHITE
            elif nearby >= 3:
                color = C.CYAN
            else:
                color = C.BLUE
            frame.pixel(px, py, color)

        boids = step(boids)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/flock.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
