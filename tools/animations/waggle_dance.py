#!/usr/bin/env python3
"""
Waggle Dance -- a honeybee giving directions, in the only language she has.

On the right, a faint blue honeycomb, and on it a forager, striped yellow and
black. She runs straight across the comb, shaking side to side with her wings
buzzing, then folds them and walks back round to the start -- right-hand
loop, waggle again, left-hand loop -- the figure eight bees have danced since
long before von Frisch decoded it. On the comb "up" stands for the sun, so the
angle of her run from vertical is the angle of the food from the sun. The
left of the panel spells that out: a hive, the sun overhead, a flower seventy
degrees round, and a dotted line to it that lights up and marches while she
waggles.

The bee is a hand-drawn sprite turned in quarter turns only -- at twelve
pixels long, any finer rotation smears her stripes into noise.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
THETA = math.radians(70)  # waggle run, clockwise from straight up
DIR = (math.sin(THETA), -math.cos(THETA))
PERP = (math.cos(THETA), math.sin(THETA))  # right of the run direction
CENTRE = (64.0, 7.5)
HALF_RUN = 8.0
BULGE = 3.5
RUN_FRAMES = 13
LOOP_FRAMES = 13
COMB_X = 31

HIVE = (4, 13)
SUN = (4, 2)
FLOWER = (HIVE[0] + 21 * DIR[0], HIVE[1] + 21 * DIR[1])


def comb_walls():
    """Voronoi edges of a flat-topped hex lattice: pixels nearly equidistant
    from their two nearest cell centres."""
    s = 4.2
    centres = []
    for col in range(-2, 40):
        for row in range(-2, 8):
            cx = COMB_X + col * 1.5 * s
            cy = row * math.sqrt(3) * s + (col % 2) * math.sqrt(3) * s / 2
            centres.append((cx, cy))
    walls = set()
    for x in range(COMB_X, 96):
        for y in range(16):
            d = sorted(math.hypot(x - cx, y - cy) for cx, cy in centres)
            if d[1] - d[0] < 0.75:
                walls.add((x, y))
    return walls


# Facing right. W is wing, Y body, "." transparent, "k" a black band that
# is drawn (so the stripes cut the comb behind her too).
BEE = [
    "......WW....",
    ".....WWW....",
    "..YkYYkYYY..",
    ".YYkYYkYYYYY",
    ".YYkYYkYYYYY",
    "..YkYYkYYY..",
    ".....WWW....",
    "......WW....",
]


def oriented(heading):
    """The sprite turned to the nearest of four headings: right, down,
    left, up. Rotating a 12-pixel bee by arbitrary angles smears the
    stripes; quarter turns keep every pixel."""
    hx, hy = heading
    rows = BEE
    if abs(hx) >= abs(hy):
        return rows if hx > 0 else [r[::-1] for r in rows]
    # Transpose so the head points down, flip for up.
    cols = ["".join(r[c] for r in rows) for c in range(len(rows[0]))]
    return cols if hy > 0 else cols[::-1]


def draw_bee(frame, x, y, heading, wing_color):
    sprite = oriented(heading)
    h, w = len(sprite), len(sprite[0])
    left, top = round(x - w / 2), round(y - h / 2)
    for r, line in enumerate(sprite):
        for c, ch in enumerate(line):
            gx, gy = left + c, top + r
            if gx < COMB_X:
                continue
            if ch == "Y":
                frame.pixel(gx, gy, C.YELLOW)
            elif ch == "k":
                frame.pixel(gx, gy, C.BLACK)
            elif ch == "W" and wing_color is not None:
                frame.pixel(gx, gy, wing_color)


def pose(index):
    """(x, y, heading, waggling) for this frame of the figure eight."""
    # One figure eight fills the loop exactly: the second return is a frame
    # longer, so 53 frames close without a repeated pose.
    cycle = index
    if cycle < RUN_FRAMES or RUN_FRAMES + LOOP_FRAMES <= cycle < 2 * RUN_FRAMES + LOOP_FRAMES:
        t = (cycle % (RUN_FRAMES + LOOP_FRAMES)) / (RUN_FRAMES - 1)
        s = -HALF_RUN + 2 * HALF_RUN * t
        shake = 0.8 if index % 2 == 0 else -0.8
        x = CENTRE[0] + s * DIR[0] + shake * PERP[0]
        y = CENTRE[1] + s * DIR[1] + shake * PERP[1]
        return x, y, DIR, True
    # Return loop: half an ellipse from the run's end back to its start,
    # bulging right on the first loop and left on the second.
    first = cycle < RUN_FRAMES + LOOP_FRAMES
    length = LOOP_FRAMES if first else FRAMES - 2 * RUN_FRAMES - LOOP_FRAMES
    k = (cycle - (RUN_FRAMES if first else 2 * RUN_FRAMES + LOOP_FRAMES) + 1) / (length + 1)
    side = 1 if first else -1
    phi = math.pi * k
    s = HALF_RUN * math.cos(phi)
    b = side * BULGE * math.sin(phi)
    x = CENTRE[0] + s * DIR[0] + b * PERP[0]
    y = CENTRE[1] + s * DIR[1] + b * PERP[1]
    ds = -HALF_RUN * math.sin(phi)
    db = side * BULGE * math.cos(phi)
    hx = ds * DIR[0] + db * PERP[0]
    hy = ds * DIR[1] + db * PERP[1]
    n = math.hypot(hx, hy) or 1.0
    return x, y, (hx / n, hy / n), False


def draw_map(frame, index, waggling):
    # Hive: a little skep.
    hx, hy = HIVE
    frame.hline(hx - 1, hy - 1, 3, C.YELLOW)
    frame.hline(hx - 2, hy, 5, C.YELLOW)
    frame.hline(hx - 2, hy + 1, 5, C.YELLOW)
    frame.pixel(hx, hy + 1, C.BLACK)
    # Sun, straight overhead, with rays that turn.
    sx, sy = SUN
    frame.rect(sx - 1, sy - 1, 3, 3, C.YELLOW, fill=True)
    rays = [(0, -2), (2, 0), (-2, 0), (0, 2)] if index % 4 < 2 else [(2, -2), (2, 2), (-2, 2), (-2, -2)]
    for dx, dy in rays:
        frame.pixel(sx + dx, sy + dy, C.YELLOW)
    # Reference line, hive to sun: faint.
    for y in range(sy + 4, hy - 2, 2):
        frame.pixel(sx, y, C.BLUE)
    # Flower.
    fx, fy = round(FLOWER[0]), round(FLOWER[1])
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        frame.pixel(fx + dx, fy + dy, C.MAGENTA)
    frame.pixel(fx, fy, C.YELLOW)
    frame.vline(fx, fy + 2, 3, C.GREEN)
    frame.pixel(fx + 1, fy + 3, C.GREEN)
    # The line the dance encodes: marching dots while she waggles.
    length = math.hypot(FLOWER[0] - hx, FLOWER[1] - hy)
    offset = (index % 3) if waggling else 0
    d = 3 + offset
    while d < length - 2:
        x = hx + d * DIR[0]
        y = hy - 1 + d * DIR[1]
        frame.pixel(round(x), round(y), C.WHITE if waggling else C.BLUE)
        d += 3


def build():
    walls = comb_walls()
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for x, y in walls:
            if (x + y) % 2 == 0:
                frame.pixel(x, y, C.BLUE)
        x, y, heading, waggling = pose(index)
        wings = (C.WHITE if index % 2 == 0 else C.CYAN) if waggling else None
        draw_bee(frame, x, y, heading, wings)
        draw_map(frame, index, waggling)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/waggle_dance.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
