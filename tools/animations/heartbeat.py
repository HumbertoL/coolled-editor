#!/usr/bin/env python3
"""
Heartbeat -- a cardiac monitor.

The trace is a fixed function of x (P wave, QRS spike, T wave, twice across
the panel) and a cursor sweeps left to right redrawing it, with a blank gap
just ahead of the cursor the way real monitors erase in front of the pen. The
newest few pixels are white, the rest green.

A heart on the left beats whenever the cursor passes a spike: it swaps to a
larger white bitmap for a frame, then back to the small red glyph. Two beats
per loop, and the cursor travels exactly the panel width, so it is seamless.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 90

TRACE_X0 = 12
SPAN = 84                    # 12..95
PERIOD = SPAN // 2           # two beats across the panel
BASELINE = 11
GAP = 8                      # unlit pixels ahead of the cursor
FRESH = 7                    # pixels behind the cursor drawn white

BIG_HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]


def ecg(p):
    """Vertical offset (positive = up) for a phase p in [0, 1)."""
    if 0.10 <= p < 0.18:
        return 1
    if 0.26 <= p < 0.28:
        return -1
    if 0.28 <= p < 0.30:
        return 5
    if 0.30 <= p < 0.32:
        return 9
    if 0.32 <= p < 0.34:
        return 4
    if 0.34 <= p < 0.37:
        return -2
    if 0.46 <= p < 0.60:
        return 2 if 0.50 <= p < 0.56 else 1
    return 0


def trace_y(x):
    return BASELINE - ecg(((x - TRACE_X0) % PERIOD) / PERIOD)


def spike_columns():
    return [TRACE_X0 + round(0.30 * PERIOD) + k * PERIOD for k in range(2)]


def build():
    anim = Animation(delay=DELAY)
    spikes = spike_columns()

    for index in range(FRAMES):
        frame = anim.frame()
        cursor = TRACE_X0 + SPAN * index / FRAMES

        previous_y = None
        for x in range(TRACE_X0, TRACE_X0 + SPAN):
            behind = (cursor - x) % SPAN
            y = trace_y(x)
            if behind < SPAN - GAP:
                color = C.WHITE if behind < FRESH else C.GREEN
                frame.pixel(x, y, color)
                # Join to the previous sample so spikes are continuous.
                if previous_y is not None:
                    lo, hi = sorted((previous_y, y))
                    for yy in range(lo + 1, hi):
                        frame.pixel(x, yy, color)
            previous_y = y

        beating = any(0 <= cursor - sx < 4 for sx in spikes)
        if beating:
            for row, line in enumerate(BIG_HEART):
                for col, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(1 + col, 4 + row, C.WHITE)
        else:
            frame.glyph("+HEART", 2, 4, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/heartbeat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
