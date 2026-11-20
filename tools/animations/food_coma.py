#!/usr/bin/env python3
"""
Food coma -- four courses, one belt, no survivors.

Side view: a diner in a cyan shirt and blue trousers sits on a magenta
chair at a red-clothed table, fork in hand, in front of an empty white
plate. The right of the panel names each course as it arrives.

Each course drops onto the plate -- a yellow roast drumstick with a white
bone, a white mound of mashed potatoes with a pat of butter, a rain of
green peas -- then a magenta gravy boat tips in from above and pours a
yellow stream over the lot. After every course the diner shovels it down,
fork to mouth and back, the heap shrinking a bite at a time, and the
belly bulges a pixel further towards the table.

Then SECONDS?: everything at once, heaped to the top of the panel. It
goes in four bites. The belly is now pressed against the table, the belt
strains, and the yellow buckle shoots off across the panel with a white
PING!. The diner slumps back, eyes shut, mouth open, cyan Zs float up
from the head, and FOOD / COMA blinks magenta and white.

Beat sheet (frame indexes):
     0-2   empty plate, DIG IN!
     3-34  four courses, eight frames each: two to serve, four bites,
           two to digest (belly grows)
    35-41  SECONDS?: the giant heap, four bites
    42-45  belt strains, buckle flies, PING!
    46-52  slump, Zs, FOOD / COMA
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16

TEXT_LEFT = 44
COURSE_START = 3
COURSE_LEN = 8
SECONDS_START = COURSE_START + 4 * COURSE_LEN   # 35
POP_START = 42
COMA_START = 46

PLATE_Y = 9
TABLE_Y = 10
PILE_X0, PILE_X1 = 23, 34          # inclusive pile span on the plate


def mound(x0, x1, top, color, cap=None):
    """A dome from x0..x1 whose peak reaches row ``top`` (above the plate)."""
    out = {}
    mid = (x0 + x1) / 2
    half = (x1 - x0) / 2 + 0.5
    height = PLATE_Y - top
    for x in range(x0, x1 + 1):
        h = height * math.sqrt(max(0.0, 1 - ((x - mid) / half) ** 2))
        for y in range(PLATE_Y - max(1, round(h)), PLATE_Y):
            out[(x, y)] = color
    if cap:
        out.update(cap)
    return out


def drumstick():
    px = {}
    # meat: a fat yellow blob with red roasted flecks
    for (x, y) in [(24, 6), (25, 6), (26, 6), (23, 7), (24, 7), (25, 7), (26, 7),
                   (27, 7), (23, 8), (24, 8), (25, 8), (26, 8), (27, 8), (28, 7),
                   (28, 8), (27, 6)]:
        px[(x, y)] = C.YELLOW
    for p in [(25, 7), (24, 8), (27, 7)]:
        px[p] = C.RED
    # bone
    for x in range(29, 32):
        px[(x, 7)] = C.WHITE
    px[(32, 6)] = C.WHITE
    px[(32, 8)] = C.WHITE
    return px


def potatoes():
    m = mound(24, 32, 4, C.WHITE)
    m[(27, 4)] = C.YELLOW
    m[(28, 4)] = C.YELLOW
    m[(28, 5)] = C.YELLOW
    return m


rnd_peas = random.Random(1126)


def peas():
    m = mound(23, 33, 5, C.BLACK)
    out = {}
    for p in m:
        if (p[0] + p[1]) % 2 == 0 or rnd_peas.random() < 0.3:
            out[p] = C.GREEN
    return out


def gravy_heap():
    m = mound(24, 33, 4, C.WHITE)
    for (x, y) in list(m):
        if y <= 5 or (x + y) % 3 == 0:
            m[(x, y)] = C.YELLOW
    return m


def seconds_heap():
    m = mound(22, 35, 1, C.WHITE)
    rnd = random.Random(7)
    for p in list(m):
        r = rnd.random()
        if p[1] <= 2:
            m[p] = C.YELLOW if r < 0.6 else C.WHITE
        elif r < 0.25:
            m[p] = C.GREEN
        elif r < 0.45:
            m[p] = C.YELLOW
        elif r < 0.55:
            m[p] = C.RED
    # a drumstick bone poking out of the top
    m[(33, 2)] = C.WHITE
    m[(34, 1)] = C.WHITE
    m[(35, 0)] = C.WHITE
    return m


COURSES = [
    ("TURKEY", drumstick()),
    ("MASH", potatoes()),
    ("PEAS", peas()),
    ("GRAVY", gravy_heap()),
]
SECONDS = seconds_heap()


def eaten(food, fraction):
    """Remove the top ``fraction`` of the heap's rows."""
    if fraction <= 0:
        return dict(food)
    top = min(y for _, y in food)
    rows = PLATE_Y - top
    cut = top + math.ceil(rows * fraction)
    return {p: c for p, c in food.items() if p[1] >= cut}


def draw_table(c):
    c.hline(17, TABLE_Y, 26, C.RED)
    c.hline(17, TABLE_Y + 1, 26, C.RED)
    c.pixel(17, TABLE_Y + 2, C.RED)        # the cloth's hanging corner
    c.vline(19, TABLE_Y + 2, 4, C.MAGENTA)
    c.vline(40, TABLE_Y + 2, 4, C.MAGENTA)
    # plate
    c.hline(PILE_X0 - 1, PLATE_Y, PILE_X1 - PILE_X0 + 3, C.WHITE)
    c.pixel(PILE_X0 - 2, PLATE_Y - 1, C.WHITE)
    c.pixel(PILE_X1 + 2, PLATE_Y - 1, C.WHITE)


def draw_chair(c, slump):
    c.vline(2 - slump, 4, 9, C.MAGENTA)          # back
    c.hline(2, 13, 9, C.MAGENTA)                 # seat
    c.vline(2, 14, 2, C.MAGENTA)
    c.vline(10, 14, 2, C.MAGENTA)


def draw_diner(c, belly, arm, slump, f, button):
    """``arm``: 'rest', 'plate', 'mouth'. ``slump`` 0 or 1 leans back."""
    hx = 5 - slump                     # head left edge
    hy = 0 + slump
    # torso
    for y in range(4 + slump, 11):
        for x in range(4 - (slump if y < 7 else 0), 8):
            c.pixel(x, y, C.CYAN)
    # belly: a half disc pushing right from the torso
    if belly:
        bcx, bcy = 7, 8
        for y in range(5, 12):
            for x in range(8, 8 + belly + 1):
                if ((x - bcx) / (belly + 0.6)) ** 2 + ((y - bcy) / (2.6 + belly * 0.2)) ** 2 <= 1:
                    c.pixel(x, y, C.CYAN)
    # trousers
    c.hline(4, 11, 10 + 0, C.BLUE)
    c.hline(4, 12, 10, C.BLUE)
    c.vline(12, 13, 3, C.BLUE)
    c.vline(13, 13, 3, C.BLUE)
    c.pixel(14, 15, C.BLUE)
    # belt and buckle
    belt_end = 8 + max(0, belly - 1)
    c.hline(4, 10, belt_end - 3, C.MAGENTA)
    if button:
        c.pixel(belt_end, 10, C.YELLOW)
    # head
    c.rect(hx, hy + 1, 4, 3, C.YELLOW, fill=True)
    c.pixel(hx + 4, hy + 2, C.YELLOW)              # nose
    c.hline(hx, hy, 4, C.RED)                      # hair
    c.pixel(hx, hy + 1, C.RED)
    if slump:
        c.hline(hx + 2, hy + 1, 2, C.BLACK)        # shut eye, a line
        c.pixel(hx + 2, hy + 1, C.YELLOW)
        c.pixel(hx + 3, hy + 3, C.BLACK)           # open mouth
        c.pixel(hx + 3, hy + 2, C.BLACK if f % 2 else C.YELLOW)
    else:
        c.pixel(hx + 2, hy + 1, C.BLACK)           # eye
        if arm == 'mouth':
            c.pixel(hx + 3, hy + 3, C.BLACK)       # chomp
    # arm
    if slump:
        c.line(5, 6, 9, 5, C.YELLOW)               # a hand on the belly
        c.pixel(10, 5, C.YELLOW)
        return
    sx, sy = 6, 5
    if arm == 'mouth':
        c.line(sx, sy + 1, 10, 3, C.YELLOW)
        c.pixel(11, 3, C.WHITE)
        c.pixel(11, 2, C.WHITE)
    elif arm == 'plate':
        c.line(sx, sy + 1, 22, 7, C.YELLOW)
        c.pixel(23, 8, C.WHITE)
    else:
        c.line(sx, sy + 1, 15, 8, C.YELLOW)
        c.pixel(16, 8, C.WHITE)
        c.pixel(17, 7, C.WHITE)


def right_text(c, top, bottom, color, color2=None):
    region = W - TEXT_LEFT
    for row, (txt, col) in enumerate(((top, color), (bottom, color2 or color))):
        if not txt:
            continue
        x = TEXT_LEFT + (region - Canvas.text_width(txt)) // 2
        c.text(txt, x, 0 if row == 0 else 9, col)


def draw_gravy_boat(c, f_in):
    """Tipping in above the plate; pours from frame 1 of the serve."""
    bx, by = 31, 0
    c.hline(bx, by + 2, 5, C.MAGENTA)
    c.hline(bx + 1, by + 3, 3, C.MAGENTA)
    c.pixel(bx - 1, by + 1, C.MAGENTA)          # spout
    c.pixel(bx + 5, by + 1, C.MAGENTA)          # handle
    c.pixel(bx + 5, by + 0, C.MAGENTA)
    if f_in >= 1:
        c.vline(bx - 2, by + 2, 3, C.YELLOW)


def main():
    rnd = random.Random(1128)
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()

        slump = 1 if f >= COMA_START else 0
        arm = 'rest'
        food = {}
        belly = 0
        button = True
        drop = 0

        if f < COURSE_START:
            right_text(c, "DIG", "IN!", C.YELLOW, C.WHITE if f % 2 else C.YELLOW)
        elif f < SECONDS_START:
            k = (f - COURSE_START) // COURSE_LEN
            t = (f - COURSE_START) % COURSE_LEN
            name, dish = COURSES[k]
            belly = k + (1 if t >= 6 else 0)
            if k == 3 and t < 2:
                # the gravy goes over the last of the mash
                food = potatoes() if t == 0 else dish
            elif t < 2:
                drop = 4 if t == 0 else 0
                food = dish
            elif t < 6:
                food = eaten(dish, (t - 1) / 4)
                arm = 'plate' if t % 2 == 0 else 'mouth'
            right_text(c, name, f"{k + 1}/4" if t < 6 else "MMM...",
                       C.YELLOW, C.WHITE if t < 6 else C.CYAN)
            if k == 3 and t < 2:
                draw_gravy_boat(c, t)
        elif f < POP_START:
            t = f - SECONDS_START
            belly = 4 + (1 if t >= 4 else 0) + (1 if t >= 6 else 0)
            if t < 2:
                food = SECONDS
                drop = 3 if t == 0 else 0
            elif t < 6:
                food = eaten(SECONDS, (t - 1) / 4)
                arm = 'plate' if t % 2 == 0 else 'mouth'
            right_text(c, "SECONDS?", "SURE!" if t >= 1 else "",
                       C.YELLOW, C.WHITE)
        elif f < COMA_START:
            t = f - POP_START
            belly = 7 if t else 6
            button = False
            # the buckle flies in an arc to the right
            bx = 16 + 7 * t
            by = 10 - (6 - (t - 1.5) ** 2 * 1.6)
            c.pixel(bx, round(by), C.YELLOW)
            if t == 0:
                right_text(c, "UH-OH", "", C.RED)
            else:
                right_text(c, "PING!", "", C.WHITE if t % 2 else C.YELLOW)
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    if t == 1:  # a white flash where the buckle was
                        c.pixel(15 + dx, 10 + dy, C.WHITE)
        else:
            belly = 7
            button = False
            t = f - COMA_START
            blink = t % 2 == 0
            right_text(c, "FOOD", "COMA", C.MAGENTA if blink else C.WHITE,
                       C.WHITE if blink else C.MAGENTA)
            # Zs floating up from the head
            # Zs drifting up and away over the table
            for i in range(3):
                p = (t * 2 + i * 5) % 15
                zx = 15 + round(p * 1.5)
                zy = 3 - p // 5
                c.small_text("Z", zx, zy, (C.WHITE, C.CYAN, C.BLUE)[p // 5])

        draw_chair(c, slump)
        draw_table(c)
        for (x, y), col in food.items():
            if col != C.BLACK:
                c.pixel(x, y - drop, col)
        draw_diner(c, belly, arm, slump, f, button)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/food_coma.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
