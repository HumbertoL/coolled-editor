#!/usr/bin/env python3
"""
Costume contest -- the laziest costume wins.

COSTUME / CONTEST flashes up in magenta and yellow. Then a stage: a magenta
floor, a blue spotlight cone with a yellow pool of light, and on the right a
judges' table with three yellow heads behind it. An entrant shuffles into
the spotlight in the laziest costume there is: a lumpy white bedsheet with
two black eye holes and a pair of red sneakers poking out the bottom.

The judges are not impressed. Three white scorecards flip up one by one --
red 4, 3, 5 -- and a red BOO drifts up from the crowd. A beat. Then the
sheet lifts off on its own, rising up and away... and underneath is a real
ghost: blue and translucent, cyan edges, a wispy tail. It floats up out of
the sneakers, which stay behind on the stage, empty. The ghost says BOO!
(properly, in white) and the cards flip, one by one, to green 10 10 10.
The cards clatter onto the table and the judges flee off the right edge,
leaving the ghost bobbing next to the empty sneakers while WINNER flashes
through the colours with sparkles around it.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
W, H = 96, 16

SPOT_X = 30            # centre of the spotlight / entrant
FLOOR_Y = 15
CARD_XS = (67, 77, 87)  # left edge of each 9-wide scorecard
JUDGE_XS = (70, 80, 90)  # left edge of each 3-wide judge head
LOW_SCORES = ("4", "3", "5")

# 11x11 bedsheet; 'o' = eye hole (black), '#' = sheet.
SHEET = [
    "....###....",
    "..#######..",
    ".#########.",
    ".##o###o##.",
    ".##o###o##.",
    "##########.",
    "###########",
    ".##########",
    "###########",
    "###########",
    "#.##.###.##",
]
SHEET_W = len(SHEET[0])

# 11x11 real ghost: '#' body (blue, cyan-dithered), 'e' edge (cyan),
# 'o' eyes/mouth (black), tail rows sway.
GHOST = [
    "...eeeee...",
    ".ee#####ee.",
    "e#########e",
    "e##oo#oo##e",
    "e##oo#oo##e",
    "e#########e",
    "e###ooo###e",
    "e#########e",
    ".e#######e.",
    "..e#####e..",
]
GHOST_TAILS = [
    ["....e#e...."],
    ["...e#e....."],
    ["....e#e...."],
    [".....e#e..."],
]
GHOST_W = 11

# Beat sheet: (name, frames).
SCRIPT = [
    ("title", 5),
    ("shuffle", 6),
    ("pose", 2),
    ("score", 3),      # 4, 3, 5 flip up one per frame
    ("boo", 4),
    ("tug", 2),
    ("lift", 4),       # sheet rises off, ghost revealed
    ("rise", 3),       # ghost floats out of the sneakers
    ("ghostboo", 4),   # BOO! and the cards flip to 10
    ("tens", 4),
    ("flee", 5),
    ("winner", 11),
]


def stage(c):
    """Spotlight cone, pool of light, floor."""
    for y in range(0, FLOOR_Y):
        half = 2 + y * 12 // 15
        for x in range(SPOT_X - half, SPOT_X + half + 1):
            if (x + 2 * y) % 4 == 0:
                c.pixel(x, y, C.BLUE)
    c.hline(0, FLOOR_Y, 64, C.MAGENTA)
    c.hline(SPOT_X - 12, FLOOR_Y, 25, C.YELLOW)


def table(c, judges=(True, True, True), offsets=(0, 0, 0)):
    for i, jx in enumerate(JUDGE_XS):
        if judges[i]:
            x = jx + offsets[i]
            c.rect(x, 9, 3, 3, C.YELLOW, fill=True)
            c.pixel(x, 9, C.BLACK)
            c.pixel(x + 2, 9, C.BLACK)
    c.hline(65, 12, 31, C.CYAN)
    c.rect(65, 13, 31, 3, C.BLUE, fill=True)


def card(c, i, text=None, color=C.RED, edge=False, y=1):
    """A scorecard on a stick. edge=True is mid-flip (seen side-on)."""
    x = CARD_XS[i]
    stick_x = x + 4
    if y + 7 < 12:
        c.vline(stick_x, y + 7, 12 - (y + 7), C.WHITE)
    if edge:
        c.vline(stick_x, y, 7, C.WHITE)
        return
    c.rect(x, y, 9, 7, C.WHITE, fill=True)
    if text:
        tx = x + (9 - Canvas.small_text_width(text)) // 2
        c.small_text(text, tx, y + 1, color)


def fallen_card(c, i, drop):
    """Card tipping onto the table: shrinks to a slab as it falls."""
    x = CARD_XS[i]
    y = 1 + drop
    if y >= 10:
        c.hline(x, 11, 9, C.WHITE)
        return
    hgt = max(1, 7 - drop)
    c.rect(x, y, 9, hgt, C.WHITE, fill=True)


def sneakers(c, x):
    for y in (13, 14):
        c.pixel(x + 2, y, C.BLACK)
        c.pixel(x + 5, y, C.BLACK)
        c.pixel(x + 9, y, C.BLACK)
    c.hline(x + 3, 13, 2, C.RED)
    c.hline(x + 6, 13, 2, C.RED)
    c.hline(x + 2, 14, 3, C.RED)
    c.hline(x + 6, 14, 3, C.RED)
    c.pixel(x + 4, 14, C.WHITE)   # toe caps
    c.pixel(x + 8, 14, C.WHITE)


def draw_sheet(c, x, y, f, droop=0, tug=False):
    for r, line in enumerate(SHEET):
        # lumpy: the hem wobbles as it walks
        dx = 0
        if r >= 8 and f % 2:
            dx = 1 if r == 9 else 0
        for k, ch in enumerate(line):
            if ch == "#":
                c.pixel(x + k + dx, y + r + droop, C.WHITE)
            elif ch == "o":
                c.pixel(x + k + dx, y + r + droop, C.BLACK)
    if tug:
        # the hem hitches up at the corners
        c.pixel(x, y + 10 + droop, C.BLACK)
        c.pixel(x + SHEET_W - 1, y + 10 + droop, C.BLACK)


def draw_ghost(c, x, y, f, clip_top=None):
    rows = GHOST + GHOST_TAILS[f % 4]
    # a black halo so the cone's dither doesn't eat the outline
    for r, line in enumerate(rows):
        for k, ch in enumerate(line):
            if ch != "." and (clip_top is None or y + r >= clip_top):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        c.pixel(x + k + dx, y + r + dy, C.BLACK)
    for r, line in enumerate(rows):
        yy = y + r
        if clip_top is not None and yy < clip_top:
            continue
        for k, ch in enumerate(line):
            xx = x + k
            if ch == "e":
                c.pixel(xx, yy, C.CYAN)
            elif ch == "#":
                c.pixel(xx, yy, C.CYAN if r >= 7 and (xx + yy + f) % 2 == 0 else C.BLUE)
            elif ch == "o":
                c.pixel(xx, yy, C.BLACK)


def sparkle(c, f):
    spots = [(58, 1), (94, 2), (60, 13), (93, 13), (76, 0), (76, 15), (66, 1), (86, 14)]
    for i, (x, y) in enumerate(spots):
        if (i + f) % 3 == 0:
            c.pixel(x, y, C.WHITE)
            c.pixel(x - 1, y, C.YELLOW)
            c.pixel(x + 1, y, C.YELLOW)
            c.pixel(x, y - 1, C.YELLOW)
            c.pixel(x, y + 1, C.YELLOW)


def main():
    beats = []
    for name, count in SCRIPT:
        beats.extend((name, k) for k in range(count))
    assert len(beats) == FRAMES, len(beats)

    sheet_x = SPOT_X - SHEET_W // 2
    ghost_x = SPOT_X - GHOST_W // 2
    flash = [C.YELLOW, C.MAGENTA, C.CYAN, C.GREEN, C.WHITE, C.RED]

    anim = Animation(delay=DELAY)
    for f, (beat, k) in enumerate(beats):
        c = anim.frame()

        if beat == "title":
            c.text("COSTUME", "center", 0, C.MAGENTA if k % 2 == 0 else C.YELLOW)
            c.text("CONTEST", "center", 8, C.YELLOW if k % 2 == 0 else C.MAGENTA)
            for i, (x, y) in enumerate([(8, 3), (86, 11), (14, 12), (80, 2), (3, 8), (92, 6)]):
                if (i + k) % 2 == 0:
                    c.pixel(x, y, C.WHITE)
            continue

        stage(c)

        if beat == "shuffle":
            # shuffle in from the left: 2 px a step, feet alternate
            sx = -SHEET_W + 2 + (k + 1) * (sheet_x + SHEET_W - 2) // 6
            draw_sheet(c, sx, 2, k)
            sneakers(c, sx + (k % 2))
            table(c)
        elif beat in ("pose", "score", "boo", "tug"):
            droop = 1 if beat == "boo" and k >= 1 else 0
            draw_sheet(c, sheet_x, 2, f if beat == "pose" else 0,
                       droop=droop, tug=beat == "tug")
            sneakers(c, sheet_x)
            table(c)
            if beat == "score":
                for i in range(3):
                    if i < k:
                        card(c, i, LOW_SCORES[i])
                    elif i == k:
                        card(c, i, edge=True)
            elif beat in ("boo", "tug"):
                for i in range(3):
                    card(c, i, LOW_SCORES[i])
            if beat == "boo":
                c.small_text("BOO", 2, 9 - k, C.RED)
                if k >= 2:
                    c.small_text("BOO", 46, 11 - (k - 2), C.RED)
        elif beat == "lift":
            # the sheet rises by itself; the ghost is under it
            sy = 2 - (k + 1) * 4
            draw_ghost(c, ghost_x, 2, f)
            sneakers(c, sheet_x)
            draw_sheet(c, sheet_x - k * 2, sy, 0)
            table(c)
            for i in range(3):
                card(c, i, LOW_SCORES[i])
        elif beat == "rise":
            draw_ghost(c, ghost_x, 1 - k // 2, f)
            sneakers(c, sheet_x)
            table(c)
            for i in range(3):
                card(c, i, LOW_SCORES[i])
        elif beat in ("ghostboo", "tens"):
            draw_ghost(c, ghost_x, 0, f)
            sneakers(c, sheet_x)
            table(c)
            if beat == "ghostboo":
                c.text("BOO!", 39 + (k % 2), 1, C.WHITE)
                for i in range(3):
                    if i < k - 1:
                        card(c, i, "10", C.GREEN)
                    elif i == k - 1:
                        card(c, i, edge=True)
                    else:
                        card(c, i, LOW_SCORES[i])
            else:
                c.text("BOO!", 39, 1, C.WHITE if k < 2 else C.CYAN)
                for i in range(3):
                    card(c, i, "10", C.GREEN)
        elif beat == "flee":
            draw_ghost(c, ghost_x, 0 + (k % 2), f)
            sneakers(c, sheet_x)
            offsets = tuple(min(40, (k + 1) * 5 + i * 2) for i in range(3))
            table(c, offsets=offsets)
            for i in range(3):
                fallen_card(c, i, (k + 1) * 3)
            if k < 3:
                c.text("!", 64 + offsets[0], 1, C.RED)
        elif beat == "winner":
            draw_ghost(c, ghost_x, [0, 1, 1, 0][k % 4], f)
            sneakers(c, sheet_x)
            # clear the right side for the title
            c.rect(56, 0, 40, 15, C.BLACK, fill=True)
            c.hline(64, FLOOR_Y, 32, C.BLACK)
            c.text("WINNER", 58, 4, flash[k % len(flash)])
            sparkle(c, k)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/costume_contest.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
