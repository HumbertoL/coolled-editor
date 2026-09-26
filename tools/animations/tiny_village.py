#!/usr/bin/env python3
"""
Tiny Village -- one day in a miniature village, midnight to midnight.

A row of cottages, a bakery with a striped awning, a church with a copper
spire and a clock, trees and two street lamps sit along the whole panel. The
sky runs night -> dawn -> day -> dusk -> night: stars and a crescent moon
give way to a red-and-magenta sunrise, the sun arcs across a blue sky, and it
sets in yellow, red and magenta before the stars come back. The church clock's
hand turns with the hours; after dark the walls go blue, the lamps and the
windows light up yellow one by one, and go out again late at night.

Tiny life on top: the baker's light is on before dawn, the shop shutter rolls
up in the morning and the baker stands in the doorway; a bird flies in and
perches on the church cross until the bell swings at noon and startles it
off; a woman walks her dog to the bakery, the dog waits outside wagging, and
the two of them hurry home at dusk; a red car drives through with its
headlights on; the cottage chimney smokes morning and evening. Frame 52 runs
straight into frame 0, so the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
W, H = 96, 16
GROUND = 15

SUNRISE, SUNSET = 7, 37  # frames the sun is up between
MOON_START, MOON_LEN = 39, 21  # moon crosses frames 39..52, 0..6

# Frames when the sky counts as dark (walls go blue, lamps on).
def is_dark(f):
    return f >= 39 or f <= 6


def hour(f):
    """Clock time: frame 0 is 02:00, one loop is 24 hours."""
    return (2 + f * 24 / FRAMES) % 24


# -- sky ------------------------------------------------------------------

# Each entry: list of (first_row, colour), top to bottom.
SKY_KEYS = {
    5: [(0, C.BLACK), (10, C.BLUE)],
    6: [(0, C.BLACK), (6, C.BLUE), (10, C.MAGENTA)],
    7: [(0, C.BLACK), (3, C.BLUE), (7, C.MAGENTA), (11, C.YELLOW)],
    8: [(0, C.BLUE), (5, C.MAGENTA), (10, C.YELLOW)],
    9: [(0, C.BLUE), (8, C.MAGENTA), (11, C.YELLOW)],
    10: [(0, C.BLUE), (10, C.YELLOW)],
    34: [(0, C.BLUE), (9, C.YELLOW)],
    35: [(0, C.BLUE), (7, C.MAGENTA), (10, C.YELLOW)],
    36: [(0, C.BLUE), (4, C.MAGENTA), (9, C.YELLOW)],
    37: [(0, C.BLUE), (5, C.MAGENTA), (12, C.YELLOW)],
    38: [(0, C.BLACK), (3, C.BLUE), (8, C.MAGENTA)],
    39: [(0, C.BLACK), (6, C.BLUE), (11, C.MAGENTA)],
    40: [(0, C.BLACK), (9, C.BLUE)],
}
DAY_SKY = [(0, C.BLUE), (11, C.CYAN)]
NIGHT_SKY = [(0, C.BLACK)]


def sky_bands(f):
    if f in SKY_KEYS:
        return SKY_KEYS[f]
    if 11 <= f <= 33:
        return DAY_SKY
    return NIGHT_SKY


def sky_colour(bands, y):
    colour = C.BLACK
    for row, c in bands:
        if y >= row:
            colour = c
    return colour


rnd = random.Random(7)
STARS = []
while len(STARS) < 22:
    x, y = rnd.randrange(W), rnd.randrange(0, 9)
    if all(abs(x - sx) + abs(y - sy) > 3 for sx, sy, _ in STARS):
        STARS.append((x, y, rnd.randrange(5)))


# -- sprites --------------------------------------------------------------

# r roof, w wall, c chimney, s spire, + cross, d door, a awning,
# digits: a window (lit by id), S shop window, o belfry, K clock face.
HOUSE_A = [
    "       cc   ",
    "  rrrrrccr  ",
    " rrrrrrrrrr ",
    "rrrrrrrrrrrr",
    " wwwwwwwwww ",
    " w11ww22www ",
    " w11ww22wdw ",
    " wwwwwwwwdw ",
    " wwwwwwwwdw ",
]
BAKERY = [
    "     rrrr     ",
    "   rrrrrrrr   ",
    " rrrrrrrrrrrr ",
    "rrrrrrrrrrrrrr",
    " ww33wwww44ww ",
    " ww33wwww44ww ",
    "aaaaaaaaaawwww",
    " wSSSSSSSwddw ",
    " wSSSSSSSwddw ",
    " wSSSSSSSwddw ",
    " wwwwwwwwwddw ",
]
TOWER = [
    "   +   ",
    "  +s+  ",
    "  sss  ",
    " sssss ",
    "sssssss",
    "wwwwwww",
    "wooooow",
    "wooooow",
    "wwwwwww",
    "w.KKK.w",
    "wKKKKKw",
    "wKKKKKw",
    "wKKKKKw",
    "w.KKK.w",
    "wwwwwww",
]
NAVE = [
    "rrrrrrrrrr  ",
    "rrrrrrrrrrr ",
    "rrrrrrrrrrrr",
    "wwwwwwwwwww ",
    "ww5ww6ww7ww ",
    "ww5ww6ww7ww ",
    "wwwwwwwwwww ",
    "wwwwwwwwwww ",
]
HOUSE_C = [
    "   rrrr   ",
    " rrrrrrrr ",
    "rrrrrrrrrr",
    " w88wwwdw ",
    " w88wwwdw ",
    " wwwwwwdw ",
    " wwwwwwdw ",
]
HOUSE_D = [
    "  rrrrrr  ",
    " rrrrrrrr ",
    "rrrrrrrrrr",
    " wwwwwwww ",
    " w99wwAAw ",
    " w99wwAAw ",
    " wwwwwwww ",
    " wBBwwddw ",
    " wBBwwddw ",
    " wwwwwddw ",
    " wwwwwddw ",
]
HOUSE_E = [
    "  rrrrr",
    " rrrrrr",
    "rrrrrrr",
    " wwwwww",
    " wCCwww",
    " wCCwdw",
    " wwwwdw",
]
TREE_ROUND = [
    " ggg ",
    "ggggg",
    "ggggg",
    " ggg ",
    "  t  ",
    "  t  ",
]
TREE_TALL = [
    " g ",
    "ggg",
    "ggg",
    "ggg",
    "ggg",
    " t ",
    " t ",
]

# (sprite, x, top_y, wall colour by day)
BUILDINGS = [
    (TREE_TALL, 0, 8, None),
    (HOUSE_A, 3, 6, C.WHITE),
    (BAKERY, 17, 4, C.MAGENTA),
    (TREE_ROUND, 32, 9, None),
    (TOWER, 41, 0, C.WHITE),
    (NAVE, 48, 7, C.WHITE),
    (TREE_TALL, 60, 8, None),
    (HOUSE_C, 63, 8, C.YELLOW),
    (HOUSE_D, 74, 4, C.WHITE),
    (TREE_ROUND, 84, 9, None),
    (HOUSE_E, 89, 8, C.CYAN),
]
LAMPS = [15, 38]
CLOCK_CENTRE = (44, 11)
BELL_X, BELL_Y = 44, 6
CHIMNEY = (10, 6)
BAKERY_DOOR_X = 27  # left column of the 2-wide door
HOUSE_C_DOOR_X = 70
SHOP_X, SHOP_Y = 19, 11  # top-left of the 7x3 shop window

# Windows: id -> list of (on, off) cyclic frame intervals when lit.
LIGHTS = {
    "1": [(38, 49)],
    "2": [(40, 2)],
    "3": [(1, 9)],  # the baker's bedroom: up before dawn
    "4": [(3, 9), (39, 46)],
    "5": [(40, 47)],  # evening service
    "6": [(40, 47)],
    "7": [(40, 47)],
    "8": [(41, 52), (6, 8)],
    "9": [(39, 50)],
    "A": [(42, 4)],  # the night owl
    "B": [(38, 45)],
    "C": [(39, 48)],
}
SHOP_LIT = [(3, 12), (33, 40)]


def in_cycle(f, intervals):
    for on, off in intervals:
        if on <= off:
            if on <= f < off:
                return True
        elif f >= on or f < off:
            return True
    return False


def draw_sprite(frame, rows, ox, oy, cmap):
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == " ":
                continue
            colour = cmap(ch) if callable(cmap) else cmap.get(ch)
            if colour is not None:
                frame.pixel(ox + dx, oy + dy, colour)


# -- the actors -----------------------------------------------------------

def draw_sky(frame, f):
    bands = sky_bands(f)
    for y in range(GROUND):
        for x in range(W):
            frame.pixel(x, y, sky_colour(bands, y))
    # stars, only where the sky is still black
    for x, y, phase in STARS:
        if sky_colour(bands, y) != C.BLACK:
            continue
        tw = (f + phase * 3) % 5
        frame.pixel(x, y, C.WHITE if tw == 0 else C.CYAN if tw < 3 else C.BLUE)
    # sun
    if SUNRISE <= f <= SUNSET:
        p = (f - SUNRISE) / (SUNSET - SUNRISE)
        # faster in the morning so it is well clear of the cross by noon
        sx = 4 + 108 * p if p < 0.5 else 58 + 70 * (p - 0.5)
        sy = 9.5 - 8.5 * math.sin(math.pi * p)
        low = f <= SUNRISE + 2 or f >= SUNSET - 2  # a red sun near the horizon
        draw_sprite(
            frame,
            [" ## ", "####", "####", " ## "],
            int(sx) - 2,
            int(sy) - 2,
            {"#": C.RED if low else C.YELLOW},
        )
    # moon
    m = (f - MOON_START) % FRAMES
    if m < MOON_LEN:
        p = m / (MOON_LEN - 1)
        mx = 4 + p * 86
        my = 8 - 7 * math.sin(math.pi * p)
        draw_sprite(frame, [" ## ", "#   ", "#   ", " ## "], int(mx) - 2, int(my) - 2, {"#": C.WHITE})


def draw_buildings(frame, f):
    dark = is_dark(f)
    for sprite, ox, oy, wall in BUILDINGS:

        def cmap(ch, wall=wall):
            if ch == "w":
                return C.BLUE if dark else wall
            if ch in "rc":
                return C.MAGENTA if dark else C.RED
            if ch == "s":
                return C.BLUE if dark else C.CYAN
            if ch == "+":
                return C.YELLOW
            if ch == "g":
                return C.GREEN
            if ch == "t":
                return C.RED
            if ch == "a":
                return None  # drawn separately
            if ch == "d":
                return C.RED if not dark else C.MAGENTA
            if ch == "K":
                return C.YELLOW
            if ch == "o":
                return C.BLACK
            if ch == ".":
                return C.BLUE if dark else wall
            if ch in LIGHTS:
                return C.YELLOW if in_cycle(f, LIGHTS[ch]) else (C.BLACK if dark else C.BLUE)
            return None

        draw_sprite(frame, sprite, ox, oy, cmap)
    # awning: red and white stripes
    for dx in range(10):
        frame.pixel(17 + dx, 10, C.RED if dx % 2 == 0 else (C.BLUE if dark else C.WHITE))
    # ground
    frame.hline(0, GROUND, W, C.BLUE if dark else C.GREEN)
    # lamps
    for lx in LAMPS:
        frame.vline(lx, 9, 6, C.WHITE if not dark else C.CYAN)
        frame.pixel(lx, 8, C.YELLOW if dark else C.WHITE)
        if dark:
            frame.pixel(lx - 1, 8, C.YELLOW)
            frame.pixel(lx + 1, 8, C.YELLOW)


def draw_clock(frame, f):
    a = hour(f) / 12 * 2 * math.pi
    cx, cy = CLOCK_CENTRE
    frame.pixel(cx, cy, C.BLACK)
    for r in (1, 2):
        frame.pixel(cx + round(r * math.sin(a)), cy - round(r * math.cos(a)), C.BLACK)


BELL_SWING = {21: -1, 22: 1, 23: -1, 24: 1, 25: -1, 26: 1, 27: 0}


def draw_bell(frame, f):
    s = BELL_SWING.get(f, 0)
    x, y = BELL_X + s, BELL_Y
    frame.pixel(x, y, C.YELLOW)
    frame.hline(x - 1, y + 1, 3, C.YELLOW)
    if s:
        # sound waves either side of the tower
        side = 40 if s < 0 else 48
        frame.pixel(side, 5, C.WHITE)
        frame.pixel(side + (-1 if s < 0 else 1), 6, C.WHITE)
        frame.pixel(side, 7, C.WHITE)


def draw_shop(frame, f):
    dark = is_dark(f)
    # shutter: 0 = closed, 3 = fully open
    if 9 <= f <= 11:
        opened = f - 8
    elif 12 <= f <= 38:
        opened = 3
    elif 39 <= f <= 41:
        opened = 41 - f
    else:
        opened = 0
    lit = in_cycle(f, SHOP_LIT)
    inside = C.YELLOW if lit else C.RED
    loaves = [" y  y  y", "yyy yyy "]
    for row in range(3):
        y = SHOP_Y + row
        visible = row >= 3 - opened
        for dx in range(7):
            if visible:
                ch = " " if row == 0 else loaves[row - 1][dx]
                colour = inside
                if ch == "y":
                    colour = C.RED if lit else C.YELLOW
                frame.pixel(SHOP_X + dx, y, colour)
            else:
                frame.pixel(SHOP_X + dx, y, C.WHITE if row % 2 == 0 else C.CYAN)
    if not lit and dark:
        # closed shutter at night, dimmer
        for row in range(3 - opened):
            frame.hline(SHOP_X, SHOP_Y + row, 7, C.CYAN if row % 2 == 0 else C.BLACK)


def draw_baker(frame, f):
    if 12 <= f <= 18:
        x = BAKERY_DOOR_X
        frame.rect(x, 11, 2, 4, C.BLACK, fill=True)
        frame.pixel(x, 11, C.WHITE)  # chef's hat
        frame.pixel(x, 12, C.YELLOW)  # face
        frame.vline(x, 13, 2, C.WHITE)  # apron
        if f in (14, 16):  # waves good morning
            frame.pixel(x + 1, 11, C.YELLOW)
        else:
            frame.pixel(x + 1, 13, C.YELLOW)


def draw_smoke(frame, f):
    dark = is_dark(f)
    for start, end in ((8, 22), (30, 45)):
        for birth in range(start, end, 2):
            age = f - birth
            if 0 <= age < 6 and birth + 6 <= end + 6:
                x = CHIMNEY[0] + age * 0.6 + (0.5 if age % 2 else 0)
                y = CHIMNEY[1] - 1 - age * 0.9
                if y >= 0:
                    colour = C.WHITE if age < 3 else C.CYAN
                    if dark:
                        colour = C.CYAN if age < 2 else C.BLUE
                    frame.pixel(int(x), int(y), colour)


# Bird: flies in from the left, perches on the cross arm, flees the bell.
PERCH = (45, 0)


def bird_pos(f):
    if 12 <= f < 20:
        p = (f - 12) / 8
        return -3 + p * (PERCH[0] + 3), 5 - 3 * p - 2 * math.sin(math.pi * p), True
    if 20 <= f <= 21:
        return PERCH[0], PERCH[1], False
    if 22 <= f <= 32:
        p = (f - 22) / 10
        return PERCH[0] + 2 + p * 56, PERCH[1] + 1 + 2 * p, True
    return None


def draw_bird(frame, f):
    pos = bird_pos(f)
    if pos is None:
        return
    x, y, flying = int(pos[0]), int(pos[1]), pos[2]
    col = C.BLACK
    if not flying:
        frame.pixel(x, y, col)
        frame.pixel(x + 1, y, col)
        return
    if f % 2:
        frame.pixel(x - 1, y, col)
        frame.pixel(x, y + 1, col)
        frame.pixel(x + 1, y, col)
    else:
        frame.pixel(x - 1, y + 1, col)
        frame.pixel(x, y + 1, col)
        frame.pixel(x + 1, y + 1, col)
        frame.pixel(x - 1, y, col)


def walker_state(f):
    """(person_x, dog_x, facing, walking, dog_waiting) or None."""
    out_start, out_end = 13, 33  # house C door -> bakery door
    back_start, back_end = 37, 52
    if out_start <= f <= out_end:
        p = (f - out_start) / (out_end - out_start)
        px = HOUSE_C_DOOR_X - p * (HOUSE_C_DOOR_X - BAKERY_DOOR_X)
        return px, px - 4, -1, f < out_end, False
    if out_end < f < back_start:
        return None, BAKERY_DOOR_X + 2, -1, False, True
    if back_start <= f <= back_end:
        p = (f - back_start) / (back_end - back_start)
        px = BAKERY_DOOR_X + p * (HOUSE_C_DOOR_X - BAKERY_DOOR_X)
        return px, px + 4, 1, f < back_end, False
    return None


def draw_walkers(frame, f):
    state = walker_state(f)
    if state is None:
        return
    px, dx, facing, walking, waiting = state
    step = f % 2
    if f in (33, 34, 37):  # bakery door open
        frame.rect(BAKERY_DOOR_X, 11, 2, 4, C.BLACK, fill=True)
    if px is not None:
        x = int(round(px))
        frame.pixel(x, 10, C.YELLOW)
        frame.vline(x, 11, 2, C.GREEN)
        frame.pixel(x + facing, 11, C.YELLOW)  # hand on the leash
        if walking and step:
            frame.pixel(x - 1, 14, C.GREEN)
            frame.pixel(x + 1, 14, C.GREEN)
            frame.pixel(x, 13, C.GREEN)
        else:
            frame.vline(x, 13, 2, C.GREEN)
        if f >= 37:  # carrying a loaf home
            frame.pixel(x - facing, 12, C.YELLOW)
    d = int(round(dx))
    head = d if facing < 0 else d + 3
    tail = d + 3 if facing < 0 else d
    dog = C.RED if not is_dark(f) else C.WHITE
    if waiting:
        # sitting, tail wagging
        frame.pixel(d, 12, dog)
        frame.hline(d, 13, 3, dog)
        frame.hline(d, 14, 3, dog)
        frame.pixel(d + 3, 13 if f % 2 else 12, dog)
        return
    frame.pixel(head, 12, dog)
    frame.hline(d, 13, 4, dog)
    frame.pixel(tail, 12, dog)
    if walking and step:
        frame.pixel(d + 1, 14, dog)
        frame.pixel(d + 2, 14, dog)
    else:
        frame.pixel(d, 14, dog)
        frame.pixel(d + 3, 14, dog)
    if px is not None:
        frame.line(int(round(px)) + facing, 11, head, 12, C.WHITE if not is_dark(f) else C.CYAN)
        frame.pixel(int(round(px)) + facing, 11, C.YELLOW)


CAR = [
    "  ccc  ",
    " cwwwc ",
    "hccccccb",
    " o   o ",
]


def draw_car(frame, f):
    start, speed = 24, 6.5
    x = W + 2 - (f - start) * speed
    if not (-10 < x < W + 2) or f < start:
        return
    x = int(x)
    dark = is_dark(f) or f >= 36
    cmap = {
        "c": C.RED,
        "w": C.CYAN,
        "h": C.YELLOW if dark else C.WHITE,
        "b": C.RED,
        "o": C.BLACK,
    }
    draw_sprite(frame, CAR, x, 12, cmap)
    if dark:
        for i in range(1, 5):
            frame.pixel(x - i, 14, C.YELLOW)
        frame.pixel(x - 3, 15, C.YELLOW)
        frame.pixel(x - 4, 15, C.YELLOW)


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        frame = anim.frame()
        draw_sky(frame, f)
        draw_smoke(frame, f)
        draw_bird(frame, f)
        draw_buildings(frame, f)
        draw_clock(frame, f)
        draw_bell(frame, f)
        draw_shop(frame, f)
        draw_baker(frame, f)
        draw_walkers(frame, f)
        draw_car(frame, f)
        # the perched bird sits in front of the cross
        if bird_pos(f) and not bird_pos(f)[2]:
            draw_bird(frame, f)
    out = Path(__file__).resolve().parents[2] / "src/sample/tiny_village.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
