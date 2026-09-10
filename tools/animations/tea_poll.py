#!/usr/bin/env python3
"""
tea_poll -- live text-poll results rolling in.

Three answer bars -- A, B and C, in a 3x5 mini-font since the real font is too
tall to stack three rows -- fill in bursts as votes arrive, each arrival
pinging a white tick at the bar head. A red LIVE dot blinks in the corner the
whole time, and once the votes stop the winning bar takes a flashing lap of
honour. The arrival schedule is deterministic, so the file regenerates
identically.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

MINI = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"],
}

BAR_X = 7
BAR_MAX = 82  # bar can run to x = BAR_X + BAR_MAX

# (label, top row, final length, color)
BARS = [
    ("A", 0, 30, C.CYAN),
    ("B", 5, 74, C.YELLOW),
    ("C", 10, 46, C.MAGENTA),
]

VOTES_DONE = 44  # all bars at final length by here


def draw_mini(frame, char, x, y, color):
    for row, line in enumerate(MINI[char]):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, y + row, color)


def growth(bar_index, final, frame_index):
    """Length at this frame: stepped, jittered, monotone, deterministic."""
    if frame_index >= VOTES_DONE:
        return final
    votes = final // 2
    length = 0
    for v in range(votes):
        # Each vote lands on its own pseudo-random frame in [2, VOTES_DONE).
        arrival = 2 + (v * 17 + bar_index * 29 + (v * v * 7) % 13) % (VOTES_DONE - 2)
        if arrival <= frame_index:
            length += 2
    return min(length, final)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()

        # LIVE dot.
        frame.pixel(94, 1, C.RED if index % 6 < 4 else C.BLACK)

        for bar_index, (label, top, final, color) in enumerate(BARS):
            draw_mini(frame, label, 1, top, C.WHITE)
            # Track.
            frame.hline(BAR_X, top + 2, BAR_MAX, C.BLUE)
            length = growth(bar_index, final, index)
            grew = index > 0 and length > growth(bar_index, final, index - 1)

            winner = label == "B" and index > VOTES_DONE + 2
            bar_color = C.WHITE if winner and index % 4 < 2 else color
            for row in range(3):
                frame.hline(BAR_X, top + 1 + row, length, bar_color)
            if grew:
                frame.vline(BAR_X + length, top + 1, 3, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tea_poll.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
