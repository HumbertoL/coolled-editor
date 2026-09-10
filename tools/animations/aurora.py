#!/usr/bin/env python3
"""
Aurora -- shimmering northern lights.

Vertical curtains of color hang from the top of the panel, undulating side
to side driven by overlapping sine waves.  The brightness within each curtain
follows the GLOW ramp (brightest at the leading/bottom edge, fading upward),
and the hue drifts across the width via SPECTRUM.

Seamless: every phase advances by exactly 2*pi/FRAMES per frame.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

# Sine-wave parameters for the curtain height envelope.
# Each tuple is (spatial_period, temporal_speed, amplitude, base).
WAVES = [
    (24.0, 1.0, 5.0, 0.0),   # broad slow sway
    (11.0, 2.3, 3.0, 0.0),   # medium ripple
    (7.0,  3.7, 2.0, 0.0),   # quick shimmer
]

# Baseline curtain height (pixels from top) before waves are added.
BASE_HEIGHT = 6.0


def curtain_height(x, phase):
    """How many pixels tall the curtain is at column x for the given phase."""
    h = BASE_HEIGHT
    for period, speed, amp, _ in WAVES:
        h += amp * math.sin(2 * math.pi * x / period + phase * speed)
    return max(0.0, h)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for x in range(frame.width):
            h = curtain_height(x, phase)
            h_int = int(h)

            # Hue shifts slowly across x, also drifting with time.
            hue_pos = (x / frame.width + phase / (2 * math.pi) * 0.3) % 1.0

            for y in range(min(h_int + 1, frame.height)):
                # Distance from the bottom edge of this curtain, normalised.
                dist_from_bottom = (h - y) / max(h, 1.0)
                # Bottom (leading edge) is brightest; top fades out.
                brightness = 1.0 - dist_from_bottom

                # Pick a GLOW level for the brightness.
                glow_index = int(brightness * len(C.GLOW))
                glow_index = max(0, min(glow_index, len(C.GLOW) - 1))
                glow_color = C.GLOW[glow_index]

                if glow_color == C.BLACK:
                    continue

                # Tint the glow with the hue: at full brightness keep white,
                # otherwise blend toward the spectrum hue.
                hue_color = C.ramp(C.SPECTRUM, hue_pos)

                if glow_color == C.WHITE:
                    color = C.WHITE
                elif glow_color == C.CYAN:
                    color = hue_color
                else:
                    # BLUE level -- dim version: use blue or the hue dimmed
                    # Only a few colors read as dim; keep blue-ish.
                    color = C.BLUE

                frame.pixel(x, y, color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/aurora.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
