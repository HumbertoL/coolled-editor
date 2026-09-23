#!/usr/bin/env python3
"""
Traffic Wave -- a phantom jam, out of nothing, going the wrong way.

Five lanes of ring road, each an independent Nagel-Schreckenberg model: every
car speeds up by one if it can, slows to the gap in front if it must, now and
then dawdles for no reason, and moves. The ends of the panel join, so every
lane is a loop. Cars are coloured by speed -- green cruising, yellow slowing,
red stopped -- and every so often one driver in one lane taps the brakes for
a moment and lights up white. Nothing is in the way, but the cars behind pile
up anyway, and a red knot of stopped traffic drifts leftward against the
flow: cars leave its front and join its back, so the jam travels backwards
while every car in it goes forwards.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 1992  # Nagel & Schreckenberg's paper year
RING = 96
CAR_LEN = 3
VMAX = 4
CARS_PER_LANE = 13
DAWDLE = 0.12
WARMUP = 40
BRAKE_FRAMES = 4
LANE_ROWS = [1, 4, 7, 10, 13]  # each lane is two rows tall
# (lane, frame the driver brakes, x the braking car is nearest)
BRAKES = [(2, 2, 80), (0, 9, 72), (4, 16, 86), (1, 23, 76), (3, 30, 82)]


def speed_color(v):
    if v == 0:
        return C.RED
    if v < VMAX - 1:
        return C.YELLOW
    return C.GREEN


class Lane:
    def __init__(self, rng):
        self.rng = rng
        spacing = RING / CARS_PER_LANE
        self.pos = [round(i * spacing + rng.uniform(-1, 1)) % RING for i in range(CARS_PER_LANE)]
        self.vel = [VMAX] * CARS_PER_LANE
        self.forced = {}  # car index -> steps left held at zero

    def step(self):
        n = len(self.pos)
        new_vel = []
        for i in range(n):
            ahead = (i + 1) % n
            gap = (self.pos[ahead] - self.pos[i]) % RING - CAR_LEN
            v = min(self.vel[i] + 1, VMAX, gap)
            if v > 0 and self.rng.random() < DAWDLE:
                v -= 1
            if self.forced.get(i, 0) > 0:
                v = 0
                self.forced[i] -= 1
            new_vel.append(max(0, v))
        self.vel = new_vel
        self.pos = [(p + v) % RING for p, v in zip(self.pos, self.vel)]

    def brake_near(self, x):
        i = min(range(len(self.pos)), key=lambda k: (self.pos[k] - x) % RING)
        self.forced[i] = BRAKE_FRAMES
        return i


def build():
    rng = random.Random(SEED)
    lanes = [Lane(rng) for _ in LANE_ROWS]
    for _ in range(WARMUP):
        for lane in lanes:
            lane.step()

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        for lane_no, at, x in BRAKES:
            if index == at:
                lanes[lane_no].brake_near(x)
        for lane in lanes:
            lane.step()

        frame = anim.frame()
        # Road: solid edges, dashed lane lines.
        frame.hline(0, 0, RING, C.BLUE)
        frame.hline(0, 15, RING, C.BLUE)
        for y in (3, 6, 9, 12):
            for x in range(0, RING, 4):
                frame.hline(x, y, 2, C.BLUE)
        for lane, top in zip(lanes, LANE_ROWS):
            for i, (p, v) in enumerate(zip(lane.pos, lane.vel)):
                color = C.WHITE if lane.forced.get(i, 0) > 0 else speed_color(v)
                # A car fills three cells but is drawn two long, so a queue
                # of bumper-to-bumper cars still reads as separate cars.
                for k in range(CAR_LEN - 1):
                    x = (p - k) % RING
                    frame.pixel(x, top, color)
                    frame.pixel(x, top + 1, color)
            # Drop finished brake orders.
            lane.forced = {i: n for i, n in lane.forced.items() if n > 0}
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/traffic_wave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
