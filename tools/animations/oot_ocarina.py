#!/usr/bin/env python3
"""
OoT ocarina -- two songs on the five-line staff.

A blue ocarina sits at the left, puffing music notes. Across the rest of the
panel a five-line staff fills one note at a time, each landing on its line
with a little drop: yellow arrows for the C buttons and a cyan disc for A, on red dotted
lines.
First Zelda's Lullaby (left, up, right, twice), then the Song of Time (right,
A, down, twice). When a song is complete its notes flash white, and its name
replaces the staff for a moment before the next one starts.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from zelda_art import stamp  # noqa: E402

FRAMES = 53
DELAY = 120
STAFF_X = 22
LINE_Y = {"^": 1, "<": 4, ">": 7, "v": 10, "A": 13}   # note -> centre row
LINES = (1, 4, 7, 10, 13)
NOTE_GAP = 12
SONGS = [
    ("ZELDA'S LULLABY", "<^><^>"),
    ("SONG OF TIME", ">Av>Av"),
]
PER_NOTE = 3
SONG_FRAMES = 26      # 6 notes x 3, then 3 of flashing, then 5 of the title

OCARINA = [
    ".........BB.",
    "...BBBBBBBB.",
    ".BBCBBBBBB..",
    "BBBBBWBBWB..",
    "BBBBBBBBB...",
    ".BBBBBBB....",
    "..BBBB......",
]
ARROWS = {
    "^": ["..#..", ".###.", "#####"],
    "v": ["#####", ".###.", "..#.."],
    "<": ["..#", ".##", "###", ".##", "..#"],
    ">": ["#..", "##.", "###", "##.", "#.."],
}
DISC = [".###.", "##W##", "#WWW#", "##W##", ".###."]
QUAVER = ["..#", "..#", "..#", "###", "##."]


def note(frame, kind, x, cy, colour=None):
    if kind == "A":
        rows, default = DISC, C.CYAN
    else:
        rows, default = ARROWS[kind], C.YELLOW
    top = cy - len(rows) // 2
    left = x - len(rows[0]) // 2
    for r, line in enumerate(rows):
        for c, cell in enumerate(line):
            if cell == "#":
                frame.pixel(left + c, top + r, colour or default)
            elif cell == "W":
                frame.pixel(left + c, top + r, colour or C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        song = min(len(SONGS) - 1, index // SONG_FRAMES)
        local = index - song * SONG_FRAMES
        name, notes = SONGS[song]

        # The ocarina breathes notes while a song is being played.
        stamp(frame, OCARINA, 1, 6)
        playing = local < len(notes) * PER_NOTE
        if playing:
            for k in range(2):
                age = (local + k * 3) % 6
                qx, qy = 8 + age + k * 3, 4 - age // 2 + k
                for r, line in enumerate(QUAVER):
                    for c, cell in enumerate(line):
                        if cell == "#":
                            frame.pixel(qx + c, qy + r - 2, C.WHITE if k else C.CYAN)

        played = min(len(notes), local // PER_NOTE + 1)
        title_at = len(notes) * PER_NOTE + 3
        if local < title_at:
            for y in LINES:
                for x in range(STAFF_X - 2, 96, 2):
                    frame.pixel(x, y, C.RED)
            flashing = local >= len(notes) * PER_NOTE
            for k in range(played):
                kind = notes[k]
                drop = 2 - min(2, local - k * PER_NOTE) if not flashing else 0
                x = STAFF_X + 6 + k * NOTE_GAP
                colour = (C.WHITE if local % 2 else None) if flashing else None
                note(frame, kind, x, LINE_Y[kind] - drop, colour)
        else:
            frame.small_text(name, STAFF_X + (74 - frame.small_text_width(name)) // 2, 6,
                             C.WHITE if (local - title_at) % 2 == 0 else C.YELLOW)
            for k in range(3):
                frame.pixel(STAFF_X + 6 + (local * 7 + k * 23) % 66, 2 + (k * 5) % 11, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/oot_ocarina.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
