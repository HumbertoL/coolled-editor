#!/usr/bin/env python3
"""
99 -- GTA 6's launch Metascore, which tied Ocarina of Time's 1998 record.

A score box counts up from 0, turning red, then yellow, then green as it
passes the review-site thresholds (50 and 75), and lands on 99 in a white
flash. Beside it: METASCORE / 158 CRITICS, then TIES OCARINA / OF TIME 1998
with a little blue ocarina puffing notes, then 100% OF CRITICS / RECOMMEND.
A shine sweeps the box every so often.
"""

from __future__ import annotations

from gta6_art import save, stamp
from jtkit import Animation, colors as C

FRAMES = 53
DELAY = 110
BOX_W = 21
COUNT = 20
OCARINA = [
    "..bbbbb..",
    ".bbcbbbbb",
    "bbbbbbbb.",
    ".bbbbbb..",
]


def score_at(i):
    t = min(1.0, i / COUNT)
    return round(99 * (1 - (1 - t) ** 3))


def box_colour(score):
    if score >= 75:
        return C.GREEN
    if score >= 50:
        return C.YELLOW
    return C.RED


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        score = score_at(i)
        flash = COUNT <= i < COUNT + 2
        fill = C.WHITE if flash else box_colour(score)
        f.rect(1, 0, BOX_W, 16, fill, fill=True)
        text = str(score)
        f.text(text, 1 + (BOX_W - f.text_width(text)) // 2 + 1, 4, C.BLACK)
        # A shine crossing the box after it lands.
        if i > COUNT + 2:
            head = (i - COUNT - 3) * 3 % 48 - 8
            for y in range(16):
                x = head + y // 2
                for dx in (0, 1):
                    if 1 <= x + dx <= BOX_W and f.get(x + dx, y) == C.GREEN:
                        f.pixel(x + dx, y, C.WHITE)

        if i < 24:
            f.small_text("METASCORE", 27, 2, C.WHITE)
            f.small_text("158 CRITICS", 27, 9, C.CYAN)
        elif i < 40:
            f.small_text("TIES OCARINA", 27, 2, C.YELLOW)
            f.small_text("OF TIME 1998", 27, 9, C.WHITE)
            stamp(f, OCARINA, 84, 9)
            note = (i - 24) % 6
            nx, ny = 88 + note // 2, 7 - note
            if ny >= 0:
                f.pixel(nx, ny, C.YELLOW)
                f.pixel(nx + 1, ny, C.YELLOW)
                f.vline(nx + 2, ny - 2, 3, C.YELLOW)
        else:
            f.small_text("100% OF CRITICS", 27, 2, C.WHITE)
            f.small_text("RECOMMEND", 27, 9, C.GREEN if i % 4 < 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    save(build(), "gta6_metascore")
