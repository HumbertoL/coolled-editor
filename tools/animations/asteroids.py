#!/usr/bin/env python3
"""
Asteroids -- the 1979 vector game, played by a ship that never misses.

Everything is outlines, as on Atari's vector monitor: jagged rocks drawn as
closed polygons, and a triangular ship at the centre that turns to face the
nearest rock, leads its shot by the rock's drift, and fires. A hit splits a
big rock into two medium ones, a medium into two small, and a small bursts
into sparks. The whole field wraps at the edges, as the original did, and
the score ticks up in the corner.

Rocks are white, the ship yellow with a red thrust flicker, sparks red and
yellow. Seeded, so every render plays the same game.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
W, H = 96, 16
SHIP = (48.0, 8.0)
SIZES = {3: 4.2, 2: 2.6, 1: 1.5}
POINTS = {3: 20, 2: 50, 1: 100}
BULLET_SPEED = 3.0
TURN_RATE = math.radians(40)
COOLDOWN = 3

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
}


class Rock:
    def __init__(self, rnd, x, y, size, vx=None, vy=None):
        self.x, self.y, self.size = x, y, size
        angle = rnd.uniform(0, 2 * math.pi)
        speed = {3: 0.35, 2: 0.55, 1: 0.8}[size]
        self.vx = vx if vx is not None else math.cos(angle) * speed
        self.vy = vy if vy is not None else math.sin(angle) * speed * 0.5
        self.spin = rnd.uniform(-0.15, 0.15)
        self.rot = rnd.uniform(0, 6.3)
        n = {3: 9, 2: 7, 1: 5}[size]
        self.shape = [
            (2 * math.pi * i / n, SIZES[size] * rnd.uniform(0.7, 1.1))
            for i in range(n)
        ]

    def move(self):
        self.x = (self.x + self.vx) % W
        self.y = (self.y + self.vy) % H
        self.rot += self.spin


def wrap_delta(a, b, span):
    return (b - a + span / 2) % span - span / 2


def line(frame, x0, y0, x1, y1, color):
    """Anti-seam line: draws with wraparound on both axes."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 1
    for i in range(steps + 1):
        t = i / steps
        frame.pixel(
            round(x0 + (x1 - x0) * t) % W, round(y0 + (y1 - y0) * t) % H, color
        )


def draw_rock(frame, rock):
    pts = [
        (rock.x + math.cos(a + rock.rot) * r, rock.y + math.sin(a + rock.rot) * r)
        for a, r in rock.shape
    ]
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        line(frame, x0, y0, x1, y1, C.WHITE)


def draw_ship(frame, heading, thrust):
    x, y = SHIP
    nose = (x + math.cos(heading) * 4, y + math.sin(heading) * 4)
    left = (x + math.cos(heading + 2.5) * 3, y + math.sin(heading + 2.5) * 3)
    right = (x + math.cos(heading - 2.5) * 3, y + math.sin(heading - 2.5) * 3)
    for a, b in ((nose, left), (nose, right), (left, right)):
        line(frame, a[0], a[1], b[0], b[1], C.YELLOW)
    if thrust:
        tail = (x - math.cos(heading) * 3.2, y - math.sin(heading) * 3.2)
        frame.pixel(round(tail[0]), round(tail[1]), C.RED)


def draw_score(frame, score):
    text = f"{score:05d}"
    for i, ch in enumerate(text):
        for r, row in enumerate(MINI[ch]):
            for c, cell in enumerate(row):
                if cell == "#":
                    frame.pixel(1 + i * 4 + c, 1 + r, C.GREEN)


def main():
    rnd = random.Random(8)
    rocks = [
        Rock(rnd, 30, 4, 3),
        Rock(rnd, 70, 11, 3),
        Rock(rnd, 10, 12, 3),
        Rock(rnd, 62, 3, 2),
        Rock(rnd, 88, 6, 3),
    ]
    bullets = []  # [x, y, vx, vy, life]
    sparks = []  # [x, y, vx, vy, life]
    heading = -math.pi / 2
    cooldown = 0
    score = 0
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        # Aim: nearest rock, led by its drift over the bullet's flight time.
        target = None
        best = 1e9
        for rock in rocks:
            dx = wrap_delta(SHIP[0], rock.x, W)
            dy = wrap_delta(SHIP[1], rock.y, H)
            d = math.hypot(dx, dy)
            if d < best:
                best, target = d, (dx, dy, rock)
        thrust = False
        if target:
            dx, dy, rock = target
            t = best / BULLET_SPEED
            want = math.atan2(dy + rock.vy * t, dx + rock.vx * t)
            diff = (want - heading + math.pi) % (2 * math.pi) - math.pi
            heading += max(-TURN_RATE, min(TURN_RATE, diff))
            thrust = abs(diff) > TURN_RATE
            if abs(diff) < math.radians(12) and cooldown == 0 and best < 26:
                bullets.append(
                    [
                        SHIP[0] + math.cos(heading) * 3,
                        SHIP[1] + math.sin(heading) * 3,
                        math.cos(heading) * BULLET_SPEED,
                        math.sin(heading) * BULLET_SPEED,
                        9,
                    ]
                )
                cooldown = COOLDOWN
        cooldown = max(0, cooldown - 1)

        for rock in rocks:
            rock.move()
        # Bullets move in sub-steps so they cannot tunnel through small rocks.
        for b in bullets:
            for _ in range(3):
                b[0] = (b[0] + b[2] / 3) % W
                b[1] = (b[1] + b[3] / 3) % H
                hit = None
                for rock in rocks:
                    if (
                        math.hypot(wrap_delta(b[0], rock.x, W), wrap_delta(b[1], rock.y, H))
                        < SIZES[rock.size] + 0.5
                    ):
                        hit = rock
                        break
                if hit:
                    rocks.remove(hit)
                    score += POINTS[hit.size]
                    b[4] = 0
                    if hit.size > 1:
                        for s in (-1, 1):
                            ang = math.atan2(b[3], b[2]) + s * math.pi / 2
                            sp = 0.5 if hit.size == 3 else 0.75
                            rocks.append(
                                Rock(
                                    rnd,
                                    hit.x,
                                    hit.y,
                                    hit.size - 1,
                                    math.cos(ang) * sp + hit.vx * 0.5,
                                    math.sin(ang) * sp * 0.5 + hit.vy * 0.5,
                                )
                            )
                    for k in range(10 if hit.size == 1 else 6):
                        a = rnd.uniform(0, 2 * math.pi)
                        sp = rnd.uniform(0.5, 1.6)
                        sparks.append(
                            [hit.x, hit.y, math.cos(a) * sp, math.sin(a) * sp * 0.6, rnd.randint(3, 6)]
                        )
                    break
            b[4] -= 1
        bullets = [b for b in bullets if b[4] > 0]
        for s in sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1
        sparks = [s for s in sparks if s[4] > 0]
        # A fresh wave drifts in from the edge when the field runs low.
        if len(rocks) < 4:
            rocks.append(Rock(rnd, rnd.choice([0, 95]), rnd.uniform(0, 15), 3))

        frame = anim.frame()
        for rock in rocks:
            draw_rock(frame, rock)
        frame.rect(0, 0, 21, 7, C.BLACK, fill=True)
        draw_score(frame, score)
        for b in bullets:
            frame.pixel(round(b[0]) % W, round(b[1]) % H, C.WHITE)
        for s in sparks:
            frame.pixel(round(s[0]) % W, round(s[1]) % H, C.YELLOW if s[4] > 2 else C.RED)
        draw_ship(frame, heading, thrust and index % 2 == 0)
    out = Path(__file__).resolve().parents[2] / "src/sample/asteroids.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
