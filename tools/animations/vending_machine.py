#!/usr/bin/env python3
"""
Vending machine -- B4 hangs on the coil, and somebody else gets it.

A red vending machine on the left: a cyan-framed window with three coil
shelves of coloured snacks, a display, a keypad and a coin slot. Someone in
a cyan shirt walks in from the right, drops a coin (CLINK), presses B4 (the
display shows B4), the coil turns, and the yellow-and-red bag creeps to the
edge of the shelf... and hangs there. A held beat and a "..." over their
head. They shake the machine (it jitters), nothing. They kick it -- THUD,
the machine jumps -- nothing. They droop and trudge off right, out of the
panel. The instant they are gone the bag drops: THUNK. A beat. A second
person in a green cap strolls in, scoops the bag out of the tray, NICE, and
turns to go -- as the first one's head peeks back in from the right edge.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130

STAND_X = 33                      # where a person stands at the machine
SHELF_Y = (4, 7, 10)              # coil rows inside the window
SHELF_X0, SHELF_LEN = 5, 12       # shelves run x 5..16; the drop gap is 17..18
SNACK_X = (5, 9, 13)
SNACKS = [
    (C.GREEN, C.MAGENTA, C.GREEN),
    (C.MAGENTA, C.GREEN, None),              # B4 is drawn separately
    (C.GREEN, C.MAGENTA, C.GREEN),
]
BAG_X = 13
BAG_Y = SHELF_Y[1] - 2            # the chosen bag sits on shelf B

# Timeline.
ARRIVE = 6                        # first person reaches the machine
COIN = range(6, 8)
CLINK = range(6, 11)
PRESS = range(8, 11)
COIL = range(11, 15)              # coil turns, bag creeps: x 14 -> 16, then tilts
HANG_FROM = 15
DOTS = range(16, 21)
SHAKE = range(21, 25)
KICK = range(25, 27)
THUD = range(25, 30)
DROOP = range(29, 32)
LEAVE = range(32, 39)
DROP = 38                         # bag falls the frame after they are gone
THUNK = range(39, 44)
ENTER_2 = range(41, 48)
PICK = 48
NICE = range(48, 53)
PEEK = range(50, 53)


def snack(frame, x, y, color, chosen=False):
    if chosen:
        frame.rect(x, y, 2, 2, C.YELLOW, fill=True)
        frame.pixel(x + 1, y, C.RED)                    # the label
    else:
        frame.rect(x, y, 2, 2, color, fill=True)


def draw_bag(frame, state, index, dx=0, dy=0):
    """The B4 bag: ``state`` is an x on the shelf, 'hang', 'fall', 'tray'."""
    if state == "hang":
        # Tipped over the shelf edge, half in the void.
        for x, y, c in ((16, 5, C.YELLOW), (17, 5, C.RED), (17, 6, C.YELLOW), (18, 6, C.YELLOW)):
            frame.pixel(x + dx, y + dy, c)
    elif state == "fall":
        snack(frame, 17 + dx, 8 + dy, None, chosen=True)
    elif state == "tray":
        snack(frame, 17 + dx, 12 + dy, None, chosen=True)
    elif state is not None:
        snack(frame, state + dx, BAG_Y + dy, None, chosen=True)


def draw_machine(frame, index, display, coil_phase, bag, dx=0, dy=0):
    frame.rect(2 + dx, 0 + dy, 28, 16, C.RED)
    frame.rect(4 + dx, 1 + dy, 16, 11, C.CYAN)
    # Coil shelves: dotted blue lines; shelf B lights white and its dots
    # step along while the coil turns.
    for row, y in enumerate(SHELF_Y):
        turning = row == 1 and coil_phase is not None
        for k in range(SHELF_LEN):
            if turning:
                color = C.WHITE if (k + coil_phase) % 2 == 0 else C.BLUE
            else:
                color = C.BLUE if k % 2 == 0 else C.BLACK
            frame.pixel(SHELF_X0 + k + dx, y + dy, color)
        for x, color in zip(SNACK_X, SNACKS[row]):
            if color is not None:
                snack(frame, x + dx, y - 2 + dy, color)
    draw_bag(frame, bag, index, dx, dy)
    # Side panel: display, keypad, coin slot.
    if display:
        frame.small_text(display, 21 + dx, 1 + dy, C.GREEN)
    else:
        frame.hline(21 + dx, 3 + dy, 7, C.BLUE)
    for y in (7, 9):
        for x in (22, 24, 26, 28):
            frame.pixel(x + dx, y + dy, C.WHITE)
    frame.vline(27 + dx, 11 + dy, 2, C.YELLOW)
    # Tray at the bottom of the window.
    frame.hline(5 + dx, 14 + dy, 14, C.WHITE)
    frame.pixel(4 + dx, 13 + dy, C.WHITE)
    frame.pixel(19 + dx, 13 + dy, C.WHITE)


def person(frame, cx, d, pose="stand", phase=0, shirt=C.CYAN, cap=None,
           droop=False, bag=False):
    """A little figure centred on cx, feet on row 14, facing d (+1 right)."""
    top = 5 if droop else 4
    frame.rect(cx - 1, top, 3, 3, C.YELLOW, fill=True)
    frame.pixel(cx + d, top + 1, C.BLACK)
    if cap is not None:
        frame.hline(cx - 1 - (d > 0), top - 1, 4, cap)
        frame.hline(cx - 1, top - 2, 3, cap)
    frame.rect(cx - 1, 7, 3, 4, shirt, fill=True)
    if pose == "walk":
        if not droop:
            frame.pixel(cx + 2 * d, 8 - (phase % 2), shirt)
            frame.pixel(cx - 2 * d, 8 + (phase % 2), shirt)
        else:
            frame.vline(cx + 2 * d, 8, 3, shirt)
        if phase % 2 == 0:
            frame.vline(cx - 1, 11, 4, C.BLUE)
            frame.vline(cx + 1, 11, 4, C.BLUE)
        else:
            frame.vline(cx, 11, 2, C.BLUE)
            frame.line(cx, 12, cx - 2, 14, C.BLUE)
            frame.line(cx, 12, cx + 2, 14, C.BLUE)
        return
    # Standing legs for every other pose.
    if pose == "kick":
        frame.vline(cx - d, 11, 4, C.BLUE)
        frame.line(cx + d, 11, cx + 4 * d, 12, C.BLUE)
        frame.pixel(cx + 5 * d, 12, C.BLUE)
    else:
        frame.vline(cx - 1, 11, 4, C.BLUE)
        frame.vline(cx + 1, 11, 4, C.BLUE)
    if pose == "stand":
        frame.vline(cx - 2, 8, 3, shirt)
        frame.vline(cx + 2, 8, 3, shirt)
    elif pose == "coin":
        frame.vline(cx - 2 * d, 8, 3, shirt)
        frame.line(cx + 2 * d, 8, cx + 4 * d, 10, shirt)
    elif pose == "press":
        frame.vline(cx - 2 * d, 8, 3, shirt)
        frame.pixel(cx + 2 * d, 8, shirt)
        frame.hline(min(cx + 3 * d, cx + 4 * d), 7, 2, shirt)
    elif pose == "shake":
        frame.hline(min(cx + 2 * d, cx + 4 * d), 7 + phase % 2, 3, shirt)
        frame.hline(min(cx + 2 * d, cx + 4 * d), 9 + phase % 2, 3, shirt)
    elif pose == "kick":
        frame.line(cx - 2 * d, 8, cx - 3 * d, 6, shirt)
        frame.pixel(cx + 2 * d, 8, shirt)
    elif pose == "droop":
        frame.vline(cx - 2, 9, 2, shirt)
        frame.vline(cx + 2, 9, 2, shirt)
    elif pose == "pick":
        frame.vline(cx - 2 * d, 8, 3, shirt)
        frame.line(cx + 2 * d, 8, cx + 4 * d, 12, shirt)
    if bag:
        snack(frame, cx + 3 * d - (d < 0), 9, None, chosen=True)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()

        # Machine state.
        display = "B4" if PRESS.start <= i < DROP else None
        coil_phase = (i - COIL.start) % 2 if i in COIL else None
        if i < COIL.start:
            bag = BAG_X
        elif i in COIL:
            bag = [14, 15, 16, "hang"][i - COIL.start]
        elif i < DROP:
            bag = "hang"
        elif i == DROP:
            bag = "fall"
        else:
            bag = "tray" if i < PICK else None
        dx = dy = 0
        if i in SHAKE:
            dx = -1 if (i - SHAKE.start) % 2 == 0 else 1
        if i == KICK.start:
            dy = -1
        draw_machine(f, i, display, coil_phase, bag, dx, dy)

        # First person.
        if i < ARRIVE:
            cx = max(STAND_X, 93 - i * 10)
            person(f, cx, -1, "walk", phase=i)
        elif i in COIN:
            person(f, STAND_X, -1, "coin")
            if i == COIN.start:
                f.pixel(28, 11, C.YELLOW)
        elif i in PRESS:
            person(f, STAND_X, -1, "press")
        elif i < DOTS.stop:
            person(f, STAND_X, -1, "stand")
        elif i in SHAKE:
            person(f, STAND_X + dx, -1, "shake", phase=i)
        elif i in KICK:
            person(f, STAND_X, -1, "kick")
        elif i < DROOP.start:
            person(f, STAND_X, -1, "stand")
        elif i in DROOP:
            person(f, STAND_X, -1, "droop", droop=True)
        elif i in LEAVE:
            cx = STAND_X + (i - LEAVE.start + 1) * 10
            person(f, cx, 1, "walk", phase=i, droop=True)
        if i in PEEK:
            # The first person's head, peeking back round the right edge.
            f.rect(93, 4, 3, 3, C.YELLOW, fill=True)
            f.pixel(93, 5, C.BLACK)
            f.rect(94, 7, 2, 2, C.CYAN, fill=True)

        # Second person.
        if i in ENTER_2:
            cx = max(STAND_X, 93 - (i - ENTER_2.start) * 10)
            person(f, cx, -1, "walk", phase=i, shirt=C.MAGENTA, cap=C.GREEN)
        elif i == PICK:
            person(f, STAND_X, -1, "pick", shirt=C.MAGENTA, cap=C.GREEN)
        elif i > PICK:
            person(f, STAND_X, 1, "stand", shirt=C.MAGENTA, cap=C.GREEN, bag=True)

        # Words.
        if i in CLINK:
            f.small_text("CLINK", 38, 1, C.YELLOW)
        if i in DOTS:
            f.small_text("...", 37, 1, C.WHITE)
        if i in THUD:
            f.text("THUD", 38 + (i == THUD.start), 0, C.WHITE if i % 2 else C.RED)
        if i in THUNK:
            f.text("THUNK", 33 + (i == THUNK.start), 1, C.YELLOW if i % 2 else C.WHITE)
        if i in NICE:
            f.text("NICE", 40, 0, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/vending_machine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
