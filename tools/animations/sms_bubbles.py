#!/usr/bin/env python3
"""
Texting -- a conversation, one bubble at a time.

Outgoing bubbles are green and hug the right edge; incoming are blue and hug
the left, and each is preceded by the three-dot typing indicator. Text is
suggested by dashes of pseudo-words rather than letters -- at four rows per
bubble there is no room for a font, and the shape of a message is what the
eye recognises anyway. When a fourth bubble arrives the thread scrolls up.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 160

SLOT_Y = [1, 6, 11]
BUBBLE_H = 4
# (frame, kind, width); typing shows for the 3 frames before each incoming.
EVENTS = [(0, "out", 34), (6, "in", 26), (9, "out", 40), (15, "in", 22), (18, "out", 30)]
TYPING_LEAD = 3


def words(seed, length):
    """A run of dash 'words' with 1px gaps, deterministic per bubble."""
    out, x, n = [], 0, seed
    while x < length:
        n = (n * 1103515245 + 12345) & 0x7FFFFFFF
        w = 2 + (n >> 16) % 4
        w = min(w, length - x)
        out.append((x, w))
        x += w + 1
    return out


def draw_bubble(frame, kind, width, y, popping=False):
    if popping:
        width = max(6, int(width * 0.6))
    x = 2 if kind == "in" else 94 - width
    fill = C.BLUE if kind == "in" else C.GREEN
    ink = C.WHITE if kind == "in" else C.BLACK
    frame.rect(x, y, width, BUBBLE_H, fill, fill=True)
    for cx, cy in ((x, y), (x + width - 1, y), (x, y + BUBBLE_H - 1), (x + width - 1, y + BUBBLE_H - 1)):
        frame.pixel(cx, cy, C.BLACK)
    tail_x = x - 1 if kind == "in" else x + width
    frame.pixel(tail_x, y + BUBBLE_H - 1, fill)
    if popping:
        return
    for row, seed in ((1, width), (2, width * 7)):
        length = width - 4 if row == 1 else width // 2
        for wx, ww in words(seed, length):
            frame.hline(x + 2 + wx, y + row, ww, ink)


def draw_typing(frame, y, tick):
    frame.rect(2, y, 11, BUBBLE_H, C.BLUE, fill=True)
    for cx, cy in ((2, y), (12, y), (2, y + BUBBLE_H - 1), (12, y + BUBBLE_H - 1)):
        frame.pixel(cx, cy, C.BLACK)
    for i in range(3):
        frame.pixel(5 + i * 2, y + 1 + (0 if i == tick % 3 else 1), C.WHITE if i == tick % 3 else C.CYAN)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shown = [e for e in EVENTS if e[0] <= index]
        typing = any(index < f <= index + TYPING_LEAD for f, kind, _ in EVENTS if kind == "in")
        rows = [("bubble", e) for e in shown] + ([("typing", None)] if typing else [])
        rows = rows[-len(SLOT_Y):]
        for slot, (what, event) in zip(SLOT_Y, rows):
            if what == "typing":
                draw_typing(frame, slot, index)
            else:
                start, kind, width = event
                draw_bubble(frame, kind, width, slot, popping=index == start)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sms_bubbles.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
