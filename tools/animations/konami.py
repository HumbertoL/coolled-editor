#!/usr/bin/env python3
"""
The Konami code, entered one input at a time.

Guessed at from the company you keep on this panel -- Pac-Man, Animal Well, a
party parrot -- so if it misses, it misses cheerfully.

Each input appears in white and settles to cyan, left to right. Once the
sequence is complete it flashes green: code accepted.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

SEQUENCE = [
    "+ARROW_U", "+ARROW_U", "+ARROW_D", "+ARROW_D",
    "+ARROW_L", "+ARROW_R", "+ARROW_L", "+ARROW_R",
    "B", "A",
]

FRAMES = 24
DELAY = 120
STEP = 6
TEXT_Y = 4
ACCEPT_FRAME = 14      # everything entered; start celebrating


def build():
    anim = Animation(delay=DELAY)
    width = len(SEQUENCE) * STEP - 1
    x0 = (anim.width - width) // 2

    for index in range(FRAMES):
        frame = anim.frame()
        accepted = index >= ACCEPT_FRAME

        for position, symbol in enumerate(SEQUENCE):
            if not accepted and position > index:
                continue        # not entered yet
            if accepted:
                color = C.GREEN if index % 2 == 0 else C.WHITE
            elif position == index:
                color = C.WHITE     # just pressed
            else:
                color = C.CYAN
            # Named symbols go through glyph(); text() would spell the name.
            frame.glyph(symbol, x0 + position * STEP, TEXT_Y, color)

        # Underline fills as the sequence is entered.
        entered = len(SEQUENCE) if accepted else min(index + 1, len(SEQUENCE))
        for x in range(x0, x0 + entered * STEP - 1):
            frame.pixel(x, TEXT_Y + 8, C.GREEN if accepted else C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/konami.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
