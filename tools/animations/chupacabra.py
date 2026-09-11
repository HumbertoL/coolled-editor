#!/usr/bin/env python3
"""
Chupacabra -- the goat sucker, doing what it says on the tin.

A goat grazes at the right in the dark. Two red eyes open at the far left
and come closer, the gap between them widening as it approaches, and the
body dithers in out of the black behind them -- pixels chosen by a hash of
their offset from the spine, so the reveal is stable while the animal moves.
Hackles up, a crouch, a lunge with a motion-blurred trail, one frame of
white. No goat. It looks up at you, the eyeshine goes bright, and it backs
into the dark eyes-last.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
GROUND = 15

# Scene beats, by frame index.
EYES_AT = 4         # two red points, far off
APPROACH_TO = 24    # it has crossed the clearing
CROUCH_AT = 26      # hackles up
LUNGE_AT = 30
FLASH_AT = 32       # the frame nobody ever gets a photograph of
FEED_TO = 40
LOOK_TO = 46        # it notices the camera
GONE_AT = 47        # and dissolves back out

START_X, GOAT_X = 8, 70


def revealed(dx, dy, visible):
    """A stable dither: the same pixels come back as the fraction grows."""
    return ((dx * 37 + dy * 91) % 101) / 101.0 < visible


def draw_goat(frame, x, bob):
    frame.rect(x, 8 + bob, 9, 4, C.WHITE, fill=True)
    frame.rect(x + 8, 10 + bob, 3, 3, C.WHITE, fill=True)   # head, down in the grass
    frame.pixel(x + 10, 9 + bob, C.WHITE)                    # horn
    for leg in (1, 3, 6, 8):
        frame.vline(x + leg, 12 + bob, GROUND - 11 - bob, C.WHITE)


def draw_beast(frame, x, visible=1.0, hackles=0, eye=C.RED, blink=False):
    """
    Low-slung body, spines, four legs, and the eyes.

    ``x`` is the shoulder; the head is forward of it, to the right.
    """
    cells = []
    for dx in range(-7, 8):
        thickness = 2 if abs(dx) < 5 else 1
        for dy in range(-thickness, thickness + 1):
            cells.append((dx, dy, C.MAGENTA))
    for dx in range(8, 13):                                   # neck and muzzle
        for dy in range(-2, 1):
            cells.append((dx, dy - 1, C.MAGENTA))
    for dx in range(-6, 6, 2):                                # spines along the back
        for step in range(1 + hackles):
            cells.append((dx, -3 - step, C.RED))
    for dx in (-6, -4, 4, 6):                                 # legs
        for dy in range(3, GROUND - 7):
            cells.append((dx, dy, C.MAGENTA))
    for step, dx in enumerate(range(-8, -12, -1)):            # tail
        cells.append((dx, -1 - step, C.MAGENTA))

    body_y = 8
    for dx, dy, color in cells:
        if revealed(dx, dy, visible):
            frame.pixel(x + dx, body_y + dy, color)
    if not blink:
        for dy in (-3, -2):
            frame.pixel(x + 11, body_y + dy, eye)
        frame.pixel(x + 9, body_y - 3, eye)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, GROUND, 96, C.BLUE)

        if index == FLASH_AT:
            frame.fill(C.WHITE)
            continue

        if index < FLASH_AT:
            draw_goat(frame, GOAT_X, 1 if index % 6 < 3 else 0)

        if index < EYES_AT:
            continue

        if index < LUNGE_AT:
            t = min(1.0, (index - EYES_AT) / (APPROACH_TO - EYES_AT))
            x = round(START_X + (44 - START_X) * t)
            visible = 0.0 if index < 10 else min(1.0, (index - 10) / 12)
            hackles = 1 if index >= CROUCH_AT else 0
            draw_beast(frame, x, visible, hackles, blink=index in (12, 20))
        elif index < FLASH_AT:
            # The lunge, with the frames it skipped drawn in behind it.
            t = (index - LUNGE_AT + 1) / (FLASH_AT - LUNGE_AT + 1)
            x = round(44 + (GOAT_X - 40) * t)
            for ghost in (10, 20):
                draw_beast(frame, x - ghost, 0.45, 1, eye=C.RED)
            draw_beast(frame, x, 1.0, 1)
        elif index <= FEED_TO:
            draw_beast(frame, GOAT_X + 2, 1.0, 1, blink=True)
        elif index <= LOOK_TO:
            eye = C.WHITE if index == LOOK_TO - 1 else C.RED
            draw_beast(frame, GOAT_X - 4, 1.0, 0, eye=eye)
        else:
            fade = 1 - (index - GONE_AT) / (FRAMES - GONE_AT)
            draw_beast(frame, GOAT_X - 4, fade, 0, blink=index == FRAMES - 2)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/chupacabra.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
