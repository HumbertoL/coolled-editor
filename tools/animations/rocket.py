#!/usr/bin/env python3
"""
Rocket -- T-minus three, and off.

The countdown runs on the left while the rocket waits on its pad at the
right. At zero the flame lights, the pad fills with a spreading cloud of blue
exhaust, and the rocket climbs off the top of the panel while LIFTOFF flashes.
The smoke then thins pixel by pixel until the panel is dark and the count
starts again.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 200
SEED = 11

ROCKET = [
    ("..#..", C.WHITE),
    (".###.", C.WHITE),
    (".###.", C.WHITE),
    (".#.#.", C.CYAN),
    (".###.", C.WHITE),
    (".###.", C.WHITE),
    ("#####", C.RED),
    ("#.#.#", C.RED),
]
PAD_X = 74
PAD_Y = 14          # row the rocket's bottom sits on before launch
COUNT_END = 9       # first frame of flight
CLIMB = 2.6         # rows per frame


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    smoke = [(PAD_X + 2 + rng.randint(-14, 14), rng.choice((13, 14, 14, 15)), rng.randint(0, 3))
             for _ in range(60)]

    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(PAD_X - 4, 15, 13, C.BLUE)          # the pad

        flying = index >= COUNT_END
        bottom = PAD_Y if not flying else PAD_Y - CLIMB * (index - COUNT_END)
        top = round(bottom) - len(ROCKET) + 1
        for row, (line, color) in enumerate(ROCKET):
            for col, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(PAD_X + col, top + row, color)

        if flying or index == COUNT_END - 1:
            flame_len = 3 if index % 2 else 2
            for k in range(flame_len):
                y = round(bottom) + 1 + k
                frame.hline(PAD_X + 1, y, 3, C.YELLOW if k == 0 else C.RED)
                frame.pixel(PAD_X + 2, y, C.WHITE if k == 0 else C.YELLOW)

        if flying:
            spread = index - COUNT_END + 1
            for sx, sy, born in smoke:
                if born < spread and abs(sx - PAD_X - 2) <= spread * 2 and spread - born < 9:
                    frame.pixel(sx, sy, C.BLUE if spread - born > 2 else C.CYAN)

        if index < COUNT_END:
            label = f"T-{3 - index // 3}"
            frame.text(label, 8, 4, C.YELLOW if index % 3 != 2 else C.WHITE)
        elif index < 20:
            frame.text("LIFTOFF", 8, 4, C.RED if index % 2 else C.WHITE)
        else:
            frame.text("LIFTOFF", 8, 4, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rocket.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
