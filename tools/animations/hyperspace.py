#!/usr/bin/env python3
"""
Hyperspace -- Millennium Falcon jump. Stars stretch into radial streaks and
the field ends in a white warp flash.

Each star has a fixed angle and initial radius; every frame its radius grows
geometrically, so it accelerates outward. The streak is drawn from the
previous position to the current one, which lengthens as the star nears the
edge. Colour steps blue -> cyan -> white with distance from centre, doubling
as depth cueing since the palette has no brightness.

Not seamless: the final two frames are the warp flash, which then hard-cuts
back to the beginning -- the way a jump should feel.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 70
SEED = 11
STAR_COUNT = 55
CENTER = (48, 8)
GROWTH = 1.28    # radius multiplier per frame
FLASH_FRAMES = 2  # trailing all-white frames


def color_for(r):
    if r < 8:
        return C.BLUE
    if r < 22:
        return C.CYAN
    return C.WHITE


def build():
    rng = random.Random(SEED)
    stars = []
    for _ in range(STAR_COUNT):
        angle = rng.uniform(0, 2 * math.pi)
        # Slight aspect skew so streaks match the panel's shape.
        stars.append([angle, rng.uniform(2.0, 6.0)])

    anim = Animation(delay=DELAY)
    cx, cy = CENTER

    for index in range(FRAMES):
        frame = anim.frame()

        if index >= FRAMES - FLASH_FRAMES:
            # White warp flash, with a residual blue haze on the flash-out.
            frame.fill(C.WHITE if index == FRAMES - FLASH_FRAMES else C.CYAN)
        else:
            for star in stars:
                angle, r = star
                prev_r = r
                new_r = r * GROWTH
                x0 = cx + prev_r * math.cos(angle) * 1.15
                y0 = cy + prev_r * math.sin(angle)
                x1 = cx + new_r * math.cos(angle) * 1.15
                y1 = cy + new_r * math.sin(angle)
                # Streak from the old head to the new one.
                if 0 <= x1 < 96 and 0 <= y1 < 16:
                    frame.line(x0, y0, x1, y1, color_for(new_r))
                else:
                    # Recycle back near centre, new angle.
                    star[0] = rng.uniform(0, 2 * math.pi)
                    star[1] = rng.uniform(2.0, 5.0)
                    continue
                star[1] = new_r

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hyperspace.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
