#!/usr/bin/env python3
"""
Roomba stuck -- one chair leg, four bonks, one cat who could not care less.

Side view of a room: a yellow chair on the right, a white wall on the left,
and a dusty magenta floor. A blue robot vacuum with a white cat loafing on
top drives confidently right and BONKs the chair leg. It backs up, turns a
few degrees, and BONKs it again -- faster each time, its light going
green -> yellow -> red and a "!" then "#@%!" over its head, while the clean
stripe it leaves in the dust stays barely longer than itself. Finally it
spins round and makes a break for it... straight into the wall. The cat
stands, hops off, and strolls away bored.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 130
W = 13            # roomba width
LEG = 60          # chair's front leg column
HIT_X = LEG - W   # roomba x when its bumper touches the leg
WALL = 1          # wall occupies columns 0..WALL

# Per frame: (roomba x, facing +1/-1, light color, event)
# events: 'bonk', 'bonk!' (with !), 'bonk#' (swearing), 'turn', 'wall'
G, Y, R = C.GREEN, C.YELLOW, C.RED
TIMELINE = [
    (36, 1, G, None), (39, 1, G, None), (42, 1, G, None), (45, 1, G, None),
    (HIT_X, 1, G, 'bonk'), (HIT_X, 1, G, 'bonk'),
    (45, 1, G, None), (43, 1, G, None), (43, 1, G, 'turn'), (43, 1, G, 'turn'),
    (45, 1, G, None),
    (HIT_X, 1, Y, 'bonk!'), (HIT_X, 1, Y, 'bonk!'),
    (44, 1, Y, None), (44, 1, Y, 'turn'),
    (HIT_X, 1, R, 'bonk!'), (HIT_X, 1, R, 'bonk!'),
    (45, 1, R, None),
    (HIT_X, 1, R, 'bonk#'), (HIT_X, 1, R, 'bonk#'), (HIT_X, 1, R, 'bonk#'),
    # Beat: sulking, light blinking red.
    (HIT_X, 1, R, 'sulk'), (HIT_X, 1, R, 'sulk'), (HIT_X, 1, R, 'sulk'),
    # Back up and spin round.
    (44, 1, R, None), (42, 1, R, 'turn'), (42, -1, R, 'turn'),
    (42, -1, G, 'free'),
    # The great escape.
    (37, -1, G, 'free'), (30, -1, G, 'free'), (22, -1, G, 'free'),
    (14, -1, G, 'free'), (6, -1, G, 'free'), (WALL + 1, -1, G, 'wall'),
    (WALL + 1, -1, R, 'wall'), (WALL + 1, -1, R, 'wall'),
    (WALL + 1, -1, R, "dazed"), (WALL + 1, -1, R, "dazed"),
]
# Then the cat leaves: roomba parked at the wall, light red.
CAT_EXIT_START = len(TIMELINE)
FRAMES = 53

# Cat sprites, facing right; '#' body, 'e' eye.
CAT_LOAF = [
    ".....#.#",
    "#....#e#",
    "#.######",
    ".#######",
    "..######",
]
CAT_SLEEPY = [
    ".....#.#",
    "#....###",
    "#.######",
    ".#######",
    "..######",
]
CAT_STAND = [
    "#....#.#",
    "#....#e#",
    ".######.",
    ".######.",
    ".#....#.",
]
CAT_WALK = [
    "#....#.#",
    "#....#e#",
    ".######.",
    ".######.",
    "..#..#..",
]


def draw_sprite(frame, rows, x, y, color, eye=C.GREEN, flip=False):
    width = len(rows[0])
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            cx = x + (width - 1 - c if flip else c)
            if cell == "#":
                frame.pixel(cx, y + r, color)
            elif cell == "e":
                frame.pixel(cx, y + r, eye)


def draw_room(frame, dust):
    frame.vline(0, 0, 15, C.WHITE)                 # wall
    frame.vline(1, 0, 15, C.BLUE)
    # Chair: seat, backrest, two legs.
    frame.hline(LEG, 4, 14, C.YELLOW)
    frame.vline(LEG + 13, 0, 4, C.YELLOW)
    frame.hline(LEG + 10, 0, 4, C.YELLOW)
    frame.vline(LEG, 5, 10, C.YELLOW)
    frame.vline(LEG + 13, 5, 10, C.YELLOW)
    for x in range(96):
        if dust[x]:
            frame.pixel(x, 15, C.MAGENTA)


def draw_roomba(frame, x, facing, light, blink=True):
    frame.hline(x + 2, 11, W - 4, C.CYAN)          # top rim
    frame.hline(x + 1, 12, W - 2, C.BLUE)
    frame.hline(x, 13, W, C.BLUE)
    frame.hline(x + 1, 14, W - 2, C.BLUE)
    front = x + W - 1 if facing > 0 else x
    frame.vline(front, 12, 2, C.WHITE)             # bumper
    frame.pixel(x + 3, 14, C.WHITE)                # wheels
    frame.pixel(x + W - 4, 14, C.WHITE)
    if blink:
        lx = x + W - 4 if facing > 0 else x + 3
        frame.pixel(lx, 11, light)


def spokes(frame, x, y, direction):
    """Little impact lines radiating back from a contact point."""
    d = -direction
    frame.pixel(x + 2 * d, y - 3, C.WHITE)
    frame.pixel(x + 3 * d, y - 4, C.WHITE)
    frame.pixel(x + 2 * d, y + 0, C.WHITE)
    frame.pixel(x + 3 * d, y + 0, C.WHITE)
    frame.pixel(x + 1 * d, y - 2, C.WHITE)
    frame.pixel(x - 1 * d, y - 3, C.WHITE)   # past the obstacle too
    frame.pixel(x - 1 * d, y - 4, C.WHITE)


def build():
    rng = random.Random(7)
    dust = [rng.random() < 0.7 for _ in range(96)]
    for x in range(LEG - 3, LEG + 16):
        dust[x] = True
    anim = Animation(delay=DELAY)
    rx, facing, light = TIMELINE[0][0], 1, G
    for index in range(FRAMES):
        frame = anim.frame()
        if index < len(TIMELINE):
            rx, facing, light, event = TIMELINE[index]
        else:
            event = None
            light = R
        # Clean under the roomba's wheels (x+1 .. x+W-2) -- but not on the
        # mad dash, so the floor is left with one tiny stripe.
        if event not in ('free', 'wall', 'dazed') and index < CAT_EXIT_START:
            for x in range(rx + 1, rx + W - 1):
                dust[x] = False
        draw_room(frame, dust)
        if event == 'wall' and TIMELINE[index - 1][3] != 'wall':
            frame.vline(0, 0, 15, C.YELLOW)
            frame.vline(1, 0, 15, C.YELLOW)
        blink = not (event == 'sulk' and index % 2) and not (
            index >= CAT_EXIT_START and index % 2)
        draw_roomba(frame, rx, facing, light, blink)

        # The cat.
        if index < CAT_EXIT_START + 2:
            pose = CAT_SLEEPY if index % 9 in (5, 6) else CAT_LOAF
            cat_x = rx + 1 if facing > 0 else rx + 4
            if index >= CAT_EXIT_START:
                pose = CAT_STAND
            # The bonk jolts the cat by one pixel -- it does not react.
            cat_y = 6
            if event and event.startswith('bonk') and TIMELINE[index - 1][3] != event:
                cat_x += facing
            if event == 'wall' and TIMELINE[index - 1][3] != 'wall':
                cat_y = 4                       # tossed up, still loafing
            draw_sprite(frame, pose, cat_x, cat_y, C.WHITE, flip=facing < 0)
        else:
            k = index - (CAT_EXIT_START + 2)
            if k == 0:
                draw_sprite(frame, CAT_STAND, rx + 13, 4, C.WHITE)   # mid hop
            else:
                cx = min(rx + 14 + 5 * (k - 1), LEG + 3)
                if cx >= LEG + 3:
                    # Curls up under the chair, done with all of this.
                    draw_sprite(frame, CAT_SLEEPY, cx, 10, C.WHITE)
                else:
                    pose = CAT_WALK if k % 2 else CAT_STAND
                    draw_sprite(frame, pose, cx, 10, C.WHITE)
                    if k in (3, 4):             # tail flick of disdain
                        frame.pixel(cx, 9, C.WHITE)
            if 1 <= k <= 4:
                frame.small_text("MEH.", rx + 19 + 4 * (k - 1) - 4, 2, C.CYAN)

        # Event overlays.
        if event and event.startswith('bonk'):
            spokes(frame, LEG, 12, 1)
            fresh = TIMELINE[index - 1][3] != event or index == 4
            if fresh:
                frame.pixel(LEG - 1, 11, C.YELLOW)
            frame.small_text("BONK", LEG - 17, 0, C.YELLOW)
            if event == 'bonk!':
                frame.text("!", rx - 8, 3, C.RED)
            if event == 'bonk#':
                frame.text("#@%!", rx - 30, 3, C.RED)
        elif event == 'turn':
            # A little rotate arrow over the roomba.
            ax = rx - 6
            frame.hline(ax, 3, 3, C.CYAN)
            frame.pixel(ax + 3, 4, C.CYAN)
            frame.pixel(ax + 3, 5, C.CYAN)
            frame.hline(ax, 6, 3, C.CYAN)
            frame.pixel(ax + 1, 5, C.CYAN)
            frame.pixel(ax + 1, 7, C.CYAN)
        elif event == 'sulk':
            frame.text("...", rx - 18, 3, C.RED)
        elif event == 'free':
            frame.small_text("FREE!", rx + 1, 0, C.GREEN)
        elif event == 'wall':
            first = TIMELINE[index - 1][3] != 'wall'
            if first:
                for px, py in ((3, 3), (4, 2), (5, 4), (6, 3), (2, 5)):
                    frame.pixel(px, py, C.WHITE)
            frame.text("BONK!", 24 if first else 25, 2, C.YELLOW,
                       proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/roomba_stuck.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
