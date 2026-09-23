#!/usr/bin/env python3
"""
Mitosis -- one cell becomes two, in five phases and fifty-three frames.

A round green cell, a blue nucleus, red and yellow chromatin drifting inside
it. The chromatin condenses into four X-shaped chromosomes, the nuclear
envelope breaks into dots and vanishes, and the two white centrosomes
slide to opposite poles. Blue spindle fibres reach in and haul the
chromosomes onto the metaphase plate down the middle of the cell, where they
wait. Then the sisters let go: each X splits into a pair of chevrons, dragged
centromere-first toward the poles, and the cell stretches after them. The
membrane pinches in at the waist, new envelopes close round each set of
chromosomes, and two daughter cells drift apart.

The membrane is a metaball field of two points, one per daughter: sitting on
top of each other they are one round cell, and as they separate the outline
narrows into a peanut and snaps in two on its own -- no furrow is drawn.
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
SEED = 1882  # Flemming names it
CX, CY = 47.5, 7.5
STRENGTH = 24.5  # per lobe: two stacked lobes give a radius of 7 rows
X_STRETCH = 1.35
MEMBRANE = C.GREEN
ENVELOPE = C.BLUE
FIBRE = C.BLUE
POLE = C.WHITE

# Four chromosomes: colour, where they condense inside the nucleus, and
# their row on the metaphase plate.
CHROMOSOMES = [
    (C.RED, (-2, -2), 2),
    (C.YELLOW, (2, -1), 5),
    (C.YELLOW, (-2, 2), 8),
    (C.RED, (2, 2), 11),
]

# Timeline (frame numbers).
CONDENSE = (6, 12)  # chromatin -> chromosomes
ENVELOPE_GONE = 15
POLES_OUT = (6, 16)
TO_PLATE = (15, 21)
ANAPHASE = (27, 34)
CYTOKINESIS = (34, 44)
REFORM = 38  # daughter nuclei appear


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def progress(index, span):
    a, b = span
    return ease((index - a) / (b - a))


def separation(index):
    """Half-distance between the two lobes of the membrane."""
    return 6 * progress(index, ANAPHASE) + 10 * progress(index, CYTOKINESIS)


def chromatid_reach(split, d):
    """How far each chromatid has been hauled from the plate."""
    return 1 + split * (d + 1.5)


def field(x, y, d):
    total = 0.0
    for sx in (-1, 1):
        dx = (x - (CX + sx * d)) / X_STRETCH
        dy = y - CY
        total += STRENGTH / (dx * dx + dy * dy + 0.01)
    return total


def draw_membrane(frame, d):
    inside = {}
    for y in range(16):
        for x in range(96):
            inside[(x, y)] = field(x, y, d) >= 1.0
    for (x, y), is_in in inside.items():
        if not is_in:
            continue
        if any(not inside.get((x + ox, y + oy), False) for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            frame.pixel(x, y, MEMBRANE)


def draw_circle(frame, cx, cy, r, color, dotted=False):
    steps = 28
    for k in range(steps):
        if dotted and k % 2:
            continue
        a = 2 * math.pi * k / steps
        frame.pixel(round(cx + r * math.cos(a)), round(cy + r * 0.9 * math.sin(a)), color)


def dotted_line(frame, x0, y0, x1, y1, color):
    """Every other pixel of a line: a fibre, not a wall."""
    n = max(1, round(max(abs(x1 - x0), abs(y1 - y0))))
    for k in range(0, n, 2):
        t = k / n
        frame.pixel(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), color)


X_SHAPE = [(-1, 0), (1, 0), (0, 1), (-1, 2), (1, 2)]
LEFT_CHEVRON = [(0, 0), (-1, 1), (0, 2)]  # "<", centromere leading left
RIGHT_CHEVRON = [(0, 0), (1, 1), (0, 2)]


def build():
    rng = random.Random(SEED)
    # Chromatin specks: several per chromosome, loose in the nucleus.
    specks = []
    for n, (color, _home, _row) in enumerate(CHROMOSOMES):
        for _ in range(4):
            specks.append((n, color, rng.uniform(-3.2, 3.2), rng.uniform(-2.6, 2.6)))

    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        d = separation(index)
        draw_membrane(frame, d)

        condense = progress(index, CONDENSE)
        to_plate = progress(index, TO_PLATE)
        split = progress(index, ANAPHASE)
        poles_out = progress(index, POLES_OUT)

        # Pole positions: centrosomes start together above the nucleus,
        # part to either end, then ride outward with the lobes.
        pole_dx = 1 + poles_out * 6 + d * 0.9
        pole_y = CY - 5 * (1 - poles_out)
        poles = [(CX - pole_dx, pole_y), (CX + pole_dx, pole_y)]
        spindle = TO_PLATE[0] <= index < CYTOKINESIS[0] + 4

        # Where each chromosome (or each chromatid pair) sits.
        centres = []
        for color, (hx, hy), row in CHROMOSOMES:
            nx, ny = CX + hx, CY - 1 + hy
            px, py = CX, row
            centres.append((color, nx + (px - nx) * to_plate, ny + (py - ny) * to_plate))

        if spindle:
            for color, x, y in centres:
                reach = chromatid_reach(split, d)
                for side, (px, py) in zip((-1, 1), poles):
                    tip = (x + side * (reach + 1), y + 1)
                    dotted_line(frame, px, py, tip[0], tip[1], FIBRE)

        if index < CONDENSE[1]:
            for n, color, sx, sy in specks:
                _c, hx, hy = centres[n]
                jitter = (index + n) % 2 * 0.4
                x = CX + sx * (1 - condense) + (hx - CX) * condense + jitter
                y = CY + sy * (1 - condense) + (hy + 1 - CY) * condense
                frame.pixel(round(x), round(y), color)
        elif index < ANAPHASE[0]:
            for color, x, y in centres:
                for ox, oy in X_SHAPE:
                    frame.pixel(round(x) + ox, round(y) + oy, color)
        elif index < REFORM + 6:
            # Chromatids drag toward the poles, then gather into the new nuclei.
            gather = progress(index, (REFORM - 2, REFORM + 5))
            for color, x, y in centres:
                reach = chromatid_reach(split, d)
                for side, shape in ((-1, LEFT_CHEVRON), (1, RIGHT_CHEVRON)):
                    lobe_x = CX + side * d
                    cx = x + side * reach
                    # Bunch up as they go: the daughters are shorter.
                    cy = CY - 1 + (y - (CY - 1)) * (1 - 0.45 * split)
                    cx += (lobe_x - cx) * gather
                    cy += (CY - 1 + (y - (CY - 1)) * 0.3 - cy) * gather
                    for ox, oy in shape:
                        frame.pixel(round(cx) + ox, round(cy) + oy, color)
        else:
            # Decondensed again: specks in each daughter nucleus.
            for side in (-1, 1):
                lobe_x = CX + side * d
                for n, color, sx, sy in specks:
                    jitter = (index + n) % 2 * 0.4
                    frame.pixel(round(lobe_x + sx * 0.6 + jitter), round(CY + sy * 0.8), color)

        # Nuclear envelope: whole, then dotted, then gone; reforming in each
        # daughter at the end.
        if index < ENVELOPE_GONE:
            draw_circle(frame, CX, CY, 4.6, ENVELOPE, dotted=index >= CONDENSE[1] - 1)
        if index >= REFORM:
            for side in (-1, 1):
                draw_circle(frame, CX + side * d, CY, 3.2, ENVELOPE, dotted=index < REFORM + 3)

        if index < CYTOKINESIS[0] + 6:
            for px, py in poles:
                frame.pixel(round(px), round(py), POLE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/mitosis.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
