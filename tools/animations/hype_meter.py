#!/usr/bin/env python3
"""
Hype Meter -- a gauge that cannot contain it.

A segmented HYPE bar sits across the bottom of the panel with its reading on
top: MEH, a couple of green segments idling. It climbs -- OK, HYPED,
UNHINGED -- lighting green, then yellow, then red, and the whole gauge
rattles harder the higher it gets. At the top it keeps going: segments burst
out past the end of the box, flashing. A one-frame white flash, the meter
blows apart into a shower of sparks, and LET'S drops in at double size,
bounces, and gives way to GOOOO!!! -- an O at a time -- strobing and shaking
while the sparks rain down.
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
SEED = 9001

BOX_X, BOX_Y, BOX_W, BOX_H = 2, 8, 80, 7
SEGMENTS = 15  # inside the box, 5px pitch
OVERLOAD = 3  # extra segments that escape past the box
FLASH_AT = 30
GO_AT = 39
LEVELS = [(0, "MEH", C.GREEN), (8, "OK", C.GREEN), (16, "HYPED", C.YELLOW), (23, "UNHINGED", C.RED)]
STROBE = [C.RED, C.YELLOW, C.WHITE]
SPARKS = [C.WHITE, C.YELLOW, C.YELLOW, C.RED, C.MAGENTA, C.CYAN]


def big_text(canvas, text, x, y, color, scale=2):
    """The 5x7 font at ``scale``x: each pixel becomes a block."""
    small = Canvas(200, 7)
    small.text(text, 0, 0, C.WHITE, proportional=True)
    for sx, sy in small.lit():
        canvas.rect(x + sx * scale, y + sy * scale, scale, scale, color, fill=True)


def big_width(text, scale=2):
    return Canvas.text_width(text, proportional=True) * scale


def segment_color(i):
    if i < 7:
        return C.GREEN
    if i < 11:
        return C.YELLOW
    return C.RED


def reading(index, rng):
    """How many segments are lit: a lazy idle, then a climb that overshoots."""
    if index < 8:
        return 2 + (index // 3) % 2
    if index < 23:
        base = 2 + (index - 8) * 0.8
        return max(1, round(base + rng.choice((-1, 0, 0, 1))))
    return min(SEGMENTS + OVERLOAD, 14 + (index - 23))


def level(index):
    name, color = LEVELS[0][1:]
    for start, n, c in LEVELS:
        if index >= start:
            name, color = n, c
    return name, color


def draw_meter(canvas, lit, index):
    canvas.rect(BOX_X, BOX_Y, BOX_W, BOX_H, C.WHITE)
    for i in range(min(lit, SEGMENTS + OVERLOAD)):
        x = BOX_X + 2 + i * 5
        if i >= SEGMENTS:
            # Escaped past the end of the gauge: flashing.
            color = C.WHITE if (index + i) % 2 else C.RED
            canvas.rect(x, BOX_Y + 1 + (i % 2), 4, 4, color, fill=True)
        else:
            canvas.rect(x, BOX_Y + 2, 4, 3, segment_color(i), fill=True)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    sparks = []  # [x, y, vx, vy]
    for index in range(FRAMES):
        frame = anim.frame()
        if index == FLASH_AT:
            frame.fill(C.WHITE)
            # The blast: sparks from every segment, flung up and out.
            for i in range(SEGMENTS + OVERLOAD):
                for _ in range(5):
                    angle = rng.uniform(math.pi * 1.05, math.pi * 1.95)
                    speed = rng.uniform(1.5, 4.5)
                    sparks.append([BOX_X + 4 + i * 5, 11, math.cos(angle) * speed, math.sin(angle) * speed * 0.9])
            continue

        scene = Canvas()
        dx = dy = 0
        strobe = STROBE[index % 3]

        if index < FLASH_AT:
            lit = reading(index, rng)
            draw_meter(scene, lit, index)
            name, color = level(index)
            scene.text("HYPE", 2, 0, C.WHITE, proportional=True)
            scene.text(name, 30, 0, color if index < 26 or index % 2 else C.WHITE, proportional=True)
            # Rattle: nothing at MEH, a twitch at OK, then harder and harder.
            # Text and gauge fill rows 0-14, so vertical rattle is downward.
            if index >= 26:
                dx, dy = rng.randint(-2, 2), rng.randint(0, 1)
            elif index >= 20:
                dx, dy = rng.randint(-1, 1), rng.randint(0, 1)
            elif index >= 12 and index % 3 == 0:
                dx = rng.choice((-1, 1))
        else:
            # Sparks rain behind the words.
            for spark in sparks:
                spark[0] += spark[2]
                spark[1] += spark[3]
                spark[3] += 0.35
                spark[2] *= 0.97
            sparks = [s for s in sparks if s[1] < 16 and -2 < s[0] < 98]
            # Fresh fizz so the shower never quite runs dry.
            for _ in range(4):
                sparks.append([rng.uniform(0, 96), -1, rng.uniform(-0.6, 0.6), rng.uniform(0.2, 1.0)])
            for spark in sparks:
                scene.pixel(round(spark[0]), round(spark[1]), rng.choice(SPARKS))

            if index < FLASH_AT + 3:
                pass  # two frames of pure blast before the words
            elif index < GO_AT:
                # LET'S drops in, overshoots, settles.
                drop = {FLASH_AT + 3: -9, FLASH_AT + 4: 3, FLASH_AT + 5: 0}.get(index, 1)
                word = "LET'S"
                x = (96 - big_width(word)) // 2
                for y in range(max(0, drop), min(16, drop + 14)):
                    scene.hline(x - 1, y, big_width(word) + 2, C.BLACK)
                big_text(scene, word, x, drop, strobe)
            else:
                # GOOOO!!!, an O at a time until there are four.
                o_count = min(4, 1 + (index - GO_AT))
                word = "G" + "O" * o_count + "!!!"
                x = (96 - big_width(word)) // 2
                for y in range(1, 15):
                    scene.hline(x - 1, y, big_width(word) + 2, C.BLACK)
                big_text(scene, word, x, 1, strobe)
            reach = 2 if index in (FLASH_AT + 1, FLASH_AT + 2, FLASH_AT + 4, GO_AT, GO_AT + 1) else 1
            dx, dy = rng.randint(-reach, reach), rng.randint(-1, 1)

        frame.blit(scene, dx, dy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hype_meter.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
