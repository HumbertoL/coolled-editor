#!/usr/bin/env python3
"""
Raycaster -- a first-person walk round a dungeon corridor, Wolfenstein-style.

Every one of the 82 view columns casts a ray into a 12x8 grid map (DDA, the
same trick id Software shipped in 1992) and draws a wall slice whose height
falls off with distance. With no brightness levels, distance is faked with
the GLOW ramp, and walls facing east-west sit one step darker than those
facing north-south, which is what makes corners read as corners. Mortar
lines give the bricks texture, so the walls visibly slide past, and dots on
the floor grid mark the ground.

The camera walks the ring corridor clockwise and turns on the spot at each
corner, arriving back where it started on frame 53, so the loop is seamless.
Each corridor ends in a coloured banner, so every
turn has a landmark. A minimap on the right shows the map, with the player as a blinking dot.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
VIEW_W = 82
H = 16
FOV = math.radians(70)

MAP = [
    "#Y###B######",
    "#..........R",
    "#.########.#",
    "#.########.#",
    "#.########.#",
    "C.########.#",
    "M..........#",
    "#####Y####G#",
]

RAMP = [C.BLACK, C.BLUE, C.CYAN, C.WHITE]
SPECIAL = {
    "R": C.RED,
    "G": C.GREEN,
    "M": C.MAGENTA,
    "Y": C.YELLOW,
    "B": C.RED,
    "C": C.GREEN,
}

# Corners of the walk, clockwise (screen y grows downwards), and the
# heading along each leg.
CORNERS = [(1.5, 1.5), (10.5, 1.5), (10.5, 6.5), (1.5, 6.5)]
SPEED = 0.8  # cells per frame on the straights
TURN = 4.5  # frames spent turning at each corner


def cell(mx, my):
    if 0 <= my < len(MAP) and 0 <= mx < len(MAP[0]):
        return MAP[my][mx]
    return "#"


def schedule():
    """Legs as (start, end, heading0, heading1, weight) in frame units."""
    legs = []
    for i in range(4):
        a, b = CORNERS[i], CORNERS[(i + 1) % 4]
        c = CORNERS[(i + 2) % 4]
        h0 = math.atan2(b[1] - a[1], b[0] - a[0])
        h1 = math.atan2(c[1] - b[1], c[0] - b[0])
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        legs.append(("walk", a, b, h0, h0, length / SPEED))
        # Clockwise on screen is a +90 degree turn in this y-down frame.
        legs.append(("turn", b, b, h0, h0 + math.pi / 2, TURN))
    return legs


LEGS = schedule()
TOTAL = sum(leg[-1] for leg in LEGS)


def smooth(t):
    return t * t * (3 - 2 * t)


def pose(t):
    """Position and heading at loop phase t in [0, 1)."""
    u = t * TOTAL
    for kind, a, b, h0, h1, w in LEGS:
        if u <= w:
            f = u / w
            if kind == "turn":
                f = smooth(f)
            else:
                # ease in and out slightly near corners
                f = 0.5 * f + 0.5 * smooth(f)
            x = a[0] + (b[0] - a[0]) * f
            y = a[1] + (b[1] - a[1]) * f
            return x, y, h0 + (h1 - h0) * f
        u -= w
    return CORNERS[0][0], CORNERS[0][1], 0.0


def shade(dist):
    if dist < 1.6:
        return 3
    if dist < 3.2:
        return 2
    if dist < 6.5:
        return 1
    return 1 if dist < 9 else 0


def cast(px, py, angle):
    """DDA ray march. Returns (distance, side, wall char, u along wall)."""
    dx, dy = math.cos(angle), math.sin(angle)
    mx, my = int(px), int(py)
    ddx = abs(1 / dx) if dx else 1e30
    ddy = abs(1 / dy) if dy else 1e30
    if dx < 0:
        sx, side_x = -1, (px - mx) * ddx
    else:
        sx, side_x = 1, (mx + 1 - px) * ddx
    if dy < 0:
        sy, side_y = -1, (py - my) * ddy
    else:
        sy, side_y = 1, (my + 1 - py) * ddy
    while True:
        if side_x < side_y:
            side_x += ddx
            mx += sx
            side = 0
        else:
            side_y += ddy
            my += sy
            side = 1
        ch = cell(mx, my)
        if ch != ".":
            break
    if side == 0:
        dist = side_x - ddx
        u = py + dist * dy
    else:
        dist = side_y - ddy
        u = px + dist * dx
    return dist, side, ch, u - math.floor(u)


def render(frame, t, index):
    px, py, heading = pose(t)
    plane = math.tan(FOV / 2)
    for col in range(VIEW_W):
        cam = (2 * (col + 0.5) / VIEW_W - 1) * plane
        ray = heading + math.atan(cam)
        dist, side, ch, u = cast(px, py, ray)
        perp = max(0.05, dist * math.cos(ray - heading))
        height = H * 1.1 / perp
        top = H / 2 - height / 2
        bottom = H / 2 + height / 2
        level = shade(perp) - side
        brick_edge = min(u, 1 - u) < 0.06 or abs(u - 0.5) < 0.03
        for row in range(H):
            yc = row + 0.5
            if top <= yc < bottom:
                v = (yc - top) / height  # 0 at wall top, 1 at bottom
                if ch in SPECIAL:
                    in_banner = 0.2 < u < 0.8 and 0.1 < v < 0.8
                    if in_banner:
                        frame.pixel(col, row, SPECIAL[ch] if perp < 7 else C.BLUE)
                        continue
                mortar = brick_edge or abs(v - 1 / 3) < 0.035 or abs(v - 2 / 3) < 0.035
                lvl = level - (2 if mortar and perp < 4 else 0)
                frame.pixel(col, row, RAMP[max(0, min(3, lvl))])
            elif yc >= bottom and row > H // 2:
                # Floor casting: where does this screen row hit the floor?
                rd = H * 1.1 / (2 * (yc - H / 2)) / math.cos(ray - heading)
                fx = px + rd * math.cos(ray)
                fy = py + rd * math.sin(ray)
                gx = abs(fx - round(fx))
                gy = abs(fy - round(fy))
                if gx < 0.12 and gy < 0.12 and rd < 5:
                    frame.pixel(col, row, C.BLUE)
    # Minimap: 1px per cell, one column of gap.
    ox, oy = VIEW_W + 2, 4
    for my, line in enumerate(MAP):
        for mx, ch in enumerate(line):
            if ch == "#":
                frame.pixel(ox + mx, oy + my, C.BLUE)
            elif ch in SPECIAL:
                frame.pixel(ox + mx, oy + my, SPECIAL[ch])
    if index % 4 != 3:
        frame.pixel(ox + int(px), oy + int(py), C.YELLOW)
    fx = ox + int(px + math.cos(heading) * 1.0)
    fy = oy + int(py + math.sin(heading) * 1.0)
    frame.pixel(fx, fy, C.WHITE)
    for row in range(H):
        frame.pixel(VIEW_W, row, C.BLACK)


def main():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        render(anim.frame(), index / FRAMES, index)
    out = Path(__file__).resolve().parents[2] / "src/sample/raycaster.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
