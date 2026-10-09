#!/usr/bin/env python3
"""
On mute -- the video call classic.

A video call. On the left, one big tile: a round yellow face, mouth going,
hands gesturing up and down, and a white mic with a red slash in the tile's
corner. On the right, a column of three tiny participant tiles. The big face
talks animatedly to an empty bubble of "...". The tiny tiles react one by
one in small text: YOU'RE ON MUTE, then MUTE, then ON MUTE!! in red. The
face keeps going, oblivious -- then stops. A red ! appears, its eyes drop to
the mic icon, a cursor slides in and clicks it, and the icon turns green.
The face says, in big letters, CAN YOU HEAR ME? The tiles: YES. YES. YES.
The face: SO AS I WAS SAYING -- and the whole panel cuts to a blue
RECONNECTING screen with a spinner. Button: the big tile is empty, and the
three little tiles say ... one after another.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130

FRAME_W = 28                    # the big tile spans x 0..27
HEAD_X, HEAD_Y = 12, 7          # centre of the round head
MIC_X, MIC_Y = 22, 10           # top-left of the mic icon's box
TILE_X, TILE_W, TILE_H = 88, 8, 5
TEXT_RIGHT = 86                 # small-text replies end here, beside the tiles
BIG_X = 30                      # the face's 5x7 lines start here

# Beats.
TILE1, TILE2, TILE3 = 7, 13, 18
FREEZE = 23
CURSOR_IN = 27
CLICK = 28
HEAR_ME = 30
YES = 36
SAYING = 40
RECONNECT = 45
BUTTON = 49

HEAD = [
    "...YYYY...",
    ".YYYYYYYY.",
    "YYYYYYYYYY",
    "YYYYYYYYYY",
    "YYYYYYYYYY",
    "YYYYYYYYYY",
    "YYYYYYYYYY",
    ".YYYYYYYY.",
    "...YYYY...",
]
CURSOR = [
    "W....",
    "WW...",
    "WWW..",
    "WWWW.",
    "WWWWW",
    "..W..",
]
PALETTE = {"Y": C.YELLOW, "W": C.WHITE}


def sprite(frame, art, x, y):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, PALETTE[ch])


def draw_layout(frame, big_color=C.WHITE):
    frame.rect(0, 0, FRAME_W, 16, big_color)
    for k in range(3):
        frame.rect(TILE_X, k * TILE_H, TILE_W, TILE_H, C.BLUE)


def draw_tile_faces(frame, speaking=()):
    """Tiny heads in each tile; a speaking tile's outline lights up."""
    for k in range(3):
        y = k * TILE_H
        if k in speaking:
            frame.rect(TILE_X, y, TILE_W, TILE_H, C.GREEN)
        frame.rect(TILE_X + 3, y + 1, 2, 2, C.YELLOW, fill=True)
        frame.hline(TILE_X + 2, y + 3, 4, C.CYAN)


def draw_face(frame, mouth_open, hands, eyes=(0, 0), hands_up=None):
    """The big face: eyes offset by ``eyes``; hands alternate with ``hands``."""
    sprite(frame, HEAD, HEAD_X - 5, HEAD_Y - 4)
    ex, ey = eyes
    for x in (HEAD_X - 2, HEAD_X + 2):
        frame.pixel(x + ex, HEAD_Y - 1 + ey, C.BLACK)
    if mouth_open:
        frame.rect(HEAD_X - 1, HEAD_Y + 2, 3, 2, C.RED, fill=True)
    else:
        frame.hline(HEAD_X - 1, HEAD_Y + 2, 3, C.RED)
    if hands is not None:
        lift = 3 if hands % 2 == 0 else 0
        for x in (2, 21):
            frame.rect(x, HEAD_Y + 2 - lift, 2, 2, C.YELLOW, fill=True)
            frame.rect(x, HEAD_Y + 4 - lift, 2, 1, C.CYAN, fill=True)   # cuff


def draw_mic(frame, muted):
    color = C.WHITE if muted else C.GREEN
    frame.rect(MIC_X + 1, MIC_Y, 2, 3, color, fill=True)       # capsule
    frame.pixel(MIC_X + 1, MIC_Y + 3, color)                   # stem
    frame.pixel(MIC_X + 2, MIC_Y + 3, color)
    frame.hline(MIC_X, MIC_Y + 4, 4, color)                     # base
    if muted:
        frame.line(MIC_X - 1, MIC_Y + 4, MIC_X + 4, MIC_Y - 1, C.RED)


def reply(frame, k, text, color):
    """
    Small text beside tile ``k``. Three 5-row lines cannot all have a gap
    in 16 rows, so the middle one is stepped left to keep them apart.
    """
    x = TEXT_RIGHT - Canvas.small_text_width(text) - (14 if k == 1 else 0)
    frame.small_text(text, x, (0, 6, 11)[k], color)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()

        if RECONNECT <= i < BUTTON:
            # The whole panel cuts to the reconnecting screen.
            f.fill(C.BLUE)
            f.text("RECONNECTING", 1, 4, C.WHITE)
            t = i - RECONNECT
            f.small_text("." * (t % 3 + 1), 73, 6, C.WHITE)
            # A spinner: a white arm sweeping round a dark hub.
            cx, cy = 88, 7
            arms = ((0, -3), (2, -2), (3, 0), (2, 2), (0, 3), (-2, 2), (-3, 0), (-2, -2))
            for k in range(8):
                dx, dy = arms[k]
                f.pixel(cx + dx, cy + dy, C.CYAN)
            for k in range(3):
                dx, dy = arms[(t * 2 + k) % 8]
                f.pixel(cx + dx, cy + dy, C.WHITE)
            continue

        draw_layout(f)
        if i >= BUTTON:
            # The big tile has gone dark; the little tiles exchange looks.
            f.small_text("...", 11, 6, C.BLUE)
            said = min(i - BUTTON + 1, 3)
            draw_tile_faces(f, speaking=range(said))
            for k in range(said):
                reply(f, k, "...", C.WHITE)
            continue

        muted = i < CLICK + 1
        draw_mic(f, muted)

        if i < FREEZE:
            # Talking away, oblivious. Hands flapping, mouth going.
            draw_face(f, mouth_open=i % 2 == 0, hands=i // 2)
            f.small_text("." * (i % 3 + 1), BIG_X, 6, C.WHITE)
            # The little tiles chime in one at a time.
            if i >= TILE3:
                reply(f, 2, "ON MUTE!!", C.RED)
                draw_tile_faces(f, speaking=(2,))
            elif i >= TILE2:
                reply(f, 1, "MUTE", C.CYAN)
                draw_tile_faces(f, speaking=(1,))
            elif i >= TILE1:
                reply(f, 0, "YOU'RE ON MUTE", C.CYAN)
                draw_tile_faces(f, speaking=(0,))
            else:
                draw_tile_faces(f)
        elif i < HEAR_ME:
            # Stops. A red !, eyes to the mic, then the cursor clicks it.
            draw_face(f, mouth_open=False, hands=1,
                      eyes=(0, 0) if i < FREEZE + 2 else (1, 1))
            if i < FREEZE + 2:
                f.text("!", 17, 1, C.RED)
            draw_tile_faces(f)
            if CURSOR_IN <= i <= CLICK + 1:
                sprite(f, CURSOR, MIC_X + 3 - (i - CURSOR_IN), MIC_Y - 1 + (i - CURSOR_IN))
            if i == CLICK:
                f.pixel(MIC_X - 1, MIC_Y - 1, C.WHITE)   # click sparkle
                f.pixel(MIC_X + 4, MIC_Y + 5, C.WHITE)
        elif i < YES:
            draw_face(f, mouth_open=i % 2 == 0, hands=i // 2)
            f.text("CAN YOU", BIG_X, 0, C.WHITE, proportional=True)
            f.text("HEAR ME?", BIG_X, 8, C.WHITE, proportional=True)
            draw_tile_faces(f)
        elif i < SAYING:
            draw_face(f, mouth_open=False, hands=1)
            said = min(i - YES + 1, 3)
            draw_tile_faces(f, speaking=range(said))
            for k in range(said):
                reply(f, k, "YES.", C.GREEN)
        else:
            draw_face(f, mouth_open=i % 2 == 0, hands=i // 2)
            f.text("SO AS I", BIG_X, 0, C.WHITE, proportional=True)
            f.text("WAS SAYING", BIG_X, 8, C.WHITE, proportional=True)
            draw_tile_faces(f)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/on_mute.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
