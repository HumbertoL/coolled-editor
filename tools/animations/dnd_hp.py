#!/usr/bin/env python3
"""
Hit points -- a bad round.

A health bar with a heart and a running HP total. Damage lands in chunks
with the number floating up in red and the lost section of bar flashing
before it vanishes; one heal floats up green and the bar grows
back a little. The last hit leaves it at 3 of 58 with the bar blinking red,
which is the state every party has been in.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
MAX_HP = 58
# (frame, change)
EVENTS = [(5, -7), (14, -12), (24, +9), (33, -20), (42, -25)]
BAR_X, BAR_Y, BAR_W = 20, 10, 72
POP_FRAMES = 5


def hp_at(index):
    hp = MAX_HP
    for at, change in EVENTS:
        if index >= at:
            hp = max(0, min(MAX_HP, hp + change))
    return hp


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        hp = hp_at(index)
        previous = hp_at(index - 1) if index else MAX_HP
        low = hp <= 10

        heart = C.RED if not low or index % 2 else C.WHITE
        frame.glyph("+HEART", 3, 1, heart)
        frame.text("HP", 11, 1, C.WHITE, proportional=True)
        frame.text(f"{hp}/{MAX_HP}", 26, 1, C.RED if low else C.YELLOW, proportional=True)

        frame.rect(BAR_X, BAR_Y, BAR_W, 4, C.BLUE)
        inner = BAR_W - 2
        filled = round(inner * hp / MAX_HP)
        bar_color = C.GREEN if hp > MAX_HP // 2 else C.YELLOW if not low else (C.RED if index % 2 else C.WHITE)
        frame.rect(BAR_X + 1, BAR_Y + 1, filled, 2, bar_color, fill=True)

        for at, change in EVENTS:
            k = index - at
            if 0 <= k < POP_FRAMES:
                if change < 0:
                    # The lost chunk of bar flashes red for two frames.
                    lost_from = round(inner * hp / MAX_HP)
                    lost_to = round(inner * min(MAX_HP, hp - change) / MAX_HP)
                    if k < 2:
                        frame.rect(BAR_X + 1 + lost_from, BAR_Y + 1, lost_to - lost_from, 2,
                                   C.RED if k == 0 else C.WHITE, fill=True)
                label = f"{change:+d}"
                color = C.RED if change < 0 else C.GREEN
                x = BAR_X + 1 + min(lost_to if change < 0 else filled, inner - 12)
                frame.text(label, x, 8 - k, C.WHITE if k == 0 else color, proportional=True)
                if change > 0 and k == 0:
                    frame.text("HEAL", 70, 1, C.GREEN, proportional=True)
        del previous
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dnd_hp.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
