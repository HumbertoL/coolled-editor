#!/usr/bin/env python3
"""
The letters dance -- the sign has a secret life.

HAVE A NICE DAY, in plain white. The most boring sign in the building. Then
the C twitches. The Y glances over its shoulder. A few more fidget, and then
they all hop off the baseline: a travelling wave, a conga line that snakes
off the right edge and back in from the left, each letter spinning (a
squash-to-one-column, mirror, unsquash cycle) through the rainbow. Then
everyone scrambles home and freezes, perfectly still, perfectly white...
except the A, which landed upside down.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.font import glyph  # noqa: E402

FRAMES = 53
DELAY = 110
MESSAGE = "HAVE A NICE DAY"
HOME_X = 3  # 15 fixed-width cells = 89px, centred
HOME_Y = 4
RAINBOW = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA, C.WHITE]

# Spin cycle: (drawn width, mirrored).
SPIN = [(5, False), (3, False), (1, False), (3, True), (5, True), (3, True), (1, True), (3, False)]

TWITCH_START = 8
WAVE_START = 17
CONGA_START = 27
SCRAMBLE_START = 39
FREEZE = 45
CONGA_SPEED = 5
WRAP = 110  # conga track length: off the right edge, back in from the left


def letters():
    out = []
    for index, ch in enumerate(MESSAGE):
        if ch != " ":
            out.append((ch, HOME_X + index * 6))
    return out


def draw_letter(canvas, ch, x, y, color, width=5, mirror=False, flip=False):
    """Draw a glyph whose 5-wide cell starts at x, squashed to ``width`` about its centre."""
    bitmap = glyph(ch)
    if flip:
        bitmap = bitmap[::-1]
    left = x + (5 - width) // 2
    for col in range(width):
        src = 2 if width == 1 else round(col * 4 / (width - 1))
        if mirror:
            src = 4 - src
        for row in range(7):
            if bitmap[row][src] == "#":
                canvas.pixel(left + col, y + row, color)


def wave_y(x, t, amplitude):
    return HOME_Y + round(amplitude * math.sin(0.33 * x - 0.9 * t))


def conga_x(home, t):
    x = home + CONGA_SPEED * (t - CONGA_START)
    return ((x + 12) % WRAP) - 12


def dancing_pose(i, home, t):
    """Where letter i is at frame t while the dance is on (t < SCRAMBLE_START)."""
    color = RAINBOW[(i + t) % len(RAINBOW)] if t >= WAVE_START + 2 else C.WHITE
    if t < CONGA_START:
        amp = min(4.0, 1.4 * (t - WAVE_START + 1))
        return home, wave_y(home, t - WAVE_START, amp), color, 5, False
    x = conga_x(home, t)
    # Each letter pirouettes once on its way round, a couple at a time, so
    # most of the line stays readable.
    phase = t - CONGA_START - (i * 3) % 8
    width, mirror = SPIN[phase] if 0 <= phase < len(SPIN) else (5, False)
    return x, wave_y(x, t - WAVE_START, 4.0), color, width, mirror


def ease(u):
    return u * u * (3 - 2 * u)


def build():
    anim = Animation(delay=DELAY)
    cast = letters()
    names = [ch for ch, _ in cast]
    c_idx = names.index("C")
    y_idx = names.index("Y")
    a_idx = names.index("A", 3)  # the lone A, not the one in HAVE
    for t in range(FRAMES):
        frame = anim.frame()
        for i, (ch, home) in enumerate(cast):
            x, y, color, width, mirror, flip = home, HOME_Y, C.WHITE, 5, False, False
            if TWITCH_START <= t < WAVE_START:
                # Fidgeting, escalating: one letter, then another, then several.
                if t == 8 and i == c_idx:
                    y -= 1
                elif t in (11, 12) and i == y_idx:
                    mirror = True
                elif t == 14 and i in (0, 11):
                    y -= 1
                elif t == 15 and i in (1, 2, 6):
                    y -= 1
                elif t == 16 and i % 2 == 0:
                    y -= 1
            elif WAVE_START <= t < SCRAMBLE_START:
                x, y, color, width, mirror = dancing_pose(i, home, t)
            elif SCRAMBLE_START <= t < FREEZE:
                # Scramble home from wherever the conga left them, spinning.
                sx, sy, _, _, _ = dancing_pose(i, home, SCRAMBLE_START - 1)
                u = ease((t - SCRAMBLE_START + 1) / (FREEZE - SCRAMBLE_START))
                x = round(sx + (home - sx) * u)
                hop = round(3 * math.sin(math.pi * u)) * (1 if i % 2 else -1)
                y = max(0, min(9, round(sy + (HOME_Y - sy) * u) + hop))
                width, mirror = SPIN[(t + i) % len(SPIN)] if i % 3 == 0 else (5, False)
                color = C.WHITE if t >= FREEZE - 2 else RAINBOW[(i + t) % len(RAINBOW)]
                if t == FREEZE - 1:
                    width, mirror = 5, False
                    flip = i == a_idx
            elif t >= FREEZE:
                flip = i == a_idx  # nobody noticed
            draw_letter(frame, ch, x, y, color, width, mirror, flip)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/letters_dance.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
