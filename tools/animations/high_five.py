#!/usr/bin/env python3
"""
High Five -- the whiff, then the slap.

Two yellow hands slide in from opposite edges, sleeves trailing, and wind
up. The left one swings... and the right one yanks away at the last moment:
a whiff into empty air, a lonely ?. They reset, wind up bigger, and this time
it lands. One full-panel white flash, a starburst from the point of contact,
sparks raining out, the whole panel shaking, and HIGH FIVE! bursting out of
the impact letter by letter in strobing colours while the hands bounce back
to the edges.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402
from jtkit.canvas import layout_text  # noqa: E402
from jtkit.font import glyph  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 5

# Left hand, palm towards the centre; column 8 is the edge that meets.
HAND = [
    "....#.#..",
    "..#.#.#..",
    "..#.#.#.#",
    "#.#.#.#.#",
    "#.#.#.#.#",
    "#########",
    ".########",
    ".########",
    "..#######",
    "...######",
    "...#####.",
]
HAND_W = 9
WRIST = (3, 7)  # first and last wrist column
HAND_Y = 1
SLEEVES = (C.GREEN, C.MAGENTA)

CONTACT_X = 47  # left hand's edge; the right hand's edge is at 48
IMPACT = 29
TEXT = "HIGH FIVE!"
TEXT_Y = 5
POP = [C.RED, C.YELLOW, C.WHITE, C.MAGENTA, C.CYAN, C.GREEN]


def draw_hand(canvas, edge_x, y, right, sleeve):
    """Draw a hand whose meeting edge sits at column ``edge_x``."""
    for r, line in enumerate(HAND):
        for c, ch in enumerate(line):
            if ch == "#":
                dx = c - (HAND_W - 1)
                canvas.pixel(edge_x - dx if right else edge_x + dx, y + r, C.YELLOW)
    # Sleeve: runs from the wrist down and outwards off the panel.
    for k in range(1, 12):
        for c in range(WRIST[0] - 1, WRIST[1] + 1):
            dx = c - (HAND_W - 1) - k
            canvas.pixel(edge_x - dx if right else edge_x + dx, y + len(HAND) - 1 + k, sleeve)


def left_edge(t):
    """Column of the left hand's meeting edge at frame t (right hand mirrors it unless it dodges)."""
    rest = 17
    if t < 7:
        return round(-3 + (rest + 3) * (1 - (1 - t / 6) ** 2))
    if t < 10:
        return rest - 2 * (t - 6)  # wind-up
    if t < 14:
        return [22, 34, 47, 55][t - 10]  # the swing, overshooting into thin air
    if t < 19:
        return [53, 52, 52, 52, 51][t - 14]  # hanging there
    if t < 22:
        return [40, 28, 17][t - 19]  # slink back
    if t < 26:
        return 17 - [2, 4, 5, 5][t - 22]  # the bigger wind-up
    if t < IMPACT:
        return [22, 33, 42][t - 26]
    if t < IMPACT + 3:
        return CONTACT_X
    # Bounce back to the edges, and stay out of the text's way.
    u = min(1.0, (t - IMPACT - 3) / 4)
    return round(CONTACT_X + (9 - CONTACT_X) * (1 - (1 - u) ** 2))


def right_edge(t):
    mirrored = 95 - left_edge(t)
    if 10 <= t < 19:
        return [80, 88, 97, 106, 106, 106, 106, 106, 106][t - 10]  # TOO SLOW
    if 19 <= t < 22:
        return [102, 90, 78][t - 19]
    return mirrored


def hand_y(t, side):
    if t >= IMPACT + 7:
        return HAND_Y + ((t // 2 + side) % 2)  # celebrating
    if 22 <= t < 26:
        return HAND_Y + (t % 2 if side else (t + 1) % 2)  # trembling with effort
    if 12 <= t < 19 and side == 0:
        return HAND_Y + (1 if t in (15, 17) else 0)  # awkward little wave
    return HAND_Y


def build():
    rng = random.Random(SEED)
    sparks = []
    positions, width = layout_text(TEXT, proportional=True)
    text_x = (96 - width) // 2
    anim = Animation(delay=DELAY)
    for t in range(FRAMES):
        frame = anim.frame()
        if t == IMPACT:
            frame.fill(C.WHITE)
            for _ in range(28):
                a = rng.uniform(0, 2 * math.pi)
                v = rng.uniform(1.2, 3.5)
                sparks.append([47.5, 5.0, v * math.cos(a) * 1.6, v * math.sin(a) - 1.0, rng.choice(POP)])
            continue

        comp = Canvas()
        payoff = t > IMPACT
        # Speed lines behind a swinging hand.
        lx, rx = left_edge(t), right_edge(t)
        if t in (11, 12, 13, 27, 28):
            for row in (3, 6, 9):
                comp.hline(lx - 16, row, 8, C.WHITE)
        if t in (27, 28):
            for row in (3, 6, 9):
                comp.hline(rx + 9, row, 8, C.WHITE)
        if 14 <= t < 19:
            comp.text("?", lx + 3, 2 + (t % 2), C.CYAN)

        if payoff:
            age = t - IMPACT
            # Starburst from the point of contact.
            if age <= 4:
                for k in range(12):
                    a = k * math.pi / 6 + (0.26 if age % 2 else 0)
                    r0, r1 = 1 + 2 * age, 4 + 4 * age
                    for s2 in range(2 * r0, 2 * r1):
                        s = s2 / 2
                        comp.pixel(47.5 + 2 * s * math.cos(a), 5.5 + s * math.sin(a) * 0.9, C.YELLOW if (k + age) % 2 else C.WHITE)
            # Sparks: fly out, fall, twinkle.
            for sp in sparks:
                sp[0] += sp[2]
                sp[1] += sp[3]
                sp[3] += 0.35
                sp[2] *= 0.9
                if rng.random() < 0.85:
                    comp.pixel(round(sp[0]), round(sp[1]), sp[4] if age % 2 else C.WHITE)
            # HIGH FIVE! bursts out of the contact point, letter by letter.
            if age >= 3:
                for n, (ch, cell_x) in enumerate(positions):
                    if ch == " ":
                        continue
                    u = min(1.0, (age - 3 - abs(n - 4.5) * 0.3) / 3)
                    if u <= 0:
                        continue
                    u = 1 - (1 - u) ** 2
                    gx = round(45 + (text_x + cell_x - 45) * u)
                    color = POP[(n + age) % len(POP)]
                    bitmap = glyph(ch)
                    for row in range(7):
                        for col in range(5):
                            if bitmap[row][col] == "#":
                                comp.pixel(gx + col, TEXT_Y + row, color)

        draw_hand(comp, lx, hand_y(t, 0), False, SLEEVES[0])
        draw_hand(comp, rx, hand_y(t, 1), True, SLEEVES[1])

        if payoff:
            age = t - IMPACT
            amp = 2 if age <= 5 else (1 if age <= 18 else 0)
            sx, sy = rng.randint(-amp, amp), rng.randint(-min(amp, 1), min(amp, 1))
        else:
            sx = sy = 0
        frame.blit(comp, sx, sy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/high_five.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
