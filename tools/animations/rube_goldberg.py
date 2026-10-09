#!/usr/bin/env python3
"""
Rube Goldberg -- an overbuilt machine for turning on a light.

A yellow marble rolls down a ramp into five dominoes, which topple in turn;
the last lands on the raised end of a seesaw and flicks a cyan ball into the
air. It drops into a bucket hanging from a rope, and the bucket's weight hauls
the rope over two pulleys to lift a switch. A spark runs along the wire and
the bulb on the right lights, rays pulsing.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
FLOOR = 15

RAMP = ((0, 3), (11, 9))
DOMINOES = (14, 18, 22, 26, 30)
DOMINO_H = 6
REST_ANGLE = math.asin(4 / DOMINO_H)     # leaning on the next domino
DOMINO_START = 8                         # first domino starts to tip
DOMINO_GAP = 2                           # frames between topples
TIP_FRAMES = 3

PIVOT = (40, 12)
PLANK = 7                                # half-length of the seesaw
FLIP = DOMINO_START + DOMINO_GAP * 4 + TIP_FRAMES   # last domino lands
FLIGHT = 10
BUCKET_X = 60
BUCKET_TOP = 9                           # bucket's rim before it drops
DROP = 2
LAND = FLIP + 1 + FLIGHT
SWITCH_X = 74
SWITCH_ON = LAND + DROP
WIRE = list(range(SWITCH_X + 3, 85))
LIT = SWITCH_ON + 1 + len(WIRE) // 2
BULB = (89, 7)


def marble(index):
    """Marble centre: down the ramp under gravity, into the first domino."""
    if index >= DOMINO_START:
        return None
    u = (index / DOMINO_START) ** 2
    (x0, y0), (x1, y1) = RAMP
    return x0 + 1 + (x1 + 1 - x0) * u, y0 - 1.5 + (y1 - y0) * u


def domino_angle(i, index):
    start = DOMINO_START + DOMINO_GAP * i
    final = REST_ANGLE if i < len(DOMINOES) - 1 else math.radians(64)
    if index < start:
        return 0.0
    u = min(1.0, (index - start) / TIP_FRAMES)
    return final * u ** 2


def seesaw_tilt(index):
    """+1: left end up (loaded). -1: right end up (after the flip)."""
    if index < FLIP:
        return 1.0
    return max(-1.0, 1.0 - 2.0 * (index - FLIP + 1) / 2)


def ball(index):
    """The cyan ball: resting on the seesaw, flying, then in the bucket."""
    right_end = (PIVOT[0] + PLANK, PIVOT[1] + 2 * seesaw_tilt(index))
    if index <= FLIP:
        return right_end[0] - 1, right_end[1] - 1
    if index <= FLIP + 1 + FLIGHT:
        u = (index - FLIP - 1) / FLIGHT
        x0, y0 = right_end[0] - 1, PIVOT[1] - 3
        x1, y1 = BUCKET_X + 2, bucket_top(index) + 1
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u - 14 * u * (1 - u)
    return BUCKET_X + 2, bucket_top(index) + 1


def bucket_top(index):
    return BUCKET_TOP + min(DROP, max(0, index - LAND))


def draw_static(frame):
    frame.hline(0, FLOOR, 96, C.BLUE)
    frame.line(*RAMP[0], *RAMP[1], C.BLUE)
    frame.vline(0, RAMP[0][1], FLOOR - RAMP[0][1], C.BLUE)
    # Seesaw fulcrum.
    frame.pixel(PIVOT[0], PIVOT[1] + 1, C.RED)
    frame.hline(PIVOT[0] - 1, FLOOR - 1, 3, C.RED)
    # Pulleys and the frame they hang from.
    frame.hline(BUCKET_X + 1, 1, SWITCH_X - BUCKET_X + 1, C.BLUE)
    for px in (BUCKET_X + 2, SWITCH_X):
        frame.pixel(px, 2, C.WHITE)
    # Bulb base and socket.
    bx, by = BULB
    frame.hline(bx - 1, by + 4, 3, C.WHITE)
    frame.hline(bx - 1, by + 5, 3, C.BLUE)
    frame.vline(bx, by + 6, FLOOR - by - 6, C.BLUE)


def draw_bulb(frame, lit, index):
    bx, by = BULB
    glass = [(dx, dy) for dy in range(-3, 4) for dx in range(-3, 4) if dx * dx + dy * dy <= 10]
    for dx, dy in glass:
        edge = dx * dx + dy * dy >= 5
        if lit:
            frame.pixel(bx + dx, by + dy, C.WHITE if not edge else C.YELLOW)
        elif edge:
            frame.pixel(bx + dx, by + dy, C.CYAN if dy < 2 else C.BLUE)
    if not lit:
        frame.pixel(bx, by, C.RED)
        frame.pixel(bx, by + 1, C.RED)
        return
    phase = (index - LIT) % 4
    for k in range(8):
        a = k * math.pi / 4
        for r in (5 + phase % 2, 6 + phase % 2):
            if k % 2 == phase // 2:
                frame.pixel(round(bx + r * math.cos(a)), round(by + r * math.sin(a)), C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_static(frame)

        m = marble(index)
        if m:
            frame.rect(round(m[0]), round(m[1]), 2, 2, C.YELLOW, fill=True)
        else:
            frame.rect(11, FLOOR - 2, 2, 2, C.YELLOW, fill=True)

        for i, x in enumerate(DOMINOES):
            a = domino_angle(i, index)
            top = (x + DOMINO_H * math.sin(a), FLOOR - 1 - DOMINO_H * math.cos(a))
            frame.line(x, FLOOR - 1, round(top[0]), round(top[1]), C.WHITE)
            frame.pixel(round(top[0]), round(top[1]), C.RED)

        tilt = seesaw_tilt(index)
        lx, ly = PIVOT[0] - PLANK, PIVOT[1] - 2 * tilt
        rx, ry = PIVOT[0] + PLANK, PIVOT[1] + 2 * tilt
        frame.line(lx, round(ly), rx, round(ry), C.MAGENTA)

        top = bucket_top(index)
        lift = top - BUCKET_TOP
        # Rope: up from the bucket, over both pulleys, down to the switch.
        frame.vline(BUCKET_X + 2, 3, top - 3, C.WHITE)
        handle_y = 9 - lift
        frame.vline(SWITCH_X, 3, handle_y - 3, C.WHITE)
        frame.rect(BUCKET_X, top, 5, 4, C.RED)
        frame.hline(BUCKET_X, top, 5, C.BLACK)
        frame.pixel(BUCKET_X, top, C.RED)
        frame.pixel(BUCKET_X + 4, top, C.RED)
        # Switch box on the floor; its lever follows the rope.
        frame.rect(SWITCH_X - 2, FLOOR - 3, 5, 3, C.GREEN if index >= SWITCH_ON else C.RED, fill=True)
        frame.line(SWITCH_X, FLOOR - 4, SWITCH_X + (-2 if index >= SWITCH_ON else 2), handle_y + 1, C.WHITE)

        bx_, by_ = ball(index)
        frame.rect(round(bx_), round(by_), 2, 2, C.CYAN, fill=True)

        # Wire to the bulb, with a spark running along it.
        for x in WIRE:
            frame.pixel(x, FLOOR - 1, C.BLUE)
        if SWITCH_ON <= index < LIT:
            spark = WIRE[min(len(WIRE) - 1, 2 * (index - SWITCH_ON))]
            frame.pixel(spark, FLOOR - 1, C.YELLOW)
            frame.pixel(spark, FLOOR - 2, C.WHITE)
        draw_bulb(frame, index >= LIT, index)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rube_goldberg.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
