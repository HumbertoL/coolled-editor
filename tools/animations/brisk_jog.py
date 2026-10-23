#!/usr/bin/env python3
"""
A brisk jog -- the footnote.

A BRISK JOG wipes in on the top line while a jogger trots in place at the
right edge, the ground ticking by under its feet. NOT A SPRINT* wipes in
below, and the asterisk blinks. Then the ground tears past, the jogger blurs
and shoots off the right edge, and the footnote arrives in red, typed a
letter a frame: *IT IS A SPRINT. The asterisk keeps blinking. Button: a lone
cyan speed line where the jogger used to be.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, wipe  # noqa: E402

FRAMES = 50
DELAY = 130

LINE1 = "A BRISK JOG"
LINE2 = "NOT A SPRINT*"
LINE3 = "*IT IS A SPRINT"
JOG_X = 86

# Beats.
WIPE1_END = 8
WIPE2_START = 9
WIPE2_END = 18
BOLT = 27            # the jogger takes off
TYPE_START = 31      # the footnote types in
TYPE_END = TYPE_START + len(LINE3)

RUN = [
    ["..HH...", "..HH...", "A.SS.A.", ".SSSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", ".ASS...", "..SSA..", "..SS...", "..LL...", ".L.L..."],
    ["..HH...", "..HH...", ".ASS.A.", "..SSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", "..SSA..", ".ASS...", "..SS...", "..LL...", "..L.L.."],
]
PALETTE = {"H": C.YELLOW, "S": C.GREEN, "A": C.WHITE, "L": C.WHITE}


def sprite(frame, art, x, y, palette=PALETTE):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, palette[ch])


def ground(frame, x0, x1, offset, period=4):
    for x in range(x0, x1):
        if (x + offset) % period == 0:
            frame.pixel(x, 15, C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    scroll = 0
    for i in range(FRAMES):
        f = anim.frame()

        # Line 1 wipes in over the first beat and then stays.
        edge1 = min(len(LINE1) * 6, (i + 1) * 9)
        f.text(LINE1, 1, 0, wipe(C.WHITE, C.BLACK, edge=1 + edge1))

        if i < BOLT:
            speed = 2
        else:
            speed = 2 + (i - BOLT) * 2
        scroll += speed

        if WIPE2_START <= i < TYPE_START:
            edge2 = min(len(LINE2) * 6, (i - WIPE2_START + 1) * 9)
            blink = i >= WIPE2_END and (i // 2) % 2 == 0
            star = C.RED if blink else C.YELLOW
            f.text(LINE2[:-1], 1, 8, wipe(C.WHITE, C.BLACK, edge=1 + edge2))
            if edge2 >= len(LINE2) * 6 - 4:
                f.text("*", 1 + 12 * 6, 8, star)

        if i >= TYPE_START:
            shown = min(len(LINE3), i - TYPE_START + 1)
            blink = (i // 2) % 2 == 0
            f.text(LINE3[1:shown], 3 + 6, 8, C.RED)
            f.text("*", 3, 8, C.YELLOW if blink else C.RED)
            if i < TYPE_END:
                f.vline(3 + shown * 6, 8, 7, C.WHITE)   # caret

        # The jogger, in place at the right edge, until it bolts.
        if i < TYPE_START:
            ground(f, 78, 96, -scroll)
            x = JOG_X
            if i >= BOLT:
                x = JOG_X + (i - BOLT) * 3
                phase = i % 4
                for k in range(1, 4):
                    f.hline(x - 2 - k * 3, 9 + k, 2, C.CYAN)   # speed lines
            else:
                phase = (i // 2) % 4
            sprite(f, RUN[phase], x, 8)
        elif i < TYPE_START + 3:
            f.hline(90, 11, 4, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/brisk_jog.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
