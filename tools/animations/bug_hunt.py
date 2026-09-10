#!/usr/bin/env python3
"""
bug_hunt -- acceptance testing, dramatised.

Rows of code scroll nowhere; a magnifying glass sweeps them line by line while
a red bug scuttles along the middle row. The lens catches up, locks on, the
bug flashes and gets squashed flat -- and the verdict comes up green: a check
and PASS. For the acceptance-test suite maintainers.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

CODE_ROWS = (1, 4, 7, 10, 13)
BUG_ROW = 7

CATCH = 28    # lens reaches the bug
SQUASH = 35   # bug squashed
VERDICT = 39  # check + PASS

CODE_COLORS = [C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]


def code_segments(row):
    """Deterministic dashes of 'code' for one row: (x, length, color)."""
    segments = []
    x = 2 + (row * 5) % 7
    i = 0
    while x < 92:
        length = 4 + (x * 3 + row * 11) % 9
        color = CODE_COLORS[(x + row + i) % len(CODE_COLORS)]
        segments.append((x, min(length, 92 - x), color))
        x += length + 3
        i += 1
    return segments


def bug_position(index):
    """The bug scuttles left along its row, pausing now and then."""
    x = 74.0
    for step in range(min(index, CATCH)):
        if step % 9 < 6:
            x -= 1.3
    return round(x), BUG_ROW


def draw_bug(frame, x, y, index, flashing):
    body = C.YELLOW if flashing and index % 2 else C.RED
    frame.rect(x - 1, y, 3, 2, body, fill=True)
    # Legs alternate as it scuttles.
    for side in (-2, 2):
        frame.pixel(x + side, y + (index % 2), body)


def draw_lens(frame, cx, cy):
    for i in range(20):
        a = 2 * math.pi * i / 20
        frame.pixel(round(cx + 3.5 * math.cos(a)), round(cy + 3.5 * math.sin(a)), C.WHITE)
    frame.line(cx + 3, cy + 3, cx + 6, cy + 6, C.WHITE)


def lens_path(index):
    """Serpentine sweep down the rows, then a straight run at the bug."""
    if index < 10:
        return 10 + index * 8, 3
    if index < 14:
        return 90 - (index - 10) * 4, 5
    x, _row = bug_position(index)
    start_x = 74
    progress = min(1.0, (index - 14) / (CATCH - 14))
    return round(90 + (x - 90) * progress), 7


def build():
    anim = Animation(delay=DELAY)
    bug_final_x, _ = bug_position(CATCH)

    for index in range(FRAMES):
        frame = anim.frame()

        # The code under review.
        for row in CODE_ROWS:
            for x, length, color in code_segments(row):
                if index >= VERDICT and row == BUG_ROW:
                    color = C.GREEN  # the fixed line
                frame.hline(x, row, length, color)

        if index < SQUASH:
            bx, by = bug_position(index)
            draw_bug(frame, bx, by, index, flashing=index >= CATCH)
        elif index < VERDICT:
            # Squashed: a flat red splat.
            frame.hline(bug_final_x - 2, BUG_ROW + 1, 5, C.RED)
            frame.pixel(bug_final_x - 3, BUG_ROW, C.RED)
            frame.pixel(bug_final_x + 3, BUG_ROW, C.RED)

        if index < SQUASH:
            lx, ly = lens_path(index)
            draw_lens(frame, lx, ly)

        if index >= VERDICT:
            # Punch a dark window in the code so the verdict reads.
            frame.rect(34, 1, 46, 13, C.BLACK, fill=True)
            pulse = (index - VERDICT) % 6 < 4
            check_color = C.GREEN if pulse else C.WHITE
            frame.line(38, 9, 41, 12, check_color)
            frame.line(41, 12, 46, 4, check_color)
            frame.text("PASS", 52, 5, C.GREEN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bug_hunt.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
