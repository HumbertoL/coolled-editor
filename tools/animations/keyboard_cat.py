#!/usr/bin/env python3
"""
Keyboard Cat (2007) -- play him off.

An orange cat sits behind a keyboard and bounces his paws on the keys, each
struck key lighting up while music notes drift up. Then PLAY HIM OFF flashes
in and a cane hooks him, dragging him tumbling off stage while the keys go
quiet; the keyboard is left alone for a beat before the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

DELAY = 100
PLAY = 30
OFF = 20
FRAMES = PLAY + OFF
KX0, KX1 = 20, 76        # keyboard extent
CAT_X = 48               # cat centre


def cat_sprite(step, blink):
    """Cat drawn on its own canvas; centre column is 48, keyboard hides row 12+."""
    c = Canvas()
    x = CAT_X
    # ears
    for ex in (-4, 3):
        c.pixel(x + ex, 0, C.YELLOW)
        c.pixel(x + ex + 1, 0, C.YELLOW)
        c.pixel(x + ex, 1, C.YELLOW)
        c.pixel(x + ex + 1, 1, C.YELLOW)
    c.pixel(x - 3, 1, C.RED)
    c.pixel(x + 3, 1, C.RED)
    c.rect(x - 4, 2, 9, 5, C.YELLOW, fill=True)
    # eyes / nose / stripes
    if blink:
        c.hline(x - 3, 4, 2, C.BLACK)
        c.hline(x + 1, 4, 2, C.BLACK)
    else:
        c.pixel(x - 3, 3, C.BLACK); c.pixel(x - 3, 4, C.BLACK)
        c.pixel(x + 2, 3, C.BLACK); c.pixel(x + 2, 4, C.BLACK)
    c.pixel(x - 1, 5, C.RED); c.pixel(x, 5, C.RED); c.pixel(x - 1, 6, C.RED)
    c.pixel(x, 2, C.RED); c.pixel(x - 2, 2, C.RED); c.pixel(x + 2, 2, C.RED)
    # body
    c.rect(x - 6, 7, 13, 6, C.YELLOW, fill=True)
    c.pixel(x - 5, 8, C.RED); c.pixel(x + 5, 8, C.RED)
    c.pixel(x - 5, 10, C.RED); c.pixel(x + 5, 10, C.RED)
    # arms + paws: one high, one low, alternating
    lp = 9 if step % 2 == 0 else 11
    rp = 11 if step % 2 == 0 else 9
    c.vline(x - 6, 8, lp - 8, C.YELLOW)
    c.vline(x + 6, 8, rp - 8, C.YELLOW)
    c.rect(x - 8, lp, 3, 2, C.WHITE, fill=True)
    c.rect(x + 5, rp, 3, 2, C.WHITE, fill=True)
    return c


def flip(c):
    out = Canvas()
    for (px, py) in c.lit():
        out.pixel(px, 15 - py, c.get(px, py))
    return out


def keyboard(f, pressed):
    f.rect(KX0, 12, KX1 - KX0, 4, C.WHITE, fill=True)
    for x in range(KX0 + 2, KX1, 4):
        f.vline(x, 12, 4, C.BLUE)
    for x in range(KX0 + 4, KX1 - 2, 4):
        f.rect(x - 1, 12, 2, 2, C.BLACK, fill=True)
    for px in pressed:
        f.rect(px, 13, 2, 3, C.CYAN, fill=True)


def note(f, x, y, color):
    f.pixel(x, y, color); f.pixel(x, y - 1, color); f.pixel(x, y - 2, color)
    f.pixel(x - 1, y, color); f.pixel(x + 1, y - 2, color)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        step = i // 2
        playing = i < PLAY + 6
        if i < PLAY:
            cat = cat_sprite(step, blink=(i % 15 == 14))
            f.blit(cat, 0, 0)
            pressed = [CAT_X - 8 + (0 if step % 2 == 0 else 1) - 2 + (step % 3) * 0, CAT_X + 5]
            pressed = [CAT_X - 8, CAT_X + 6] if step % 2 == 0 else [CAT_X - 5, CAT_X + 9]
            keyboard(f, pressed)
            for n in range(4):
                t = (i * 2 + n * 8) % 32
                ny = 11 - t // 2
                if ny >= 3:
                    nx = [KX0 - 10, KX1 + 6, KX0 - 4, KX1 + 12][n]
                    note(f, nx + (t // 4) % 2, ny + 2, [C.MAGENTA, C.CYAN, C.GREEN, C.RED][n])
        else:
            k = i - PLAY
            keyboard(f, [])
            # cane comes in from the right at k>=4
            if k < 2:
                f.blit(cat_sprite(k, blink=False), 0, 0)
            else:
                t = k - 2
                shift = -t * 11
                spr = cat_sprite(0, blink=False)
                if 1 <= t < 4:
                    spr = flip(spr)
                f.blit(spr, shift, 0)
                hx = CAT_X + shift + 10
                if hx > 0:
                    f.hline(hx, 6, 96 - hx, C.WHITE)
                    f.pixel(hx, 7, C.WHITE)
                    f.pixel(hx, 5, C.WHITE)
                    f.pixel(hx, 4, C.WHITE)
            keyboard(f, [])
            if k >= 5:
                col = C.RED if k % 2 else C.YELLOW
                f.text("PLAY HIM OFF", "center", 1, col, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/keyboard_cat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
