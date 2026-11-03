#!/usr/bin/env python3
"""
Every vote counts -- the tie, and the one who breaks it.

A scoreboard across the top reads a dead heat on an unnamed ballot measure:
YES 4,999, NO 4,999, with TIE blinking yellow between them. Below, on a
blue floor, stands a blue ballot box marked VOTE. A little voter walks in
from the left, white ballot in hand, legs scissoring, stops at the box,
lifts the ballot over the slot and drops it in.

The box gives a jolt, a green +1 pops up beside it, and the YES counter flashes
white and rolls over to 5,000. TIE becomes +1. Confetti bursts across the
whole panel and the voter hops with arms up.

Then the message: EVERY VOTE over COUNTS, revealed left to right, and
finally BE THE ONE. over GO VOTE! with a check mark, both held long enough
to read.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, wipe  # noqa: E402

FRAMES = 53
DELAY = 130
W, H = 96, 16

# Scoreboard (3x5 font, rows 0-4) and the line under it.
YES_X, YES_NUM_X = 2, 16
NO_X, NO_NUM_X = 62, 74
MID_X = 48
SEP_Y = 6
FLOOR_Y = 15

# Ballot box.
BOX_X, BOX_Y, BOX_W, BOX_H = 56, 9, 19, 6
SLOT_X = BOX_X + BOX_W // 2 - 2        # 5-wide slot on the lid

# Beat sheet.
WALK_END = 12          # 0-12 walk in
STOP_X = 48            # voter's left edge when standing at the box
LIFT = 13              # 13-14 ballot raised, 15-16 dropping
DROP_IN = 17           # ballot gone; box jolts
TICK = 18              # 18 flash, 19+ 5,000
CONFETTI = 19          # 19-29 celebration
TEXT1 = 30             # 30-41 EVERY VOTE / COUNTS
TEXT2 = 42             # 42-52 BE THE ONE. / GO VOTE!

CONFETTI_COLORS = (C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA, C.WHITE)


def centered(text):
    return (W - Canvas.text_width(text)) // 2


def draw_scoreboard(c, f):
    c.small_text("YES", YES_X, 0, C.CYAN)
    c.small_text("NO", NO_X, 0, C.CYAN)
    c.small_text("4,999", NO_NUM_X, 0, C.WHITE)
    if f < TICK:
        c.small_text("4,999", YES_NUM_X, 0, C.WHITE)
        if f % 4 < 3:
            c.small_text("TIE", MID_X - Canvas.small_text_width("TIE") // 2, 0, C.YELLOW)
    elif f == TICK:
        c.small_text("5,000", YES_NUM_X, 0, C.WHITE)
    else:
        col = C.GREEN if f % 2 else C.YELLOW
        c.small_text("5,000", YES_NUM_X, 0, col)
        c.small_text("+1", MID_X - Canvas.small_text_width("+1") // 2, 0, C.GREEN)
    c.hline(0, SEP_Y, W, C.BLUE)


def draw_box(c, jolt=0):
    y = BOX_Y + jolt
    c.rect(BOX_X, y, BOX_W, BOX_H - jolt, C.BLUE, fill=True)
    c.hline(BOX_X, y, BOX_W, C.WHITE)
    c.hline(SLOT_X, y, 5, C.BLACK)
    c.small_text("VOTE", BOX_X + (BOX_W - Canvas.small_text_width("VOTE")) // 2, y + 1, C.YELLOW)


def draw_ballot(c, x, y):
    c.rect(x, y, 3, 3, C.WHITE, fill=True)
    c.pixel(x + 1, y + 1, C.RED)     # the filled-in oval


def draw_voter(c, x, step, arms_up=False, hop=0):
    """3 wide, 7 tall; feet on row 14 unless hopping."""
    y = 8 - hop
    c.rect(x, y, 3, 2, C.YELLOW, fill=True)            # head
    c.rect(x, y + 2, 3, 3, C.MAGENTA, fill=True)       # shirt
    if arms_up:
        for ax, d in ((x - 1, -1), (x + 3, 1)):       # a V for hooray
            c.pixel(ax, y + 2, C.MAGENTA)
            c.pixel(ax + d, y + 1, C.MAGENTA)
            c.pixel(ax + d, y, C.YELLOW)
    if step % 2:
        c.pixel(x, y + 5, C.WHITE)
        c.pixel(x + 2, y + 6, C.WHITE)
        c.pixel(x, y + 6, C.WHITE)
    else:
        c.pixel(x + 1, y + 5, C.WHITE)
        c.pixel(x + 1, y + 6, C.WHITE)


def main():
    rnd = random.Random(2026)
    anim = Animation(delay=DELAY)
    confetti = []
    for f in range(FRAMES):
        c = anim.frame()

        if f < TEXT1:
            draw_scoreboard(c, f)
            c.hline(0, FLOOR_Y, W, C.BLUE)
            draw_box(c, jolt=1 if f == DROP_IN else 0)

            if f <= WALK_END:
                vx = -3 + round((STOP_X + 3) * f / WALK_END)
                draw_voter(c, vx, f)
                draw_ballot(c, vx + 3, 10)
            elif f < DROP_IN:
                draw_voter(c, STOP_X, 0, arms_up=f < DROP_IN - 1)
                path = {13: (52, 8), 14: (SLOT_X + 1, 7), 15: (SLOT_X + 1, 7), 16: (SLOT_X + 1, 8)}
                bx, by = path[f]
                draw_ballot(c, bx, by)
                if f == 16:
                    c.hline(SLOT_X, BOX_Y, 5, C.BLACK)  # lid stays dark over it
            elif f < CONFETTI:
                draw_voter(c, STOP_X, 0)
            else:
                k = f - CONFETTI
                draw_voter(c, STOP_X, 0, arms_up=True, hop=1 if k % 2 == 0 else 0)

            # +1 pops up beside the box
            if TICK <= f < TICK + 4:
                c.small_text("+1", BOX_X + BOX_W + 3, BOX_Y - 1 + max(0, 2 - (f - TICK)), C.GREEN)

            # confetti: a burst from the box, then it rains
            if f >= CONFETTI:
                if f == CONFETTI:
                    for _ in range(40):
                        confetti.append([rnd.uniform(0, W), rnd.uniform(SEP_Y + 1, 14),
                                         rnd.uniform(-0.6, 0.6), rnd.uniform(0.5, 1.2),
                                         rnd.choice(CONFETTI_COLORS)])
                else:
                    for _ in range(4):
                        confetti.append([rnd.uniform(0, W), -1.0, rnd.uniform(-0.4, 0.4),
                                         rnd.uniform(0.6, 1.2), rnd.choice(CONFETTI_COLORS)])
                for p in confetti:
                    p[0] += p[2]
                    p[1] += p[3]
                confetti = [p for p in confetti if p[1] < FLOOR_Y]
                for p in confetti:
                    x, y = int(p[0]), int(p[1])
                    if SEP_Y < y < FLOOR_Y and c.get(x, y) == C.BLACK:
                        c.pixel(x, y, p[4])

        elif f < TEXT2:
            k = f - TEXT1
            edge = 40 + k * 22
            c.text("EVERY VOTE", centered("EVERY VOTE"), 0, wipe(C.WHITE, C.BLACK, edge=edge))
            c.text("COUNTS", centered("COUNTS"), 9,
                   wipe(C.YELLOW if k % 4 else C.GREEN, C.BLACK, edge=edge - 30))
        else:
            k = f - TEXT2
            c.text("BE THE ONE.", centered("BE THE ONE."), 0, C.CYAN)
            gx = centered("GO VOTE!") - 4
            c.text("GO VOTE!", gx, 9, C.YELLOW)
            if k >= 2:
                c.glyph("+CHECK", gx + Canvas.text_width("GO VOTE!") + 3, 9,
                        C.GREEN if k % 2 else C.WHITE)
            # a little confetti still drifting at the sides
            for i in range(3):
                c.pixel((k * 3 + i * 5) % 12, (k * 2 + i * 6) % 16, CONFETTI_COLORS[(k + i) % 6])
                c.pixel(W - 1 - (k * 3 + i * 7) % 12, (k * 2 + i * 5 + 3) % 16,
                        CONFETTI_COLORS[(k + i + 3) % 6])

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/vote_every_vote_counts.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
