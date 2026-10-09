#!/usr/bin/env python3
"""
Snooze -- the alarm clock inches out of reach.

A bedside alarm clock on the left, a lump under a magenta blanket on the
right with a head on the pillow, Zs drifting up. The red display reads 6:00
and the clock goes off: bells rock, BRRING! flashes, the clock jitters. A
very long arm comes out of the covers and slams the bells -- SNOOZE -- and
withdraws. 6:09, ring, slam. 6:18, ring, the arm takes its time and flops.
Then the gaps jump: 7:30, 9:15, the ring gets bigger each time, the clock
has inched away from the bed, and the arm pats the nightstand beside it.
11:47. The eyes snap open, the sleeper launches bolt upright, LATE!!! in red
with the whole panel shaking. The clock's display reads TOLD U.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

TABLE_Y = 13          # nightstand top; the clock sits on it
BOX_W = 26            # clock box, wide enough for a 5x7 "6:00"
BED_X = 57            # left end of the bed (pillow end)
SHOULDER = (66, 9)    # where the arm comes out of the covers
HIT_X = 28            # where the hand lands, in world columns

BELL = [
    ".#.",
    "###",
    "###",
]

# One entry per round: display time, clock x, ring text, ring text size,
# and the frame ranges for ring / extend / slam / withdraw. The rounds are
# laid out by hand so the beats land where they should.
ROUNDS = [
    # time, clock_x, ring text, big?, first frame, ring frames, arm kind
    ("6:00", 6, "BRRING!", False, 2, 4, "slam"),
    ("6:09", 6, "BRRING!", False, 11, 3, "slam"),
    ("6:18", 6, "BRRING!", False, 18, 3, "lazy"),
    ("7:30", 2, "BRRING!!", True, 26, 3, "miss"),
    ("9:15", 0, "BRRRING!!", True, 33, 3, "miss"),
    ("11:47", 0, "BRRRING!!!", True, 41, 3, "wake"),
]
NEXT_TIME = {"6:00": "6:09", "6:09": "6:18", "6:18": "7:30", "7:30": "9:15",
             "9:15": "11:47"}


def draw_clock(f, cx, display, ringing, index, big=False, display_small=None):
    """The clock with its box at x=cx. ``ringing`` rocks the bells and jitters."""
    jitter = 0
    jy = 0
    if ringing:
        jitter = (index % 2) if cx == 0 else (1 if index % 2 else -1)
        if big:
            jy = -(index % 2)
    x = cx + jitter
    top = 3 + jy
    f.rect(x, top, BOX_W, TABLE_Y - top, C.CYAN)
    f.hline(x + 1, TABLE_Y - 1, BOX_W - 2, C.CYAN)      # thicker base
    if display_small is not None:
        f.small_text(display_small, x + 2, top + 3, C.WHITE)
    else:
        tx = x + (BOX_W - Canvas.text_width(display, proportional=True)) // 2
        f.text(display, tx, top + 2, C.RED, proportional=True)
    # Bells on top, rocking when ringing.
    for k, bx in enumerate((x + 4, x + BOX_W - 7)):
        rock = 0
        if ringing:
            rock = (1 if (index + k) % 2 else -1)
        for r, row in enumerate(BELL):
            for c, ch in enumerate(row):
                if ch == "#":
                    f.pixel(bx + c + rock, top - 3 + r, C.YELLOW)
        if ringing:
            # Sound marks beside each bell.
            side = -2 if rock < 0 else 4
            f.pixel(bx + side + rock, top - 2, C.WHITE if big else C.YELLOW)
    # Clapper between the bells.
    f.pixel(x + BOX_W // 2, top - 1, C.WHITE)


def draw_table(f):
    f.hline(0, TABLE_Y, 36, C.WHITE)
    f.vline(1, TABLE_Y + 1, 2, C.WHITE)
    f.vline(34, TABLE_Y + 1, 2, C.WHITE)


def draw_bed(f, index, eyes="shut", upright=False, breathe=True):
    # Mattress and legs.
    f.hline(BED_X, 13, 96 - BED_X, C.CYAN)
    f.hline(BED_X, 12, 96 - BED_X, C.BLUE)
    f.vline(BED_X + 1, 14, 2, C.CYAN)
    f.vline(93, 14, 2, C.CYAN)
    f.vline(95, 8, 6, C.CYAN)                      # footboard
    f.pixel(94, 8, C.CYAN)
    if upright:
        # Sitting bolt upright on the mattress, blanket thrown back.
        hx = 62
        f.rect(hx, 1, 5, 5, C.YELLOW, fill=True)       # head
        f.pixel(hx + 1, 3, C.WHITE)
        f.pixel(hx + 3, 3, C.WHITE)                    # wide eyes
        f.pixel(hx + 2, 5, C.BLACK)                    # mouth open
        f.rect(hx + 1, 6, 3, 6, C.MAGENTA, fill=True)  # pyjama top
        f.line(hx, 7, hx - 3, 2, C.YELLOW)             # arms thrown up
        f.line(hx + 4, 7, hx + 7, 2, C.YELLOW)
        # Blanket heaped at the foot.
        for r, w in ((11, 20), (10, 14), (9, 6)):
            f.hline(93 - w, r, w, C.MAGENTA)
        return
    # Pillow, head, blanket lump.
    f.hline(BED_X + 1, 11, 9, C.WHITE)
    hx = BED_X + 2                                   # head at 59..63
    f.rect(hx, 7, 5, 5, C.YELLOW, fill=True)
    if eyes == "shut":
        f.pixel(hx + 1, 9, C.BLACK)
        f.pixel(hx + 3, 9, C.BLACK)
    elif eyes == "open":
        for ex in (hx + 1, hx + 3):
            f.pixel(ex, 8, C.WHITE)
            f.pixel(ex, 9, C.WHITE)
    rise = (index // 2) % 2 if breathe else 0
    # The lump: a hump from the shoulders to the feet.
    profile = [(64, 10), (65, 9), (66, 8), (67, 8 - rise), (70, 7 - rise),
               (75, 7 - rise), (80, 8 - rise), (85, 9), (89, 10), (92, 11)]
    for (x0, y0), (x1, y1) in zip(profile, profile[1:]):
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            y = round(y0 + (y1 - y0) * t)
            f.vline(x, y, 12 - y, C.MAGENTA)
    f.hline(64, 11, 29, C.MAGENTA)


def draw_zs(f, index, far=False):
    base = 84 if far else 67
    for k in range(2):
        phase = (index // 2 + k * 2) % 4
        f.small_text("Z", base + k * 4 + phase // 2, 5 - phase - k * 1, C.CYAN)


def draw_arm(f, hand, hx, hy, droop=False):
    """Arm from the shoulder to the hand; the hand is a 3x2 block."""
    sx, sy = SHOULDER
    f.line(sx, sy, hx + 1, hy + 1, C.YELLOW)
    f.line(sx, sy + 1, hx + 1, hy + 2, C.YELLOW)
    f.rect(hx, hy, 3, 2, C.WHITE if hand else C.YELLOW, fill=True)
    if droop:
        f.pixel(hx + 3, hy + 2, C.YELLOW)


def arm_for(kind, step, hits):
    """Return (hx, hy, slam, droop) for the arm, or None when withdrawn."""
    sx, sy = SHOULDER
    if kind == "slam":
        # 0 extend, 1 slam, 2 half withdrawn
        if step == 0:
            return (HIT_X + 8, 1, False, False)
        if step == 1:
            return (HIT_X, 0, True, False)
        if step == 2:
            return ((HIT_X + sx) // 2, 5, False, False)
    if kind == "lazy":
        # 0 half out, 1 nearly, 2 flop on, 3 resting, 4 half back
        if step == 0:
            return ((HIT_X + sx) // 2 + 4, 6, False, True)
        if step == 1:
            return (HIT_X + 5, 2, False, True)
        if step == 2:
            return (HIT_X, 0, True, False)
        if step == 3:
            return (HIT_X, 0, False, True)
        if step == 4:
            return ((HIT_X + sx) // 2, 6, False, True)
    if kind == "miss":
        # 0 extend to where the clock was, 1 drop, 2 pat, 3 pat, 4 withdraw
        if step == 0:
            return (HIT_X, 0, False, False)
        if step == 1:
            return (HIT_X, TABLE_Y - 2, True, False)
        if step == 2:
            return (HIT_X + 1, TABLE_Y - 3, False, False)
        if step == 3:
            return (HIT_X - 1, TABLE_Y - 2, True, False)
        if step == 4:
            return ((HIT_X + sx) // 2, 8, False, False)
    return None


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        scene = Canvas(anim.width, anim.height)
        shake = (0, 0)

        # Find the round this frame belongs to.
        state = None
        for n, (time, cx, ring_text, big, start, ring_n, kind) in enumerate(ROUNDS):
            end = ROUNDS[n + 1][4] if n + 1 < len(ROUNDS) else FRAMES
            if start - (2 if n == 0 else 0) <= i < end:
                state = (time, cx, ring_text, big, start, ring_n, kind, i - start)
                break
        time, cx, ring_text, big, start, ring_n, kind, t = state

        draw_table(scene)
        ringing = t >= 0
        arm = None
        text = None
        display = time
        eyes = "shut"
        upright = False
        display_small = None
        if t < 0:
            pass                                     # the opening quiet
        elif t < ring_n:
            text = ("ring", ring_text, big)
        elif kind in ("slam", "lazy"):
            step = t - ring_n
            arm = arm_for(kind, step, True)
            if kind == "slam":
                if step >= 1:
                    ringing = False
                    display = NEXT_TIME[time]
                    text = ("snooze", "SNOOZE", False)
            else:
                if step >= 2:
                    ringing = False
                    display = NEXT_TIME[time]
                    text = ("snooze", "SNOOZE...", False)
                else:
                    text = ("ring", ring_text, big) if step == 0 else None
        elif kind == "miss":
            step = t - ring_n
            arm = arm_for(kind, step, False)
            if step >= 1 and arm is not None:
                text = ("ring", ring_text, big)
            if arm is None:
                # Slept through it; the alarm gives up and the time jumps.
                ringing = False
                display = NEXT_TIME[time]
        elif kind == "wake":
            step = t - ring_n
            if step < 2:
                eyes = "open"
                text = ("ring", ring_text, big)
            else:
                upright = True
                ringing = False
                text = ("late", "LATE!!!", True)
                if step < 6:
                    shake = ((1, 0), (-1, 1), (0, -1), (1, 1))[step - 2]
                else:
                    display_small = "TOLD U"

        draw_clock(scene, cx, display, ringing, i, big, display_small)
        draw_bed(scene, i, eyes=eyes, upright=upright, breathe=not upright)
        if not upright and eyes == "shut" and arm is None:
            draw_zs(scene, i, far=big)
        if arm is not None:
            hx, hy, slam, droop = arm
            draw_arm(scene, slam, hx, hy, droop)
            if slam and kind in ("slam", "lazy"):
                # Impact star over the bells.
                for dx, dy in ((-1, -1), (3, -1), (1, -2), (-2, 1), (4, 1)):
                    scene.pixel(hx + dx, hy + dy, C.WHITE)

        if text is not None:
            which, s, is_big = text
            right_edge = cx + BOX_W
            if which == "ring":
                color = C.YELLOW if i % 2 else C.WHITE
                if is_big:
                    scene.text(s, right_edge + 3 + (i % 2), 0, color, proportional=True)
                else:
                    gap = BED_X - right_edge
                    x = right_edge + (gap - Canvas.small_text_width(s)) // 2
                    scene.small_text(s, x + (i % 2), 1, color)
            elif which == "snooze":
                gap = BED_X - right_edge
                x = right_edge + (gap - Canvas.small_text_width(s)) // 2
                scene.small_text(s, x, 8, C.WHITE if s == "SNOOZE" else C.CYAN)
            elif which == "late":
                scene.text(s, right_edge + 2, 2, C.RED, proportional=True)

        f.blit(scene, *shake)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/snooze.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
