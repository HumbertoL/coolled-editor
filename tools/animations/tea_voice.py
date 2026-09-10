#!/usr/bin/env python3
"""
Voice broadcast -- the other half of what Text-Em-All does.

Text-Em-All sends voice as well as text, so this is the phone-call side: a
handset on the left rings (shaking while it flashes), fans out expanding sound
arcs, and a live "CALLS" counter on the right ticks up as the broadcast
connects. A voice waveform jitters along the floor while calls are speaking.

Not seamless -- it plays one broadcast, ending on the settled total.
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
W, H = 96, 16
TOTAL = 24817
PCX, PCY = 12, 7            # handset centre


def ease(p):
    return 1 - (1 - p) ** 3


def build():
    anim = Animation(delay=DELAY)
    rng = random.Random(5)

    for index in range(FRAMES):
        frame = anim.frame()
        ringing = index < 40

        # Phone body, shaking a pixel while ringing.
        shake = (1 if index % 2 else -1) if ringing else 0
        px = 6 + shake
        frame.rect(px, 1, 8, 12, C.WHITE)
        frame.hline(px + 1, 3, 6, C.CYAN)          # screen
        frame.pixel(px + 3, 11, C.CYAN)            # home dot

        # Sound arcs fanning right, spawned on a cycle.
        for spawn in range(0, FRAMES, 7):
            age = index - spawn
            if 0 <= age < 6:
                r = 5 + age * 3
                for deg in range(-50, 51, 7):
                    a = math.radians(deg)
                    x = PCX + 3 + r * math.cos(a)
                    y = PCY + r * math.sin(a) * 0.55
                    if x < 52:
                        frame.pixel(x, y, C.CYAN if age < 4 else C.BLUE)

        # Live counter easing to the total.
        p = ease(min(1.0, index / 44))
        value = int(TOTAL * p)
        text = f"{value:,}"
        frame.text(text, x=94 - frame.text_width(text), y=1, color=C.YELLOW)
        frame.text("CALLS", x=94 - frame.text_width("CALLS"), y=9,
                   color=C.GREEN)

        # Voice waveform jittering along the floor while connected.
        for x in range(1, 52):
            amp = rng.randint(0, 2)
            frame.pixel(x, 15 - amp, C.GREEN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_voice.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
