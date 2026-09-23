#!/usr/bin/env python3
"""
Oh yeah! -- running through a wall, literally.

A brick wall fills the panel, red and magenta courses on black mortar. It
trembles. A rumble, a pause, a bigger rumble, and yellow cracks spread from
a point on the left, light already leaking through. Then a white flash and
the round red pitcher bursts through grinning: every brick becomes a
particle flung outward on its own arc, and OH YEAH! slams in at double size
beside him while the whole panel shakes and the letters strobe.

The wall is drawn once as a list of bricks, so the burst can turn each brick
into a debris particle with a velocity pointing away from the impact.
Everything is composed on a scratch canvas and blitted at a shake offset, so
the pitcher, the debris and the words shake as one piece.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 1975
BRICK_W, BRICK_H = 8, 4          # including one row / column of mortar
IMPACT = (10, 8)                 # where he comes through
BURST_AT = 30                    # the white flash
TEXT_AT = 38                     # OH YEAH! lands
# Build-up rumbles: (first frame, last frame, amplitude).
RUMBLES = [(6, 8, 1), (14, 17, 1), (21, 23, 1), (25, 29, 1)]

PITCHER = [
    "....WWWWWWW....",
    "..RRRRRRRRRRR..",
    ".RRRRRRRRRRRRR.",
    "RRRRRRRRRRRRRRR",
    "RRRRKKRRRRKKRRR",
    "RRRRKKRRRRKKRRR",
    "RRRRRRRRRRRRRRR",
    "RRKRRRRRRRRRKRR",
    "RRRKKRRRRRKKRRR",
    "RRRRKKKKKKKRRRR",
    "RRRRRKKKKKRRRRR",
    ".RRRRRRRRRRRRR.",
    "..RRRRRRRRRRR..",
    "....RRRRRRR....",
]
PITCHER_COLORS = {"R": C.RED, "W": C.WHITE, "K": C.BLACK}
PITCHER_X = 1
WORD_GAP = 5
SHOCKWAVE_SPEED = 16            # px per frame


def bricks(rng):
    """Every brick as (x, y, w, h, color), running bond."""
    out = []
    for course in range(16 // BRICK_H):
        y = course * BRICK_H
        offset = 0 if course % 2 == 0 else -BRICK_W // 2
        for x in range(offset, 96, BRICK_W):
            color = C.MAGENTA if rng.random() < 0.25 else C.RED
            out.append((x, y, BRICK_W - 1, BRICK_H - 1, color))
    return out


def crack_paths(rng):
    """Jagged rays out of the impact point, each a list of pixels in order."""
    paths = []
    for k in range(7):
        angle = -math.pi / 2 + k * math.pi / 6 + rng.uniform(-0.25, 0.25)
        if k == 6:
            angle = math.pi * 0.85
        x, y = IMPACT
        path = []
        for _ in range(40):
            angle += rng.uniform(-0.5, 0.5)
            x += math.cos(angle) * 1.0 * 1.6
            y += math.sin(angle) * 0.6
            px, py = round(x), round(y)
            if not (0 <= px < 96 and 0 <= py < 16):
                break
            if not path or path[-1] != (px, py):
                path.append((px, py))
        paths.append(path)
    return paths


def draw_pitcher(canvas, x, y):
    for r, line in enumerate(PITCHER):
        for c, ch in enumerate(line):
            if ch in PITCHER_COLORS:
                color = PITCHER_COLORS[ch]
                canvas.pixel(x + c, y + r, color)
                if color == C.BLACK:
                    # pixel() treats black as "unset"; punch the hole explicitly.
                    canvas._pixels.pop((x + c, y + r), None)


def big_text(canvas, text, x, y, color, scale=2):
    """The 5x7 font at ``scale``x, proportional, one pixel of tracking per scale."""
    positions, _ = layout_text(text, 1, proportional=True)
    for char, cell_x in positions:
        bitmap = glyph(char)
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            canvas.pixel(x + (cell_x + col) * scale + dx, y + row * scale + dy, color)


def build():
    rng = random.Random(SEED)
    wall = bricks(rng)
    cracks = crack_paths(rng)

    # Debris: one particle per brick, flung away from the impact. A brick
    # holds until the shockwave reaches it, so the wall comes apart from the
    # impact outward instead of vanishing at once.
    debris = []
    for bx, by, bw, bh, color in wall:
        cx, cy = bx + bw / 2, by + bh / 2
        dx, dy = cx - IMPACT[0], cy - IMPACT[1]
        dist = max(1.0, math.hypot(dx, dy))
        speed = rng.uniform(2.5, 4.5)
        start = dist / SHOCKWAVE_SPEED
        vx, vy = dx / dist * speed, dy / dist * speed * 0.5 - rng.uniform(0.3, 1.2)
        debris.append((bx, by, bw, bh, color, start, vx, vy))

    anim = Animation(delay=DELAY)
    # "OH" and "YEAH!" set separately with a tight word gap, so the pair fits
    # beside the pitcher at double size.
    oh_width = layout_text("OH", 1, proportional=True)[1] * 2
    yeah_width = layout_text("YEAH!", 1, proportional=True)[1] * 2
    text_x = 96 - (oh_width + WORD_GAP + yeah_width) - 1
    strobe = [C.YELLOW, C.WHITE, C.YELLOW, C.RED]

    for index in range(FRAMES):
        scene = Canvas()
        shake = 0
        for first, last, amp in RUMBLES:
            if first <= index <= last:
                shake = amp
        if index > BURST_AT:
            shake = 2 if index < TEXT_AT + 4 else 1

        if index == BURST_AT:
            scene.fill(C.WHITE)
        elif index < BURST_AT:
            for bx, by, bw, bh, color in wall:
                scene.rect(bx, by, bw, bh, color, fill=True)
            # Cracks spread from frame 10, faster as the rumbles build.
            if index >= 10:
                t = (index - 10) / (BURST_AT - 10)
                reach = int(40 * t ** 1.3) + 2
                for path in cracks:
                    for step, (px, py) in enumerate(path[:reach]):
                        near = step < reach // 3
                        scene.pixel(px, py, C.WHITE if near and index >= 26 else C.YELLOW)
                # A glow at the impact point in the last beats.
                if index >= 24:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            scene.pixel(IMPACT[0] + dx, IMPACT[1] + dy, C.WHITE)
        else:
            k = index - BURST_AT
            # Bricks hold, then fly (with a little gravity) once hit.
            for bx, by, bw, bh, color, start, vx, vy in debris:
                t = k - start
                if t < 0:
                    scene.rect(bx, by, bw, bh, color, fill=True)
                elif t < 9:
                    px = bx + bw / 2 + vx * t
                    py = by + bh / 2 + vy * t + 0.45 * t * t
                    size = 3 if t < 3 else 2
                    scene.rect(round(px) - 1, round(py) - 1, size, 2, color, fill=True)
            # The pitcher: rushes in from behind the wall, big grin.
            py = 1 if k > 2 else 1 + (3 - k)
            draw_pitcher(scene, PITCHER_X, py)
            if index >= TEXT_AT:
                bob = 0 if (index - TEXT_AT) < 2 else 0
                color = C.WHITE if index == TEXT_AT else strobe[index % len(strobe)]
                big_text(scene, "OH", text_x, 1 + bob, color)
                big_text(scene, "YEAH!", text_x + oh_width + WORD_GAP, 1 + bob, color)
                if index < TEXT_AT + 2:
                    # Impact sparks around the words.
                    for sx, sy in ((text_x - 2, 0), (text_x - 2, 15), (95, 0), (95, 15)):
                        scene.pixel(sx, sy, C.WHITE)

        frame = anim.frame()
        sx = rng.randint(-shake, shake) if shake else 0
        sy = rng.randint(-1, 1) if shake else 0
        frame.blit(scene, sx, sy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/oh_yeah.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
