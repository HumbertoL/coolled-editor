#!/usr/bin/env python3
"""
Ripples -- concentric water ripples from random drop points.

Several drops land at staggered intervals.  Each spawns an expanding ring
whose brightness decays with distance and age.  Where ripples overlap their
amplitudes add, so constructive interference produces brighter spots.
Brightness is quantised to the GLOW ramp.

Seamless: the drop schedule and wave function repeat exactly over FRAMES.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80

# Wave physics.
WAVE_SPEED = 1.8       # pixels per frame
WAVELENGTH = 10.0      # pixels between crests
DECAY_DIST = 0.04      # amplitude decay per pixel of radius
DECAY_AGE = 0.03       # amplitude decay per frame of age

# Drop schedule: (frame_offset, x, y).  These repeat every FRAMES frames
# for seamlessness.  Use a fixed set so the pattern is deterministic.
DROPS = [
    (0,  20, 8),
    (8,  72, 4),
    (16, 45, 12),
    (24, 10, 3),
    (32, 85, 10),
    (40, 55, 7),
    (48, 30, 14),
]


def wave_amplitude(dist, age):
    """
    Amplitude of a single ripple at a given distance from the centre and age.

    Returns a value in roughly [-1, 1] that decays toward 0.
    """
    if age < 0:
        return 0.0
    # The ring expands; only near the wavefront is the amplitude significant.
    ring_radius = age * WAVE_SPEED
    # Distance from the wavefront.
    dr = abs(dist - ring_radius)
    # Gaussian-ish envelope around the wavefront.
    envelope = math.exp(-0.5 * (dr / (WAVELENGTH * 0.4)) ** 2)
    # Sinusoidal wave.
    phase = 2 * math.pi * (dist - ring_radius) / WAVELENGTH
    wave = math.sin(phase) * envelope
    # Decay with distance and age.
    decay = max(0.0, 1.0 - DECAY_DIST * dist - DECAY_AGE * age)
    return wave * decay


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()

        def color_at(x, y):
            total = 0.0
            for drop_frame, dx, dy in DROPS:
                # Age of this drop in the current frame, wrapping for
                # seamless looping.
                age = (index - drop_frame) % FRAMES
                dist = math.sqrt((x - dx) ** 2 + (y - dy) ** 2)
                total += wave_amplitude(dist, age)
                # Also include the "previous cycle" so ripples that started
                # near the end of the loop are still visible at the start.
                age_prev = age + FRAMES
                total += wave_amplitude(dist, age_prev)

            # Map the summed amplitude to GLOW colours.
            # Positive amplitude = bright, negative/zero = dark.
            if total <= 0.05:
                return C.BLACK
            if total < 0.25:
                return C.BLUE
            if total < 0.55:
                return C.CYAN
            return C.WHITE

        frame.each(color_at)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/ripples.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
