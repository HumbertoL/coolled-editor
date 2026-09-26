#!/usr/bin/env python3
"""
Slime Mold -- Physarum polycephalum wiring up a network between oat flakes.

Physarum has no brain, yet given food at the positions of Tokyo's suburbs it
grows a network close to the real rail map. This is Jeff Jones' agent model
of it: 260 particles each sniff the chemical trail ahead-left, ahead and
ahead-right, turn toward the strongest, step, and deposit more. The trail
diffuses and decays. Nothing else -- the veins, and their thinning to the
efficient routes, emerge from that.

Six oat flakes (red) leak attractant. The agents start scattered at random
as faint blue noise; within a few frames it knits into a mesh of veins, the
veins that touch flakes thicken, and the network consolidates into a few
bright tubes between them while dead-end branches fade. Trail strength is
drawn BLUE (faint), GREEN, YELLOW, then WHITE for the busiest tubes.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
W, H = 96, 16
AGENTS = 260
SENSE_ANGLE = math.radians(45)
SENSE_DIST = 3.0
TURN = math.radians(40)
STEP = 0.8
DEPOSIT = 1.0
DECAY = 0.85
DIFFUSE = 0.2  # how much of each step's 3x3 blur mixes in
STEPS_PER_FRAME = 2
FOOD = [(22, 4), (40, 12), (55, 3), (70, 11), (86, 5), (12, 12)]


def main():
    rnd = random.Random(21)
    trail = [[0.0] * W for _ in range(H)]
    agents = []
    for _ in range(AGENTS):
        agents.append([rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0, 2 * math.pi)])

    def sense(x, y, heading):
        sx = int(x + math.cos(heading) * SENSE_DIST)
        sy = int(y + math.sin(heading) * SENSE_DIST)
        if 0 <= sx < W and 0 <= sy < H:
            return trail[sy][sx]
        return -1.0

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        for _ in range(STEPS_PER_FRAME):
            for agent in agents:
                x, y, h = agent
                f = sense(x, y, h)
                l = sense(x, y, h - SENSE_ANGLE)
                r = sense(x, y, h + SENSE_ANGLE)
                if f >= l and f >= r:
                    pass
                elif l > r:
                    h -= TURN
                elif r > l:
                    h += TURN
                else:
                    h += rnd.choice((-TURN, TURN))
                h += rnd.uniform(-0.15, 0.15)
                nx, ny = x + math.cos(h) * STEP, y + math.sin(h) * STEP
                if not (0 <= nx < W and 0 <= ny < H):
                    h += math.pi + rnd.uniform(-0.5, 0.5)
                    nx, ny = x, y
                agent[0], agent[1], agent[2] = nx, ny, h
                trail[int(ny)][int(nx)] += DEPOSIT
            for fx, fy in FOOD:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if 0 <= fy + dy < H:
                            trail[fy + dy][fx + dx] += 0.7
            # 3x3 blur, then decay.
            new = [[0.0] * W for _ in range(H)]
            for y in range(H):
                for x in range(W):
                    total = 0.0
                    n = 0
                    for dy in (-1, 0, 1):
                        yy = y + dy
                        if 0 <= yy < H:
                            row = trail[yy]
                            for dx in (-1, 0, 1):
                                xx = x + dx
                                if 0 <= xx < W:
                                    total += row[xx]
                                    n += 1
                    new[y][x] = (trail[y][x] * (1 - DIFFUSE) + total / n * DIFFUSE) * DECAY
            trail = new
        frame = anim.frame()
        for y in range(H):
            for x in range(W):
                v = trail[y][x]
                if v > 10:
                    frame.pixel(x, y, C.WHITE)
                elif v > 5:
                    frame.pixel(x, y, C.YELLOW)
                elif v > 2.5:
                    frame.pixel(x, y, C.GREEN)
                elif v > 1.1:
                    frame.pixel(x, y, C.BLUE)
        for fx, fy in FOOD:
            frame.rect(fx, fy, 2, 1, C.RED, fill=True)
    out = Path(__file__).resolve().parents[2] / "src/sample/slime_mold.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
