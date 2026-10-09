#!/usr/bin/env python3
"""
Toaster -- launch, long wait, perfect landing.

A chrome toaster (white outline, cyan body, a white glint) on a blue
counter, lever down, its two slots glowing red while a little dial ticks
round and TICK... flickers beside it. DING! The lever snaps up and both
slices rocket straight out of the top of the panel on speed lines. Then:
an empty toaster and a very long wait while ". . ." fills in one dot at a
time. A whistle of red streaks from above -- and the toast comes back down,
charred black with red char marks and on fire, dropping exactly into the
slots. The toaster squashes on impact, a smoke puff rolls up, and NAILED IT
appears while the flames flicker on.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 120
TX, TW = 8, 26           # toaster body x 8..33
TOP = 6                  # top edge of the toaster body
COUNTER = 15
SLOTS = (12, 23)         # slot x starts, each 7 wide
SLOT_W = 7
TEXT_X = 42


def toaster(f, lever_down=False, glow=False, squash=0, dial=0):
    top = TOP + squash
    x0, w = TX - squash, TW + 2 * squash
    # Body: cyan fill, white outline with rounded top corners.
    f.rect(x0, top, w, COUNTER - top, C.CYAN, fill=True)
    f.hline(x0 + 1, top, w - 2, C.WHITE)
    f.vline(x0, top + 1, COUNTER - top - 1, C.WHITE)
    f.vline(x0 + w - 1, top + 1, COUNTER - top - 1, C.WHITE)
    # Glint.
    f.vline(x0 + 3, top + 2, 4 - squash, C.WHITE)
    f.pixel(x0 + 4, top + 2, C.WHITE)
    # Slots.
    for sx in SLOTS:
        f.hline(sx, top, SLOT_W, C.RED if glow else C.BLACK)
        if glow:
            f.hline(sx + 1, top + 1, SLOT_W - 2, C.RED)
    # Dial on the front.
    cx, cy = x0 + w - 6, top + 4
    f.rect(cx - 1, cy - 1, 3, 3, C.BLUE, fill=True)
    hand = ((0, -1), (1, 0), (0, 1), (-1, 0))[dial % 4]
    f.pixel(cx, cy, C.WHITE)
    f.pixel(cx + hand[0], cy + hand[1], C.RED)
    # Lever on the right side.
    lx = x0 + w
    f.vline(lx, top + 1, COUNTER - top - 2, C.BLUE)
    ly = (COUNTER - 3) if lever_down else top + 1
    f.rect(lx, ly, 3, 2, C.YELLOW, fill=True)
    # Feet.
    f.pixel(x0 + 1, COUNTER, C.WHITE)
    f.pixel(x0 + w - 2, COUNTER, C.WHITE)


def counter(f):
    f.hline(0, COUNTER, 96, C.BLUE)


def toast(f, sx, top, burnt=False, flame=None, limit=TOP):
    """
    One slice, 5 wide x 8 tall with a rounded top, its top row at ``top``.
    Only rows above ``limit`` are drawn: below that it is inside the toaster.
    """
    x = sx + 1
    w = 5

    def px(px_x, px_y, color):
        if px_y < limit:
            f.pixel(px_x, px_y, color)

    body = C.BLACK if burnt else C.YELLOW
    edge = C.RED if burnt else C.YELLOW
    for row in range(8):
        y = top + row
        if row == 0:
            for k in range(1, w - 1):
                px(x + k, y, edge)
        else:
            for k in range(w):
                px(x + k, y, edge if k in (0, w - 1) else body)
    if burnt:
        for dx, dy in ((2, 2), (1, 4), (3, 5), (2, 7)):
            px(x + dx, top + dy, C.RED)
    if flame is not None:
        # Flames licking off the top, flickering with ``flame``.
        tips = ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1)) if flame % 2 == 0 else \
            ((0, 2), (1, 1), (2, 2), (3, 1), (4, 2))
        for dx, h in tips:
            for k in range(h):
                px(x + dx, top - 1 - k, C.YELLOW if k == 0 else C.RED)


def scene(f, **kw):
    counter(f)
    toaster(f, **kw)


def build():
    anim = Animation(delay=DELAY)
    new = anim.frame

    # 0-9: toasting. Lever down, slots glow, dial ticks.
    for i in range(10):
        f = new()
        scene(f, lever_down=True, glow=True, dial=i)
        # Heat shimmer over the slots.
        for sx in SLOTS:
            f.pixel(sx + 2 + (i % 2), TOP - 2, C.RED)
            f.pixel(sx + 4 - (i % 2), TOP - 4, C.RED)
        f.small_text("TICK" if i % 2 == 0 else "TOCK", TEXT_X, 6,
                     C.WHITE if i % 2 == 0 else C.CYAN)
    # 10: DING! Lever snaps up, toast pops.
    f = new()
    scene(f, dial=0)
    for sx in SLOTS:
        toast(f, sx, 0)
    f.text("DING!", TEXT_X, 4, C.YELLOW, proportional=True)
    # 11-12: launch. Toast streaks off the top.
    for i, ty in enumerate((-5, -12)):
        f = new()
        scene(f)
        for sx in SLOTS:
            toast(f, sx, ty)
            length = 6 if i == 0 else 4
            for dx in (1, 3, 5):
                f.vline(sx + dx, max(0, ty + 8), length, C.WHITE if i == 0 else C.BLUE)
        f.text("DING!", TEXT_X + (i % 2), 4, C.YELLOW, proportional=True)
    # 13-27: empty toaster. Long beat while the dots fill in.
    for i in range(15):
        f = new()
        scene(f)
        dots = min(3, i // 4)
        for d in range(dots):
            f.rect(TEXT_X + 8 + d * 8, 9, 2, 2, C.WHITE, fill=True)
        if i == 0:
            # Last wisps of the launch.
            for sx in SLOTS:
                f.pixel(sx + 3, 1, C.BLUE)
                f.pixel(sx + 3, 3, C.BLUE)
    # 28-29: incoming -- red streaks fall in from the top.
    for i in range(2):
        f = new()
        scene(f)
        for d in range(3):
            f.rect(TEXT_X + 8 + d * 8, 9, 2, 2, C.WHITE, fill=True)
        for sx in SLOTS:
            f.vline(sx + 2 + i, 0, 2 + 3 * i, C.RED)
            f.vline(sx + 4 - i, 0, 1 + 2 * i, C.YELLOW)
        f.text("!", TEXT_X + 34, 4, C.RED, proportional=True)
    # 30-31: the burnt, flaming toast falls in.
    for i, ty in enumerate((-6, -1)):
        f = new()
        scene(f)
        for sx in SLOTS:
            toast(f, sx, ty, burnt=True, flame=i)
            for dx in (1, 5):
                f.vline(sx + dx, 0, max(0, ty - 1), C.RED)
    # 32: impact. Toaster squashes, toast lands home.
    f = new()
    scene(f, squash=1)
    for sx in SLOTS:
        toast(f, sx, 2, burnt=True, flame=0, limit=TOP + 1)
    for dx, dy in ((-2, 0), (-4, -1), (2, 0), (4, -1)):
        f.pixel(TX - 3 + dx, COUNTER - 1 + dy, C.WHITE)
        f.pixel(TX + TW + 5 + dx, COUNTER - 1 + dy, C.WHITE)
    # 33-37: smoke puff rolls up off the top.
    cx = (SLOTS[0] + SLOTS[1] + SLOT_W) // 2
    for i in range(5):
        f = new()
        scene(f)
        cy = 2 - i
        r = 2 + i // 2
        color = (C.WHITE, C.WHITE, C.CYAN, C.CYAN, C.BLUE)[i]
        for bx, by in ((-r - 1, 1), (0, 0), (r + 1, 1)):
            for y in range(cy + by - r, cy + by + r + 1):
                for x in range(cx + bx - 2 * r, cx + bx + 2 * r + 1):
                    if ((x - cx - bx) / 2) ** 2 + (y - cy - by) ** 2 <= r * r:
                        f.pixel(x, y, color)
        for sx in SLOTS:
            toast(f, sx, 2, burnt=True, flame=i)
    # 38-52: NAILED IT, flames flickering on.
    for i in range(15):
        f = new()
        scene(f)
        for sx in SLOTS:
            toast(f, sx, 2, burnt=True, flame=i)
        msg = "NAILED IT"
        shown = msg[: min(len(msg), 3 + 2 * i)]
        f.text(shown, TEXT_X - 2, 4, C.YELLOW if i < 13 else C.WHITE,
               proportional=True)
        if i >= 6:
            # A smug sparkle on the chrome.
            if i % 3 == 0:
                f.pixel(TX + 3, TOP + 2, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/toaster.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
