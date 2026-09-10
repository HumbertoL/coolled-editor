#!/usr/bin/env python3
"""
tea_heartbeat -- Company pulse dashboard with beating heart, TEA wordmark,
and a live messages-per-second ticker.
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
SEED = 7

BEAT_PERIOD = 8  # heart beats every 8 frames


def build():
    rng = random.Random(SEED)

    # Pre-generate metric values: fluctuate around 1.2K/s
    base_rate = 1200
    metrics = []
    for i in range(FRAMES):
        # On beat frames, spike the metric up
        beat_phase = i % BEAT_PERIOD
        if beat_phase == 0:
            jitter = rng.randint(80, 150)
        elif beat_phase == 1:
            jitter = rng.randint(40, 80)
        else:
            jitter = rng.randint(-30, 30)
        metrics.append(base_rate + jitter)

    anim = Animation(delay=DELAY)

    for i in range(FRAMES):
        f = anim.frame()
        beat_phase = i % BEAT_PERIOD
        is_beat = beat_phase == 0
        is_post_beat = beat_phase == 1

        # --- Left third: beating heart ---
        heart_x, heart_y = 4, 4
        if is_beat:
            # Big bright beat: draw heart glyph in WHITE and a halo
            f.glyph('+HEART', heart_x, heart_y, C.WHITE)
            # Draw a slightly larger halo around heart position
            for dx in range(-1, 7):
                for dy in range(-1, 9):
                    px, py = heart_x + dx, heart_y + dy
                    if f.in_bounds(px, py) and f.get(px, py) == C.BLACK:
                        # Sparse halo
                        if (dx + dy) % 3 == 0:
                            f.pixel(px, py, C.GREEN)
        elif is_post_beat:
            # Settling: green heart with cyan edges
            f.glyph('+HEART', heart_x, heart_y, C.CYAN)
        else:
            # Resting: green heart
            f.glyph('+HEART', heart_x, heart_y, C.GREEN)

        # --- Pulse line on beat frames ---
        if is_beat:
            # Draw an ECG-style pulse line from heart to text area
            line_y = heart_y + 3  # middle of heart
            for px in range(10, 30):
                # Simple ECG shape: flat, spike up, spike down, flat
                rel = px - 10
                if 6 <= rel <= 8:
                    spike_y = line_y - (3 if rel == 7 else 1)
                    f.pixel(px, spike_y, C.GREEN)
                    f.pixel(px, line_y, C.GREEN)
                elif 9 <= rel <= 10:
                    spike_y = line_y + (2 if rel == 9 else 1)
                    f.pixel(px, spike_y, C.GREEN)
                    f.pixel(px, line_y, C.GREEN)
                else:
                    f.pixel(px, line_y, C.GREEN)
        elif is_post_beat:
            # Fading pulse line
            line_y = heart_y + 3
            for px in range(10, 25):
                if px % 2 == 0:
                    f.pixel(px, line_y, C.BLUE)

        # --- Center: "TEA" text ---
        # Place TEA centered roughly in the middle band (x ~33-62)
        f.text('TEA', 'center', 4, C.WHITE)

        # --- Right third: metric display ---
        rate = metrics[i]
        if rate >= 1000:
            label = f'{rate / 1000:.1f}K'
        else:
            label = str(rate)
        # Draw the rate value
        metric_x = 72
        metric_color = C.WHITE if is_beat else C.CYAN
        f.text(label, metric_x, 1, metric_color)

        # "/s" below
        f.text('/s', metric_x + 6, 9, C.BLUE)

        # Small bar graph below the metric showing recent activity
        bar_y = 12
        for b in range(8):
            idx = max(0, i - 7 + b)
            bar_h = max(1, min(4, (metrics[idx] - 1100) // 30))
            bar_color = C.GREEN if not (is_beat and b == 7) else C.WHITE
            for dy in range(bar_h):
                bx = metric_x + b * 3
                by = bar_y + (3 - dy)
                if f.in_bounds(bx, by):
                    f.pixel(bx, by, bar_color)
                    if f.in_bounds(bx + 1, by):
                        f.pixel(bx + 1, by, bar_color)

    return anim


if __name__ == '__main__':
    animation = build()
    out = Path(__file__).resolve().parents[2] / 'src/sample/tea_heartbeat.jt'
    animation.save(out)
    print(f'{out.name}: {animation.describe()}')
