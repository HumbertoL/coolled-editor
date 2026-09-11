#!/usr/bin/env python3
"""
BIOS -- the power-on self test, two lines at a time.

White text on black, the way it looked before the splash screen hid it. Each
line appears and the last one scrolls up to make room; the memory test counts
up in 64K steps to 640K OK, the keyboard check passes, and it boots to a
C:\\> prompt with a blinking cursor.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130

# (frame it appears, text). MEMORY is special-cased to count.
LINES = [
    (0, "AWARD BIOS V4.51"),
    (5, "CPU: 486DX2 66MHZ"),
    (11, "MEMORY TEST:"),
    (24, "IDE0: 540MB  OK"),
    (30, "KEYBOARD..  OK"),
    (36, "BOOT FROM C:"),
    (42, "C:\\>"),
]
MEM_START, MEM_END = 11, 22


def color_for(text, index):
    if text.endswith("OK"):
        return C.WHITE
    return C.WHITE


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shown = [(at, text) for at, text in LINES if index >= at]
        visible = shown[-2:]
        for row, (at, text) in enumerate(visible):
            y = 0 if len(visible) == 2 and row == 0 else 9
            if text.startswith("MEMORY"):
                k = min(MEM_END, index) - MEM_START
                kb = min(640, 64 * (k + 1))
                text = f"MEMORY TEST: {kb}K" + (" OK" if index >= MEM_END else "")
            frame.text(text, 1, y, C.WHITE, proportional=True)
            if text.endswith("OK"):
                w = frame.text_width(text, proportional=True)
                frame.text("OK", 1 + w - frame.text_width("OK", proportional=True), y, C.GREEN, proportional=True)
            if text == "C:\\>" and index % 2 == 0:
                w = frame.text_width(text, proportional=True)
                frame.rect(1 + w + 2, y, 4, 7, C.WHITE, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bios.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
