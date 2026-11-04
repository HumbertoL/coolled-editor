#!/usr/bin/env python3
"""
Blue wave surf -- a big wave barrels, a surfer gets spat out, and the words
BLUE WAVE splash up out of the whitewater.

Beats:

1. Calm sea. Low blue swell with cyan ripples rolling along the bottom rows.
2. The build. A swell rises at the right edge and runs left, growing into a
   wall of water almost the full height of the panel: a blue body shot through
   with drifting cyan streaks, a cyan face and a white-foamed crest.
3. The drop. A tiny surfer -- yellow board, red figure -- appears on the crest
   and drops down the face into the trough.
4. The barrel. The lip pitches forward and curls over in a white arc, hollowing
   a black tube. The surfer rides deep in it, cyan spray hanging in the air.
5. The spit. The lip slams down, the tube collapses, and a burst of white and
   cyan spray blasts out of the mouth -- carrying the surfer out the end and
   off to the left.
6. The splash. The wave folds into a band of churning whitewater, and
   "BLUE WAVE" erupts out of it with droplets falling round it, then holds,
   cyan ripples rolling through the white letters.
7. The wash. A second surge of whitewater sweeps right to left across the
   panel, takes the words with it, and leaves the calm sea of frame 0.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.canvas import Canvas  # noqa: E402

FRAMES = 52
DELAY = 110
SEED = 1104
W, H = 96, 16

SEA = 13                       # resting sea level (top water row)
RIPPLE_K = 5                   # ripple cycles per loop -> seamless

# Beat sheet (frame numbers)
BUILD = (2, 15)                # swell runs in and rises
DROP = (11, 16)                # surfer drops down the face
CURL = (14, 23)                # lip pitches and curls into a barrel
SPIT = 24                      # tube collapses, spray and surfer blast out
CRASH = (24, 31)               # wave folds into whitewater
TEXT_RISE = (29, 34)           # words splash up
WASH = (44, 50)                # surge sweeps the words away

TEXT = "BLUE WAVE"
TEXT_Y = 3
TEXT_W = Canvas.text_width(TEXT)
TEXT_X = (W - TEXT_W) // 2
assert TEXT_X >= 0 and TEXT_X + TEXT_W <= W

PEAK_H = 12                    # wave height in rows above SEA
MAX_R = 6.0                    # barrel radius


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def phase(t, span):
    return (t - span[0]) / (span[1] - span[0])


def sea_level(x, f):
    """Gentle rolling sea surface, seamless over the loop."""
    a = 2 * math.pi * RIPPLE_K * f / FRAMES
    return SEA + 0.6 * math.sin(x * 0.33 - a) + 0.4 * math.sin(x * 0.11 + a * 0.4 * 0)


def wave_state(f):
    """(crest x, height in rows, curl 0..1, collapse 0..1) for frame f."""
    if f < BUILD[0]:
        return None
    b = ease(phase(f, BUILD))
    cx = 108 - 50 * b                       # crest runs in from off the right
    if f > BUILD[1]:
        cx = 58 - 1.4 * (f - BUILD[1])      # then keeps creeping left
    height = PEAK_H * b
    curl = ease(phase(f, CURL))
    collapse = ease_out(phase(f, CRASH)) if f >= CRASH[0] else 0.0
    if f > CRASH[1] + 3:
        return None
    return cx, height, curl, collapse


def water_field(f, rng):
    """Returns dict (x, y) -> color for the ocean in frame f, plus geometry."""
    grid = {}
    a = 2 * math.pi * RIPPLE_K * f / FRAMES
    state = wave_state(f)
    geom = None

    # Base sea.
    for x in range(W):
        top = round(sea_level(x, f))
        for y in range(top, H):
            grid[(x, y)] = C.BLUE
        grid[(x, top)] = C.CYAN if math.sin(x * 0.33 - a) > -0.2 else C.BLUE

    if state is None:
        return grid, geom

    cx, height, curl, collapse = state
    height *= (1 - collapse)
    top = SEA - height
    R = MAX_R * curl * (1 - collapse * 0.6)
    ccx, ccy = cx - R, top + R               # barrel centre
    ext = math.radians(135 * curl + 85 * collapse)   # lip sweep from the top
    back = 22.0
    front = 1.6 + 2.5 * collapse

    def surface(x):
        if x >= cx:
            t = (x - cx) / back
            return top + (SEA - top) * (1 - math.exp(-t * t * 2.2))
        if R > 0.5 and x >= ccx - R:
            if x >= ccx:
                return top
            dx = x - ccx
            return ccy + math.sqrt(max(0.0, R * R - dx * dx))
        if R > 0.5:
            return SEA                       # open tube mouth, no front wall
        return SEA - (SEA - top) * math.exp(-(cx - x) / front)

    def in_disk(x, y):
        return R > 0.5 and math.hypot(x - ccx, y - ccy) < R - 0.4

    air = set()
    for x in range(W):
        s = surface(x)
        sea = sea_level(x, f)
        s = min(s, sea)
        for y in range(H):
            wet = y >= s - 0.3 and not in_disk(x, y)
            if wet:
                # Liquid shimmer: drifting cyan streaks through the body.
                streak = math.sin(x * 0.55 + y * 0.9 - f * 0.9)
                grid[(x, y)] = C.CYAN if streak > 0.9 else C.BLUE
            elif (x, y) in grid:
                del grid[(x, y)]
            if not wet:
                air.add((x, y))

    # Face and crest colouring.
    for (x, y), _ in list(grid.items()):
        if y >= SEA:
            continue
        if (x, y - 1) in air:
            grid[(x, y)] = C.CYAN
        if (x - 1, y) in air or (x - 2, y) in air:
            grid[(x, y)] = C.CYAN
    # Foam on the crest.
    for x in range(int(cx) - 1, int(cx) + 5):
        for y in range(H):
            if (x, y) in grid and (x, y - 1) not in grid and y < SEA - 1:
                grid[(x, y)] = C.WHITE
                if rng.random() < 0.5 and height > 3:
                    grid[(x, y - 1)] = C.WHITE
                break

    # The lip: an arc from the top of the barrel sweeping forward and down.
    if R > 0.5:
        steps = 60
        for i in range(steps + 1):
            th = math.pi / 2 + ext * i / steps
            # Thick near the crest, thinning to the tip.
            thick = 1.6 - 1.1 * i / steps
            for rr, col in ((R - thick, C.BLUE), (R - thick * 0.5, C.CYAN),
                            (R + 0.2, C.WHITE), (R + 0.6, C.WHITE)):
                px = ccx + rr * math.cos(th)
                py = ccy - rr * math.sin(th)
                p = (round(px), round(py))
                if 0 <= p[0] < W and 0 <= p[1] < H:
                    if col == C.BLUE and math.sin(i * 0.8 - f * 1.7) > 0.6:
                        col = C.CYAN
                    grid[p] = col
        # Lip tip throws a little spray.
        tip = math.pi / 2 + ext
        tx, ty = ccx + R * math.cos(tip), ccy - R * math.sin(tip)
        for _ in range(2):
            p = (round(tx + rng.uniform(-1.5, 0.5)), round(ty + rng.uniform(-0.5, 1.5)))
            if p not in grid:
                grid[p] = C.WHITE
    geom = (cx, top, R, ccx, ccy, collapse)
    return grid, geom


def draw_surfer(frame, x, y, tilt=0):
    """Board centred on (x, y); figure stands above it."""
    x, y = round(x), round(y)
    for dx in range(-2, 3):
        frame.pixel(x + dx, y + (round(dx * tilt) if tilt else 0), C.YELLOW)
    frame.pixel(x, y - 1, C.RED)          # legs
    frame.pixel(x - 1, y - 1, C.RED)
    frame.pixel(x, y - 2, C.RED)          # body
    frame.pixel(x + 1, y - 2, C.RED)      # arm out
    frame.pixel(x, y - 3, C.YELLOW)       # head


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    spit = []          # (start, x, y, vx, vy, colour)
    splash = []        # droplets thrown when the words erupt
    surfer = None

    for f in range(FRAMES):
        frame = anim.frame()
        grid, geom = water_field(f, rng)

        # Wash: a surge of whitewater sweeping right to left.
        if WASH[0] <= f <= WASH[1]:
            t = (f - WASH[0]) / (WASH[1] - WASH[0])
            fx = W + 6 - (W + 30) * t
            for x in range(W):
                d = x - fx
                if d < -1:
                    continue
                lift = 9 * math.exp(-d / 14) if d >= 0 else 0
                if lift < 0.6 and d > 6:
                    continue
                top = SEA - lift
                for y in range(H):
                    if y >= top - 0.3:
                        grid[(x, y)] = C.BLUE
                    elif (x, y) in grid and y < SEA:
                        del grid[(x, y)]
                # Foam at the front edge and on top.
                for y in range(max(0, round(top)), H):
                    if d < 3:
                        grid[(x, y)] = C.WHITE if rng.random() < 0.75 else C.CYAN
                    elif d < 7 and rng.random() < 0.5:
                        grid[(x, y)] = C.CYAN
                if 0 <= d < 24 and 0 <= round(top) < H:
                    grid[(x, round(top))] = C.WHITE if rng.random() < 0.6 else C.CYAN
            for _ in range(6):
                sx = round(fx + rng.uniform(-3, 2))
                sy = rng.randrange(0, 6)
                grid[(sx, sy)] = C.WHITE

        # Whitewater band after the crash.
        if CRASH[0] + 2 <= f < TEXT_RISE[1] + 4:
            age = f - CRASH[0] - 2
            reach = 18 + age * 7
            centre = 40 - age * 1.5
            for x in range(W):
                d = abs(x - centre)
                if d > reach:
                    continue
                strength = max(0.0, 1 - age / 9)
                bump = 0.6 * math.sin(x * 0.7 - f * 2.1)
                hgt = round((4 - 3 * d / max(reach, 1)) * strength + bump)
                for y in range(SEA - hgt, H):
                    r = rng.random()
                    depth = y - (SEA - hgt)
                    if depth == 0:
                        c = C.WHITE if r < 0.8 * strength + 0.1 else C.CYAN
                    elif r < 0.35 * strength:
                        c = C.WHITE
                    elif r < 0.75:
                        c = C.CYAN
                    else:
                        c = C.BLUE
                    grid[(x, y)] = c

        # Paint the water.
        for (x, y), c in grid.items():
            frame.pixel(x, y, c)

        # Words splash up out of the whitewater, hold, then get washed.
        if f >= TEXT_RISE[0] and f < WASH[1] + 2:
            t = phase(f, TEXT_RISE)
            # Ease out with a little overshoot.
            rise = 1 - (1 - min(1, t)) ** 2 * math.cos(min(1, t) * 3)
            y = round(H + (TEXT_Y - H) * min(1.0, rise if t < 1 else 1))
            a = 2 * math.pi * RIPPLE_K * f / FRAMES

            def tcol(px, py):
                if t < 0.8:
                    return C.CYAN if (px + py) % 2 else C.WHITE
                return C.CYAN if math.sin(px * 0.45 - a * 1.6 + py * 0.5) > 0.55 else C.WHITE

            tmp = Canvas(W, H)
            tmp.text(TEXT, TEXT_X, y, tcol)
            fx = None
            if f >= WASH[0]:
                tw = (f - WASH[0]) / (WASH[1] - WASH[0])
                fx = W + 6 - (W + 30) * tw
            for (px, py), c in tmp._pixels.items():
                if fx is not None and px >= fx - 1:
                    continue
                if py >= SEA and (px, py) in grid:
                    continue
                frame.pixel(px, py, c)
            # Keep a black moat round the letters so they read.
            if t >= 1:
                for (px, py) in list(frame._pixels):
                    if TEXT_Y - 1 <= py <= TEXT_Y + 7 and (px, py) not in tmp._pixels \
                            and TEXT_X - 1 <= px <= TEXT_X + TEXT_W and \
                            (fx is None or px < fx - 4):
                        del frame._pixels[(px, py)]

            if TEXT_RISE[0] <= f <= TEXT_RISE[1]:
                for _ in range(10):
                    splash.append((f, rng.uniform(TEXT_X, TEXT_X + TEXT_W), SEA - 1,
                                   rng.uniform(-1.2, 1.2), rng.uniform(-3.2, -1.6),
                                   rng.choice([C.WHITE, C.CYAN, C.CYAN])))

        # Splash droplets.
        for start, sx, sy, vx, vy, c in splash:
            age = f - start
            if 0 < age < 7:
                px = sx + vx * age
                py = sy + vy * age + 0.5 * 0.7 * age * age
                in_box = (TEXT_Y - 1 <= py <= TEXT_Y + 7 and TEXT_X - 1 <= px <= TEXT_X + TEXT_W
                          and f > TEXT_RISE[1])
                if py < SEA and not in_box and frame.get(round(px), round(py)) == C.BLACK:
                    frame.pixel(round(px), round(py), c if age < 4 else C.BLUE)

        # Surfer.
        if geom is not None and DROP[0] <= f < SPIT:
            cx, top, R, ccx, ccy, _ = geom
            if f < DROP[1]:
                t = ease(phase(f, DROP))
                sx = cx + 1 - 5 * t
                sy = top - 1 + (SEA - 1 - (top - 1)) * t
                surfer = (sx, sy)
                draw_surfer(frame, sx, sy, tilt=0.5 * (1 - t) if 0 < t < 1 else 0)
            else:
                # Deep in the pocket: inside the barrel, bobbing.
                sx = ccx + R * 0.35 - 2 + math.sin(f * 1.3) * 0.6
                sy = SEA - 1
                surfer = (sx, sy)
                draw_surfer(frame, sx, sy)
                # Hanging spray inside the tube.
                if R > 2:
                    for _ in range(2):
                        ang = rng.uniform(0, 2 * math.pi)
                        rr = rng.uniform(0, R - 1.5)
                        p = (round(ccx + rr * math.cos(ang)), round(ccy + rr * math.sin(ang)))
                        if frame.get(*p) == C.BLACK:
                            frame.pixel(*p, C.CYAN)

        if f == SPIT and geom is not None:
            cx, top, R, ccx, ccy, _ = geom
            mx, my = ccx - 2, ccy + 1
            for _ in range(26):
                ang = rng.uniform(math.pi * 0.85, math.pi * 1.25)
                sp = rng.uniform(2.5, 6.0)
                spit.append((f, mx, my, math.cos(ang) * sp,
                             -abs(math.sin(ang)) * sp * 0.6 - rng.uniform(0.2, 1.2),
                             rng.choice([C.WHITE, C.WHITE, C.CYAN])))
            surfer = (mx, SEA - 1)

        # Spit spray.
        for start, sx, sy, vx, vy, c in spit:
            age = f - start
            if 0 <= age < 7:
                px = sx + vx * age
                py = sy + vy * age + 0.5 * 0.55 * age * age
                if py < H - 1:
                    if age < 5:
                        frame.pixel(round(px), round(py), c if age < 3 else C.CYAN)
                    if age < 2:
                        frame.pixel(round(px) + 1, round(py), C.WHITE)
        if f == SPIT:
            mx, my = surfer
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (-2, 0)):
                frame.pixel(round(mx) + dx, round(ccy) + dy, C.WHITE)

        # Surfer shooting out the end and away.
        if surfer is not None and SPIT <= f < SPIT + 6:
            age = f - SPIT
            sx = surfer[0] - 5 * age - 1
            sy = SEA - 1 - (2.5 * age - 0.5 * age * age if age < 4 else 0)
            if sx > -3:
                draw_surfer(frame, sx, sy, tilt=-0.3 if age in (1, 2) else 0)
                # wake
                for k in range(1, 4):
                    frame.pixel(round(sx) + 2 + k, round(sy) + 1, C.WHITE if k < 3 else C.CYAN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/blue_wave_surf.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
