#!/usr/bin/env python3
"""
Welcome, SGLA -- for the Small Giants Leadership Academy graduation visit.

The Academy is a nine-month programme for next-generation, purpose-driven
leaders, and it ends with a September graduation trip that visits Small
Giants member companies; Text-Em-All hosted the 2022 cohort, and the
Community's write-up of that trip was titled "Congrats, Y'All". So: three
screens, each held long enough to read from across a lobby.

  WELCOME / SGLA          the words wipe in
  CONGRATS, / Y'ALL!      the Texas version, with a mortarboard tossed up
  CLASS OF 2026           held under a slow fall of confetti

Confetti falls throughout in every colour the panel has, and the cap's
tassel swings as it rises. 53 frames at 150ms is eight seconds, which is
about how long someone walking past a sign gives it.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
SEED = 2026

SCREEN_A, SCREEN_B = 17, 35      # first frame of screens two and three
WIPE = 8

CAP = [
    "....#....",
    "..#####..",
    "#########",
    "..#####..",
    "..#...#..",
]
CONFETTI = [C.YELLOW, C.CYAN, C.MAGENTA, C.GREEN, C.WHITE, C.RED]


def wipe_color(lit, edge, leading=C.WHITE):
    def color_at(x, _y):
        if x >= edge:
            return C.BLACK
        return leading if x >= edge - 2 else lit
    return color_at


def two_lines(frame, top, bottom, step, top_color, bottom_color):
    """Both lines wipe in left to right over WIPE frames; step >= WIPE is settled."""
    if step >= WIPE:
        frame.text(top, "center", 0, top_color, proportional=True)
        frame.text(bottom, "center", 9, bottom_color, proportional=True)
        return
    for text, y, color in ((top, 0, top_color), (bottom, 9, bottom_color)):
        width = frame.text_width(text, proportional=True)
        x = (frame.width - width) // 2
        edge = x + (width + 3) * (step + 1) / WIPE
        frame.text(text, x, y, wipe_color(color, edge), proportional=True)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    # Confetti: (x, start frame, speed, colour), drifting one way or the other.
    flakes = [(rng.randrange(96), rng.randrange(-16, FRAMES), rng.choice((1, 1, 2)),
               rng.choice(CONFETTI), rng.choice((-1, 0, 0, 1))) for _ in range(70)]

    for index in range(FRAMES):
        frame = anim.frame()

        for x, born, speed, color, drift in flakes:
            age = index - born
            if age < 0:
                continue
            y = age * speed - 1
            if 0 <= y < anim.height:
                frame.pixel((x + drift * (age // 3)) % anim.width, y, color)

        if index < SCREEN_A:
            two_lines(frame, "WELCOME", "SGLA", index, C.CYAN, C.WHITE)
        elif index < SCREEN_B:
            step = index - SCREEN_A
            two_lines(frame, "CONGRATS,", "Y'ALL!", step, C.YELLOW, C.WHITE)
            # A cap tossed from the right edge: up fast, slowing, then down.
            rise = [12, 8, 5, 3, 1, 0, 0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            top = rise[min(step, len(rise) - 1)]
            cap_x = 84
            for r, line in enumerate(CAP):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(cap_x + c, top + r, C.YELLOW if r == 3 else C.WHITE)
            tassel = 1 if (step // 2) % 2 else -1
            frame.pixel(cap_x + 8 + (1 if tassel > 0 else 0), top + 3, C.YELLOW)
            frame.pixel(cap_x + 9, top + 4 + (0 if tassel > 0 else -1), C.YELLOW)
        else:
            step = index - SCREEN_B
            two_lines(frame, "CLASS OF", "2026", step, C.WHITE, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sgla_welcome.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
