#!/usr/bin/env python3
"""
Great wave -- a pixel tribute to Hokusai's "The Great Wave off Kanagawa"
(c. 1831, public domain), recomposed for a wide 96x16 strip.

A living tableau, not a story. Everything holds its place and breathes:

- On the left the great wave towers the full height of the panel: a deep
  BLUE body swept with CYAN striations that follow its back and run round
  the curl, its crest rolling over to the right in a thick lip outlined in
  WHITE foam. The wave itself stays poised -- the iconic instant before the
  crash.
- From the lip hang the famous claws: white fingers of foam reaching down
  and out over the trough, each flexing and flickering on its own beat.
  Foam dots spray off the crest, arc right and fall.
- In the distance, framed beneath the curl, a small Mount Fuji: a BLUE cone
  with a WHITE snowcap.
- Three slender YELLOW boats with hunched white rowers ride the trough, the
  first right under the claws, rising and falling on the swells.
- Foreground swells roll right across the bottom rows, BLUE with CYAN faces
  and WHITE foam caps, and a small second wave breaks at the right edge,
  echoing the big one.

Seamless: every motion is a function of 2*pi*frame/FRAMES with an integer
multiplier, and every particle cycle divides FRAMES.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 120
W, H = 96, 16
TAU = 2 * math.pi

SEA = 13.0                     # mean foreground water line

FUJI_X, FUJI_TOP, FUJI_BASE = 58, 6, 13

# Boats: (centre x, length, bob phase, bob cycles per loop)
BOATS = [(34.5, 9, 0.0, 2), (53.5, 7, 2.1, 2), (88.5, 9, 4.0, 2)]


def sea_surface(x, f):
    """Foreground swells rolling right, seamless over the loop."""
    a = TAU * f / FRAMES
    return (SEA + 0.9 * math.sin(TAU * x / 24 - 2 * a)
            + 0.5 * math.sin(TAU * x / 16 - 3 * a + 1.0))


def put(grid, x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        grid[(x, y)] = c


def draw_fuji(grid):
    for y in range(FUJI_TOP, FUJI_BASE + 1):
        half = (y - FUJI_TOP) * 1.25 + 0.6
        lo, hi = round(FUJI_X - half), round(FUJI_X + half)
        if y - FUJI_TOP <= 1:
            # Snowcap fills the top rows.
            for x in range(lo, hi + 1):
                grid[(x, y)] = C.WHITE
        else:
            grid[(lo, y)] = C.BLUE
            grid[(hi, y)] = C.BLUE
            if y - FUJI_TOP == 2:
                # Ragged lower edge of the snow.
                for x in (lo + 1, FUJI_X - 1, FUJI_X + 1, hi - 1):
                    grid[(x, y)] = C.WHITE


def draw_sea(grid, f):
    a = TAU * f / FRAMES
    for x in range(W):
        s = sea_surface(x, f)
        top = int(round(s))
        for y in range(top, H):
            stripe = math.sin(TAU * x / 12 + y * 1.3 - 4 * a)
            grid[(x, y)] = C.CYAN if (y > top and stripe > 0.85) else C.BLUE
        # Swell faces cyan, crests foam-capped white.
        slope = sea_surface(x + 1, f) - s
        if 0 <= top < H:
            if s < SEA - 0.6:
                grid[(x, top)] = C.WHITE
                if s < SEA - 1.0:
                    put(grid, x, top - 1, C.WHITE if (x + f) % 3 else C.CYAN)
            elif slope > 0.15:
                grid[(x, top)] = C.CYAN


def draw_small_wave(grid, f):
    """A little breaker at the right edge, echoing the great wave."""
    a = TAU * f / FRAMES
    peak_x = 75
    h = 4.0 + 0.4 * math.sin(2 * a)
    for x in range(64, 83):
        d = x - peak_x
        top = SEA - h * math.exp(-(d / (5.5 if d < 0 else 2.2)) ** 2)
        for y in range(int(round(top)), H):
            if (x, y) not in grid or grid[(x, y)] == C.BLACK:
                grid[(x, y)] = C.BLUE
            elif y < SEA:
                grid[(x, y)] = C.BLUE
        t = int(round(top))
        if top < SEA - 0.8:
            grid[(x, t)] = C.WHITE if d >= -3 else C.CYAN
    # Tiny curling tip and claws.
    tip = [(peak_x + 1, 8), (peak_x + 2, 9)]
    for p in tip:
        put(grid, *p, C.WHITE)
    if (f // 3) % 2 == 0:
        put(grid, peak_x + 3, 10, C.WHITE)
    else:
        put(grid, peak_x + 2, 10, C.WHITE)


# The great wave as row spans (x0, x1 inclusive): a back rising from the
# left, a thick crest thrown out to the right, and a lip that hooks down and
# back in at its end. The hollow under the crest opens onto the trough.
WAVE_SPANS = {
    0: [(22, 36)],
    1: [(19, 40)],
    2: [(16, 42)],
    3: [(14, 27), (36, 44)],
    4: [(12, 25), (39, 45)],
    5: [(10, 24), (41, 46)],
    6: [(8, 24), (41, 46)],
    7: [(6, 24), (40, 45)],
    8: [(4, 25)],
    9: [(2, 26)],
    10: [(0, 27)],
    11: [(0, 29)],
    12: [(0, 32)],
    13: [(0, 36)],
}

# Claws: talons of foam off the lip. Each starts at (x, y), heads off at
# `deg` (0 = right, 90 = straight down) and bends by `bend` degrees per
# pixel, hooking back toward the face. (x, y, deg, bend, length, cycles, phase)
CLAWS = [
    # Short fringe under the crest.
    (30, 3, 110, 10, 1.2, 4, 0.0), (34, 3, 100, 12, 1.6, 3, 1.3),
    (38, 4, 110, 12, 1.4, 6, 2.6),
    # The big talons at the hooked tip, splayed and curling back in
    # toward the boat beneath.
    (40, 8, 120, 14, 3.0, 3, 0.7), (43, 8, 95, 20, 4.2, 4, 3.1),
    (45, 8, 65, 26, 4.6, 3, 4.4), (47, 6, 30, 28, 4.0, 6, 1.9),
]

# Spray dots: (start x, start y, vx, vy, cycle length in frames, offset)
SPRAY = [
    (36, 0, 0.9, -0.9, 12, 0), (39, 0, 1.2, -0.7, 12, 4), (41, 1, 1.0, -0.5, 12, 8),
    (34, 0, 0.7, -1.0, 16, 2), (42, 2, 1.4, -0.4, 16, 10), (38, 0, 1.1, -1.1, 16, 6),
    (44, 4, 1.3, -0.3, 24, 13), (33, 0, 0.5, -0.8, 24, 19),
]


def wave_mask():
    wet = set()
    for y, spans in WAVE_SPANS.items():
        for x0, x1 in spans:
            for x in range(x0, x1 + 1):
                wet.add((x, y))
    return wet


WET = wave_mask()


def depth_map(wet):
    """Distance (4-connected) from each wet pixel to the air."""
    from collections import deque
    dist = {}
    q = deque()
    for (x, y) in wet:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in wet and 0 <= n[0] < W and -1 <= n[1] < 14:
                dist[(x, y)] = 1
                q.append((x, y))
                break
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in wet and n not in dist:
                dist[n] = dist[(x, y)] + 1
                q.append(n)
    return dist


DEPTH = depth_map(WET)


def draw_wave(grid, f):
    a = TAU * f / FRAMES
    for (x, y) in WET:
        d = DEPTH.get((x, y), 9)
        col = C.BLUE
        # Striations: contours of depth, so they follow the curve; dashes
        # flow along them up the back and out along the crest.
        if d in (3, 6, 10) and math.sin(x * 0.8 - y * 0.8 - 3 * a + d) > -0.55:
            col = C.CYAN
        grid[(x, y)] = col

    # Foam outline: white over the crest, under the lip and down the face;
    # the lower back gets a cyan edge.
    for (x, y) in WET:
        if DEPTH.get((x, y)) != 1:
            continue
        above_air = (x, y - 1) not in WET
        lower_back = x < 20 and y > 5 and above_air
        if lower_back:
            grid[(x, y)] = C.CYAN if (x + y) % 3 else C.WHITE
        elif x <= 27 and y >= 3 and (x + 1, y) not in WET:
            # The face under the curl: cyan, flecked with foam.
            grid[(x, y)] = C.WHITE if (y * 5 + f // 4) % 4 == 0 else C.CYAN
        elif y <= 13 - (x < 30) * 2:
            grid[(x, y)] = C.WHITE
    # Foam tufts flickering on top of the crest.
    for x in range(20, 42, 3):
        top = min(y for (xx, y) in WET if xx == x)
        if math.sin(4 * a + x * 1.7) > 0.3 and top > 0:
            put(grid, x, top - 1, C.WHITE)

    # Claws: white fingers reaching down off the lip, hooking back in.
    for cx, cy, deg, bend, length, cyc, ph in CLAWS:
        reach = length + 1.1 * math.sin(cyc * a + ph)
        steps = max(1, int(round(reach)))
        px, py, th = float(cx), float(cy), math.radians(deg)
        for k in range(steps):
            put(grid, px, py, C.WHITE)
            px += math.cos(th)
            py += math.sin(th)
            th += math.radians(bend)
        # A fingertip droplet now and then.
        if math.sin(2 * cyc * a + ph) > 0.5:
            put(grid, px + 0.5 * math.cos(th), py + 1, C.CYAN)

    # Spray: foam dots thrown off the crest, arcing right and falling.
    for sx, sy, vx, vy, cycle, off in SPRAY:
        age = (f + off) % cycle
        life = cycle * 0.75
        if age > life:
            continue
        px = sx + vx * age
        py = sy + vy * age + 0.16 * age * age
        if py < -0.5 or py > 11:
            continue
        p = (int(round(px)), int(round(py)))
        if p not in WET and p not in grid:
            put(grid, *p, C.WHITE if age < life * 0.6 else C.CYAN)


def draw_boat(grid, f, cx, length, ph, cyc):
    a = TAU * f / FRAMES
    y = sea_surface(cx, f) - 0.6 + 0.6 * math.sin(cyc * a + ph)
    yi = int(round(y))
    half = length // 2
    x0 = int(round(cx)) - half
    for i in range(length):
        x = x0 + i
        dy = -1 if i in (0, length - 1) else 0
        put(grid, x, yi + dy, C.YELLOW)
        # Water laps the hull from below.
        if (x, yi + 1) not in grid:
            put(grid, x, yi + 1, C.BLUE)
    # Hunched rowers: a row of small white backs.
    for i in range(2, length - 2, 2):
        put(grid, x0 + i, yi - 1, C.WHITE)
    # Clear the row above the rowers so they read against the water.
    for i in range(1, length - 1):
        if i % 2 or i < 2 or i >= length - 2:
            grid.pop((x0 + i, yi - 1), None)
        if grid.get((x0 + i, yi - 2)) == C.BLUE:
            del grid[(x0 + i, yi - 2)]


def build():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        grid = {}
        draw_fuji(grid)
        draw_sea(grid, f)
        draw_small_wave(grid, f)
        draw_wave(grid, f)
        for boat in BOATS:
            draw_boat(grid, f, *boat)
        frame = anim.frame()
        for (x, y), c in grid.items():
            frame.pixel(x, y, c)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/great_wave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
