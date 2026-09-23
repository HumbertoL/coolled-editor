#!/usr/bin/env python3
"""
washing_machine -- a front-loader, through the porthole.

A white box with a control panel: a dial whose pointer steps round, a drawer,
and a light that blinks while it runs. In the porthole a red sock, a blue
shirt, a yellow towel and a magenta something tumble slowly through cyan
water, bubbles rising past them, the drum changing direction halfway. Then
the water drains and it winds up to SPIN: the clothes pin to the drum wall
and smear into a rotating ring of colour -- each item drawn as an arc whose
length grows with the speed, a motion blur in 3 bits -- while the whole
machine walks a pixel side to side. The readout on the right climbs from 45
to 1400 RPM. It slows, refills, and goes back to washing for the loop.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 1400

BOX_X, BOX_W = 14, 20
INNER_R, RING_R = 4.2, 5.3

# Phases (frame indexes).
REVERSE_AT = 14   # wash drum changes direction
SPIN_UP = 26      # drain and wind up
SPIN_FULL = 33    # full speed
SPIN_DOWN = 45    # brake
REFILL_AT = 48    # water comes back for the loop

# (colour, pixel offsets, starting angle, radius)
CLOTHES = [
    (C.RED, [(0, 0), (0, 1), (1, 1)], 0.3, 2.6),              # sock
    (C.BLUE, [(-1, 0), (0, 0), (1, 0), (0, 1)], 2.0, 2.2),    # shirt
    (C.YELLOW, [(0, 0), (1, 0), (0, 1), (1, 1)], 3.7, 2.8),   # towel
    (C.MAGENTA, [(0, 0), (1, 0)], 5.0, 1.4),                  # pants
]


def omega(index):
    """Drum speed in radians per frame (signed)."""
    if index < REVERSE_AT:
        return 0.45
    if index < SPIN_UP:
        return -0.45
    if index < SPIN_FULL:
        t = (index - SPIN_UP) / (SPIN_FULL - SPIN_UP)
        return 0.45 + t * 2.3
    if index < SPIN_DOWN:
        return 2.75
    t = min(1.0, (index - SPIN_DOWN) / (FRAMES - SPIN_DOWN - 1))
    return 2.75 - t * 2.3


def rpm(index):
    if index < SPIN_UP:
        return 45
    if index < SPIN_FULL:
        t = (index - SPIN_UP) / (SPIN_FULL - SPIN_UP)
        return max(45, int(round((45 + t * t * 1355) / 10) * 10))
    if index < SPIN_DOWN:
        return 1400
    t = min(1.0, (index - SPIN_DOWN) / (FRAMES - SPIN_DOWN - 1))
    return max(45, int(round((1400 - (1 - (1 - t) ** 2) * 1355) / 10) * 10))


def water_level(index):
    """Row of the water surface inside the porthole (16 = empty)."""
    wash = 9.5
    if index < SPIN_UP:
        return wash
    if index < SPIN_FULL:
        return wash + (index - SPIN_UP + 1) * 1.0
    if index < REFILL_AT:
        return 16
    t = (index - REFILL_AT + 1) / (FRAMES - REFILL_AT)
    return 16 - t * (16 - wash)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    angle = 0.0
    bubbles = []
    for index in range(FRAMES):
        frame = anim.frame()
        speed = omega(index)
        angle += speed
        spinning = SPIN_UP + 4 <= index < SPIN_DOWN + 2
        dx = (0, 1, 0, -1)[index % 4] if SPIN_FULL <= index < SPIN_DOWN else 0
        x0 = BOX_X + dx
        cx, cy = x0 + (BOX_W - 1) / 2, 9.5

        # Cabinet.
        frame.rect(x0, 0, BOX_W, 16, C.WHITE)
        # Control panel: dial, drawer, blinking light.
        dial_x = x0 + 3
        for px, py in ((0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)):
            frame.pixel(dial_x - 1 + px, 1 + py, C.CYAN)
        step = min(7, index * 8 // FRAMES)
        pointer = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)][step]
        frame.pixel(dial_x + pointer[0], 2 + pointer[1], C.WHITE)
        frame.hline(x0 + 7, 2, 5, C.WHITE)  # detergent drawer
        light = C.RED if spinning else C.GREEN
        if index % 4 < 2:
            frame.pixel(x0 + BOX_W - 3, 2, light)
        # Feet.
        frame.pixel(x0 + 2, 15, C.BLACK)
        frame.pixel(x0 + BOX_W - 3, 15, C.BLACK)

        # Porthole ring and water.
        level = water_level(index)
        slosh = math.sin(index * 0.9) * 0.6 if index < SPIN_UP else 0
        for py in range(4, 16):
            for px in range(x0 + 1, x0 + BOX_W - 1):
                d = math.hypot(px - cx, py - cy)
                if INNER_R <= d < RING_R:
                    frame.pixel(px, py, C.WHITE)
                elif d < INNER_R and py >= level + slosh * (px - cx) / 3:
                    frame.pixel(px, py, C.CYAN)

        # Clothes.
        for colour, shape, start, radius in CLOTHES:
            theta = start + angle
            if abs(speed) > 1.0 or spinning:
                # Pinned to the wall and smeared along it.
                arc = min(1.2, 0.12 + abs(speed) * 0.4)
                steps = 12
                for k in range(steps + 1):
                    a = theta - arc * k / steps
                    for r in (3.0, 3.6):
                        px = round(cx + r * math.cos(a))
                        py = round(cy + r * math.sin(a))
                        if math.hypot(px - cx, py - cy) < INNER_R:
                            frame.pixel(px, py, colour)
            else:
                # Tumbling: carried round, and dropping as they reach the top.
                fall = 0.8 * math.sin(theta * 2 + start)
                bx = round(cx + (radius + fall) * math.cos(theta) - 0.5)
                by = round(cy + (radius + fall) * math.sin(theta) - 0.5)
                for ox, oy in shape:
                    px, py = bx + ox, by + oy
                    if math.hypot(px - cx, py - cy) < INNER_R - 0.1:
                        frame.pixel(px, py, colour)

        # Bubbles rising through the water.
        if level < 14 and not spinning:
            for _ in range(2):
                bubbles.append([rng.uniform(-3, 3), 13.0])
        next_bubbles = []
        for b in bubbles:
            b[1] -= 1.2
            px, py = round(cx + b[0]), round(b[1])
            if py >= level and math.hypot(px - cx, py - cy) < INNER_R:
                if frame.get(px, py) == C.CYAN:
                    frame.pixel(px, py, C.WHITE)
                next_bubbles.append(b)
        bubbles = next_bubbles

        # Readout.
        text_x = 42
        if index < SPIN_UP:
            frame.text("WASH", text_x, 0, C.CYAN)
        elif index < SPIN_DOWN:
            colour = C.WHITE if index >= SPIN_FULL and index % 2 else C.YELLOW
            frame.text("SPIN", text_x + dx, 0, colour)
            if index >= SPIN_FULL:
                for k in range(3):
                    frame.hline(text_x + 26 + dx + (k == 1), 1 + k * 2, 4 - (k == 1), C.YELLOW)
        else:
            frame.text("RINSE" if index >= REFILL_AT else "SPIN", text_x, 0, C.CYAN if index >= REFILL_AT else C.YELLOW)
        frame.text(f"{rpm(index)} RPM", text_x, 9, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/washing_machine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
