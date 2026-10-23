#!/usr/bin/env python3
"""
The pace-o-meter.

A four-zone pace gauge across the bottom: WALK in green, JOG in yellow, BRISK
JOG in magenta, SPRINT in red, with the current zone named in big letters up
top. A white needle sets off from the left and the label reads WALK, then
JOG, then settles on BRISK JOG and holds, with a tick of approval. Then a
hand comes in along the gauge and shoves the needle on into SPRINT; the
label flips to red SPRINT, and a yellow label drops over it reading BRISK
JOG. The hand keeps pushing: the needle runs off the end of the gauge, bends
against the edge, and the SPRINT zone strobes. The sticker says BRISK JOG
throughout. Button: a second, smaller sticker lands over the SPRINT zone's
own label, re-labelling it BRISK.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

BAR_Y, BAR_H = 8, 2
ZONES = [  # name, x0, x1, color
    ("WALK", 0, 24, C.GREEN),
    ("JOG", 24, 48, C.YELLOW),
    ("BRISK", 48, 72, C.MAGENTA),
    ("SPRINT", 72, 96, C.RED),
]
LABEL_OF = {"WALK": "WALK", "JOG": "JOG", "BRISK": "BRISK JOG", "SPRINT": "SPRINT"}

# Beats.
ARRIVE = 16        # needle reaches the brisk-jog zone's middle
HOLD_END = 24
HAND_IN = 25
SHOVE = 28         # the needle starts moving again
STICKER = 33
BEND = 42
SAME = 48

HAND = [          # a fist with the index finger out, pushing right
    "...WWW",
    "WWWWWW",
    "WWWW..",
    "WWWW..",
    ".WWW..",
]


def zone_at(x):
    for name, x0, x1, _color in ZONES:
        if x0 <= x < x1:
            return name
    return "SPRINT"


def draw_gauge(frame, strobe=False):
    for name, x0, x1, color in ZONES:
        if name == "SPRINT" and strobe:
            color = C.WHITE
        frame.rect(x0, BAR_Y, x1 - x0, BAR_H, color, fill=True)
        frame.pixel(x0, BAR_Y - 1, C.WHITE)
        label_x = x0 + (x1 - x0 - Canvas.small_text_width(name)) // 2
        frame.small_text(name, label_x, 11, color)
    frame.pixel(95, BAR_Y - 1, C.WHITE)


def draw_needle(frame, x, bent=0):
    """A white needle through the gauge; ``bent`` folds its top over."""
    x = min(x, 95)
    frame.vline(x, BAR_Y - 2 + bent, BAR_H + 3 - bent, C.WHITE)
    for k in range(bent):
        frame.pixel(x - 1 - k, BAR_Y - 2 + bent - 1 - k, C.WHITE)


def draw_label(frame, text, color):
    frame.text(text, "center", 0, color, proportional=True)


def draw_sticker(frame, text, x, y, w, color=C.YELLOW):
    """A bordered label in the 3x5 font, blanking whatever is under it."""
    frame.rect(x, y, w, 7, C.BLACK, fill=True)
    frame.rect(x, y, w, 7, color)
    frame.small_text(text, x + (w - Canvas.small_text_width(text)) // 2, y + 1, color)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        strobe = i >= BEND and i % 2 == 0
        draw_gauge(f, strobe=strobe)

        if i < ARRIVE:
            x = int(60 * (i + 1) / ARRIVE)
        elif i < SHOVE:
            x = 60
        else:
            x = 60 + (i - SHOVE) * 4
        bent = 0
        if x > 95:
            bent = min(3, (x - 95) // 4 + 1)
        draw_needle(f, x, bent=bent)

        zone = zone_at(min(x, 95))
        if i < STICKER:
            color = dict((z[0], z[3]) for z in ZONES)[zone]
            draw_label(f, LABEL_OF[zone], color)
            if ARRIVE <= i < HAND_IN and (i - ARRIVE) >= 2:
                f.glyph("+CHECK", 82, 0, C.GREEN)
        else:
            draw_label(f, "SPRINT", C.RED)
            drop = max(0, STICKER + 3 - i)            # slides down into place
            draw_sticker(f, "BRISK JOG", 25, -drop * 3, 46)
            if i >= SAME:
                # A second sticker over the SPRINT zone's own label.
                f.rect(72, 11, 24, 5, C.BLACK, fill=True)
                f.vline(72, 11, 5, C.YELLOW)
                f.vline(95, 11, 5, C.YELLOW)
                f.small_text("BRISK", 72 + (24 - Canvas.small_text_width("BRISK")) // 2, 11, C.YELLOW)

        # The hand: slides in from the left along the gauge, then pushes.
        if i >= HAND_IN:
            hx = min(x, 95) - 6
            if i < SHOVE:
                hx -= (SHOVE - i) * 6
            if i >= BEND:
                hx -= i % 2
            for r, row in enumerate(HAND):
                for c, ch in enumerate(row):
                    if ch == "W":
                        f.pixel(hx + c, BAR_Y - 2 + r, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/brisk_meter.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
