#!/usr/bin/env python3
"""
tea_uptime -- Service uptime monitor showing 99.99% with a 30-day status
bar and ALL SYSTEMS GO confirmation.
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

# Which of the 30 days are degraded (yellow instead of green)
DEGRADED_DAYS = {7, 22}

# The percentage types through these values
PCT_STAGES = [
    (0, ''),
    (2, '9'),
    (4, '99'),
    (5, '99.'),
    (7, '99.9'),
    (9, '99.97'),
    (11, '99.98'),
    (13, '99.99'),
    (15, '99.99%'),
]


def build():
    anim = Animation(delay=DELAY)

    for i in range(FRAMES):
        f = anim.frame()

        # --- Phase 1 (frames 0-15): Percentage types in ---
        # --- Also shown in phases 2 and 3 ---
        pct_text = ''
        for threshold, text in PCT_STAGES:
            if i >= threshold:
                pct_text = text

        if pct_text:
            # Main percentage display, centered, y=1 (top area)
            pct_color = C.GREEN
            # In phase 3, gentle pulse
            if i >= 45:
                pulse = (i - 45) % 6
                pct_color = C.WHITE if pulse < 2 else C.GREEN
            f.text(pct_text, 'center', 1, pct_color)

        # --- Phase 2 (frames 15-40): Status squares fill in ---
        if i >= 15:
            # 30 squares, each 2x2, with 1px gap = 3px per square
            # Total width: 30 * 3 - 1 = 89px, fits in 96
            # Start x to roughly center: (96 - 89) // 2 = 3
            squares_base_x = 3
            squares_y = 10  # below the percentage text

            # How many squares are visible
            fill_progress = min(30, int((i - 15) * 30 / 25))

            for day in range(fill_progress):
                sx = squares_base_x + day * 3
                sy = squares_y
                is_degraded = day in DEGRADED_DAYS
                sq_color = C.YELLOW if is_degraded else C.GREEN

                # In phase 3, pulse the squares too
                if i >= 45:
                    pulse = (i - 45 + day) % 8
                    if pulse < 1 and not is_degraded:
                        sq_color = C.CYAN

                # Draw 2x2 square
                f.pixel(sx, sy, sq_color)
                f.pixel(sx + 1, sy, sq_color)
                f.pixel(sx, sy + 1, sq_color)
                f.pixel(sx + 1, sy + 1, sq_color)

        # --- Phase 3 (frames 40-53): "ALL SYSTEMS GO" wipes in ---
        if i >= 40:
            msg = 'ALL SYSTEMS GO'
            # Wipe in from left: reveal more characters over time
            chars_visible = min(len(msg), int((i - 40) * len(msg) / 10) + 1)
            visible_text = msg[:chars_visible]
            # Place at bottom, centered
            f.text(visible_text, 'center', 9, C.CYAN)

            # When fully revealed, add subtle decorations
            if i >= 50:
                # Small check marks or dots at the ends
                f.glyph('+CHECK', 1, 9, C.GREEN)
                f.glyph('+CHECK', 89, 9, C.GREEN)

    return anim


if __name__ == '__main__':
    animation = build()
    out = Path(__file__).resolve().parents[2] / 'src/sample/tea_uptime.jt'
    animation.save(out)
    print(f'{out.name}: {animation.describe()}')
