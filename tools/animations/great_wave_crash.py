#!/usr/bin/env python3
"""
Great wave crash -- a story version of Hokusai's woodblock print "The Great
Wave off Kanagawa" (1831, public domain), told in eight colors.

Beats:

1. Calm sea. A low blue sea with drifting cyan ripples; a small Mount Fuji --
   blue-outlined cone, white snowcap -- on the horizon right of centre, and
   two slender yellow boats with tiny red rowers bobbing to its right.
2. The swell. A hump of water gathers at the left edge and rises, rolling
   right as it grows: a deep blue body streaked with cyan.
3. The curl. The crest towers to the top of the panel and pitches forward
   over a hollow, the lip curling right. Its white edge splits into clawed
   fingers of foam that reach down toward the boats, cyan striations follow
   the curve through the blue, and Fuji sits small beneath the curl.
4. The hold. That composition holds for about a second, so it reads as the
   print, with only the striations and the claws stirring.
5. The crash. The claws close, the lip slams down over the boats and bursts
   into an explosion of white and cyan spray.
6. The settle. The spray falls back, a band of churning foam spreads and
   thins, and the boats bob back up -- they survive -- with Fuji still there,
   leaving the calm sea of frame 0 for the loop.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52
DELAY = 110
SEED = 1831
W, H = 96, 16

SEA = 13                       # resting sea level (top water row)
RIPPLE_K = 4                   # ripple cycles per loop -> seamless

# Beat sheet (frame numbers)
GROW = (4, 19)                 # swell gathers and rises (g: 0 -> 1)
HOLD = (19, 30)                # the print: held composition
CLOSE = (30, 35)               # claws close, lip pitches down (k: 0 -> 1)
IMPACT = 35                    # lip hits the water: spray burst
SETTLE_END = 46                # foam gone, sea calm again
SURFACE = (40, 45)             # boats bob back up

# Peak geometry
PEAK_CX = 40                   # crest column
PEAK_RX = 17.0                 # curl ellipse half-width
PEAK_RY = 7.0                  # curl ellipse half-height (top row 0)
PEAK_END = -22.0               # lip tip angle, degrees
INNER = 0.52                   # hollow radius (fraction of the ellipse)

FUJI_X, FUJI_TOP = 45, 6       # apex
BOATS = [(64, 0.0), (79, 2.1)]  # (left x, bob phase)
BOAT_LEN = 9


def clamp(t):
    return max(0.0, min(1.0, t))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def phase(f, span):
    return (f - span[0]) / (span[1] - span[0])


def ripple_angle(f):
    return 2 * math.pi * RIPPLE_K * f / FRAMES


# -- the wave --------------------------------------------------------------

def wave_params(f):
    """Geometry of the wave in frame f, or None when there is no wave."""
    if f < GROW[0] or f >= IMPACT:
        return None
    g = ease(phase(f, GROW))
    c = ease((phase(f, GROW) - 0.45) / 0.55)          # curl amount
    k = ease(phase(f, CLOSE)) if f >= CLOSE[0] else 0.0
    cx = 6 + (PEAK_CX - 6) * g + 12 * k
    top = SEA - (SEA - 0.0) * g + 2.5 * k
    rx = 3 + (PEAK_RX - 3) * c + 4 * k
    ry = 1.0 + (PEAK_RY - 1.0) * c
    end = 90 - (90 - PEAK_END) * c - 33 * k
    back = 10 + 34 * g
    front = 2 + 9 * (1 - c)
    return dict(cx=cx, top=top, rx=rx, ry=ry, cy=top + ry, end=end,
                back=back, front=front, c=c, k=k, g=g)


def mound_top(p, x):
    cx, top = p["cx"], p["top"]
    if x <= cx:
        t = (x - (cx - p["back"])) / p["back"]
        return SEA - (SEA - top) * ease(t) ** 0.8 if t > 0 else SEA + 1
    t = (x - cx) / p["front"]
    return top + (SEA - top) * ease(t)


def polar(p, x, y):
    """Normalised ellipse radius and angle (degrees, y up) about the curl."""
    dx = (x - p["cx"]) / p["rx"]
    dy = (p["cy"] - y) / p["ry"]
    return math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))


def lip_inner(p, th):
    """Inner radius of the lip: thick at the crest, thin at the tip."""
    span = 180 - p["end"]
    s = clamp((th - p["end"]) / span) if span > 0 else 1.0
    return INNER + 0.3 * (1 - s) ** 2.2 if p["c"] > 0.05 else 0.0


def in_hollow(p, x, y):
    if p["c"] < 0.15:
        return False
    d, th = polar(p, x, y)
    r = INNER * p["c"]
    if d < r:
        return True
    # Below the curl the concave face drops away to the left of the hollow.
    if y >= p["cy"]:
        face = p["cx"] - p["rx"] * r - (y - p["cy"]) * 0.25
        return x >= face
    return False


def in_lip(p, x, y):
    if p["c"] <= 0.05:
        return False
    d, th = polar(p, x, y)
    if d > 1.0 or th < p["end"] or th > 180:
        return False
    return d >= lip_inner(p, th)


def wave_cells(p, f):
    """dict (x, y) -> colour for the wave body."""
    cells = {}
    drift = f * 0.35 if not (HOLD[0] <= f < HOLD[1]) else HOLD[0] * 0.35 + (f - HOLD[0]) * 0.12
    for x in range(W):
        mt = mound_top(p, x)
        for y in range(H):
            lip = in_lip(p, x, y)
            mound = y >= mt - 0.35 and mt < SEA - 0.5
            if (mound and not in_hollow(p, x, y)) or lip:
                if lip and not (mound and not in_hollow(p, x, y)):
                    d, th = polar(p, x, y)
                    u = (1 - d) / max(0.05, 1 - lip_inner(p, th))
                    v = u * 3.2 + 0.25 * math.sin(math.radians(th) * 3 - drift)
                else:
                    depth = y - mt
                    v = depth / 2.8 + 0.25 * math.sin(x * 0.3 - drift)
                frac = v - math.floor(v)
                streak = math.sin(x * 0.45 + y * 0.8 - drift * 2) > -0.6
                cells[(x, y)] = C.CYAN if 0.4 < frac < 0.6 and streak else C.BLUE
    # Edges: the lip rim and the back slope's surface.
    for (x, y) in list(cells):
        above = (x, y - 1) not in cells
        right = (x + 1, y) not in cells
        if not (above or right) or y >= SEA:
            continue
        d, th = polar(p, x, y)
        on_lip = in_lip(p, x, y) and p["c"] > 0.3
        if on_lip and th < 75:
            cells[(x, y)] = C.WHITE
        elif on_lip or above:
            cells[(x, y)] = C.CYAN
    # The front of the lip is a broad band of white foam.
    if p["c"] > 0.3:
        for (x, y) in list(cells):
            d, th = polar(p, x, y)
            if in_lip(p, x, y) and th < 55 and d > 0.9:
                cells[(x, y)] = C.WHITE
    # Inner edge of the lip, under the hook: a cyan line.
    for (x, y) in list(cells):
        if (x, y + 1) not in cells and y + 1 < SEA and in_lip(p, x, y) \
                and cells[(x, y)] == C.BLUE:
            cells[(x, y)] = C.CYAN
    return cells


def claws(p, f, rng):
    """White foam fingers raking forward and down from the lip."""
    if p["c"] < 0.6:
        return []
    out = []
    stir = (f // 2) % 2 if HOLD[0] <= f < HOLD[1] else f
    # Rim angles for the fingers: from the shoulder of the curl to the tip.
    angles = [58, 40, 22, 5, p["end"] + 3]
    for i, th in enumerate(angles):
        th = th - 30 * p["k"] if i < 4 else th
        a = math.radians(th)
        bx = p["cx"] + p["rx"] * math.cos(a)
        by = p["cy"] - p["ry"] * math.sin(a)
        # Each finger leaves the rim on its outward normal, bent down.
        nx = math.cos(a) / p["rx"]
        ny = math.sin(a) / p["ry"]
        n = math.hypot(nx, ny)
        nx, ny = nx / n, ny / n
        bend = math.radians((-50, -36, -30, -32, -40)[i]) - 1.2 * p["k"]
        dx = nx * math.cos(bend) - ny * math.sin(bend)
        dy = nx * math.sin(bend) + ny * math.cos(bend)
        length = (3.0 + 0.4 * i) * (1 - 0.4 * p["k"]) + 0.6 * ((i + stir) % 2)
        x, y = bx, by
        pts = []
        for _ in range(int(round(length))):
            x += dx
            y -= dy
            pts.append((round(x), round(y)))
        # The talon hooks back under at its tip.
        if pts:
            pts.append((pts[-1][0] - 1, pts[-1][1] + 1))
        out += pts
    # Talons dangling from the underside of the tip toward the boats.
    tip = math.radians(p["end"])
    for j, frac in enumerate((0.72, 0.86)):
        tx = p["cx"] + p["rx"] * frac * math.cos(tip)
        ty = p["cy"] - p["ry"] * frac * math.sin(tip)
        ln = 2 + ((j + stir) % 2)
        for st in range(1, ln + 1):
            out.append((round(tx + st * 0.45), round(ty + st)))
        out.append((round(tx + ln * 0.45) - 1, round(ty + ln) + 1))
    return out


# -- scenery -------------------------------------------------------------

def draw_fuji(frame):
    for y in range(FUJI_TOP, SEA):
        half = (y - FUJI_TOP) * 1.25
        lx, rx = round(FUJI_X - half), round(FUJI_X + half)
        if y - FUJI_TOP <= 1:
            for x in range(lx, rx + 1):
                frame.pixel(x, y, C.WHITE)
        elif y - FUJI_TOP == 2:
            # Jagged snowline.
            for x in range(lx, rx + 1):
                frame.pixel(x, y, C.WHITE if (x - FUJI_X) % 2 == 0 else C.BLUE)
            frame.pixel(lx, y, C.BLUE)
            frame.pixel(rx, y, C.BLUE)
        else:
            frame.pixel(lx, y, C.BLUE)
            frame.pixel(rx, y, C.BLUE)
            if y == SEA - 1:
                for x in range(lx, rx + 1):
                    frame.pixel(x, y, C.BLUE)


def sea_cells(f):
    cells = {}
    a = ripple_angle(f)
    for x in range(W):
        for y in range(SEA, H):
            cells[(x, y)] = C.BLUE
        if math.sin(x * 0.3 - a) > 0.35:
            cells[(x, SEA)] = C.CYAN
        if math.sin(x * 0.21 + a + 1.0) > 0.8:
            cells[(x, SEA + 2)] = C.CYAN
    return cells


def draw_boat(frame, x0, y):
    """Slender yellow hull, raised prow, tiny red rowers."""
    y = round(y)
    for x in range(x0 + 1, x0 + BOAT_LEN - 1):
        frame.pixel(x, y, C.YELLOW)
    frame.pixel(x0, y - 1, C.YELLOW)
    frame.pixel(x0 + BOAT_LEN - 1, y - 1, C.YELLOW)
    frame.pixel(x0 + BOAT_LEN, y - 2, C.YELLOW)       # prow
    for x in range(x0 + 2, x0 + BOAT_LEN - 1, 2):
        frame.pixel(x, y - 1, C.RED)


def boat_bob(f, ph):
    return 0.45 * math.sin(2 * math.pi * 2 * f / FRAMES + ph)


# -- build -----------------------------------------------------------------

def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    spray = []      # (start, x, y, vx, vy)

    for f in range(FRAMES):
        frame = anim.frame()
        p = wave_params(f)

        # Distant mountain, then the sea in front of it.
        draw_fuji(frame)
        for (x, y), c in sea_cells(f).items():
            frame.pixel(x, y, c)

        # Boats: ride the sea; dragged under at impact, bob back up after.
        sunk = 0.0
        if f >= IMPACT - 1 and f < SURFACE[0]:
            sunk = 3.0
        elif SURFACE[0] <= f < SURFACE[1]:
            sunk = 3.0 * (1 - ease(phase(f, SURFACE)))
            sunk -= 0.6 * math.sin(math.pi * phase(f, SURFACE))
        boat_layer = []
        for bx, ph in BOATS:
            by = SEA - 0.5 + boat_bob(f, ph) + sunk
            if p is not None and p["k"] > 0:
                by += 0.5 * p["k"]
            boat_layer.append((bx, by))
        for bx, by in boat_layer:
            draw_boat(frame, bx, by)
        if sunk > 0.2:
            # Water closes over whatever is below the surface.
            for x in range(W):
                for y in range(SEA + 1, H):
                    if frame.get(x, y) in (C.YELLOW, C.RED):
                        frame.pixel(x, y, C.BLUE)

        # The wave itself.
        if p is not None:
            for (x, y), c in wave_cells(p, f).items():
                frame.pixel(x, y, c)
            for (x, y) in claws(p, f, rng):
                if y < SEA:
                    frame.pixel(x, y, C.WHITE)
            # Foam blown off the crest.
            if p["c"] > 0.5:
                for _ in range(2 if HOLD[0] <= f < HOLD[1] else 3):
                    sx = round(p["cx"] - rng.uniform(1, 8))
                    sy = round(p["top"] + rng.uniform(-1, 1))
                    if frame.get(sx, sy) == C.BLACK:
                        frame.pixel(sx, sy, C.WHITE)

        # Impact: the explosion of spray.
        if IMPACT <= f <= IMPACT + 1:
            ix = PEAK_CX + 22
            for _ in range(55):
                ang = rng.uniform(math.radians(20), math.radians(160))
                sp = rng.uniform(1.5, 5.0)
                spray.append((f, ix + rng.uniform(-12, 10), SEA - 6 + 2 * (f - IMPACT),
                              math.cos(ang) * sp * 1.6, -math.sin(ang) * sp))

        # Churning whitewater after impact.
        if IMPACT <= f < SETTLE_END:
            age = f - IMPACT
            span = SETTLE_END - IMPACT
            strength = 1 - age / span
            centre = PEAK_CX + 22
            reach = 18 + age * 6
            for x in range(W):
                dist = abs(x - centre) / (reach * (1.7 if x < centre else 1.0))
                if dist > 1:
                    continue
                hgt = (10 * strength ** 1.6) * (1 - dist ** 1.5) \
                    + rng.uniform(-1.5, 1.5) * strength
                top = SEA - hgt
                for y in range(max(0, math.floor(top)), H):
                    r = rng.random()
                    if y < SEA and r > 0.25 + 0.75 * strength:
                        continue
                    if y <= top + 0.8:
                        col = C.WHITE if r < 0.55 + 0.4 * strength else C.CYAN
                    elif r < 0.45 * strength:
                        col = C.WHITE
                    elif r < 0.45 + 0.3 * strength:
                        col = C.CYAN
                    else:
                        col = C.BLUE
                    frame.pixel(x, y, col)
            if SURFACE[0] <= f:
                for bx, by in boat_layer:
                    draw_boat(frame, bx, by)

        # Airborne spray: white, cooling to cyan, then blue as it falls.
        for start, sx, sy, vx, vy in spray:
            age = f - start
            if 0 <= age < 6:
                px = sx + vx * age * 0.8
                py = sy + vy * age + 0.5 * 0.9 * age * age
                if py < SEA and 0 <= py:
                    col = C.WHITE if age < 3 else C.CYAN
                    frame.pixel(round(px), round(py), col)
                    if age == 0:
                        frame.pixel(round(px) + 1, round(py), C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/great_wave_crash.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
