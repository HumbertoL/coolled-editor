#!/usr/bin/env python3
"""
tea_network -- Network effect visualization: a single sender's message
cascades through four generations of recipients, filling the display.
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
SEED = 13

# Generation colors
GEN_COLORS = [C.WHITE, C.CYAN, C.GREEN, C.YELLOW]

# Timing: when each generation activates and starts forwarding
GEN_START = [0, 10, 20, 30, 40]  # sender, gen1, gen2, gen3, gen4
PULSE_START = 50  # all-pulse phase


def build():
    rng = random.Random(SEED)

    # Sender node
    sender = (4, 8)

    # Generate recipient nodes in 4 columns
    columns = [20, 40, 60, 80]
    generations = []  # list of lists of (x, y)
    for col_idx, col_x in enumerate(columns):
        count = 5 + col_idx * 3  # 5, 8, 11, 14 nodes per column
        nodes = []
        used_ys = set()
        for _ in range(count):
            for _attempt in range(50):
                y = rng.randint(1, 14)
                if y not in used_ys:
                    used_ys.add(y)
                    break
            x = col_x + rng.randint(-3, 3)
            x = max(columns[col_idx] - 4, min(columns[col_idx] + 4, x))
            nodes.append((x, y))
        generations.append(nodes)

    # Pre-compute connections: each node in gen N connects to 1-3 nodes in gen N+1
    # Sender connects to all gen-0 nodes
    connections = []  # list per generation: list of (src_idx, dst_idx) pairs
    # sender -> gen0
    sender_conns = [(0, j) for j in range(len(generations[0]))]
    connections.append(sender_conns)
    # gen0->gen1, gen1->gen2, gen2->gen3
    for g in range(3):
        gen_conns = []
        src_nodes = generations[g]
        dst_nodes = generations[g + 1]
        # Each dst gets at least one connection
        for di in range(len(dst_nodes)):
            si = rng.randint(0, len(src_nodes) - 1)
            gen_conns.append((si, di))
        connections.append(gen_conns)

    anim = Animation(delay=DELAY)

    for frame_idx in range(FRAMES):
        f = anim.frame()

        # Determine which generation is active
        def gen_progress(gen_idx):
            """Return 0-1 progress for this generation's activation."""
            start = GEN_START[gen_idx]
            end = GEN_START[gen_idx + 1] if gen_idx + 1 < len(GEN_START) else PULSE_START
            if frame_idx < start:
                return -1.0
            return min(1.0, (frame_idx - start) / max(1, end - start))

        # Draw sender
        sender_prog = gen_progress(0)
        if sender_prog >= 0:
            # Sender pulses in first phase
            if sender_prog < 0.5:
                brightness = C.ramp(C.GLOW, 0.5 + sender_prog)
            else:
                brightness = C.WHITE
            f.pixel(sender[0], sender[1], brightness)
            f.pixel(sender[0] + 1, sender[1], brightness)
            f.pixel(sender[0], sender[1] + 1, brightness)
            f.pixel(sender[0] + 1, sender[1] + 1, brightness)
            # Sender label
            if frame_idx < 6:
                f.pixel(sender[0] - 1, sender[1] - 1, C.BLUE)
                f.pixel(sender[0] + 2, sender[1] - 1, C.BLUE)

        # Draw each generation of recipients
        for g_idx, gen_nodes in enumerate(generations):
            prog = gen_progress(g_idx + 1)
            if prog < 0:
                # Not yet active -- draw as dim dots
                for nx, ny in gen_nodes:
                    f.pixel(nx, ny, C.BLUE)
                continue

            color = GEN_COLORS[min(g_idx, len(GEN_COLORS) - 1)]
            nodes_lit = int(len(gen_nodes) * min(1.0, prog * 1.5))

            for ni, (nx, ny) in enumerate(gen_nodes):
                if ni < nodes_lit:
                    # Lit node
                    node_color = color
                    if frame_idx >= PULSE_START:
                        # Pulse phase: flash white
                        pulse_phase = (frame_idx - PULSE_START + ni) % 6
                        node_color = C.WHITE if pulse_phase < 2 else color
                    f.pixel(nx, ny, node_color)
                else:
                    f.pixel(nx, ny, C.BLUE)

        # Draw traveling message dots between generations
        # Sender -> gen0
        s_prog = gen_progress(0)
        if 0.3 <= s_prog <= 1.0:
            dot_t = (s_prog - 0.3) / 0.7
            for si, di in connections[0]:
                sx, sy = sender
                dx, dy = generations[0][di]
                dot_x = int(sx + (dx - sx) * dot_t)
                dot_y = int(sy + (dy - sy) * dot_t)
                if f.in_bounds(dot_x, dot_y):
                    f.pixel(dot_x, dot_y, C.WHITE)

        # Gen-to-gen message dots
        for g in range(3):
            g_prog = gen_progress(g + 1)
            if 0.3 <= g_prog <= 0.9:
                dot_t = (g_prog - 0.3) / 0.6
                for si, di in connections[g + 1]:
                    sx, sy = generations[g][si % len(generations[g])]
                    dx, dy = generations[g + 1][di % len(generations[g + 1])]
                    dot_x = int(sx + (dx - sx) * dot_t)
                    dot_y = int(sy + (dy - sy) * dot_t)
                    if f.in_bounds(dot_x, dot_y):
                        f.pixel(dot_x, dot_y, GEN_COLORS[g])

        # Connection lines (subtle, behind dots) during active phases
        for g in range(4):
            g_prog = gen_progress(g)
            if g_prog >= 0.8:
                if g == 0:
                    # Sender to gen0
                    for si, di in connections[0]:
                        sx, sy = sender
                        dx, dy = generations[0][di]
                        # Just draw a few midpoint pixels for subtlety
                        mx = (sx + dx) // 2
                        my = (sy + dy) // 2
                        if f.in_bounds(mx, my) and f.get(mx, my) == C.BLACK:
                            f.pixel(mx, my, C.BLUE)
                elif g < 4:
                    for si, di in connections[g]:
                        sx, sy = generations[g - 1][si % len(generations[g - 1])]
                        dx, dy = generations[g][di % len(generations[g])]
                        mx = (sx + dx) // 2
                        my = (sy + dy) // 2
                        if f.in_bounds(mx, my) and f.get(mx, my) == C.BLACK:
                            f.pixel(mx, my, C.BLUE)

    return anim


if __name__ == '__main__':
    animation = build()
    out = Path(__file__).resolve().parents[2] / 'src/sample/tea_network.jt'
    animation.save(out)
    print(f'{out.name}: {animation.describe()}')
