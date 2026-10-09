#!/usr/bin/env python3
"""
Magic 8-ball -- ask, shake, believe.

WILL IT / LOOP? types itself out in yellow beside a black 8-ball with a white
window showing the 8. The ball shakes on jittering offsets while the window
clouds blue and magenta question marks fly, then settles with a cyan triangle
and the answer fades up in the little font: SIGNS POINT / TO YES blinking green and yellow.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
CX, CY, R = 9.0, 8.0, 7.5
QUESTION = ["WILL IT", "LOOP?"]
ANSWER = ["SIGNS POINT", "TO YES"]


def ball(frame, dx, dy, face):
    for y in range(16):
        for x in range(20):
            d = math.hypot(x - CX, y - CY)
            if d <= R:
                frame.pixel(x + dx, y + dy, C.BLUE if d > R - 1 else C.BLACK)
    frame.pixel(round(CX + dx - 3), round(CY + dy - 4), C.WHITE)     # highlight
    frame.pixel(round(CX + dx - 4), round(CY + dy - 3), C.WHITE)
    # The little window: a bright disc with the '8' while idle, a triangle when it answers.
    for y in range(16):
        for x in range(20):
            if math.hypot(x - CX, y - CY) <= 3.2:
                frame.pixel(x + dx, y + dy, C.WHITE if face == "8" else (C.BLUE if face == "mix" else C.CYAN))
    if face == "8":
        frame.text("8", round(CX + dx) - 2, round(CY + dy) - 3, C.BLACK)
    if face == "ans":
        for r_, half in enumerate((0, 1, 2)):
            frame.hline(round(CX + dx) - half, round(CY + dy) - 1 + r_, 2 * half + 1, C.BLUE)


def build():
    rng = random.Random(8)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shaking = 16 <= index < 30
        answered = index >= 32
        if shaking:
            dx, dy = rng.choice((-2, -1, 1, 2)), rng.choice((-2, -1, 0, 1, 2))
            face = "mix"
        else:
            dx = dy = 0
            face = "ans" if answered else "8"
        ball(frame, dx, dy, face)
        # Question types out, then the answer replaces it in cyan.
        if not answered:
            n = min(len("".join(QUESTION)), (index // 1) * 1)
            typed = ""
            line = 0
            for li, text in enumerate(QUESTION):
                take = max(0, min(len(text), n - sum(len(q) for q in QUESTION[:li])))
                frame.text(text[:take], 28, 1 + li * 8, C.YELLOW)
        else:
            reveal = min(1.0, (index - 32) / 6)
            for li, text in enumerate(ANSWER):
                color = C.WHITE if reveal >= 1 else C.BLUE
                if li == 1 and reveal >= 1:
                    color = C.GREEN if index % 6 < 3 else C.YELLOW
                frame.small_text(text, 28, 3 + li * 7, color)
        if shaking:
            frame.text("?", 80, 4, C.MAGENTA if index % 2 else C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/magic_8_ball.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
