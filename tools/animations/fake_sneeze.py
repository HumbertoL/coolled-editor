#!/usr/bin/env python3
"""
Fake sneeze -- the build-up, the letdown, then the ambush.

A big yellow face fills the left of the panel. AH... AHH... AHHHH...: each
time the head tips further back (features slide up, nostrils flare wider),
eyes squeeze shut, and it holds there, quivering. Then it all drains away:
...NEVERMIND. A quiet beat -- and the panel flashes white as a double-size
CHOO!! detonates, the head snapping forward and a spray of cyan, white and
green droplets blasting across all 96 columns. The droplets stay stuck to
the glass and slide down while the face, blushing and glancing away with a
drip on its nose, mumbles ...EXCUSE ME.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

DELAY = 130
TEXT_X = 26
# Head outline: per-row inset from each side, rows 0..15.
INSETS = (4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 4)
HX, HW = 3, 19          # head spans x 3..21
CX = HX + HW // 2       # 12


def big_text(frame, text, x, y, color):
    """The 5x7 font at double size (10x14 per glyph)."""
    positions, _ = layout_text(text, 1, proportional=True)
    for char, cell_x in positions:
        bitmap = glyph(char)
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    frame.rect(x + 2 * (cell_x + col), y + 2 * row, 2, 2, color, fill=True)


def head(frame, dy=0, skin=C.YELLOW):
    for row, inset in enumerate(INSETS):
        frame.hline(HX + inset, row + dy, HW - 2 * inset, skin)
    # Ears.
    for ear_x in (HX - 1, HX + HW):
        frame.vline(ear_x, 6 + dy, 4, skin)


def face(frame, tilt=0, eyes="open", nostrils=0, mouth=(3, 2), brows=0,
         dy=0, blush=False, look=0, jitter=0):
    """
    Draw the face. ``tilt`` > 0 tips the head back (features slide up),
    < 0 snaps it forward. ``nostrils`` 0..2 is how flared they are.
    """
    dx = jitter
    head(frame, dy)
    lift = -tilt + dy

    def px(x, y, color=C.BLACK):
        frame.pixel(x + dx, y + lift, color)

    def hl(x, y, n, color=C.BLACK):
        frame.hline(x + dx, y + lift, n, color)

    # Eyebrows: raised by ``brows``.
    by = 3 - brows
    if eyes == "shut":
        # Scrunched-down brows angled in.
        hl(CX - 6, by + 1, 3)
        px(CX - 3, by + 2)
        hl(CX + 4, by + 1, 3)
        px(CX + 3, by + 2)
    else:
        hl(CX - 6, by, 4)
        hl(CX + 3, by, 4)
    # Eyes.
    ey = 5
    if eyes == "open":
        for ex in (CX - 5, CX + 4):
            frame.rect(ex + dx, ey + lift, 2, 2, C.WHITE, fill=True)
            px(ex + (1 if look > 0 else 0), ey + 1)
    elif eyes == "half":
        for ex in (CX - 5, CX + 4):
            hl(ex - 1, ey, 4)
            px(ex + (1 if look > 0 else 0), ey + 1)
            px(ex + (2 if look > 0 else 1), ey + 1)
    elif eyes == "shut":
        # > <
        px(CX - 6, ey - 1); px(CX - 5, ey); px(CX - 4, ey); px(CX - 6, ey + 1)
        px(CX + 6, ey - 1); px(CX + 5, ey); px(CX + 4, ey); px(CX + 6, ey + 1)
    elif eyes == "dazed":
        for ex in (CX - 5, CX + 4):
            hl(ex - 1, ey + 1, 4)
    # Nose shading and nostrils.
    ny = 9
    px(CX, ny - 2, C.RED)
    px(CX, ny - 1, C.RED)
    if nostrils == 0:
        px(CX - 1, ny); px(CX + 1, ny)
    elif nostrils == 1:
        hl(CX - 2, ny, 2); hl(CX + 1, ny, 2)
    else:
        hl(CX - 3, ny, 3); hl(CX + 1, ny, 3)
        hl(CX - 2, ny + 1, 2); hl(CX + 1, ny + 1, 2)
        px(CX - 4, ny - 1, C.RED); px(CX + 4, ny - 1, C.RED)
    # Mouth: an open black hole, w x h, centred.
    mw, mh = mouth
    my = 12 if nostrils < 2 else 12
    if mh == 0:
        # Closed, slightly wobbly line (sheepish).
        hl(CX - 2, my, 2)
        hl(CX, my + 1, 2)
        px(CX + 2, my)
    else:
        frame.rect(CX - mw // 2 + dx, my + lift, mw, mh, C.BLACK, fill=True)
        if mh >= 3 and mw >= 3:
            frame.hline(CX - mw // 2 + 1 + dx, my + mh - 1 + lift, mw - 2, C.RED)
    if blush:
        frame.hline(CX - 7 + dx, 9 + dy, 2, C.RED)
        frame.hline(CX + 6 + dx, 9 + dy, 2, C.RED)


def spray_drops(seed=7, count=95):
    rng = random.Random(seed)
    drops = []
    for _ in range(count):
        x = rng.uniform(17, 95)
        # Fan out from the mouth: wider the further right.
        spread = 2 + (x - 14) * 0.15
        y = 11 + rng.uniform(-spread, spread * 0.6)
        speed = rng.uniform(0.6, 1.0)
        col = rng.choice((C.CYAN, C.CYAN, C.WHITE, C.WHITE, C.GREEN))
        drips = rng.random() < 0.45
        drops.append((x, y, speed, col, drips))
    return drops


DROPS = spray_drops()


def build():
    anim = Animation(delay=DELAY)

    def new():
        return anim.frame()

    # 0-3: innocent face.
    for i in range(4):
        f = new()
        face(f, eyes="open" if i != 2 else "half", mouth=(3, 1))
    # 4-7: AH... (tilt 1)
    for i in range(4):
        f = new()
        face(f, tilt=1, eyes="half", nostrils=1, mouth=(3, 2), brows=1)
        f.text("AH..."[: 2 + i + 1], TEXT_X, 5, C.WHITE, proportional=True)
    # 8-11: AHH... (tilt 2)
    for i in range(4):
        f = new()
        face(f, tilt=2, eyes="half", nostrils=1, mouth=(5, 3), brows=1)
        f.text("AHH..."[: 3 + i], TEXT_X, 5, C.CYAN, proportional=True)
    # 12-16: AHHHH... (tilt 3, eyes shut, nostrils flared)
    for i in range(5):
        f = new()
        face(f, tilt=3, eyes="shut", nostrils=2, mouth=(5, 4), brows=1,
             jitter=(i % 2))
        f.text("AHHHH..."[: min(8, 4 + i)], TEXT_X, 5, C.YELLOW, proportional=True)
    # 17-21: held, quivering on the brink.
    for i in range(5):
        f = new()
        face(f, tilt=3, eyes="shut", nostrils=2, mouth=(5, 4), brows=1,
             jitter=(i % 2))
        f.text("AHHHH...", TEXT_X + (i % 2), 5, C.YELLOW, proportional=True)
    # 22-23: it drains away.
    f = new()
    face(f, tilt=2, eyes="half", nostrils=1, mouth=(3, 2))
    f = new()
    face(f, tilt=1, eyes="half", nostrils=0, mouth=(3, 1))
    # 24-29: ...NEVERMIND
    for i in range(6):
        f = new()
        face(f, eyes="half", mouth=(4, 1))
        msg = "...NEVERMIND"
        f.text(msg[: min(len(msg), 4 + 2 * i)], TEXT_X, 5, C.BLUE if i < 1 else C.CYAN,
               proportional=True)
    # 30-32: quiet beat. Just the face.
    for i in range(3):
        f = new()
        face(f, eyes="open" if i < 2 else "half", mouth=(2, 1), look=1 if i == 1 else 0)
    # 33: FLASH.
    f = new()
    f.fill(C.WHITE)
    head(f, 1, skin=C.YELLOW)
    face(f, tilt=-1, eyes="shut", nostrils=2, mouth=(7, 3))
    big_text(f, "CHOO!!", TEXT_X + 2, 1, C.RED)
    # 34-39: CHOO!! with the spray blasting right.
    for i in range(6):
        f = new()
        reach = 22 + (i + 1) * 16
        face(f, tilt=-1, eyes="shut", nostrils=2, mouth=(7, 3) if i < 4 else (5, 2),
             jitter=1 if i == 0 else 0)
        big_text(f, "CHOO!!", TEXT_X + 2 + (1 if i == 0 else 0), 1,
                 C.YELLOW if i % 2 else C.RED)
        # Droplets fly over everything, streaking.
        for x, y, speed, col, _ in DROPS:
            if x < reach * speed + 10 and x > HX + HW - 2:
                f.pixel(x, y, col)
                if i < 4:
                    f.pixel(x - 1, y, C.BLUE)
                    if i < 2:
                        f.pixel(x - 2, y, C.BLUE)
    # 40-45: droplets stuck on the glass, sliding down. Face dazed.
    for i in range(6):
        f = new()
        for x, y, speed, col, drips in DROPS:
            yy = y + (i * 1.2 * speed if drips else 0)
            f.pixel(x, yy, col)
            if drips and i > 0:
                f.pixel(x, yy - 1, C.BLUE)
        face(f, eyes="dazed", mouth=(3, 1))
    # 46-52: sheepish: blush, glance away, a drip on the nose.
    for i in range(7):
        f = new()
        for x, y, speed, col, drips in DROPS:
            yy = y + (6 * 1.2 * speed if drips else 0)
            if yy < 16:
                f.pixel(x, yy, col)
                if drips:
                    f.pixel(x, yy - 1, C.BLUE)
                    f.pixel(x, yy - 2, C.BLUE)
        # Blank a box behind the words so they read.
        f.rect(TEXT_X - 1, 4, 62, 9, C.BLACK, fill=True)
        face(f, eyes="open", mouth=(0, 0), blush=True, look=1)
        # Nose drip, growing.
        drip = min(3, i // 2 + 1)
        f.vline(CX + 1, 10, drip, C.CYAN)
        msg = "...EXCUSE ME"
        f.text(msg[: min(len(msg), 5 + 3 * i)], TEXT_X, 5, C.MAGENTA, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fake_sneeze.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
