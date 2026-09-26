#!/usr/bin/env python3
"""
The Marauder's Map -- "I solemnly swear that I am up to no good."

The oath is written out in small white letters, then yellow ink spreads from
the centre of the parchment, a white wet edge leading it, and draws a floor of
Hogwarts: a long corridor, rooms above and below with doorways, a staircase in
the corner.

Then the footprints. Pairs of tiny prints walk the corridor, left foot and
right foot alternating, the oldest fading as new ones land, each trail with its
name riding above it in a black banner. HARRY (red) creeps in from the left;
SNAPE (green) sweeps in from the right. Harry ducks through a doorway into a
room below just in time and freezes. Snape stops dead at the door -- his banner
blinks SNAPE? -- then turns on his heel and stalks back the way he came. RON
(magenta) scurries up from the left to find Harry, and the two sets of prints
stand together.

Mischief managed: the ink drains back to the centre and vanishes, the words
MISCHIEF MANAGED write themselves across the empty parchment, and then they
too dissolve.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402
from jtkit.canvas import wipe  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16
INK = C.YELLOW
WET = C.WHITE

OATH_END = 6          # frames 0-5: the oath
SPREAD = (6, 12)      # ink spreads over these frames
RECEDE = (45, 48)     # ink drains away
MISCHIEF = 48         # MISCHIEF MANAGED writes in from here
FADE_AFTER = 5        # a footprint lasts this many frames
STRIDE = 4

CORRIDOR_Y = 9        # walkers' centre line in the corridor
ROOM_Y = 13           # centre line inside the lower rooms
DOOR_X = 36           # the doorway Harry ducks through


def build_map():
    """The floor plan as a set of ink pixels."""
    m = Canvas(W, H)
    # Corridor walls, with doorways cut into them.
    m.hline(0, 7, W, INK)
    m.hline(0, 11, W, INK)
    for gap in (6, 24, 66, 86):  # doors up into the top rooms
        for dx in (-1, 0, 1):
            m.pixel(gap + dx, 7, C.BLACK)
    for gap in (DOOR_X, 62):  # doors down into the bottom rooms
        for dx in (-1, 0, 1):
            m.pixel(gap + dx, 11, C.BLACK)
    # Top rooms.
    m.hline(0, 0, 78, INK)
    for x in (0, 16, 34, 56, 77):
        m.vline(x, 0, 7, INK)
    # A long table in the great room, a desk in another.
    m.rect(40, 3, 12, 2, INK)
    m.rect(20, 3, 4, 2, INK)
    # The staircase: stepping up to the right, in the far corner.
    for i in range(6):
        m.hline(78 + i * 3, 6 - i, 3, INK)
        m.vline(78 + i * 3, 6 - i, 1, INK)
    m.vline(95, 0, 7, INK)
    # Bottom rooms.
    m.hline(0, 15, W, INK)
    for x in (0, 52, 74, 95):
        m.vline(x, 11, 5, INK)
    # A few pieces of furniture below.
    m.rect(78, 13, 6, 1, INK)
    m.pixel(88, 13, INK)
    m.pixel(90, 13, INK)
    m.rect(6, 13, 3, 1, INK)
    return m


def ink_radius(x, y):
    return math.hypot(x - 47.5, (y - 7.5) * 2.2)


MAX_R = max(ink_radius(x, y) for x in (0, 95) for y in (0, 15)) + 1


class Walker:
    """A pair of feet following a script of moves; leaves a trail of prints."""

    def __init__(self, name, color, start, x, y, script):
        self.name, self.color = name, color
        self.positions = {}   # frame -> (x, y)
        self.prints = []      # (frame, px, py, horizontal, heel_dx, heel_dy)
        f, step = start, 0
        for move in script:
            if move[0] == "wait":
                for _ in range(move[1]):
                    self.positions[f] = (x, y)
                    f += 1
                continue
            tx, ty = move[1], move[2]
            while (x, y) != (tx, ty):
                dx = max(-STRIDE, min(STRIDE, tx - x))
                dy = max(-STRIDE, min(STRIDE, ty - y)) if dx == 0 else 0
                x, y = x + dx, y + dy
                side = 1 if step % 2 else -1
                if dx:  # walking sideways: feet above/below the line
                    d = 1 if dx > 0 else -1
                    self.prints.append((f, x, y - side * d, True, -d, 0))
                else:  # walking up/down: feet left/right of the line
                    d = 1 if dy > 0 else -1
                    self.prints.append((f, x + side * d, y, False, 0, -d))
                step += 1
                self.positions[f] = (x, y)
                f += 1
        self.end = f
        self.final = (x, y)

    def at(self, frame):
        if frame in self.positions:
            return self.positions[frame]
        return None

    def draw_prints(self, frame, canvas):
        made = [p for p in self.prints if p[0] <= frame]
        still = frame not in self.positions or (
            made and made[-1][0] < frame
        )
        for i, (f, px, py, _h, hx, hy) in enumerate(made):
            age = frame - f
            standing = still and i >= len(made) - 2
            if age >= FADE_AFTER and not standing:
                continue
            canvas.pixel(px, py, self.color)
            canvas.pixel(px + hx, py + hy, self.color)

    def draw_banner(self, frame, canvas, taken, label=None):
        """Draw the name above the feet, sliding aside from banners in ``taken``."""
        pos = self.at(frame)
        if pos is None:
            return
        label = label or self.name
        w = Canvas.small_text_width(label)

        def clamp(x):
            return max(1, min(W - w - 1, x))

        def clear(x):
            return all(x + w + 2 <= a or x >= b + 2 for a, b in taken)

        want = clamp(pos[0] - w // 2)
        options = [want] + [clamp(b + 2) for _, b in taken] + [clamp(a - w - 2) for a, _ in taken]
        options = [x for x in options if clear(x)] or [want]
        bx = min(options, key=lambda x: (abs(x - want), x))
        taken.append((bx, bx + w))
        canvas.rect(bx - 1, 0, w + 2, 7, C.BLACK, fill=True)
        canvas.small_text(label, bx, 1, self.color)


def main():
    anim = Animation(delay=DELAY)
    floor = build_map()

    harry = Walker("HARRY", C.RED, 11, -4, CORRIDOR_Y, [
        ("walk", DOOR_X, CORRIDOR_Y),
        ("walk", DOOR_X, ROOM_Y),
        ("walk", 24, ROOM_Y),
        ("wait", 40),
    ])
    snape = Walker("SNAPE", C.GREEN, 15, 96, CORRIDOR_Y, [
        ("walk", DOOR_X, CORRIDOR_Y),
        ("wait", 6),
        ("walk", 104, CORRIDOR_Y),
    ])
    ron = Walker("RON", C.MAGENTA, 34, -4, CORRIDOR_Y, [
        ("walk", DOOR_X, CORRIDOR_Y),
        ("walk", DOOR_X, ROOM_Y),
        ("wait", 20),
    ])
    snape_pause = [f for f, p in snape.positions.items() if p == (DOOR_X, CORRIDOR_Y)]

    rnd = random.Random(7)
    dissolve_order = list(range(W * H))
    rnd.shuffle(dissolve_order)

    for index in range(FRAMES):
        frame = anim.frame()

        if index < OATH_END:
            edge1 = 15 + index * 34
            edge2 = 13 + (index - 2) * 34
            frame.small_text("I SOLEMNLY SWEAR", "center", 2,
                             wipe(C.WHITE, C.BLACK, edge=edge1))
            frame.small_text("I AM UP TO NO GOOD", "center", 9,
                             wipe(C.WHITE, C.BLACK, edge=edge2))
            continue

        # How much of the map is inked this frame.
        if index < SPREAD[1]:
            t = (index - SPREAD[0] + 1) / (SPREAD[1] - SPREAD[0])
            radius, wet = t * MAX_R, True
        elif index < RECEDE[0]:
            radius, wet = MAX_R + 10, False
        else:
            t = (index - RECEDE[0] + 1) / (RECEDE[1] - RECEDE[0] + 1)
            radius, wet = (1 - t) * MAX_R, True

        if radius > 0:
            for (x, y), color in floor._pixels.items():
                r = ink_radius(x, y)
                if r < radius:
                    frame.pixel(x, y, WET if wet and r > radius - 9 else color)

        if SPREAD[1] - 1 <= index < RECEDE[0]:
            for walker in (harry, snape, ron):
                walker.draw_prints(index, frame)
            # Banners: the one being watched is drawn last, on top.
            taken = []
            harry.draw_banner(index, frame, taken)
            label = "SNAPE?" if index in snape_pause and index % 2 == 0 else None
            snape.draw_banner(index, frame, taken, label)
            ron.draw_banner(index, frame, taken)

        if index >= MISCHIEF:
            text = "MISCHIEF MANAGED"
            x = (W - Canvas.text_width(text, proportional=True)) // 2
            edge = x + (index - MISCHIEF + 1) * 48
            ink = wipe(C.YELLOW, C.BLACK, edge=edge)
            frame.text(text, x, 4, ink, proportional=True)
            gone = {FRAMES - 2: 0.35, FRAMES - 1: 0.75}.get(index, 0)
            if gone:
                for k in dissolve_order[: int(W * H * gone)]:
                    frame.pixel(k % W, k // W, C.BLACK)

    out = Path(__file__).resolve().parents[2] / "src/sample/marauders_map.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
