#!/usr/bin/env python3
"""
Cat box -- eighty-nine dollars, and the cat picks the packaging.

A yellow cardboard box with a red shipping label slides in from the right
to a person waiting on the doorstep. The flaps lift, and out comes a fancy
magenta cat bed with a white cushion, a little red heart and an $89 price
tag swinging from the corner. They set it on the floor in the middle and
step back, hands clasped. A white cat strolls in from the left, tail
flicking, stops at the bed and sniffs it (?), looks up at the person, down
at the bed... and walks straight past it, hops into the empty box, and
settles: two ears and two green eyes over the rim, blinking. The person's
shoulders drop; the price tag falls off the bed and lands flat. Caption:
IF I FITS I SITS. Button: the eyes close and a cyan Z rises from the box.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
FLOOR = 15                # the floor line
BOTTOM = FLOOR - 1        # feet rest on this row

BOX_X = 61                # final box position (left edge)
BOX_W, BOX_H = 16, 8      # rows 7..14
BOX_Y = FLOOR - BOX_H
BED_X, BED_W = 33, 14     # bed on the floor, rows 11..14
PERSON_X = 83

# Cat sprites facing right, feet on the last row. Head is cols 10..13.
CAT_A = [
    "..........#..#",
    "..........####",
    "..........####",
    "#..##########.",
    "#.###########.",
    ".###########..",
    "..#..#..#..#..",
    "..#..#..#..#..",
]
CAT_B = [
    "..........#..#",
    "..........####",
    "..........####",
    "#..##########.",
    "#.###########.",
    ".###########..",
    "...#.#...#.#..",
    "...#.#...#.#..",
]
CAT_JUMP = [
    "..........#..#",
    "..........####",
    "..........####",
    "#..##########.",
    "#.###########.",
    ".############.",
    "...#..#...##..",
    "..#..#........",
]


def sprite(frame, art, x, bottom, color):
    height = len(art)
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == "#":
                frame.pixel(x + c, bottom - height + 1 + r, color)


def cat(frame, x, bottom, art=CAT_A, look="ahead", tail=0, sniff=False):
    """A white cat whose head is at the right end; ``look`` steers the pupil."""
    sprite(frame, art, x, bottom, C.WHITE)
    top = bottom - len(art) + 1
    # Tail: rises from the rump, tip flicking back and forth.
    frame.pixel(x, top + 2, C.WHITE)
    frame.pixel(x - tail, top + 1, C.WHITE)
    # Eye: a 2x2 green block with a dark pupil.
    ex, ey = x + 11, top + 1
    frame.rect(ex, ey, 2, 2, C.GREEN, fill=True)
    pupil = {"ahead": (1, 1), "up": (1, 0), "down": (1, 1), "back": (0, 0)}[look]
    if look == "down":
        frame.pixel(ex + 1, ey + 1, C.BLACK)
        frame.pixel(ex, ey + 1, C.BLACK)
    else:
        frame.pixel(ex + pupil[0], ey + pupil[1], C.BLACK)
    # Nose.
    frame.pixel(x + 13 + (1 if sniff else 0), top + 2, C.MAGENTA)


def box(frame, x, flaps=0, label=True):
    """A filled yellow box; ``flaps`` 0..3 is how far the lid has opened."""
    frame.rect(x, BOX_Y, BOX_W, BOX_H, C.YELLOW, fill=True)
    # A red shipping label, stamped.
    if label:
        frame.rect(x + 2, BOX_Y + 2, 5, 3, C.RED, fill=True)
        frame.pixel(x + 3, BOX_Y + 3, C.WHITE)
        frame.pixel(x + 5, BOX_Y + 3, C.WHITE)
    if flaps:
        # Lid flaps hinged at the top corners, swinging outward and up.
        for k, dx in enumerate((1, 2, 2)[:flaps]):
            frame.pixel(x - dx, BOX_Y - 1 - k, C.YELLOW)
            frame.pixel(x + BOX_W - 1 + dx, BOX_Y - 1 - k, C.YELLOW)


def bed(frame, x, y):
    """The fancy bed: magenta rim, white cushion, a red heart on the front."""
    frame.rect(x, y + 1, BED_W, 3, C.MAGENTA, fill=True)
    frame.pixel(x, y, C.MAGENTA)
    frame.pixel(x + BED_W - 1, y, C.MAGENTA)
    frame.hline(x + 2, y + 1, BED_W - 4, C.WHITE)
    frame.pixel(x + 6, y + 2, C.RED)
    frame.pixel(x + 8, y + 2, C.RED)
    frame.pixel(x + 7, y + 3, C.RED)


def tag(frame, x, y, swing=0):
    """A white price tag, $89, hanging from a string to (x, y)."""
    frame.pixel(x, y - 1, C.WHITE)
    frame.pixel(x + swing, y - 2, C.WHITE)
    tx, ty = x + swing * 2 - 6, y - 9
    frame.rect(tx, ty, 13, 7, C.WHITE)
    frame.small_text("$89", tx + 1, ty + 1, C.YELLOW)


def person(frame, cx, pose="stand", drop=0, target=None):
    """A little person facing left, feet on BOTTOM, 9px tall."""
    head = 6 + drop
    frame.rect(cx - 1, head, 3, 3, C.YELLOW, fill=True)
    frame.pixel(cx - 1, head + 1, C.BLACK)          # eye, looking left
    frame.rect(cx - 1, 9, 3, 3, C.CYAN, fill=True)   # torso
    frame.vline(cx - 1, 12, 3, C.BLUE)              # legs
    frame.vline(cx + 1, 12, 3, C.BLUE)
    if pose == "stand":
        frame.vline(cx - 2, 9, 3, C.CYAN)
        frame.vline(cx + 2, 9, 3, C.CYAN)
    elif pose == "hold":
        # Both arms stretched toward ``target``: the box lid, then the bed.
        tx, ty = target
        frame.line(cx - 2, 9, tx, ty, C.CYAN)
        frame.line(cx - 2, 10, tx, ty + 1, C.CYAN)
        frame.pixel(tx, ty, C.YELLOW)
        frame.pixel(tx, ty + 1, C.YELLOW)
    elif pose == "clasp":
        # Hands clasped in front, hopeful.
        frame.pixel(cx - 2, 9, C.CYAN)
        frame.pixel(cx + 2, 9, C.CYAN)
        frame.pixel(cx - 2, 10, C.CYAN)
        frame.pixel(cx + 2, 10, C.CYAN)
        frame.hline(cx - 1, 11, 3, C.YELLOW)
    elif pose == "slump":
        # Shoulders dropped: arms hang straight down past the hips.
        frame.vline(cx - 2, 10, 4, C.CYAN)
        frame.vline(cx + 2, 10, 4, C.CYAN)
        frame.pixel(cx - 1, head + 1, C.BLACK)
        frame.pixel(cx - 1, head + 2, C.BLACK)      # mouth: a small o


def peek(frame, x, eyes="open"):
    """Just two ears and two eyes over the rim of the box."""
    rim = BOX_Y
    for ex in (x, x + 6):
        frame.pixel(ex + 1, rim - 4, C.WHITE)
        frame.hline(ex, rim - 3, 3, C.WHITE)
        frame.hline(ex, rim - 2, 3, C.WHITE)
    if eyes == "open":
        frame.hline(x + 1, rim - 1, 2, C.GREEN)
        frame.hline(x + 6, rim - 1, 2, C.GREEN)
    elif eyes == "shut":
        frame.hline(x + 1, rim - 1, 2, C.WHITE)
        frame.hline(x + 6, rim - 1, 2, C.WHITE)


def floor(frame):
    frame.hline(0, FLOOR, 96, C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    box_in = [96, 89, 82, 76, 70, 65, BOX_X]
    bed_out = [(BOX_X + 1, 7), (BOX_X + 1, 5), (BOX_X + 1, 3), (BOX_X + 1, 2)]
    bed_down = [(51, 4), (45, 6), (39, 9), (BED_X, 11)]
    opener = BOX_X + BOX_W + 3       # where the person stands to open the box
    lid = (BOX_X + BOX_W - 1, BOX_Y)
    for i in range(FRAMES):
        f = anim.frame()
        floor(f)
        flaps = 3
        bed_pos = (BED_X, 11)
        tag_fall = None
        if i <= 6:
            # Delivery: the box slides in from the right, past the person.
            person(f, opener, "stand")
            box(f, box_in[i])
            continue
        if i <= 9:
            # Flaps lift.
            flaps = i - 6
            box(f, BOX_X, flaps)
            person(f, opener, "hold", target=(lid[0], lid[1] - flaps))
            continue
        if i <= 13:
            # The bed rises out of the box.
            bx, by = bed_out[i - 10]
            bed(f, bx, by)
            box(f, BOX_X, flaps)
            person(f, opener, "hold", target=(bx + BED_W, by + 1))
            continue
        if i <= 17:
            # Carried to the middle and set down.
            bx, by = bed_down[i - 14]
            bed(f, bx, by)
            if i == 17:
                tag(f, bx + BED_W - 2, by, swing=1)
            box(f, BOX_X, flaps)
            person(f, bx + BED_W + 3, "hold", target=(bx + BED_W, by + 1))
            continue

        # From here the bed sits on the floor at the centre.
        bx, by = bed_pos
        swing = (0, 1, 0, -1)[i % 4]
        if i <= 20:
            # Steps back past the box to admire it. Hands clasped.
            walk = (66, 75, PERSON_X)[i - 18]
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, swing)
            box(f, BOX_X, flaps)
            person(f, walk, "clasp" if i == 20 else "stand")
            continue

        if i <= 30:
            # The cat strolls in from the left.
            t = i - 21
            cx = -14 + round(t * 33 / 9)
            art = CAT_A if t % 2 == 0 else CAT_B
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, swing)
            cat(f, cx, BOTTOM, art, tail=(t // 2) % 2)
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue
        if i <= 33:
            # Sniff.
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, swing)
            cat(f, 19, BOTTOM, CAT_A, sniff=(i % 2 == 1))
            f.small_text("?", 30, 0, C.WHITE)
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue
        if i <= 35:
            # Looks up at the person.
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, 0)
            cat(f, 19, BOTTOM, CAT_A, look="up")
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue
        if i <= 37:
            # Looks down at the bed.
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, 0)
            cat(f, 19, BOTTOM, CAT_A, look="down")
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue
        if i <= 41:
            # Walks straight past.
            t = i - 38
            cx = 19 + (t + 1) * 7
            art = CAT_A if t % 2 == 0 else CAT_B
            bed(f, bx, by)
            cat(f, cx, BOTTOM, art, tail=t % 2)
            tag(f, bx + BED_W - 2, by, swing)
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue
        if i <= 43:
            # Hops into the box: drawn first, so the box hides what is inside.
            t = i - 42
            bed(f, bx, by)
            tag(f, bx + BED_W - 2, by, swing)
            cat(f, BOX_X - 10 + t * 6, BOTTOM - 4 - t * 3, CAT_JUMP, look="ahead")
            box(f, BOX_X, flaps)
            person(f, PERSON_X, "clasp")
            continue

        # In the box. Ears and eyes over the rim.
        t = i - 44
        bed(f, bx, by)
        if t < 2:
            tag(f, bx + BED_W - 2, by, swing)
        elif t < 4:
            # The tag drops off and lands flat beside the bed.
            fall = 4 + (t - 2) * 4
            tx, ty = bx + BED_W - 8, by - 9 + fall
            f.rect(tx, ty, 13, 7, C.WHITE)
            f.small_text("$89", tx + 1, ty + 1, C.YELLOW)
        else:
            f.hline(bx + BED_W + 1, BOTTOM, 8, C.WHITE)
        box(f, BOX_X, flaps)
        eyes = "open"
        if t == 3:
            eyes = "blink"
        if t >= 7:
            eyes = "shut"
        peek(f, BOX_X + 5, eyes)
        if t >= 2:
            person(f, PERSON_X, "slump", drop=1)
        else:
            person(f, PERSON_X, "clasp")
        if t >= 2:
            f.small_text("IF I FITS I SITS", 0, 0, C.WHITE)
        if t >= 7:
            f.small_text("Z", BOX_X + 8, 2 - (t - 7), C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cat_box.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
