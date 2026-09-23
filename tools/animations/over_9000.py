#!/usr/bin/env python3
"""
It's over 9000! (2006) -- the scouter reading.

A spiky-haired fighter clenches his fists on the left while a scouter
readout on the right climbs: POWER LEVEL, 1000, 3000, 5000, 8000. His aura
grows as it counts, BLUE to CYAN to WHITE to YELLOW, and rocks lift off the
ground around him. The number goes yellow, then red, then blows straight
past 9000; the readout cracks, the scouter pops in a white flash, and IT'S
OVER / 9000!!! screams in at double size over a blaze that fills the panel,
the whole thing shaking.

The aura is the fighter's silhouette dilated on the fly, with flame tongues
licking upward at seeded random columns, and a one-pixel black gap kept
between body and aura so he stays readable whatever colour it is.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 9001
PAST_AT = 28            # the counter passes 9000
CRACK_AT = 31
POP_AT = 33             # the scouter explodes: one white frame
OVER_AT = 34            # IT'S OVER
NINE_AT = 42            # 9000!!!
FIGHTER_X, FIGHTER_Y = 9, 2
BLAZE_W = 34            # the 9000!!! beat: fire up to here
LENS_X = 32             # left edge of the scouter readout

FIGHTER = [
    "H..H.H..H",
    ".HHHHHHH.",
    "HHHHHHHHH",
    ".HSSSSSH.",
    "..SKSKS..",
    "...SSS...",
    ".GGGGGGG.",
    "GGGGGGGGG",
    "S.GGGGG.S",
    "S.BBBBB.S",
    "..GGGGG..",
    "..GG.GG..",
    ".GG...GG.",
    ".BB...BB.",
]


def fighter_cells():
    for r, line in enumerate(FIGHTER):
        for c, ch in enumerate(line):
            if ch != ".":
                yield FIGHTER_X + c, FIGHTER_Y + r, ch


def draw_fighter(canvas, super_mode):
    colors = {
        "H": C.YELLOW if super_mode else C.BLUE,
        "S": C.WHITE,
        "G": C.RED,
        "B": C.BLUE,
        "K": None,
    }
    for x, y, ch in fighter_cells():
        color = colors[ch]
        if color is None:
            canvas._pixels.pop((x, y), None)
        else:
            canvas.pixel(x, y, color)


def draw_aura(canvas, rng, reach, color, tongues):
    """Everything 2..reach px from the body, plus flames licking upward."""
    body = {(x, y) for x, y, _ in fighter_cells()}
    near = set()
    for bx, by in body:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                near.add((bx + dx, by + dy))
    for x in range(FIGHTER_X - reach - 1, FIGHTER_X + 9 + reach + 1):
        for y in range(0, 16):
            if (x, y) in near:
                continue
            d = min(max(abs(x - bx), abs(y - by)) for bx, by in body)
            if 2 <= d <= reach and rng.random() < 0.8:
                canvas.pixel(x, y, color)
    for _ in range(tongues):
        x = rng.randint(FIGHTER_X - reach, FIGHTER_X + 8 + reach)
        top = rng.randint(0, 3)
        length = rng.randint(2, 5)
        for y in range(top, top + length):
            if (x, y) not in near:
                canvas.pixel(x, y, color)


def big_text(canvas, text, x, y, color, scale=2):
    """The 5x7 font at ``scale``x, proportional."""
    positions, _ = layout_text(text, 1, proportional=True)
    for char, cell_x in positions:
        bitmap = glyph(char)
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            canvas.pixel(x + (cell_x + col) * scale + dx, y + row * scale + dy, color)


def outlined(canvas, draw):
    """Run ``draw`` on a scratch canvas and stamp it with a black halo."""
    layer = Canvas()
    draw(layer)
    for x, y in layer.lit():
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                canvas._pixels.pop((x + dx, y + dy), None)
    canvas.blit(layer)


def power_level(index):
    """The reading: eases up from 1000 to just short of 9000, then blows past."""
    if index < PAST_AT:
        t = index / (PAST_AT - 1)
        value = 1000 + 7950 * t ** 1.6
        return int(value) // 10 * 10 + (index * 7) % 10
    return 9000 + [1, 480, 3702, 12944, 88888][min(4, index - PAST_AT)]


def blaze(canvas, rng, width):
    """Flames from the floor to the ceiling: red base, yellow, white tips."""
    for x in range(width):
        height = rng.randint(6, 16)
        for y in range(16 - height, 16):
            depth = y - (16 - height)
            color = C.WHITE if depth < 1 else C.YELLOW if depth < 5 else C.RED
            if rng.random() < 0.85:
                canvas.pixel(x, y, color)


def build():
    rng = random.Random(SEED)
    rocks = [[rng.randint(0, 28), 15 + rng.randint(0, 20), rng.choice((0.5, 0.7, 1.0))] for _ in range(9)]
    shards = [(rng.uniform(-4, 4), rng.uniform(-1.5, 1.5)) for _ in range(24)]
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        scene = Canvas()
        payoff = index >= OVER_AT

        if index >= NINE_AT:
            blaze(scene, rng, BLAZE_W)
        elif not payoff:
            scene.hline(0, 15, LENS_X - 2, C.BLUE)

        # Aura: grows and changes colour as the reading climbs.
        if index >= 3 and not payoff:
            stage = min(3, index * 4 // PAST_AT)
            color = [C.BLUE, C.CYAN, C.WHITE, C.YELLOW][stage]
            reach = 2 + min(4, index // 7)
            draw_aura(scene, rng, reach, color, tongues=2 + stage * 2)

        # Rocks float up, faster once the counter tops out.
        if 6 <= index < POP_AT:
            for rock in rocks:
                x, start, speed = rock
                y = start - (index - 6) * speed * (2 if index >= PAST_AT else 1)
                if 0 <= y < 15:
                    scene.rect(x, round(y), 2, 1 if speed > 0.8 else 2, C.MAGENTA, fill=True)


        if not payoff:
            draw_fighter(scene, super_mode=index >= PAST_AT)
        elif index >= NINE_AT:
            outlined(scene, lambda layer: draw_fighter(layer, super_mode=True))

        # The scouter readout.
        if index < POP_AT:
            value = power_level(index)
            if index >= PAST_AT:
                color = C.RED if index % 2 else C.YELLOW
            elif value >= 8000:
                color = C.YELLOW
            else:
                color = C.GREEN
            for y in range(0, 16, 2):
                scene.pixel(LENS_X - 2, y, C.GREEN)
            scene.text("POWER LEVEL", LENS_X + 1, 0, C.GREEN, proportional=True)
            digits = str(value)
            scene.text(digits, 95 - len(digits) * 6 + 1, 9, color)
            # A little reticle that twitches while it reads.
            if index % 3 != 2 or index >= PAST_AT:
                scene.glyph("+ARROW_R", LENS_X, 9, color)
            if index >= CRACK_AT:
                for x0, y0, x1, y1 in ((60, 0, 52, 6), (52, 6, 58, 10), (58, 10, 50, 15), (52, 6, 44, 8), (58, 10, 70, 12), (70, 12, 80, 9)):
                    scene.line(x0, y0, x1, y1, C.WHITE)
        elif index == POP_AT:
            scene.fill(C.WHITE)

        # Shards of scouter glass, flying from the readout.
        if POP_AT < index < POP_AT + 5:
            t = index - POP_AT
            for vx, vy in shards:
                scene.pixel(round(62 + vx * t * 2), round(8 + vy * t + 0.2 * t * t), C.GREEN)

        if payoff:
            strobe = [C.RED, C.YELLOW, C.WHITE][index % 3]
            if index < NINE_AT:
                text = "IT'S OVER"
                width = layout_text(text, 1, proportional=True)[1] * 2
                x = (96 - width) // 2
            else:
                text = "9000!!!"
                width = layout_text(text, 1, proportional=True)[1] * 2
                x = 95 - width
            big_text(scene, text, x, 1, strobe)
            if index in (OVER_AT, NINE_AT):
                for sx, sy in ((x - 2, 0), (x - 2, 15), (x + width + 1, 0), (x + width + 1, 15)):
                    scene.pixel(sx, sy, C.WHITE)

        shake = 0
        if PAST_AT <= index < POP_AT:
            shake = 1
        elif payoff:
            shake = 2 if index in (OVER_AT, OVER_AT + 1, NINE_AT, NINE_AT + 1) else 1
        frame = anim.frame()
        sx = rng.randint(-shake, shake) if shake else 0
        sy = rng.randint(-1, 1) if shake else 0
        frame.blit(scene, sx, sy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/over_9000.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
