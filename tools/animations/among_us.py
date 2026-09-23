#!/usr/bin/env python3
"""
Among Us (2020) -- when the crewmate is sus, and the vote goes wrong.

Red walks in along the deck -- bean body, cyan visor with its glint,
backpack bump -- and stops. The verdict lands beside it in double-height
letters: SUS. Cut to space: the ejected crewmate tumbles end over end across
a parallax starfield, a quarter turn every two frames, and drifts off the
right edge. Then the game's own epitaph types itself out one letter at a
time over the stars: RED WAS NOT / THE IMPOSTOR.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.font import glyph  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 2020
# '#' suit, 'P' backpack, 'V' visor, 'W' visor glint.
CREW = [
    "...#####...",
    "..#######..",
    "..####VVVV.",
    "PP###VWVVVV",
    "PP###VVVVV.",
    "PP#######..",
    "PP#######..",
    "PP#######..",
    "..#######..",
    "..#######..",
]
LEGS = [
    ["..###.###..", "..###.###.."],
    ["..###.###..", ".###...###."],
]
COLORS = {"#": C.RED, "P": C.RED, "V": C.CYAN, "W": C.WHITE}

WALK_END, SUS_AT, EJECT_AT, TYPE_AT = 10, 5, 12, 30
FLOOR_Y = 15
LINES = [("RED WAS NOT", 0), ("THE IMPOSTOR.", 8)]
TYPE_RATE = 1.5  # characters per frame


def crew_sprite(walk_phase):
    return CREW + LEGS[walk_phase]


def rotate(rows, quarter_turns):
    for _ in range(quarter_turns % 4):
        rows = ["".join(row[c] for row in reversed(rows)) for c in range(len(rows[0]))]
    return rows


def draw(frame, rows, x0, y0):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in COLORS:
                frame.pixel(x0 + c, y0 + r, COLORS[ch])


def big_text(frame, text, x, y, color):
    """The 5x7 font at double size, for SUS."""
    for char in text:
        bitmap = glyph(char)
        for r, line in enumerate(bitmap):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.rect(x + c * 2, y + r * 2, 2, 2, color, fill=True)
        x += 12


def build():
    rng = random.Random(SEED)
    stars = [(rng.uniform(0, 96), rng.randrange(16), rng.choice([1, 1, 2, 3])) for _ in range(34)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index < EJECT_AT:
            # On the ship: a deck line, the crewmate walking in and halting.
            frame.hline(0, FLOOR_Y, 96, C.BLUE)
            for x in range(4, 96, 12):
                frame.pixel(x, FLOOR_Y, C.WHITE)
            t = min(index, WALK_END) / WALK_END
            x = round(-11 + 25 * (1 - (1 - t) ** 2))
            phase = (index // 2) % 2 if index < WALK_END else 0
            draw(frame, crew_sprite(phase), x, FLOOR_Y - 12)
            if index >= SUS_AT:
                k = index - SUS_AT
                color = C.WHITE if k == 0 else C.RED if k % 4 < 2 else C.YELLOW
                big_text(frame, "SUS", 42, 1, color)
            continue

        # Space. Stars stream left: slow ones dim, fast ones bright.
        typing = index >= TYPE_AT
        t = index - EJECT_AT
        for sx, sy, speed in stars:
            x = round(sx - speed * t * 1.5) % 96
            if typing and speed < 3:
                if speed == 1:
                    frame.pixel(x, sy, C.BLUE)
                continue
            frame.pixel(x, sy, C.BLUE if speed == 1 else C.CYAN if speed == 2 else C.WHITE)

        if not typing:
            # The body tumbles across: a quarter turn every two frames.
            span = TYPE_AT - EJECT_AT
            x = round(-13 + (96 + 14) * t / (span - 1))
            y = round(2 + 1.5 * math.sin(t * 0.6))
            rows = rotate(crew_sprite(0), t // 2)
            # Rotated sprites are wider than tall; keep them vertically centred.
            y = max(0, min(16 - len(rows), y - (len(rows) - 12) // 2))
            draw(frame, rows, x, y)
            continue

        shown = int((index - TYPE_AT + 1) * TYPE_RATE)
        for text, y in LINES:
            part = text[:max(0, shown)]
            shown -= len(text)
            if part:
                x = (96 - frame.text_width(text, proportional=True)) // 2
                # Wipe stars out of the text's own rows so the letters stay clean.
                frame.rect(x - 1, y, frame.text_width(text, proportional=True) + 2, 7, C.BLACK, fill=True)
                frame.text(part, x, y, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/among_us.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
