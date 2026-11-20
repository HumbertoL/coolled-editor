#!/usr/bin/env python3
"""
Wishbone -- two hands, one wish.

A white wishbone lies in the bottom half of the panel, its knob at the top
and its two arms splayed down to either side. Two fists slide in from the
edges -- yellow hands, a red sleeve on the left, a green one on the right --
and close on the ends of the arms. MAKE A WISH lights in yellow above them,
a twinkle crossing it.

Then the tug: PULL! flashes red, the fists shake and draw apart, the arms
of the bone bow and strain and its knob sags under the load. It SNAPS --
one white frame, then sparks fly from the break, high on the left arm --
and both hands recoil outward.

The right hand has the knob, and so the wish. It lifts its prize and
shakes it in triumph under I WIN! while yellow and white stars burst around
it; the left hand sinks, its sad little stick of bone wilting flat, under a
small blue AW. Then WISH GRANTED spreads across the top and
confetti rains down over everything.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
W, H = 96, 16

APEX = (48, 8)            # top of the knob
REST_L = (38, 14)         # where the left fist grips at rest
REST_R = (58, 14)
BREAK_T = 0.25            # the left arm snaps a quarter of the way down from the knob

# Beat sheet (frame indexes).
HANDS_IN = range(0, 5)    # fists slide in from the edges
WISH_START = 4            # MAKE A WISH, a letter-pair per frame
TUG_START = 18            # PULL! and the strain
SNAP = 30                 # the white frame
SPARK_END = 34
WIN_START = 33            # I WIN! / AW
GRANTED_START = 42        # WISH GRANTED and confetti

SKIN = C.YELLOW
SLEEVE_L = C.RED
SLEEVE_R = C.GREEN
BONE = C.WHITE


def bezier(p0, p1, p2, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((round(x), round(y)))
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    return out


def arm_points(apex, end, bow):
    """An arm of the bone from the knob to a fist, bowed inward by ``bow``."""
    mx, my = (apex[0] + end[0]) / 2, (apex[1] + end[1]) / 2
    # inward (toward the centre line) and down a little
    dx = 1 if end[0] < apex[0] else -1
    return bezier(apex, (mx + dx * bow, my + bow * 0.6), end)


def draw_knob(c, apex):
    x, y = apex
    c.hline(x - 1, y, 3, BONE)
    c.pixel(x, y + 1, BONE)


def draw_fist(c, x, y, side, sleeve):
    """A fist centred on (x, y) with its forearm running to the panel edge."""
    if side == "L":
        c.rect(x - 1, y - 1, 3, 3, SKIN, fill=True)
        c.pixel(x + 1, y - 1, C.BLACK)              # knuckle notch
        if x - 2 >= 0:
            c.vline(x - 2, y - 1, 3, C.WHITE)       # cuff
        for xx in range(0, x - 2):
            c.vline(xx, y - 1, 3, sleeve)
    else:
        c.rect(x - 1, y - 1, 3, 3, SKIN, fill=True)
        c.pixel(x - 1, y - 1, C.BLACK)
        if x + 2 < W:
            c.vline(x + 2, y - 1, 3, C.WHITE)
        for xx in range(x + 3, W):
            c.vline(xx, y - 1, 3, sleeve)


def plot(c, pts, color, dx=0, dy=0):
    for x, y in pts:
        c.pixel(x + dx, y + dy, color)


def wish_text(c, f):
    text = "MAKE A WISH"
    n = min(len(text), (f - WISH_START + 1) * 2)
    x0 = c.center_x(text)
    shine = (f - WISH_START - 6) * 8 + x0      # a twinkle sweeping across
    for i in range(n):
        x = x0 + 6 * i
        col = C.WHITE if abs(x + 2 - shine) <= 3 else C.YELLOW
        c.text(text[i], x, 0, col)


def sparkle(c, x, y, size, color):
    c.pixel(x, y, color)
    for d in range(1, size + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            c.pixel(x + dx, y + dy, color)


def main():
    rnd = random.Random(1127)
    anim = Animation(delay=DELAY)
    confetti = [
        [rnd.randrange(W), rnd.uniform(-20, 0), rnd.uniform(0.5, 1.1),
         rnd.choice((C.RED, C.YELLOW, C.MAGENTA, C.CYAN, C.GREEN, C.WHITE))]
        for _ in range(48)
    ]
    # where the left arm breaks, fixed by the rest geometry
    rest_left = arm_points(APEX, REST_L, 0)
    brk = rest_left[int(len(rest_left) * BREAK_T)]

    for f in range(FRAMES):
        c = anim.frame()

        if f < SNAP:
            # --- before the snap: one bone, two fists ---------------------
            if f in HANDS_IN:
                k = 1 - f / (len(HANDS_IN) - 1)       # 1 -> 0
                lx = REST_L[0] - round(k * 24)
                rx = REST_R[0] + round(k * 24)
                ly = ry = REST_L[1]
                pull = 0
            elif f < TUG_START:
                lx, rx, ly, ry, pull = REST_L[0], REST_R[0], REST_L[1], REST_R[1], 0
            else:
                p = (f - TUG_START) / (SNAP - TUG_START)      # 0 -> 1
                pull = p
                shake = (1 if f % 2 else -1) if p > 0.2 else 0
                lx = REST_L[0] - round(3 * p) + shake
                rx = REST_R[0] + round(3 * p) + shake
                ly = REST_L[1] + (f % 3 == 0)
                ry = REST_R[1] + (f % 3 == 1)
            apex = (APEX[0] + (round(pull) if f % 2 else 0), APEX[1] + round(pull * 2))
            bow = 0 if f in HANDS_IN else pull * 3
            if f not in HANDS_IN or f == HANDS_IN[-1]:
                plot(c, arm_points(apex, (REST_L[0], REST_L[1]) if f in HANDS_IN else (lx, ly), bow), BONE)
                plot(c, arm_points(apex, (REST_R[0], REST_R[1]) if f in HANDS_IN else (rx, ry), bow), BONE)
                draw_knob(c, apex)
            else:
                # the bone just lies there while the hands arrive
                plot(c, arm_points(APEX, REST_L, 0), BONE)
                plot(c, arm_points(APEX, REST_R, 0), BONE)
                draw_knob(c, APEX)
            draw_fist(c, lx, ly, "L", SLEEVE_L)
            draw_fist(c, rx, ry, "R", SLEEVE_R)

            if WISH_START <= f < TUG_START:
                wish_text(c, f)
            elif f >= TUG_START:
                # PULL! flashes, with strain marks by the fists
                if f % 4 < 3:
                    c.text("PULL!", "center", 0, C.RED)
                if pull > 0.3 and f % 2:
                    for sx, sy in ((lx - 1, ly - 4), (lx + 2, ly - 3), (rx + 1, ry - 4), (rx - 2, ry - 3)):
                        c.pixel(sx, sy, C.CYAN)
                if pull > 0.6:
                    # the bone creaks at the weak point
                    c.pixel(brk[0] - 1, brk[1] - 1, C.RED if f % 2 else C.YELLOW)
            continue

        if f == SNAP:
            # --- the snap: a white frame with SNAP! knocked out of it -----
            c.fill(C.WHITE)
            c.text("SNAP!", "center", 4, C.BLACK)
            continue

        # --- after the snap ------------------------------------------------
        t = f - SNAP
        recoil = {1: 6, 2: 5, 3: 3, 4: 2}.get(t, 1)

        # winner (right): fist raises its prize and shakes it in triumph
        lift = 0
        if WIN_START <= f < GRANTED_START:
            lift = 2 + (f % 2)
        rx = REST_R[0] + recoil + (1 if f >= WIN_START and f % 4 < 2 else 0)
        ry = REST_R[1] - lift
        off_x, off_y = rx - REST_R[0], ry - REST_R[1]
        right_arm = arm_points(APEX, REST_R, 0)
        plot(c, right_arm, BONE, off_x, off_y)
        draw_knob(c, (APEX[0] + off_x, APEX[1] + off_y))
        # the stub of the left arm still attached to the knob
        stub = [p for p in rest_left if p[1] <= brk[1]]
        plot(c, stub, BONE, off_x, off_y)
        draw_fist(c, rx, ry, "R", SLEEVE_R)

        # loser (left): a short stick of bone that wilts flat as the hand sinks
        droop = min(3, max(0, (f - WIN_START) // 2)) if f >= WIN_START else 0
        lx = REST_L[0] - recoil
        ly = REST_L[1] + (1 if droop >= 2 else 0)
        rise = (brk[1] - REST_L[1]) * (3 - droop) // 3       # -4 .. 0
        run = brk[0] - REST_L[0]
        c.line(lx + 1, ly - 1, lx + run, ly - 1 + rise, BONE)
        draw_fist(c, lx, ly, "L", SLEEVE_L)

        # sparks from the break
        if f < SPARK_END:
            r = 2 * t
            bx, by = brk[0] + off_x // 2, brk[1]
            for ang in range(0, 360, 45):
                a = math.radians(ang + 20 * t)
                sx, sy = bx + round(r * math.cos(a)), by + round(r * 0.7 * math.sin(a))
                c.pixel(sx, sy, C.WHITE if t == 1 else C.YELLOW if t == 2 else C.RED)

        if WIN_START <= f < GRANTED_START:
            # I WIN! over the winner, AW over the loser
            col = C.WHITE if f % 4 < 2 else C.YELLOW
            c.text("I WIN!", W - Canvas.text_width("I WIN!"), 0, col)
            c.small_text("AW", 14, 2 + min(droop, 3), C.BLUE)
            # stars bursting round the prize
            for i, (sx, sy) in enumerate(((38, 4), (72, 8), (31, 8), (86, 8), (54, 2))):
                if (f + i) % 3 == 0:
                    sparkle(c, sx, sy, 1, C.YELLOW if i % 2 else C.WHITE)
                elif (f + i) % 3 == 1:
                    c.pixel(sx, sy, C.YELLOW)
        elif f >= GRANTED_START:
            g = f - GRANTED_START
            text = "WISH GRANTED"
            x0 = c.center_x(text)
            # spreads out from the middle
            half = min(len(text), 2 + g * 2) / 2
            mid = len(text) / 2
            for i, ch in enumerate(text):
                if abs(i + 0.5 - mid) <= half:
                    hot = (i + g) % 6 == 0
                    c.text(ch, x0 + 6 * i, 0, C.WHITE if hot else C.YELLOW)
            for p in confetti:
                y = p[1] + p[2] * g * 1.6
                if 0 <= y < H:
                    x = (p[0] + round(math.sin(y * 0.8 + p[0]))) % W
                    c.pixel(x, int(y), p[3])

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/wishbone.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
