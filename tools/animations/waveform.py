#!/usr/bin/env python3
"""
Oscilloscope -- a green phosphor trace sweeps across the screen showing a
complex waveform built from three sine components.  The phases shift each
frame so the waveform morphs over time.  A faint grid of BLUE dots and a
dashed center line give the CRT-scope look.  The trace uses GLOW persistence:
current position WHITE, recent CYAN, older BLUE.

53 frames, seamless loop, DELAY=60 for that fast CRT feel.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 60
WIDTH = 96
HEIGHT = 16

# Three sine components with different frequencies.
# Frequencies chosen so phase advance per frame makes a seamless 53-frame loop.
# Each component's phase advances by (2*pi * cycles / FRAMES) per frame.
COMPONENTS = [
    # (amplitude_weight, frequency_in_x, cycles_per_loop)
    (0.50, 0.08, 3),   # slow, dominant wave
    (0.30, 0.18, 7),   # medium harmonic
    (0.20, 0.35, 13),  # fast ripple
]


def waveform_y(x, phases):
    """Compute the waveform value at column x, returning a float in [0, HEIGHT-1]."""
    total = 0.0
    for amp, freq, _cycles in COMPONENTS:
        phase = phases[COMPONENTS.index((amp, freq, _cycles))]
        total += amp * math.sin(freq * x + phase)
    # total is in roughly [-1, 1]; map to pixel rows with margin
    margin = 1.5
    y = (total + 1.0) / 2.0 * (HEIGHT - 1 - 2 * margin) + margin
    return max(0, min(HEIGHT - 1, y))


def compute_phases(frame_index):
    """Phase offsets for each component at a given frame."""
    phases = []
    for _amp, _freq, cycles in COMPONENTS:
        phase = 2.0 * math.pi * cycles * frame_index / FRAMES
        phases.append(phase)
    return phases


def draw_grid(frame):
    """Draw the oscilloscope grid: dots every 12 columns and 4 rows,
    plus a dashed center line at y=8."""
    for gx in range(0, WIDTH, 12):
        for gy in range(0, HEIGHT, 4):
            frame.pixel(gx, gy, C.BLUE)
    # Dashed center line at y=8: draw every other pair of pixels
    center_y = HEIGHT // 2
    for x in range(WIDTH):
        if (x // 2) % 2 == 0:
            frame.pixel(x, center_y, C.BLUE)


def build():
    anim = Animation(delay=DELAY)

    # Pre-compute all waveform y-values for every frame.
    all_ys = []
    for f in range(FRAMES):
        phases = compute_phases(f)
        ys = [waveform_y(x, phases) for x in range(WIDTH)]
        all_ys.append(ys)

    for f in range(FRAMES):
        frame = anim.frame()

        # Grid first (background layer).
        draw_grid(frame)

        # Phosphor persistence: draw older trails first so brighter ones
        # paint over them.
        trail_colors = [C.BLUE, C.CYAN, C.GREEN]
        trail_offsets = [2, 1, 0]  # 2 frames ago, 1 frame ago, current

        for trail_idx, offset in enumerate(trail_offsets):
            src = (f - offset) % FRAMES
            ys = all_ys[src]
            color = trail_colors[trail_idx]

            if offset == 2:
                # Oldest trail: just dots at each column
                for x in range(WIDTH):
                    frame.pixel(x, round(ys[x]), color)
            else:
                # Draw connected line segments for current and recent trail.
                for x in range(WIDTH - 1):
                    y0 = round(ys[x])
                    y1 = round(ys[x + 1])
                    frame.line(x, y0, x + 1, y1, color)

        # Brighten the very tip of the trace (rightmost few columns) to WHITE
        # for the "beam" effect.
        ys_current = all_ys[f]
        for x in range(WIDTH - 4, WIDTH):
            frame.pixel(x, round(ys_current[x]), C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/waveform.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
