#!/usr/bin/env python3
"""
Mosquito -- the lamp goes on, and there is nothing there.

Night. Someone is asleep in a bed on the right, Zs drifting up off the
pillow, a lamp on the nightstand beside them. A mosquito -- one white pixel
with a flicker of magenta wings -- comes in from the left trailing a small
BZZZ. The sleeper's eye opens. CLICK: the lamp lights yellow, the room
brightens, and there is nothing there. Lamp off. BZZZZ, right in the face.
Lamp on: nothing. Lamp off: a big red BZZZZ. A held beat, then they slap
their own face -- SLAP!, stars, a red mark on the cheek -- and the mosquito,
untouched, flies off whistling a cyan note. The sleeper lies there with one
eye twitching. Caption: 3:47 AM.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130

# Scene geometry. The bed fills the right third, the lamp sits just left of it.
HEAD_X, HEAD_Y = 85, 7            # 5x4 head, lying on the pillow, face left
EYE = (86, 8)                     # top-left of the 2x2 eye
FACE_X = 82                       # where the mosquito hovers, in front of the eye
LAMP_X = 54                       # stem column
SHADE = [(53, 3, 3), (52, 4, 5), (51, 5, 7), (51, 6, 7)]   # (x, y, width)

# Timeline (frame indexes).
ENTER = 2                         # mosquito appears at the left edge
AT_FACE = 9                       # ... and arrives in front of the face
EYE_OPENS = 7
LAMP_ON_1 = range(10, 15)
BUZZ_2 = range(16, 21)
LAMP_ON_2 = range(21, 26)
BUZZ_3 = range(26, 31)            # the loud one
HOLD = range(31, 35)              # held beat, mosquito hovering
SLAP = 35
SLAP_TEXT = range(35, 40)
STARS = range(35, 42)
ESCAPE = range(35, 46)
TWITCH_FROM = 41
CAPTION_FROM = 46

NOTE = [
    ".##",
    ".#.",
    "##.",
]


def lit(on, dark, bright):
    return bright if on else dark


def draw_room(frame, on):
    """Bed, nightstand, lamp and floor. ``on`` is whether the lamp is lit."""
    line = lit(on, C.BLUE, C.WHITE)
    frame.hline(0, 15, 96, line)                        # floor
    # Night sky through a window top-left: a crescent and two stars.
    if not on:
        for x, y in ((6, 1), (5, 2), (5, 3), (6, 4), (7, 2), (7, 3)):
            frame.pixel(x, y, C.WHITE)
        frame.pixel(14, 3, C.BLUE)
        frame.pixel(11, 6, C.BLUE)
    # Bed: headboard on the right, footboard left, mattress, blanket, pillow.
    frame.vline(93, 4, 11, line)
    frame.vline(94, 4, 11, line)
    frame.vline(60, 10, 5, line)
    frame.hline(60, 13, 34, line)
    frame.pixel(61, 14, line)
    frame.pixel(92, 14, line)
    blanket = C.RED
    frame.hline(62, 12, 22, blanket)                    # blanket over the body
    frame.hline(66, 11, 10, blanket)                    # the hump of the body
    frame.hline(68, 10, 5, blanket)
    frame.hline(84, 12, 8, lit(on, C.BLUE, C.WHITE))    # pillow
    frame.hline(85, 11, 7, lit(on, C.BLUE, C.WHITE))
    # Nightstand and lamp.
    frame.hline(50, 12, 9, line)
    frame.vline(51, 13, 2, line)
    frame.vline(57, 13, 2, line)
    frame.hline(52, 11, 5, line)                        # lamp base
    frame.vline(LAMP_X, 7, 4, line)                     # stem
    for x, y, w in SHADE:
        frame.hline(x, y, w, lit(on, C.BLUE, C.YELLOW))
    if on:
        # Light spilling out of the shade.
        for x, y in ((49, 2), (48, 1), (59, 2), (60, 1), (54, 1), (54, 0),
                     (50, 7), (58, 7), (48, 9), (60, 9)):
            frame.pixel(x, y, C.YELLOW)


def draw_person(frame, eye, mark=False, hand=None):
    """Head on the pillow. ``eye`` is closed / open / wide / squint."""
    frame.rect(HEAD_X, HEAD_Y, 5, 4, C.YELLOW, fill=True)
    frame.pixel(HEAD_X - 1, HEAD_Y + 2, C.YELLOW)       # nose, pointing left
    ex, ey = EYE
    if eye == "closed":
        frame.hline(ex, ey, 2, C.BLACK)
    elif eye == "open":
        frame.rect(ex, ey - 1, 2, 2, C.BLACK, fill=True)
        frame.pixel(ex, ey - 1, C.WHITE)                # pupil, looking left
    elif eye == "wide":
        frame.rect(ex, ey - 1, 2, 3, C.BLACK, fill=True)
        frame.pixel(ex, ey, C.WHITE)
    elif eye == "squint":
        frame.hline(ex, ey, 2, C.BLACK)
        frame.pixel(ex, ey - 1, C.BLACK)
    if mark:
        frame.pixel(ex, ey + 2, C.RED)
        frame.pixel(ex + 1, ey + 2, C.RED)
    if hand == "strike":
        # Arm up out of the blanket, palm flat on the face.
        frame.line(80, 12, 83, 9, C.YELLOW)
        frame.rect(84, 7, 3, 4, C.YELLOW, fill=True)
        frame.rect(84, 7, 3, 4, C.WHITE)
    elif hand == "lower":
        frame.line(80, 12, 83, 10, C.YELLOW)
        frame.rect(83, 9, 2, 3, C.YELLOW, fill=True)


def draw_mosquito(frame, x, y, index):
    frame.pixel(x, y, C.WHITE)
    if index % 2:
        frame.pixel(x - 1, y - 1, C.MAGENTA)
        frame.pixel(x + 1, y - 1, C.MAGENTA)
    else:
        frame.pixel(x - 1, y, C.MAGENTA)
        frame.pixel(x + 1, y, C.MAGENTA)


def draw_note(frame, x, y):
    for r, row in enumerate(NOTE):
        for c, ch in enumerate(row):
            if ch == "#":
                frame.pixel(x + c, y + r, C.CYAN)


def draw_zs(frame, index):
    for k in range(2):
        phase = (index + k * 6) % 12
        y = 9 - phase
        if -4 <= y <= 9:
            frame.small_text("Z", 79 + (phase // 4), y, C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        on = i in LAMP_ON_1 or i in LAMP_ON_2
        draw_room(f, on)

        # The sleeper.
        if i < EYE_OPENS:
            eye = "closed"
        elif i in LAMP_ON_2 or i in BUZZ_3 or i in HOLD:
            eye = "wide"
        elif i >= TWITCH_FROM:
            eye = "open" if (i // 2) % 2 == 0 else "squint"
        else:
            eye = "open"
        hand = None
        if i in (SLAP, SLAP + 1):
            hand = "strike"
        elif i in (SLAP + 2, SLAP + 3):
            hand = "lower"
        draw_person(f, eye, mark=i > SLAP + 1, hand=hand)
        if i < EYE_OPENS:
            draw_zs(f, i)

        # The mosquito and its noise.
        if ENTER <= i < AT_FACE:
            t = (i - ENTER) / (AT_FACE - 1 - ENTER)
            mx = round(-1 + t * (FACE_X + 1))
            my = 8 - (i % 3 == 1)
            draw_mosquito(f, mx, my, i)
            f.small_text("BZZZ", mx - 21, my - 2, C.WHITE)
        elif i in BUZZ_2:
            draw_mosquito(f, FACE_X, 8 - (i % 2), i)
            f.small_text("BZZZZ", 60, 2, C.WHITE)
        elif i in BUZZ_3:
            draw_mosquito(f, FACE_X, 8 - (i % 2), i)
            f.text("BZZZZ", 60 + (i % 2), 0, C.RED)
        elif i in HOLD:
            draw_mosquito(f, FACE_X, 8, i)
        elif i in ESCAPE:
            t = i - ESCAPE.start
            mx = FACE_X - 2 - t * 8
            my = 9 if t < 2 else 10
            if mx >= -2:
                draw_mosquito(f, mx, my, i)
                draw_note(f, mx + 3 + (t % 2), my - 3 + (t // 2) % 2)

        # Lamp clicks and the slap.
        if on:
            f.small_text("CLICK", 30, 1, C.WHITE)
        if i in SLAP_TEXT:
            f.text("SLAP!", 60 - (i == SLAP), 0, C.YELLOW if i % 2 else C.RED)
        if i in STARS:
            k = i - STARS.start
            stars = [(91, 3), (92, 6), (90, 9)] if k % 2 else [(92, 4), (90, 2), (91, 8)]
            for x, y in stars:
                f.pixel(x, y, C.WHITE if k % 2 else C.YELLOW)
        if i >= CAPTION_FROM:
            f.small_text("3:47 AM", 4, 9, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/mosquito.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
