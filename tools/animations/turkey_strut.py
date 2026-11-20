#!/usr/bin/env python3
"""
Turkey strut -- in, fan, gobble, out.

A turkey walks in from the left with a head-bobbing strut: red body with a
magenta wing, cyan head, yellow beak and legs, a red wattle swinging under
its chin and its tail folded into a little wedge behind. It stops in the
middle of the panel, legs together, and puffs up: the tail opens feather
by feather into a full fan, sweeping up from behind its back to over its
head, banded like a rainbow -- yellow, green, magenta, red from the inside
out -- with dark quills between the feathers and a white tip on each.

Then it gobbles. The head thrusts forward with the beak open and GOBBLE
lands on the right in yellow; again, and a second GOBBLE lands under it.
The fan rattles (the feathers shiver a few degrees either way), the words
flash white on the beat, and the turkey, very pleased with itself, struts
off to the right with the fan still up, walking straight across its own
words.

Beat sheet (frame indexes):
  0-9    strut in
  10     stop, legs together
  11-21  tail opens, one feather a frame
  22-23  rattle
  24-27  first gobble   (GOBBLE, line 1)
  28-31  second gobble  (GOBBLE, line 2)
  32-39  rattle and flash
  40-52  strut off to the right, fan open
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16

BODY_Y = 10.0
BODY_RX, BODY_RY = 5.0, 3.2
N_FEATHERS = 9
FAN_FROM, FAN_TO = 182.0, 56.0          # degrees: back-horizontal to up-front
FAN_R0, FAN_R1 = 2.5, 9.6
# rainbow bands, inside out
BANDS = [(4.8, C.YELLOW), (6.5, C.GREEN), (8.1, C.MAGENTA), (99, C.RED)]

STOP_X = 24
IN_END = 10            # frames 0-9 walk in
FAN_START = 11
GOBBLES = (24, 28)
OUT_START = 40

TEXT = "GOBBLE"
TEXT_X = 42 + (W - 42 - Canvas.text_width(TEXT)) // 2


def body_x(f):
    if f < IN_END:
        return -7 + (STOP_X + 7) * f / IN_END
    if f < OUT_START:
        return STOP_X
    return STOP_X + 7.0 * (f - OUT_START + 1)


def feathers_open(f):
    if f < FAN_START:
        return 0
    return min(N_FEATHERS, f - FAN_START + 1)


def walking(f):
    return f < IN_END or f >= OUT_START


def draw_fan(c, bx, n_open, jitter):
    """Fill the open feathers' sectors, behind the body, in rainbow bands."""
    cx, cy = bx - 1, BODY_Y
    span = (FAN_FROM - FAN_TO) / N_FEATHERS
    for y in range(H):
        for x in range(int(cx - FAN_R1) - 1, int(cx + FAN_R1) + 2):
            dx, dy = x - cx, cy - y
            r = math.hypot(dx, dy)
            if not FAN_R0 <= r <= FAN_R1:
                continue
            k = (FAN_FROM - math.degrees(math.atan2(dy, dx)) + jitter) / span
            if not 0 <= k < n_open:
                continue
            frac = k - int(k)
            # a dark quill between feathers, once they are wide enough to show it
            if r > 5.2 and (frac < 0.12 or frac > 0.88):
                continue
            col = next(col for edge, col in BANDS if r < edge)
            if r > FAN_R1 - 1.0 and 0.35 < frac < 0.65:
                col = C.WHITE                         # a pale tip on each feather
            c.pixel(x, y, col)


def draw_folded_tail(c, bx):
    for i, (ang, col) in enumerate(((150, C.YELLOW), (162, C.MAGENTA), (174, C.GREEN))):
        a = math.radians(ang)
        for r in (4.5, 5.5, 6.5, 7.2):
            c.pixel(round(bx + r * math.cos(a)), round(BODY_Y - 1 - r * math.sin(a)), col)


def draw_body(c, bx):
    for y in range(6, 14):
        for x in range(int(bx) - 6, int(bx) + 7):
            if ((x - bx) / BODY_RX) ** 2 + ((y - BODY_Y) / BODY_RY) ** 2 <= 1.0:
                c.pixel(x, y, C.RED)
    # wing: a magenta crescent along the side
    for x, y in ((-3, 9), (-2, 9), (-1, 9), (0, 9), (-3, 10), (-2, 11), (-1, 11), (0, 10), (1, 10)):
        c.pixel(round(bx) + x, y, C.MAGENTA)


def draw_legs(c, bx, phase):
    """phase -1/+1 while walking (legs scissored), 0 standing."""
    x0 = round(bx)
    for base, s in ((x0 - 1, phase), (x0 + 2, -phase)):
        top = base
        foot = base + s
        c.pixel(top, 14, C.YELLOW)
        c.pixel(foot, 15, C.YELLOW)
        c.pixel(foot + 1, 15, C.YELLOW)


def draw_head(c, bx, push, gobble):
    """Neck rises from the front of the body; push moves the head forward."""
    x0 = round(bx)
    hx, hy = x0 + 5 + push, 3 + (1 if gobble else 0)
    # neck
    for x, y in ((x0 + 4, 8), (x0 + 4, 7), (x0 + 5 + push // 2, 6), (hx, hy + 2)):
        c.pixel(x, y, C.RED)
    # head
    for x in range(hx, hx + 3):
        for y in (hy, hy + 1):
            c.pixel(x, y, C.CYAN)
    c.pixel(hx + 1, hy, C.BLACK)          # eye
    # beak
    if gobble:
        c.pixel(hx + 3, hy - 1, C.YELLOW)
        c.pixel(hx + 3, hy + 1, C.YELLOW)
        c.pixel(hx + 4, hy - 1, C.YELLOW)
    else:
        c.pixel(hx + 3, hy + 1, C.YELLOW)
    # wattle, swinging with the stride
    swing = 1 if push else 0
    c.pixel(hx + 2 + swing, hy + 2, C.RED)
    c.pixel(hx + 2 + swing, hy + 3, C.RED)


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        bx = body_x(f)

        # words behind the turkey
        for i, g in enumerate(GOBBLES):
            if f >= g:
                beat = f - g < 2 or (32 <= f < OUT_START and (f + i) % 4 < 2)
                c.text(TEXT, TEXT_X, 0 if i == 0 else 9, C.WHITE if beat else C.YELLOW)

        n_open = feathers_open(f)
        rattling = 22 <= f < OUT_START
        jitter = (3 if f % 2 else -3) if rattling else 0
        if n_open:
            draw_fan(c, bx, n_open, jitter)
        else:
            draw_folded_tail(c, bx)

        draw_body(c, bx)
        step = f % 2
        draw_legs(c, bx, (1 if step else -1) if walking(f) else 0)

        gobble = any(g <= f < g + 2 for g in GOBBLES)
        if gobble:
            push = 2
        elif walking(f):
            push = step
        else:
            push = 0
        draw_head(c, bx, push, gobble)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/turkey_strut.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
