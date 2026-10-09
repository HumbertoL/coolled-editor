#!/usr/bin/env python3
"""
Piano -- the opening of Fur Elise, Synthesia style.

Twenty-two white keys from E2 to E5 span the panel, with the black keys cut
into them. Notes fall as bars onto the keys they play, their length the
note's duration: the right hand in cyan, the left in green, and a key lights
in its hand's colour for as long as it is held. The phrase ends on D#5 and
the piece goes straight back to E5, so the loop is seamless.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 85
STEP = 2              # frames per sixteenth note
FRAMES = 26 * STEP    # 26 sixteenths in the phrase
LOWEST = 40           # E2
PITCH = 4             # white keys 3px wide with a 1px gap
X0 = 4                # 22 white keys span 88px; centre them
KEYS_TOP = 6
BLACK_BOTTOM = 11
NAMES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
WHITE_CLASSES = (0, 2, 4, 5, 7, 9, 11)

RIGHT = "E5 D#5 E5 D#5 E5 B4 D5 C5 A4:2 . C4 E4 A4 B4:2 . E4 G#4 B4 C5:2 . E4 E5 D#5"
LEFT = {8: "A2", 9: "E3", 10: "A3", 14: "E2", 15: "E3", 16: "G#3", 20: "A2", 21: "E3", 22: "A3"}


def midi(name):
    note, octave = name[:-1], int(name[-1])
    return 12 * (octave + 1) + NAMES[note]


def notes():
    """(start sixteenth, midi, length in sixteenths, colour)."""
    out, t = [], 0
    for token in RIGHT.split():
        if token == ".":
            t += 1
            continue
        name, _, length = token.partition(":")
        length = int(length or 1)
        out.append((t, midi(name), length, C.CYAN))
        t += length
    assert t == FRAMES // STEP, t
    for start, name in LEFT.items():
        out.append((start, midi(name), 1, C.GREEN))
    return out


def white_index(m):
    return sum(1 for k in range(LOWEST, m) if k % 12 in WHITE_CLASSES)


def key_span(m):
    """(x, width, is_black) for a key."""
    x = X0 + PITCH * white_index(m)
    if m % 12 in WHITE_CLASSES:
        return x, PITCH - 1, False
    return x - 2, 3, True


def build():
    song = notes()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        held = {}
        # Draw this loop's notes and the next loop's, so bars fall in seamlessly.
        for start, m, length, colour in song:
            for shift in (0, FRAMES, -FRAMES):
                s = start * STEP + shift
                d = length * STEP
                x, width, _ = key_span(m)
                if s <= index < s + d:
                    held[m] = colour
                # Rows above the keys: the bar's bottom reaches the keys at s.
                bottom = KEYS_TOP - 1 - (s - index)
                top = bottom - d + 2          # a one-row gap between notes
                for y in range(max(0, top), min(KEYS_TOP, bottom + 1)):
                    frame.hline(x, y, width, colour)
        # White keys, then black keys cut over them.
        for m in range(LOWEST, midi("E5") + 1):
            x, width, black = key_span(m)
            if not black:
                frame.rect(x, KEYS_TOP, width, 16 - KEYS_TOP, held.get(m, C.WHITE), fill=True)
        for m in range(LOWEST, midi("E5") + 1):
            x, width, black = key_span(m)
            if black:
                colour = held.get(m, C.BLACK)
                frame.rect(x, KEYS_TOP, width, BLACK_BOTTOM - KEYS_TOP + 1, colour, fill=True)
                if colour == C.BLACK:
                    frame.vline(x + 1, KEYS_TOP, BLACK_BOTTOM - KEYS_TOP + 1, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/piano.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
