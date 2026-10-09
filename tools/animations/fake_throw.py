#!/usr/bin/env python3
"""
Fake throw -- the dog saw that.

A park: a green lawn, a person on the left holding a red ball, a yellow dog
on the right bouncing on the spot, tail a blur. The person winds up and
swings -- the ball vanishes behind their back -- and the dog ROCKETS off the
right edge in a cloud of dust. A held beat: the person smirks, ball tucked
behind their back. The dog trots back slowly, looks left, looks right (?),
looks at the ground, looks at the hand with the ball... then turns its head
to the viewer, eyes narrowed to slits: I SAW THAT. Sheepish, the person
throws it for real; the ball sails over the dog and bounces off the right
edge. The dog does not move. Button: NOPE.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
GROUND = 15

FUR = C.YELLOW
SKIN = C.WHITE
SHIRT = C.CYAN
TROUSERS = C.BLUE
BALL = C.RED

PERSON_X = 12               # body centre
DOG_X = 66                  # dog's nose column when standing by the person

# Beats (first frame of each).
WIND, SWING, ROCKET, SMIRK, TROT, LOOK_L, LOOK_R, LOOK_DOWN, LOOK_HAND, \
    STARE, SHEEPISH, THROW, FLIGHT, REST = (
        6, 8, 10, 15, 20, 26, 28, 30, 32, 34, 39, 41, 43, 48,
    )
NOPE_FROM = 48

DOG_BODY = [          # cols 2..11 of a dog facing left, rows 4..8
    "..##########.",
    "..##########.",
    "...##....##..",
    "...##....##..",
    "...##....##..",
]
DOG_BODY_STEP = [
    "..##########.",
    "..##########.",
    "...##....##..",
    "..#.#...#.#..",
    ".#...#.#...#.",
]
DOG_RUN = [           # stretched flat out, facing left
    "..#..........",
    ".####........",
    "M####........",
    ".###########.",
    "..##########.",
    ".#.........#.",
    "#...........#",
]
HEAD_SIDE = [         # rows 0..3, cols 0..4; nose on the left
    "..#..",
    ".####",
    "M####",
    ".####",
]
HEAD_DOWN = [         # sniffing the ground
    "..#..",
    ".####",
    ".####",
    "M###.",
]
HEAD_FRONT = [        # facing the viewer, eyes narrowed to slits
    "#.....#",
    "#######",
    "#KK#KK#",
    ".##M##.",
]
TAILS = {
    "up": [(12, 3), (12, 2), (13, 1)],
    "mid": [(12, 3), (13, 3), (14, 3)],
    "down": [(12, 5), (13, 6)],
}
PALETTE = {"#": FUR, "M": C.MAGENTA, "K": C.BLACK}


def art(frame, rows, x, y, facing=1, width=None):
    width = width or max(len(r) for r in rows)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            col = c if facing > 0 else width - 1 - c
            frame.pixel(x + col, y + r, PALETTE[ch])


def draw_dog(frame, x, bottom=14, body="stand", head="left", tails=("mid",),
             eye="left", dy=0):
    """Dog facing left with its nose at column ``x``; feet on ``bottom``."""
    top = bottom - 8 + dy
    if body == "run":
        art(frame, DOG_RUN, x, bottom - 6, facing=-1)
        return
    rows = DOG_BODY_STEP if body == "step" else DOG_BODY
    art(frame, rows, x, top + 4)
    for name in tails:
        for tx, ty in TAILS[name]:
            frame.pixel(x + tx, top + ty, FUR)
    if head == "front":
        art(frame, HEAD_FRONT, x, top)
        return
    if head == "down":
        art(frame, HEAD_DOWN, x, top + 2)
        frame.pixel(x + 1, top + 4, C.BLACK)
        return
    hy = top
    if head == "right":
        art(frame, HEAD_SIDE, x, hy, facing=-1, width=5)
        frame.pixel(x + 3, hy + 2, C.BLACK)
        return
    art(frame, HEAD_SIDE, x, hy)
    if eye == "left":
        frame.pixel(x + 2, hy + 2, C.BLACK)
    elif eye == "low":
        frame.pixel(x + 1, hy + 3, C.BLACK)


def draw_person(frame, cx=PERSON_X, arm="hold", ball=True, face="plain"):
    """Facing the dog (right), feet on row 14."""
    frame.rect(cx - 1, 4, 3, 3, SKIN, fill=True)
    if face == "plain":
        frame.pixel(cx + 1, 5, C.BLACK)
    elif face == "smirk":
        frame.pixel(cx + 1, 5, C.BLACK)
        frame.hline(cx, 6, 2, C.BLACK)
    elif face == "sheepish":
        frame.pixel(cx + 1, 4, C.BLACK)
        frame.pixel(cx + 3, 4, C.CYAN)             # a bead of sweat
    frame.rect(cx - 1, 7, 3, 4, SHIRT, fill=True)
    frame.vline(cx - 1, 11, 4, TROUSERS)
    frame.vline(cx + 1, 11, 4, TROUSERS)
    if arm == "hold":
        frame.vline(cx - 2, 7, 3, SKIN)
        frame.line(cx + 2, 7, cx + 4, 4, SKIN)
        if ball:
            frame.rect(cx + 5, 2, 2, 2, BALL, fill=True)
    elif arm == "back":
        frame.vline(cx + 2, 7, 3, SKIN)
        frame.line(cx - 2, 7, cx - 4, 4, SKIN)
        if ball:
            frame.rect(cx - 6, 2, 2, 2, BALL, fill=True)
    elif arm == "over":
        frame.vline(cx - 2, 7, 3, SKIN)
        frame.line(cx + 2, 7, cx + 1, 2, SKIN)
        if ball:
            frame.rect(cx + 1, 0, 2, 2, BALL, fill=True)
    elif arm == "out":
        frame.vline(cx - 2, 7, 3, SKIN)
        frame.hline(cx + 2, 7, 4, SKIN)
    elif arm == "behind":
        frame.vline(cx + 2, 7, 3, SKIN)
        frame.line(cx - 2, 7, cx - 3, 9, SKIN)
        if ball:
            frame.rect(cx - 5, 8, 2, 2, BALL, fill=True)


def ground(frame):
    frame.hline(0, GROUND, 96, C.GREEN)
    for x in range(1, 96, 9):
        frame.pixel(x + (x * 7) % 4, GROUND - 1, C.GREEN)


def dust(frame, t):
    """A puff where the dog launched, spreading and fading."""
    puffs = {
        0: ([(66, 13), (68, 12), (70, 13), (72, 14), (67, 14)], C.WHITE),
        1: ([(64, 12), (66, 11), (69, 11), (72, 12), (75, 13), (63, 14),
             (70, 14)], C.WHITE),
        2: ([(62, 11), (65, 10), (69, 9), (73, 10), (77, 12), (61, 13),
             (79, 14)], C.CYAN),
        3: ([(60, 10), (64, 9), (70, 8), (76, 9), (81, 12), (59, 13)], C.BLUE),
        4: ([(58, 9), (66, 7), (78, 8), (84, 11)], C.BLUE),
        5: ([(56, 8), (80, 7)], C.BLUE),
    }
    if t in puffs:
        for x, y in puffs[t][0]:
            frame.pixel(x, y, puffs[t][1])


def build():
    anim = Animation(delay=DELAY)
    # Real throw: ball positions by frame, then the bounce off the right edge.
    flight = {43: (22, 3), 44: (46, 0), 45: (70, 0), 46: (94, 4),
              47: (89, 9), 48: (84, 13)}
    for i in range(FRAMES):
        f = anim.frame()
        ground(f)
        wag = ("up", "mid") if i % 2 else ("mid", "down")
        if i < WIND:
            draw_person(f, arm="hold")
            draw_dog(f, DOG_X, tails=wag, dy=-(i % 2))
        elif i < SWING:
            draw_person(f, arm="back")
            draw_dog(f, DOG_X, tails=wag, dy=-(i % 2))
        elif i < ROCKET:
            draw_person(f, arm="over" if i == SWING else "out", ball=False)
            draw_dog(f, DOG_X, tails=("up",), dy=-1)
        elif i < SMIRK:
            t = i - ROCKET
            draw_person(f, arm="out", ball=False)
            dx = DOG_X + (0, 9, 20, 34, 50)[t]
            if dx < 96:
                draw_dog(f, dx, body="run")
                for row in (9, 12):
                    f.hline(dx - 5 - row % 2, row, 3, C.WHITE)
            dust(f, t)
        elif i < TROT:
            t = i - SMIRK
            draw_person(f, arm="behind", face="smirk")
            dust(f, t + 5)
        elif i < LOOK_L:
            t = i - TROT
            draw_person(f, arm="behind", face="smirk")
            dx = (96, 90, 84, 78, 72, DOG_X)[t]
            draw_dog(f, dx, body="step" if t % 2 else "stand", tails=("down",))
        elif i < LOOK_R:
            draw_person(f, arm="behind", face="smirk")
            draw_dog(f, DOG_X, tails=("down",))
            f.small_text("?", DOG_X + 2, 0, C.WHITE)
        elif i < LOOK_DOWN:
            draw_person(f, arm="behind", face="smirk")
            draw_dog(f, DOG_X, head="right", tails=("down",))
            f.small_text("?", DOG_X + 2, 0, C.WHITE)
        elif i < LOOK_HAND:
            draw_person(f, arm="behind", face="smirk")
            draw_dog(f, DOG_X, head="down", eye="low", tails=("down",))
        elif i < STARE:
            draw_person(f, arm="behind", face="smirk")
            draw_dog(f, DOG_X, eye="low", tails=("down",))
            # A dotted sightline from the dog's eye to the ball behind the back.
            for x in range(22, 62, 8):
                f.pixel(x, 8 + (x > 40), C.BLUE)
        elif i < SHEEPISH:
            draw_person(f, arm="behind", face="smirk" if i == STARE else "plain")
            draw_dog(f, DOG_X, head="front", tails=("down",))
            f.small_text("I SAW THAT.", "center", 0, C.WHITE)
        elif i < THROW:
            draw_person(f, arm="behind", face="sheepish")
            draw_dog(f, DOG_X, head="front", tails=("down",))
        elif i < FLIGHT:
            draw_person(f, arm="back" if i == THROW else "over", face="sheepish")
            draw_dog(f, DOG_X, head="front", tails=("down",))
        else:
            draw_person(f, arm="out", ball=False, face="plain")
            draw_dog(f, DOG_X, head="front", tails=("down",))
            bx, by = flight.get(i, (84, 13))
            f.rect(bx, by, 2, 2, BALL, fill=True)
            if i == 46:
                f.small_text("!", 92, 9, C.WHITE)     # the thud off the edge
            if i >= NOPE_FROM:
                f.text("NOPE.", 33, 2, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fake_throw.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
