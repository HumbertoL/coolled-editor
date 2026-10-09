#!/usr/bin/env python3
"""
Chicken road -- why did the chicken cross the road? To come back for the egg.

A title card asks the old question. Then the panel is a two-lane road seen
from above: green verges top and bottom, a dashed white line down the
middle, cars zooming left in the upper lane and right in the lower. A white
chicken (red comb, yellow beak) on the bottom verge, next to its egg, dashes
across -- each lane's car missing it by a pixel, feathers flying -- and
celebrates on the far side. Then it looks back: "...WAIT. MY EGG!" It runs
back into traffic. HONK. A puff of feathers, and a plucked pink chicken
stands dazed in the stopped traffic -- one last feather see-sawing down
onto its head -- while the egg hatches and a yellow
chick strolls across the jammed road without a care.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140

CX = 30                 # chicken's left column
EGG_X = 22
CAR_LEN = 10
SPEED = 6
PERIOD = 29             # spacing of each lane's traffic, px
LANE1_ROW = 4           # upper lane, cars move left
LANE2_ROW = 9           # lower lane, cars move right
LANE_COLORS = {1: [C.RED, C.CYAN, C.MAGENTA], 2: [C.MAGENTA, C.CYAN, C.RED]}

TITLE_END = 7
HIT = 30
FREEZE = 33             # traffic stops (jam) from this frame on

# Chicken top row per frame, and facing (+1 right, -1 left); None = not drawn
# as the normal chicken.
CHICKEN = {}
for f in range(TITLE_END, 9):
    CHICKEN[f] = (12, 1)
for f, y in zip(range(9, 16), (12, 10, 8, 6, 4, 2, 0)):
    CHICKEN[f] = (y, 1)
for f in range(16, 27):
    CHICKEN[f] = (0, 1 if f < 20 else -1)
for f, y in zip(range(27, 31), (2, 4, 5, 8)):
    CHICKEN[f] = (y, -1)
NEAR_MISSES = (10, 13, 15)

# Lane phases chosen so the dash threads the gaps (asserted in build()).
PHASE = {1: CX + 18 + 6 * 12, 2: CX + 6 - 6 * 10}
# Cars left out so the run back has a clear path for its one fatal car...
SKIP = {1: {3}, 2: {-4, -5}}
# ...which is this one: lower lane, at the chicken's column on the HIT frame.
HONK_CAR_AT_HIT = CX - 2

CHICKEN_SPRITE = [   # facing right: c comb, w body, b beak, l legs
    "...c.",
    "w.wwb",
    "wwww.",
    ".l.l.",
]
CHICKEN_RUN = [
    "...c.",
    "w.wwb",
    "wwww.",
    "l...l",
]
CHICK = [
    ".yo",
    "yy.",
    "y.y",
]


def car_xs(lane, t):
    """Left x of every car in this lane at frame t (traffic frozen later)."""
    t = min(t, FREEZE)
    if lane == 1:
        base = PHASE[1] - SPEED * t
    else:
        base = PHASE[2] + SPEED * t
    xs = []
    start = base % PERIOD - PERIOD * 2
    k0 = (base - start) // PERIOD
    for k in range(8):
        x = start + k * PERIOD
        if -CAR_LEN < x < 96 and (k - k0) not in SKIP[lane]:
            xs.append((x, int(k - k0)))
    if lane == 2:
        x = HONK_CAR_AT_HIT + SPEED * (t - HIT)
        if -CAR_LEN < x < 96:
            xs.append((x, "honk"))
    return xs


def draw_car(frame, x, top, color, direction):
    # Roof toward the back of the car, headlights at the front.
    roof = x + 3 if direction < 0 else x + 2
    frame.hline(roof, top, 5, color)
    frame.hline(x, top + 1, CAR_LEN, color)
    frame.hline(x, top + 2, CAR_LEN, color)
    front = x if direction < 0 else x + CAR_LEN - 1
    frame.pixel(front, top + 1, C.WHITE)
    frame.pixel(x + 2, top + 2, C.BLACK)
    frame.pixel(x + CAR_LEN - 3, top + 2, C.BLACK)


def draw_sprite(frame, rows, x, y, palette, flip=False):
    width = len(rows[0])
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell in palette:
                cx = x + (width - 1 - c if flip else c)
                frame.pixel(cx, y + r, palette[cell])


def chicken_palette(body=C.WHITE):
    return {"c": C.RED, "w": body, "b": C.YELLOW, "l": C.YELLOW}


def draw_road(frame, t):
    frame.rect(0, 0, 96, 3, C.GREEN, fill=True)
    frame.rect(0, 13, 96, 3, C.GREEN, fill=True)
    for x in range(96):
        if x % 6 < 3:
            frame.pixel(x, 7, C.WHITE)
    for lane, top, direction in ((1, LANE1_ROW, -1), (2, LANE2_ROW, 1)):
        for x, k in car_xs(lane, t):
            color = C.YELLOW if k == "honk" else LANE_COLORS[lane][k % 3]
            draw_car(frame, x, top, color, direction)


def overlaps(t, y):
    """Does a chicken at rows y..y+3, columns CX..CX+4 touch a car at t?"""
    for lane, top in ((1, LANE1_ROW), (2, LANE2_ROW)):
        if y + 3 < top or y > top + 2:
            continue
        for x, _ in car_xs(lane, t):
            if x <= CX + 4 and x + CAR_LEN - 1 >= CX:
                return True
    return False


def boxed_small(frame, text, x, y, color):
    w = frame.small_text_width(text)
    frame.rect(x - 1, y - 1, w + 2, 7, C.BLACK, fill=True)
    frame.small_text(text, x, y, color)


def build():
    for f, (y, _) in CHICKEN.items():
        assert f == HIT or not overlaps(f, y), f"chicken hit at frame {f}"
    assert overlaps(HIT, 8), "the honk car misses"

    rng = random.Random(3)
    feathers = []           # [x, y, vx, vy]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < TITLE_END:
            frame.small_text("WHY DID THE CHICKEN", "center", 0, C.WHITE)
            frame.text("CROSS THE ROAD?", "center", 8, C.YELLOW)
            if index >= 2:
                draw_sprite(frame, CHICKEN_SPRITE, 87, 0, chicken_palette())
                draw_sprite(frame, CHICKEN_SPRITE, 4, 0, chicken_palette(),
                            flip=True)
            continue

        draw_road(frame, index)

        # Egg on the start verge (until it hatches).
        hatch = index - 37
        if hatch < 0:
            egg = C.YELLOW if 22 <= index <= 26 and index % 2 else C.WHITE
            frame.hline(EGG_X + 1, 13, 2, egg)
            frame.hline(EGG_X, 14, 4, egg)
            frame.hline(EGG_X + 1, 15, 2, egg)
            if 35 <= index <= 36:                         # wobble
                frame.pixel(EGG_X + (index % 2) * 3, 13, egg)
        elif hatch < 3:
            frame.hline(EGG_X, 14, 4, C.WHITE)            # bottom shell
            frame.hline(EGG_X + 1, 15, 2, C.WHITE)
            frame.pixel(EGG_X + 1, 13 - hatch, C.YELLOW)
            frame.pixel(EGG_X + 2, 13 - hatch, C.YELLOW)
            frame.pixel(EGG_X - 1 + hatch, 12 - hatch, C.WHITE)  # cap flies
            frame.pixel(EGG_X + 4 + hatch, 12 - hatch, C.WHITE)
        else:
            frame.hline(EGG_X, 14, 4, C.WHITE)
            frame.hline(EGG_X + 1, 15, 2, C.WHITE)

        # The chicken.
        if index in CHICKEN and index != HIT:
            y, facing = CHICKEN[index]
            running = 9 <= index <= 15 or 27 <= index
            sprite = CHICKEN_RUN if running and index % 2 else CHICKEN_SPRITE
            dy = 0
            if 16 <= index <= 19 and index % 2:
                sprite = CHICKEN_RUN
            draw_sprite(frame, sprite, CX, y + dy, chicken_palette(),
                        flip=facing < 0)
            if 16 <= index <= 19:                         # flapping + YAY
                wing = 1 if index % 2 else 2
                frame.pixel(CX + 1, wing, C.WHITE)
                frame.pixel(CX - 1, wing - 1 if wing > 1 else 0, C.WHITE)
                boxed_small(frame, "YAY!", CX + 8, 1, C.YELLOW)
                for k in range(3):
                    sx = rng.randrange(CX - 10, CX + 30)
                    frame.pixel(sx, rng.randrange(0, 3),
                                rng.choice([C.YELLOW, C.MAGENTA, C.CYAN]))
            if 20 <= index <= 21:
                boxed_small(frame, "?", CX + 7, 1, C.WHITE)
            if 22 <= index <= 26:
                boxed_small(frame, "...WAIT. MY EGG!", CX + 7, 1, C.WHITE)
        elif index >= HIT:
            # Plucked: the same chicken, pink, dazed in the road.
            if index >= HIT + 2:
                draw_sprite(frame, CHICKEN_SPRITE, CX, 8,
                            {"c": C.RED, "w": C.MAGENTA, "b": C.YELLOW,
                             "l": C.YELLOW}, flip=True)
                if index < 40:
                    star = (index // 2) % 2
                    frame.pixel(CX + 1 + 2 * star, 6, C.YELLOW)
                    frame.pixel(CX + 3 - 2 * star, 5, C.YELLOW)
                else:
                    # The last feather see-saws down and lands on its head.
                    fy = min(index - 40, 7)
                    fx = CX + 2 + (0 if fy == 7 else (1 if index % 2 else -1))
                    frame.hline(fx - 1, fy, 3, C.WHITE)

        # Near misses throw a feather or two.
        if index in NEAR_MISSES:
            y = CHICKEN[index][0]
            for _ in range(2):
                feathers.append([CX + rng.randrange(0, 5), y + 1,
                                 rng.choice([-1, 1]), -1])
        if index == HIT:
            for _ in range(18):
                feathers.append([CX + rng.uniform(-1, 5), rng.uniform(7, 11),
                                 rng.uniform(-3, 3), rng.uniform(-2.5, 1.5)])
        for p in feathers:
            frame.pixel(round(p[0]), round(p[1]), C.WHITE)
        for p in feathers:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.6
            p[3] = min(p[3] + 0.5, 0.7)
        feathers[:] = [p for p in feathers
                       if 0 <= p[0] < 96 and p[1] < 16 and index - HIT < 9]

        if HIT <= index <= HIT + 3:
            boxed_small(frame, "HONK!", CX + 22, 1, C.YELLOW)

        # The chick strolls across the jammed road.
        if index >= 40:
            step = index - 40
            cy = max(0, 13 - 2 * step)
            pose = CHICK
            draw_sprite(frame, pose, EGG_X + 1, cy,
                        {"y": C.YELLOW, "o": C.RED})
            if cy == 0:
                boxed_small(frame, "PEEP!", EGG_X + 7, 1, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/chicken_road.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
