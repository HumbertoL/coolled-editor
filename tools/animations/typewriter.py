#!/usr/bin/env python3
"""
Typewriter -- two lines are typed out, the bell rings, and the paper feeds away.

One character lands a frame, with an underline cursor under the next position.
A line feed holds the carriage for two frames while the bell flashes the border
red, then the page rolls up one row a frame until it is blank again. Text is the
5x7 font, so it is uppercase only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

DELAY = 110
LEFT = 4
LINES = ["HELLO WORLD", "LOOK AT ME"]
# The 5x7 glyphs fill rows top..top+6; the cursor sits on the row below them.
ROW_TOPS = [1, 8]
FEED_ROWS = 16


def stream():
    """Frames while typing, as (line, typed_so_far, bell) for each frame."""
    out = []
    for index, line in enumerate(LINES):
        for n in range(1, len(line) + 1):
            out.append((index, line[:n], False))
        if index < len(LINES) - 1:
            out += [(index, line, True)] * 2
            out.append((index + 1, "", False))
    return out


def draw_page(frame, typed, line, cursor_on, shift=0, bell=False):
    if bell:
        frame.rect(0, 0, 96, 16, C.RED, fill=False)
    for index, text in enumerate(typed):
        if text:
            frame.text(text, x=LEFT, y=ROW_TOPS[index] - shift, color=C.WHITE)
    if cursor_on:
        x = LEFT + Canvas.text_width(typed[line]) + 1
        frame.hline(x, ROW_TOPS[line] + 7 - shift, 5, C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    typed = ["", ""]
    for line, text, bell in stream():
        typed[line] = text
        frame = anim.frame()
        draw_page(frame, typed, line, True, bell=bell)
    last = len(LINES) - 1
    for hold in range(4):
        draw_page(anim.frame(), typed, last, hold % 2 == 0)
    for shift in range(1, FEED_ROWS + 1):
        draw_page(anim.frame(), typed, last, False, shift=shift)
    while len(anim) < 53:
        anim.frame()
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/typewriter.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
