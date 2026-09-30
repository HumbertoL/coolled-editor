#!/usr/bin/env python3
"""
Surprised Pikachu (2018) -- the face you make when the consequence arrives.

The setup types out on the left, STUDY FOR EXAM? then NAH, while a
contented yellow mouse face watches from the right. Then the text flips to
FAILED THE EXAM, the eyes swell, the ears jolt and the mouth stretches
into a wide O. The whole frame stays shocked for a beat, and the loop resets.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 46
DELAY = 100
FX, FY = 80, 0  # face origin (15 wide, 16 tall)


def face(frame, ox, oy, eye, mouth, ear_jolt=0):
    """eye 0..2 size, mouth 0..3 openness (0 = little smile)."""
    y = C.YELLOW
    # ears: 2px bars leaning outward, tips left dark (black-tipped)
    for k in range(5):
        row = oy + 5 - k - ear_jolt
        for x in (3 - k // 3, 4 - k // 3, 10 + k // 3, 11 + k // 3):
            if k >= 2 or True:
                frame.pixel(ox + x, row, y)
    # head: ellipse
    cx, cy, rx, ry = 7.0, 9.8, 7.4, 6.4
    for row in range(16):
        for col in range(15):
            if ((col - cx) / rx) ** 2 + ((row - cy) / ry) ** 2 <= 1.0:
                frame.pixel(ox + col, oy + row, y)
    # cheeks
    for cxp in (0, 12):
        frame.rect(ox + cxp + 1, oy + 11, 2, 2, C.RED, fill=True)
    # eyes
    for ex in (3, 10):
        if eye == 0:
            frame.rect(ox + ex, oy + 8, 2, 2, C.BLACK, fill=True)
        elif eye == 1:
            frame.rect(ox + ex, oy + 7, 2, 3, C.BLACK, fill=True)
            frame.pixel(ox + ex, oy + 8, C.WHITE)
        else:
            x0 = ex if ex < 7 else ex - 1
            frame.rect(ox + x0, oy + 7, 3, 3, C.BLACK, fill=True)
            frame.pixel(ox + x0 + 1, oy + 8, C.WHITE)
    frame.pixel(ox + 7, oy + 10, C.BLACK)
    # mouth
    if mouth == 0:
        frame.hline(ox + 6, oy + 12, 3, C.BLACK)
    elif mouth == 1:
        frame.rect(ox + 6, oy + 12, 3, 2, C.BLACK, fill=True)
    elif mouth == 2:
        frame.rect(ox + 6, oy + 11, 3, 3, C.BLACK, fill=True)
        frame.pixel(ox + 7, oy + 13, C.RED)
    else:
        frame.rect(ox + 5, oy + 11, 5, 4, C.BLACK, fill=True)
        frame.pixel(ox + 7, oy + 14, C.RED)
        frame.pixel(ox + 5, oy + 11, C.YELLOW)
        frame.pixel(ox + 9, oy + 11, C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    line1, line2 = "STUDY FOR", "EXAM?"
    for i in range(FRAMES):
        f = anim.frame()
        if i < 26:
            n1 = min(len(line1), 1 + i)
            f.text(line1[:n1], 1, 1, C.WHITE, proportional=True)
            if i >= 9:
                f.text(line2[: min(len(line2), i - 8)], 1, 9, C.WHITE, proportional=True)
            if i >= 17:
                f.text("NAH", 34, 9, C.YELLOW if (i // 2) % 2 else C.WHITE, proportional=True)
            blink = i % 12 == 10
            face(f, FX, FY, 0, 0)
            if blink:
                f.rect(FX + 3, FY + 8, 2, 2, C.YELLOW, fill=True)
                f.rect(FX + 10, FY + 8, 2, 2, C.YELLOW, fill=True)
        else:
            k = i - 26
            eye = 1 if k < 2 else 2
            mouth = 0 if k < 1 else min(3, k - 0)
            jolt = 1 if k in (1, 2, 4) else 0
            jx = 1 if k in (2, 3) else 0
            face(f, FX + jx, FY, eye, mouth, jolt)
            if k >= 1:
                fl = C.RED if (k // 2) % 2 == 0 else C.WHITE
                f.text("FAILED", 1, 1, fl, proportional=True)
                f.text("THE EXAM", 1, 9, C.RED, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/surprised_pikachu.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
