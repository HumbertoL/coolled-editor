#!/usr/bin/env python3
"""
Wordle (2022) -- five letters, six tries, one grid of little squares.

Sixteen rows cannot hold six rows of lettered tiles, so the panel splits the
game in two. On the left, the current guess, five big tiles: letters type in
and each tile flips in turn -- squash, swap colour, spring back -- to grey,
yellow or green. On the right, the spoiler-free share grid builds a row at a
time as each guess resolves. STORM, CRANE, NAVEL, PANEL: every colour follows
the real rules for the answer PANEL, and each guess uses what the last one
taught. The winning row hops in a wave, and the toast says what Wordle says
for a four: SPLENDID.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
ANSWER = "PANEL"
GUESSES = ["STORM", "CRANE", "NAVEL", "PANEL"]
GREY, YELLOW, GREEN = C.BLUE, C.YELLOW, C.GREEN

TILE_W, TILE_H, TILE_PITCH, TILE_X, TILE_Y = 11, 13, 12, 1, 2
GRID_X, GRID_Y, CELL, CELL_PITCH = 68, 1, 3, 4
PER_GUESS = 11
TYPE_FRAMES = 4
WIN_AT = PER_GUESS * len(GUESSES)       # 44
TOAST_AT = WIN_AT + 4


def score(guess, answer):
    """Wordle's colouring, duplicates included: greens first, then yellows
    from whatever letters the greens left unclaimed."""
    result = [GREY] * 5
    spare = []
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = GREEN
        else:
            spare.append(a)
    for i, g in enumerate(guess):
        if result[i] != GREEN and g in spare:
            result[i] = YELLOW
            spare.remove(g)
    return result


def draw_tile(frame, i, letter, fill, height, hop=0):
    x = TILE_X + i * TILE_PITCH
    top = TILE_Y - hop + (TILE_H - height) // 2
    if fill is None:
        frame.rect(x, top, TILE_W, height, C.WHITE if letter else C.BLUE)
    else:
        frame.rect(x, top, TILE_W, height, fill, fill=True)
    if letter and height == TILE_H:
        ink = C.WHITE if fill in (None, GREY) else C.BLACK
        frame.text(letter, x + 3, TILE_Y - hop + 3, ink)


def build():
    rows = [score(g, ANSWER) for g in GUESSES]
    assert rows[-1] == [GREEN] * 5
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        g = min(index // PER_GUESS, len(GUESSES) - 1)
        s = g * PER_GUESS
        guess, colours = GUESSES[g], rows[g]

        typed = min(5, round((index - s + 1) * 1.25))
        for i in range(5):
            k = index - (s + TYPE_FRAMES + i)       # this tile's flip phase
            letter = guess[i] if i < typed else ""
            hop = 0
            if index >= WIN_AT:
                w = index - WIN_AT - i // 2
                hop = 2 if w in (0, 1) else 0
            if k < 0:
                draw_tile(frame, i, letter, None, TILE_H)
            elif k == 0:
                draw_tile(frame, i, letter, None, 5)
            elif k == 1:
                draw_tile(frame, i, letter, colours[i], 5)
            else:
                draw_tile(frame, i, letter, colours[i], TILE_H, hop)

        # The share grid: a row per resolved guess, outlines for the rest.
        for row in range(len(GUESSES)):
            done = index >= row * PER_GUESS + PER_GUESS - 1
            for col in range(5):
                x = GRID_X + col * CELL_PITCH
                y = GRID_Y + row * CELL_PITCH
                if done:
                    frame.rect(x, y, CELL, CELL, rows[row][col], fill=True)
                else:
                    frame.pixel(x + 1, y + 1, C.BLUE)

        if index >= TOAST_AT:
            text = "SPLENDID"
            width = frame.text_width(text, proportional=True)
            x = TILE_X + (5 * TILE_PITCH - 1 - width) // 2
            frame.rect(x - 3, 3, width + 6, 11, C.WHITE, fill=True)
            frame.text(text, x, 5, C.BLACK, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/wordle.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
