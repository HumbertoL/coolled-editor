#!/usr/bin/env python3
"""
Retro pager -- a nod to Text-Em-All's roots in mass messaging.

The whole sign becomes a pager LCD. It sits idle showing "TEXT-EM-ALL",
then the receiver buzzes (a horizontal shake plus flashing red LEDs at each
end), and a new message types itself in one glyph at a time -- "HI HUMBERTO"
-- with a blinking cursor. Ends with a heart pulse.

Yellow throughout to sell the amber-LCD feel: on this palette YELLOW is the
closest thing to that colour.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 130
IDLE = "TEXT-EM-ALL"
MESSAGE = "HI HUMBERTO"

# Timing (start frame -> phase). 24 frames total.
IDLE_UNTIL = 5    # 0..4 idle
BUZZ_UNTIL = 9    # 5..8 buzzing
TYPE_UNTIL = 20   # 9..19 typing (11 chars, one per frame)
FRAMES = 24       # 20..23 heart pulse


def led(frame, on):
    """Little red status LED in each corner -- on during the buzz."""
    color = C.RED if on else C.BLACK
    for cx, cy in ((1, 1), (94, 1), (1, 14), (94, 14)):
        frame.pixel(cx, cy, color)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()

        if index < IDLE_UNTIL:
            # Steady branding.
            frame.text(IDLE, "center", 4, C.YELLOW, proportional=True)
            led(frame, on=False)

        elif index < BUZZ_UNTIL:
            # Shake the text horizontally while the LEDs flash red.
            offset = (2, -2, 2, -2)[index - IDLE_UNTIL]
            width = frame.text_width(IDLE, proportional=True)
            x = (frame.width - width) // 2 + offset
            frame.text(IDLE, x, 4, C.YELLOW, proportional=True)
            led(frame, on=True)
            # A tiny "BEEP" chevron pair at each side to look like radio waves.
            for dx, side in ((6, 4), (6, 91)):
                frame.pixel(side, 7, C.RED)
                frame.pixel(side, 8, C.RED)

        elif index < TYPE_UNTIL:
            # Type one glyph per frame with a blinking underscore cursor.
            typed = MESSAGE[: index - BUZZ_UNTIL + 1]
            width = frame.text_width(MESSAGE, proportional=True)
            x0 = (frame.width - width) // 2
            frame.text(typed, x0, 4, C.YELLOW, proportional=True)
            typed_w = frame.text_width(typed, proportional=True)
            if index % 2 == 0:
                frame.hline(x0 + typed_w + 1, 11, 4, C.YELLOW)
            led(frame, on=False)

        else:
            # Message stays put; a heart on the right pulses.
            width = frame.text_width(MESSAGE, proportional=True)
            x0 = (frame.width - width) // 2
            frame.text(MESSAGE, x0, 4, C.YELLOW, proportional=True)
            beat = index % 2 == 0
            frame.glyph("+HEART", 88, 5, C.RED if beat else C.MAGENTA)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/retro_pager.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
