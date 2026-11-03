#!/usr/bin/env python3
"""
Vote ballot box -- mark it, fold it, drop it in. Election Day, nonpartisan.

On the left a hand in a cyan sleeve holds up a white paper ballot: two
choices, each a blue box with blue name lines beside it. Next to it stands
a ballot box -- blue body, white outline, VOTE on its front in the small
font, and a white lid with a black slot. On the right GO VOTE! types itself
out in white, with TODAY in yellow underneath.

A yellow pencil with a magenta eraser swoops in and ticks a black check
mark into the first box, stroke by stroke, then leaves. The ballot folds
in half, then in half again, and the hand carries the little folded square
up and over the box and lets go: it sinks through the slot and is gone.

The box gives a thunk -- the lid flashes yellow -- a green check pops up
above it, then a magenta heart floats up among yellow and white sparkles.
The text wipes over to YOUR VOTE / COUNTS! and holds, twinkling, before the
loop starts again with a fresh blank ballot.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, wipe  # noqa: E402

DELAY = 130
W, H = 96, 16

# Ballot paper, unfolded: x 4..15, y 1..14.
PAPER_X, PAPER_Y, PAPER_W, PAPER_H = 4, 1, 12, 14
BOX1 = (6, 3)                      # top-left of the first 4x4 choice box
BOX2 = (6, 9)
# The check mark, stroke order: down into the box, then the long up-stroke.
CHECK = [(6, 4), (7, 5), (8, 6), (9, 5), (10, 4), (11, 3), (12, 2), (13, 1)]

# Ballot box: lid row at y 7, body below.
BOX_X, BOX_W = 25, 19
LID_Y = 7
SLOT_X0, SLOT_X1 = 29, 39

# Right-hand text panel.
TEXT_X = 48
GO = "GO VOTE!"
TODAY = "TODAY"
YOUR = "YOUR VOTE"
COUNTS = "COUNTS!"
GO_X = TEXT_X + (W - TEXT_X - Canvas.text_width(GO)) // 2
TODAY_X = TEXT_X + (W - TEXT_X - Canvas.small_text_width(TODAY)) // 2
YOUR_X = TEXT_X + (W - TEXT_X - Canvas.small_text_width(YOUR)) // 2
COUNTS_X = TEXT_X + (W - TEXT_X - Canvas.text_width(COUNTS)) // 2

# Beat sheet: (name, frames).
SCRIPT = [
    ("intro", 6),
    ("pencil_in", 2),
    ("tick", 5),
    ("pencil_out", 2),
    ("admire", 2),
    ("fold", 3),
    ("carry", 5),
    ("drop", 4),
    ("thunk", 2),
    ("cheer", 6),
    ("counts", 14),
]


def ballot_box(c, flash=False):
    body_top = LID_Y + 1
    c.rect(BOX_X, body_top, BOX_W, H - body_top, C.BLUE, fill=True)
    c.vline(BOX_X, body_top, H - body_top, C.WHITE)
    c.vline(BOX_X + BOX_W - 1, body_top, H - body_top, C.WHITE)
    lid = C.YELLOW if flash else C.WHITE
    c.hline(BOX_X - 1, LID_Y, BOX_W + 2, lid)
    c.hline(SLOT_X0, LID_Y, SLOT_X1 - SLOT_X0 + 1, C.BLACK)
    vx = BOX_X + (BOX_W - Canvas.small_text_width("VOTE")) // 2
    c.small_text("VOTE", vx, 9, C.YELLOW if flash else C.WHITE)


def hand(c, x, y):
    """A yellow fist whose right edge is at x, gripping rows y..y+3, with a
    cyan sleeve running back to the left edge of the panel."""
    if x - 3 > 0:
        c.rect(0, y + 1, x - 3, 2, C.CYAN, fill=True)
    c.rect(x - 3, y, 3, 4, C.YELLOW, fill=True)
    c.pixel(x, y + 1, C.YELLOW)     # thumb over the paper's edge


def ballot_open(c, marks=0):
    c.rect(PAPER_X, PAPER_Y, PAPER_W, PAPER_H, C.WHITE, fill=True)
    for bx, by in (BOX1, BOX2):
        c.rect(bx, by, 4, 4, C.BLUE)
        c.hline(bx + 6, by + 1, 4, C.BLUE)
        c.hline(bx + 6, by + 3, 3, C.BLUE)
    for x, y in CHECK[:marks]:
        c.pixel(x, y, C.BLACK)


def pencil(c, tx, ty):
    """Tip at (tx, ty), body running up and to the right, 2 px thick."""
    c.pixel(tx, ty, C.BLACK if c.get(tx, ty) == C.WHITE else C.WHITE)
    for i in range(1, 7):
        color = C.MAGENTA if i >= 6 else C.YELLOW
        c.pixel(tx + i, ty - i, color)
        c.pixel(tx + i + 1, ty - i + 1, color)


def folded(c, x, y, w, h):
    c.rect(x, y, w, h, C.WHITE, fill=True)
    c.hline(x + 1, y + h // 2, w - 2, C.CYAN)   # the crease


def sparkle(c, x, y, color, big=False):
    c.pixel(x, y, color)
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c.pixel(x + dx, y + dy, color)


def go_text(c, f, start):
    shown = max(0, min(len(GO), (f - start + 1) * 2))
    c.text(GO[:shown], GO_X, 0, C.WHITE)
    if shown == len(GO):
        c.small_text(TODAY, TODAY_X, 10, C.YELLOW)


def counts_text(c, k):
    edge = TEXT_X + k * 12
    c.small_text(YOUR, YOUR_X, 1, wipe(C.WHITE, C.BLACK, edge))
    c.text(COUNTS, COUNTS_X, 8, wipe(C.YELLOW, C.BLACK, edge - 6))
    if k >= 5:
        stars = [(49, 1), (92, 2), (48, 12), (94, 12)]
        x, y = stars[k % 4]
        sparkle(c, x, y, C.WHITE if k % 2 else C.CYAN)


def main():
    beats = []
    for name, count in SCRIPT:
        beats.extend((name, k) for k in range(count))
    frames = len(beats)
    assert frames <= 53, frames
    assert GO_X + Canvas.text_width(GO) <= W
    assert COUNTS_X + Canvas.text_width(COUNTS) <= W
    assert YOUR_X >= TEXT_X - 1

    anim = Animation(delay=DELAY)
    hand_y = 10

    for f, (beat, k) in enumerate(beats):
        c = anim.frame()
        under_box = None        # a ballot sinking through the slot
        box_flash = False
        text = "go"

        if beat == "intro":
            # the ballot rises into view from below
            dy = max(0, 6 - 2 * k)
            c.rect(PAPER_X, PAPER_Y + dy, PAPER_W, PAPER_H, C.WHITE, fill=True)
            if dy == 0:
                ballot_open(c)
            else:
                for bx, by in (BOX1, BOX2):
                    c.rect(bx, by + dy, 4, 4, C.BLUE)
                    c.hline(bx + 6, by + dy + 1, 4, C.BLUE)
                    c.hline(bx + 6, by + dy + 3, 3, C.BLUE)
            hand(c, PAPER_X, hand_y + dy)
        elif beat in ("pencil_in", "tick", "pencil_out", "admire"):
            marks = 0
            if beat == "tick":
                marks = [2, 3, 5, 7, 8][k]
            elif beat in ("pencil_out", "admire"):
                marks = len(CHECK)
            ballot_open(c, marks)
            hand(c, PAPER_X, hand_y)
            if beat == "pencil_in":
                tip = [(16, 1), (9, 2)][k]
                pencil(c, *tip)
            elif beat == "tick":
                pencil(c, *CHECK[marks - 1])
            elif beat == "pencil_out":
                pencil(c, 15 + 4 * k, -2 - 3 * k)
        elif beat == "fold":
            if k == 0:
                # top half folding down: the back of the paper shows
                c.rect(PAPER_X, 4, PAPER_W, 11, C.WHITE, fill=True)
                c.hline(PAPER_X, 8, PAPER_W, C.CYAN)
                for x, y in CHECK:
                    if y >= 8:
                        c.pixel(x, y, C.BLACK)
                c.rect(BOX2[0], BOX2[1], 4, 4, C.BLUE)
                hand(c, PAPER_X, hand_y)
            elif k == 1:
                folded(c, PAPER_X, 8, PAPER_W, 7)
                hand(c, PAPER_X, hand_y)
            else:
                folded(c, PAPER_X, 9, 8, 5)
                hand(c, PAPER_X, hand_y)
        elif beat == "carry":
            # up and over to the slot
            path = [(8, 6), (13, 3), (19, 1), (25, 1), (30, 1)]
            x, y = path[k]
            folded(c, x, y, 8, 5)
            hand(c, x, y + 1)
        elif beat == "drop":
            y = [3, 5, 7, 10][k]
            under_box = (31, y)
            if k == 0:
                hand(c, 30, 2)
            elif k == 1:
                hand(c, 22, 1)
            elif k == 2:
                hand(c, 10, 1)
        elif beat == "thunk":
            box_flash = k == 0
            if k == 1:
                c.glyph("+CHECK", 32, 0, C.GREEN)
        elif beat == "cheer":
            c.glyph("+HEART", 32, max(0, 1 - k // 2), C.MAGENTA)
            spots = [(27, 2), (40, 1), (22, 5), (42, 4), (29, 0), (38, 5)]
            for i, (x, y) in enumerate(spots):
                if (i + k) % 3 == 0:
                    sparkle(c, x, y, C.YELLOW, big=True)
                elif (i + k) % 3 == 1:
                    c.pixel(x, y, C.WHITE)
            text = "go" if k < 3 else "counts"
        elif beat == "counts":
            text = "counts"
            if k % 4 < 2:
                c.glyph("+HEART", 32, 0, C.MAGENTA)
            else:
                sparkle(c, 34, 3, C.YELLOW, big=True)

        ballot_box(c, flash=box_flash)
        if under_box:
            # only the part still above the lid shows; the rest is inside
            x, y = under_box
            for yy in range(y, min(y + 5, LID_Y + 1)):
                color = C.CYAN if yy == y + 2 else C.WHITE
                xs = range(x, x + 8) if color == C.WHITE else range(x + 1, x + 7)
                for xx in range(x, x + 8):
                    c.pixel(xx, yy, color if xx in xs else C.WHITE)

        if text == "go":
            go_text(c, f, start=1)
        else:
            k_text = k if beat == "counts" else k - 3
            if beat == "counts":
                k_text += 3
            counts_text(c, k_text)

    out = Path(__file__).resolve().parents[2] / "src/sample/vote_ballot_box.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
