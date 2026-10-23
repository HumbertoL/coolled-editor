#!/usr/bin/env python3
"""
The marathon.

A BRISK JOG stands on the top line the whole way. Below it a jogger runs in
place at the left while the road scrolls past, and mile markers come by on
posts: MI 1, MI 13, MI 20. The jogger wilts a marker at a time: sweat flies,
the head goes red, the tongue comes out, the shoulders drop. A chequered
FINISH banner goes past like everything else, and the jogger keeps going,
now a white, floating ghost of itself, past MI 30 and MI 40. The top line
never changes. Button: the ghost jogs on under A BRISK JOG as a red marker
reading Q4 rolls into view.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

JOG_X = 3
SPEED = 4                     # road pixels per frame
MARKERS = [                   # (frame it passes the jogger, text)
    (6, "MI 1"),
    (14, "MI 13"),
    (22, "MI 20"),
    (30, "FINISH"),
    (38, "MI 30"),
    (46, "MI 40"),
    (55, "Q4"),               # never quite arrives: it is the button
]

RUN = [
    ["..HH...", "..HH...", "A.SS.A.", ".SSSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", ".ASS...", "..SSA..", "..SS...", "..LL...", ".L.L..."],
    ["..HH...", "..HH...", ".ASS.A.", "..SSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", "..SSA..", ".ASS...", "..SS...", "..LL...", "..L.L.."],
]
# Wilted: head drooped forward a row, tongue out.
SLUMP = [
    [".......", "...HH..", "...HHT.", "A.SS.A.", ".SSSS..", ".L..L..", "L....L."],
    [".......", "...HH..", "...HHT.", ".ASS...", "..SSA..", "..LL...", ".L.L..."],
    [".......", "...HH..", "...HHT.", ".ASS.A.", "..SSS..", ".L..L..", "L....L."],
    [".......", "...HH..", "...HHT.", "..SSA..", ".ASS...", "..LL...", "..L.L.."],
]


def sprite(frame, art, x, y, palette):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, palette[ch])


def draw_marker(frame, x, text):
    """A sign on a post, the sign's left edge at ``x``."""
    if text == "FINISH":
        # A chequered banner across two posts.
        w = Canvas.small_text_width(text) + 4
        for k in range(w):
            frame.pixel(x + k, 8, C.WHITE if k % 2 == 0 else C.BLACK)
            frame.pixel(x + k, 14, C.WHITE if k % 2 == 1 else C.BLACK)
        frame.small_text(text, x + 2, 9, C.YELLOW)
        frame.vline(x, 9, 7, C.WHITE)
        frame.vline(x + w - 1, 9, 7, C.WHITE)
        return
    w = Canvas.small_text_width(text) + 2
    color = C.RED if text == "Q4" else C.GREEN
    frame.rect(x, 8, w, 7, color)
    frame.small_text(text, x + 1, 9, C.WHITE)
    frame.vline(x + w // 2, 15, 1, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        f.text("A BRISK JOG", 30, 0, C.WHITE)

        # The road: dashes scrolling left.
        for x in range(96):
            if (x + i * SPEED) % 6 < 3:
                f.pixel(x, 15, C.BLUE)

        # Markers scroll in from the right and pass behind the jogger.
        for at, text in MARKERS:
            x = JOG_X + 10 + (at - i) * SPEED
            if -30 < x < 96:
                draw_marker(f, x, text)
        f.rect(JOG_X - 1, 7, 9, 8, C.BLACK, fill=True)

        # How far gone the jogger is, by the last marker passed.
        stage = sum(1 for at, _ in MARKERS if i >= at)
        ghost = stage >= 4
        if ghost:
            palette = {"H": C.WHITE, "S": C.CYAN, "A": C.WHITE, "L": C.WHITE, "T": C.WHITE}
        else:
            head = C.YELLOW if stage < 2 else C.RED
            palette = {"H": head, "S": C.GREEN, "A": C.WHITE, "L": C.WHITE, "T": C.RED}
        phase = (i // 2) % 4
        if ghost:
            # Floats a row up and wobbles, legs trailing away to a tail.
            art = [row for row in RUN[phase][:5]] + [".LLLL..", "..LL..."]
            sprite(f, art, JOG_X, 7 + (i // 3) % 2, palette)
        elif stage >= 3:
            sprite(f, SLUMP[phase], JOG_X, 8, palette)
        else:
            sprite(f, RUN[phase], JOG_X, 8, palette)
        if 1 <= stage < 4:
            for k in range(min(stage, 3)):
                f.pixel(JOG_X + 1 - k * 2 - (i % 2), 8 + (i + k * 2) % 5, C.CYAN)
        if ghost and i % 2 == 0:
            f.small_text("...", JOG_X + 8, 9, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/brisk_marathon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
