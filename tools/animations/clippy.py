#!/usr/bin/env python3
"""
Clippy -- the paperclip who noticed you typing.

A bent cyan paperclip with googly eyes and eyebrows bounces in from the left
and a yellow speech box opens beside him. The offer types itself out, scrolling
as it outgrows the box: IT LOOKS LIKE YOU'RE WRITING A LETTER... Two options
appear underneath, a cursor drifts to the wrong one and the "user" picks it.
The box shuts, Clippy gives a slow wink and shrinks away to nothing, and then
he bounces back in to ask again.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import Canvas  # noqa: E402

FRAMES = 53
DELAY = 110
QUESTION = "IT LOOKS LIKE YOU'RE WRITING A LETTER..."
BOX_X, BOX_W = 17, 79
IN_FRAMES = 8
TYPE_START, TYPE_END = 9, 30
OPTS_AT = 31
PICK_AT = 41
CLOSE_AT = 44
WINK_AT = 45
SHRINK_AT = 47

CLIP_W, CLIP_H = 11, 15


BODY = [
    "...........",
    "..CCCCCCC..",
    ".C.......C.",
    ".C.......C.",
    ".C.......C.",
    ".C.......C.",
    ".C..C.C..C.",
    ".C..C.C..C.",
    ".C..C.C..C.",
    ".C..C.C..C.",
    ".C..CCC..C.",
    ".C.......C.",
    "..C.....C..",
    "...CCCCC...",
    "...........",
]


def clippy(wink=False, look=0, blink=False):
    """The clip on its own 11x15 canvas. look is -1, 0 or 1."""
    c = Canvas(CLIP_W, CLIP_H + 1)
    for r, line in enumerate(BODY):
        for col, ch in enumerate(line):
            if ch == "C":
                c.pixel(col, r + 1, C.CYAN)
    for r in range(7, 11):                       # white highlight on the wire
        c.pixel(1, r + 1, C.WHITE)
    # googly eyes: 3x3 whites with a pupil that looks around
    for n, ex in enumerate((2, 6)):
        closed = blink or (wink and n == 1)
        if closed:
            c.hline(ex, 4, 3, C.WHITE)
        else:
            c.rect(ex, 3, 3, 3, C.WHITE, fill=True)
            c.pixel(ex + 1 + look, 4 + (1 if look else 0), C.BLACK)
    # eyebrows: raised, one arched higher while winking
    c.hline(2, 1 if not wink else 1, 3, C.YELLOW)
    c.hline(6, 1 if not wink else 2, 3, C.YELLOW)
    return c


def scaled(src, factor):
    """Nearest-neighbour shrink about the bottom centre."""
    out = Canvas(src.width, src.height)
    if factor <= 0:
        return out
    for y in range(src.height):
        for x in range(src.width):
            sx = int((x - src.width / 2) / factor + src.width / 2)
            sy = int((y - src.height + 1) / factor + src.height - 1)
            if 0 <= sx < src.width and 0 <= sy < src.height:
                color = src.get(sx, sy)
                out.pixel(x, y, color)
    return out


def window_text(frame, text, x, y, width, color, tail=True):
    """Small text clipped to [x, x+width); shows the end if it overflows."""
    scratch = Canvas(200, 16)
    end = scratch.small_text(text, 0, 0, C.WHITE)
    shift = max(0, end + 1 - width) if tail else 0
    for yy in range(5):
        for xx in range(width):
            col = scratch.get(xx + shift, yy)
            if col != C.BLACK:
                frame.pixel(x + xx, y + yy, color)


def draw_box(frame, height_frac):
    top = 0
    h = max(1, round(16 * height_frac))
    y0 = 8 - h // 2
    frame.rect(BOX_X, y0, BOX_W, h, C.YELLOW, fill=True)
    # tail pointing at Clippy
    frame.pixel(BOX_X - 1, 8, C.YELLOW)
    frame.pixel(BOX_X - 2, 9, C.YELLOW)
    frame.pixel(BOX_X - 1, 9, C.YELLOW)
    return y0, h


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        frame = anim.frame()
        # Clippy's position and pose
        x, y, factor = 2, 0, 1.0
        if i < IN_FRAMES:
            u = i / IN_FRAMES
            x = round(-13 + 15 * u)
            y = -round(abs(math.sin(u * math.pi * 2.5)) * 4 * (1 - u))
        elif i >= SHRINK_AT:
            factor = max(0.0, 1 - (i - SHRINK_AT + 1) / 6)
        wiggle = 0
        if TYPE_START <= i < OPTS_AT:
            wiggle = [0, 1, 0, -1][i % 4]
        x += wiggle
        blink = (i % 17 == 13)
        look = 1 if TYPE_START <= i < PICK_AT else 0
        wink = WINK_AT <= i < SHRINK_AT + 1
        clip = clippy(wink=wink, look=look, blink=blink and not wink)
        if factor < 1.0:
            clip = scaled(clip, factor)
        frame.blit(clip, x, y)

        # the speech box
        if TYPE_START - 2 <= i < CLOSE_AT + 2:
            if i < TYPE_START:
                frac = (i - (TYPE_START - 3)) / 3
            elif i >= CLOSE_AT:
                frac = max(0.0, 1 - (i - CLOSE_AT + 1) / 3)
            else:
                frac = 1.0
            frac = min(1.0, max(0.0, frac))
            if frac > 0.05:
                y0, h = draw_box(frame, frac)
                if frac >= 1.0:
                    tx = BOX_X + 2
                    tw = BOX_W - 4
                    chars = 0
                    if i >= TYPE_START:
                        span = TYPE_END - TYPE_START
                        chars = min(len(QUESTION), round(len(QUESTION) * (i - TYPE_START + 1) / span))
                    cursor = (i % 2 == 0) and chars < len(QUESTION)
                    shown = QUESTION[:chars] + ("-" if cursor else "")
                    if i < OPTS_AT:
                        window_text(frame, shown, tx, 5, tw, C.BLACK)
                    else:
                        window_text(frame, QUESTION[-19:], tx, 0, tw, C.BLACK)
                        pick = i >= PICK_AT - 4
                        second = i >= PICK_AT - 4
                        opts = [("WRITE THE LETTER", 6), ("JUST TYPE, THANKS", 11)]
                        chosen = 1 if i >= PICK_AT - 3 else 0
                        for n, (label, oy) in enumerate(opts):
                            if i < OPTS_AT + 1 + n * 2:
                                continue
                            sel = (n == chosen) and i >= OPTS_AT + 5
                            if sel:
                                frame.rect(tx - 1, oy, tw + 2, 5, C.BLACK, fill=True)
                                window_text(frame, label, tx + 1, oy, tw - 2, C.YELLOW)
                            else:
                                window_text(frame, label, tx + 1, oy, tw - 2, C.RED if n == 0 else C.BLUE)
                        if i >= PICK_AT and i % 2 == 0:
                            frame.rect(tx - 1, 11, tw + 2, 5, C.WHITE, fill=True)
                            window_text(frame, opts[1][0], tx + 1, 11, tw - 2, C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/clippy.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
