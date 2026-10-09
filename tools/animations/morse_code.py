#!/usr/bin/env python3
"""
Morse code -- HELLO sent by a signal lamp, decoded on the panel as it goes.

The lamp is a square on the left. A dot is one frame lit, a dash three, with
one frame dark between the symbols of a letter and three between letters.
Each letter appears in the readout the moment its last symbol is sent. The
whole message fits in 52 frames; the last frame is held to fill the 53.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
MESSAGE = "HELLO"
CODE = {"H": "....", "E": ".", "L": ".-..", "O": "---"}
LAMP = (8, 2, 12, 12)


def timeline():
    """(lamp_on, symbol, letters_shown) for every frame of the message."""
    states = []
    shown = 0
    for letter in MESSAGE:
        symbols = CODE[letter]
        for position, symbol in enumerate(symbols):
            lit = 1 if symbol == "." else 3
            states += [(True, symbol, shown)] * lit
            if position < len(symbols) - 1:
                states.append((False, symbol, shown))
        shown += 1
        states += [(False, "", shown)] * 3
    return states


def build():
    states = timeline()
    states += [(False, "", len(MESSAGE))] * (FRAMES - len(states))
    anim = Animation(delay=DELAY)
    for lamp_on, symbol, shown in states:
        frame = anim.frame()
        x, y, width, height = LAMP
        if lamp_on:
            colour = C.WHITE if symbol == "-" or symbol == "" else C.YELLOW
            if symbol == "." or symbol == "-":
                colour = C.YELLOW if symbol == "." else C.WHITE
            frame.rect(x, y, width, height, colour, fill=True)
        else:
            frame.rect(x, y, width, height, C.BLUE, fill=False)
        frame.text("MORSE", x=30, y=1, color=C.CYAN)
        frame.text(MESSAGE[:shown], x=30, y=8, color=C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/morse_code.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
