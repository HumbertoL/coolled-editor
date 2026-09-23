#!/usr/bin/env python3
"""
Distracted Boyfriend (2017) -- the stock photo, relabelled for this panel.

A couple stands at the right. A woman in red walks in from the left, and the
boyfriend's head swings round to follow her while his body stays put. Behind
him the girlfriend's face falls, then sets: face flushing red, mouth open, a red
anger mark over her head. Then the labels land, as they always do: ME over
him, LED SIGN over the woman in red, MY JOB over the girlfriend. The 5x7 font
is too tall to stack over a figure in 16 rows, so the labels use a 3x5
mini-font with proportional letters, leaving ten rows for the people.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

MINI = {
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "G": [".##", "#..", "#.#", "#.#", ".##"],
    "I": ["#", "#", "#", "#", "#"],
    "J": ["..#", "..#", "..#", "#.#", ".#."],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    " ": ["..", "..", "..", "..", ".."],
}


def mini_width(text):
    return sum(len(MINI[ch][0]) + 1 for ch in text) - 1


def mini_text(frame, text, center_x, y, color):
    x = center_x - mini_width(text) // 2
    for ch in text:
        for r, line in enumerate(MINI[ch]):
            for c, cell in enumerate(line):
                if cell == "#":
                    frame.pixel(x + c, y + r, color)
        x += len(MINI[ch][0]) + 1


# Figures are 10 rows tall, standing on the bottom row: a 4-row head, a
# 3-row torso, 3 rows of legs. f face, k eye / mouth (cut out), r a scowling brow, h hair,
# s top, a arm, p legs.
BOY_FORWARD = ["hhhh.", "hfkf.", "hffff", ".fff."]
BOY_BACK = [".hhhh", ".fkfh", "ffffh", ".fff."]
BOY_BODY = [
    ".sssssaa",
    "assssss.",
    "a.sss...",
    "..p.p...",
    "..p.p...",
    ".pp.pp..",
]
GIRL_CALM = [".hhhh", "fkffh", "ffffh", ".fffh"]
GIRL_ANGRY = ["r.hhh", ".rffh", "kkffh", ".fffh"]
GIRL_BODY = [
    "aassssh",
    ".sssss.",
    "..sss..",
    "..p.p..",
    "..p.p..",
    ".pp.pp.",
]
WOMAN_HEAD = [".hhh.", "hffffk", "hffff", "h.ff."]
WOMAN_BODY = [
    "a.sss.a",
    ".sssss.",
    "sssssss",
]
WALK_LEGS = [["..p.p..", ".p...p.", "p.....p"], ["...p...", "...p...", "..pp..."]]
STAND_LEGS = ["..p.p..", "..p.p..", "..p.p.."]

WOMAN_X = 16               # where she stops
WOMAN_STOP = 18            # the frame she gets there
TURN_AT = 10               # his head whips round
ANGRY_AT = 18
LABELS_AT = (26, 30, 34)   # ME, LED SIGN, MY JOB
BOY_X, GIRL_X = 50, 64


def paint(frame, rows, x, y, colors):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in colors:
                frame.pixel(x + c, y + r, colors[ch])


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        # The woman in red, walking in from the left.
        walking = index < WOMAN_STOP
        wx = WOMAN_X - (WOMAN_STOP - index) if walking else WOMAN_X
        woman = {"f": C.YELLOW, "k": C.BLACK, "h": C.MAGENTA, "s": C.RED, "a": C.YELLOW, "p": C.YELLOW}
        paint(frame, WOMAN_HEAD, wx + 1, 6, woman)
        paint(frame, WOMAN_BODY, wx, 10, woman)
        paint(frame, WALK_LEGS[index // 2 % 2] if walking else STAND_LEGS, wx, 13, woman)

        # The boyfriend: body towards his girlfriend, head after the woman.
        boy = {"f": C.YELLOW, "k": C.BLACK, "h": C.WHITE, "s": C.CYAN, "a": C.YELLOW, "p": C.BLUE}
        paint(frame, BOY_BODY, BOY_X, 10, boy)
        looking_back = index >= TURN_AT
        if looking_back:
            paint(frame, BOY_BACK, BOY_X, 6, boy)
            if index < TURN_AT + 6:
                # Whoa marks as his head whips round.
                for dx, dy in ((-2, 6), (-3, 5), (-2, 9), (-4, 9)):
                    frame.pixel(BOY_X + dx, dy, C.WHITE)
        else:
            paint(frame, BOY_FORWARD, BOY_X + 1, 6, boy)

        # The girlfriend, facing him, going red.
        angry = index >= ANGRY_AT
        girl = {"f": C.RED if angry else C.YELLOW, "k": C.BLACK, "h": C.MAGENTA, "r": C.WHITE, "s": C.BLUE, "a": C.YELLOW, "p": C.CYAN}
        paint(frame, GIRL_BODY, GIRL_X - 1, 10, girl)
        paint(frame, GIRL_ANGRY if angry else GIRL_CALM, GIRL_X + 1, 6, girl)
        if angry and index % 4 < 3:
            # Anger mark, pulsing, beside her head.
            for dx, dy in ((7, 7), (8, 6), (9, 7), (8, 8)):
                frame.pixel(GIRL_X + dx, dy, C.RED)

        if index >= LABELS_AT[0]:
            mini_text(frame, "ME", BOY_X + 3, 0, C.WHITE)
        if index >= LABELS_AT[1]:
            mini_text(frame, "LED SIGN", WOMAN_X + 3, 0, C.RED)
        if index >= LABELS_AT[2]:
            mini_text(frame, "MY JOB", GIRL_X + 14, 0, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/distracted_boyfriend.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
