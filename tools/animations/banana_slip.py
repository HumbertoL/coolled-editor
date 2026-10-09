#!/usr/bin/env python3
"""
Banana slip -- eyes on the phone, feet on the peel.

A white stick figure strides in from the left, nose in a cyan phone,
whistling: little green and magenta notes bob up off its head. A yellow
banana peel lies ahead on the floor. It steps square on it. The feet shoot
out, the phone flies, and the whole body hangs horizontal in midair for a
long cartoon beat. Then it slams flat: OOF!, dust puffs, white and cyan stars
circling the head. Meanwhile the peel has been spinning up off the panel,
and drops back down to land draped over the face. One leg twitches.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

BODY = C.WHITE
PEEL_X, PEEL_Y = 63, 12          # the peel's stem column, and its top row
WALK_END = 18                    # frame the foot lands on the peel
SLIP = WALK_END
CRASH = 28
PEEL_LANDS = 33
TWITCH = (41, 42, 47)

PEEL_UP = ["...#...", "..###..", ".#.#.#.", "#..#..#"]
PEEL = {
    "up": PEEL_UP,
    "down": PEEL_UP[::-1],
    "right": ["".join(row[i] for row in PEEL_UP[::-1]) for i in range(7)],
    "left": ["".join(row[i] for row in PEEL_UP)[::-1] for i in range(7)],
}
SPIN = ["up", "right", "down", "left"]
NOTE = [".##", ".#.", ".#.", "##."]


def sprite(frame, rows, x, y, color):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r, color)


def rotate(point, angle):
    """Tip a body-local point backwards by ``angle`` (head swings left)."""
    x, y = point
    ca, sa = math.cos(angle), math.sin(angle)
    return x * ca + y * sa, -x * sa + y * ca


def figure(frame, hip, angle, pose):
    """Draw the stick figure from body-local joints around the hip."""
    hx, hy = hip

    def at(p):
        x, y = rotate(p, angle)
        return round(hx + x), round(hy + y)

    head = at(pose["head"])
    frame.rect(head[0] - 1, head[1] - 1, 3, 3, BODY)
    neck, hip_pt = at((0, -6)), at((0, 0))
    frame.line(*neck, *hip_pt, BODY)
    for limb in pose["limbs"]:
        pts = [at(p) for p in limb]
        for a, b in zip(pts, pts[1:]):
            frame.line(*a, *b, BODY)
    if pose.get("phone"):
        px, py = at(pose["phone"])
        frame.pixel(px, py, C.CYAN)
        frame.pixel(px, py - 1, C.CYAN)
    return head


def walk_pose(phase):
    # Legs: a four-step cycle. Arm with the phone stays put; the other swings.
    legs = [
        [[(0, 0), (-2, 3), (-3, 5)], [(0, 0), (2, 3), (3, 5)]],
        [[(0, 0), (0, 3), (-1, 5)], [(0, 0), (2, 2), (2, 4)]],
        [[(0, 0), (2, 3), (3, 5)], [(0, 0), (-2, 3), (-3, 5)]],
        [[(0, 0), (2, 2), (2, 4)], [(0, 0), (0, 3), (-1, 5)]],
    ][phase % 4]
    swing = [(-2, -2), (0, -1), (2, -2), (0, -1)][phase % 4]
    return {
        "head": (1, -8),                      # bent forward over the phone
        "limbs": legs + [
            [(0, -5), (2, -4), (3, -5)],      # phone arm
            [(0, -5), swing],
        ],
        "phone": (4, -5),
    }


# Midair, drawn at a quarter turn: local (x, y) lands at screen (y, -x), so
# these put both legs kicking up-right and both arms flung up.
FLAIL = {
    "head": (0, -8),
    "limbs": [
        [(0, 0), (2, 2), (3, 4)],
        [(0, 0), (1, 3), (1, 5)],
        [(0, -5), (3, -6)],
        [(0, -5), (3, -3)],
    ],
}
FLAT = {
    "head": (0, -8),
    "limbs": [
        [(0, 0), (2, 2), (0, 5)],             # knee up
        [(0, 0), (0, 5)],                     # leg flat
        [(0, -5), (2, -3)],
        [(0, -5), (-1, -3)],
    ],
}


def build():
    anim = Animation(delay=DELAY)
    peel_start = (PEEL_X - 3, PEEL_Y)
    for index in range(FRAMES):
        frame = anim.frame()
        head = None

        if index < WALK_END:
            hip = (5 + round(index * 55 / WALK_END), 10)
            head = figure(frame, hip, 0.0, walk_pose(index))
            # Whistled notes: one every three frames, left hanging in the air
            # as the walker strides on, drifting up.
            for born in range(0, index + 1, 3):
                age = index - born
                if age > 4:
                    continue
                bx = 5 + round(born * 55 / WALK_END) - 4
                by = -(age // 2)
                color = C.MAGENTA if (born // 3) % 2 else C.GREEN
                sprite(frame, NOTE, bx, by, color)
        elif index == SLIP:
            # Foot hits the peel and shoots forward.
            pose = walk_pose(0)
            pose["limbs"][1] = [(0, 0), (3, 2), (6, 3)]
            head = figure(frame, (60, 10), 0.15, pose)
        elif index < CRASH:
            k = index - SLIP
            angle, hip = {
                1: (0.6, (60, 9)),
                2: (1.2, (59, 7)),
                9: (math.pi / 2, (57, 10)),
            }.get(k, (math.pi / 2, (58, 7 - (4 <= k <= 6))))
            head = figure(frame, hip, angle, FLAIL)
            if 3 <= k <= 8:
                # Hang-time: blue motion lines under the body.
                for dx in (-6, -2, 2):
                    frame.pixel(hip[0] + dx, hip[1] + 3 + (k % 2), C.BLUE)
        else:
            k = index - CRASH
            hip = (57, 13)
            pose = FLAT
            if index in TWITCH:
                pose = dict(FLAT)
                pose["limbs"] = list(FLAT["limbs"])
                pose["limbs"][0] = [(0, 0), (3, 1), (3, 4)]
            head = figure(frame, hip, math.pi / 2, pose)
            if k <= 2:
                # Dust puffs either side on impact.
                for dx, dy in ((-12 - k, 0), (-11 - k, -1 - k // 2), (9 + k, 0), (8 + k, -1 - k // 2)):
                    frame.pixel(hip[0] + dx, hip[1] + 2 + dy, C.BLUE if k else C.WHITE)
            if k <= 9:
                frame.text("OOF!", 22, 2 - (k == 0), C.RED if k % 2 == 0 else C.WHITE, proportional=True)
            if k >= 1:
                # Stars circling the head.
                for s in range(3):
                    theta = index * 0.9 + s * 2 * math.pi / 3
                    sx = head[0] + round(5 * math.cos(theta))
                    sy = head[1] - 4 + round(2 * math.sin(theta))
                    star = C.WHITE if (index + s) % 2 else C.CYAN
                    frame.pixel(sx, sy, star)
                    if s == 0:
                        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                            frame.pixel(sx + dx, sy + dy, star)

        # The phone: flies out of the hand at the slip, lands far right.
        if SLIP < index:
            t = index - SLIP
            if t < 9:
                px = 64 + 3 * t
                py = 4 - 3 * t + round(0.45 * t * t)
                frame.pixel(px, py, C.CYAN)
                frame.pixel(px, py + 1, C.CYAN)
            else:
                frame.hline(90, 15, 2, C.CYAN)
                if t == 9:
                    frame.pixel(89, 14, C.WHITE)
                    frame.pixel(92, 14, C.WHITE)

        # The peel.
        if index <= SLIP:
            sprite(frame, PEEL["up"], *peel_start, C.YELLOW)
        elif index < PEEL_LANDS:
            # A spinning arc: up and to the right, then back onto the face.
            t = (index - SLIP) / (PEEL_LANDS - SLIP)
            (x0, y0), (x1, y1), (x2, y2) = peel_start, (80, -12), (46, 10)
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2
            sprite(frame, PEEL[SPIN[(index - SLIP) % 4]], round(x), round(y), C.YELLOW)
        else:
            # Draped over the face, flaps hanging down either side.
            bounce = 1 if index == PEEL_LANDS else 0
            sprite(frame, PEEL["up"], head[0] - 3, head[1] - 3 - bounce, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/banana_slip.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
