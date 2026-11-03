#!/usr/bin/env python3
"""
I Voted -- an Election Day nudge, strictly nonpartisan.

A red-and-white striped flag with a blue canton of white star dots ripples
on its pole across the left of the panel the whole time. The wave travels
exactly two wavelengths per loop, so it never jumps at the seam.

On the right, an oval sticker slaps on: it lands oversized, squashes,
rebounds and settles -- white face, red rim, I VOTED in blue. It holds,
then a white glint sweeps across it, turning the rim and letters white as
it passes.

The text blinks out and swaps to DID YOU? in red -- a playful nudge -- and
holds. The sticker then peels away, shrinking to nothing, and GO VOTE!
stamps in letter by letter in tall double-height white letters, with
yellow, white and cyan stars twinkling in the margins around it and a
yellow shine running through the words before the loop restarts.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402
from jtkit.canvas import layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

FRAMES = 52
DELAY = 120
W, H = 96, 16

# --- flag -------------------------------------------------------------
POLE_X = 1
FLAG_X0, FLAG_WIDTH = 3, 34          # x 3..36
FLAG_Y0, STRIPE_ROWS = 1, 2          # seven stripes of two rows: y 1..14
STRIPES = [C.RED, C.WHITE, C.RED, C.WHITE, C.RED, C.WHITE, C.RED]
CANTON_W, CANTON_STRIPES = 14, 4     # blue field over the top four stripes
WAVELENGTH = 17
AMPLITUDE = 1.6
WAVE_CYCLES = 2                      # whole wavelengths per loop: seamless

# --- sticker ----------------------------------------------------------
SX, SY = 67.0, 7.5                   # oval centre
SRX, SRY = 27.5, 7.9                 # x 40..94, y 0..15
TEXT_Y = 4
OVAL_POWER = 2.8

# --- beats (frame indexes) --------------------------------------------
SLAP = {2: 1.35, 3: 0.75, 4: 1.12, 5: 0.94}   # frame -> sticker scale
SETTLED = 6
SHINE = range(15, 23)                # glint sweeps left to right
SWAP_BLANK = 25                      # face goes blank for a frame
DID_YOU = 26                         # 26-33 DID YOU?
PEEL = {34: 0.75, 35: 0.4, 36: 0.15}  # sticker peels away
GO_START = 37                        # GO VOTE! stamps in, one letter a frame
GO_SHINE = range(45, 51)

I_VOTED, DID_YOU_TEXT, GO_VOTE = "I VOTED", "DID YOU?", "GO VOTE!"


def flag_offset(x, f):
    along = (x - FLAG_X0) / FLAG_WIDTH
    phase = 2 * math.pi * WAVE_CYCLES * f / FRAMES
    return round(AMPLITUDE * along * math.sin(2 * math.pi * (x - FLAG_X0) / WAVELENGTH - phase))


def draw_flag(c, f):
    c.vline(POLE_X, 0, H, C.WHITE)
    c.pixel(POLE_X, 0, C.YELLOW)
    for x in range(FLAG_X0, FLAG_X0 + FLAG_WIDTH):
        dy = flag_offset(x, f)
        cx = x - FLAG_X0
        for stripe, color in enumerate(STRIPES):
            for row in range(STRIPE_ROWS):
                y = FLAG_Y0 + stripe * STRIPE_ROWS + row
                if cx < CANTON_W and stripe < CANTON_STRIPES:
                    ry = y - FLAG_Y0
                    # staggered star dots on the blue field
                    star = cx % 2 == 1 and ry % 2 == 1 and (cx // 2 + ry // 2) % 2 == 0 and cx < CANTON_W - 1
                    color = C.WHITE if star else C.BLUE
                    c.pixel(x, y + dy, color)
                else:
                    c.pixel(x, y + dy, color)


def oval_cells(scale):
    """(x, y) -> 'rim' | 'face' for an oval of the given scale."""
    rx, ry = SRX * scale, SRY * scale
    out = {}
    if rx < 1:
        return out
    # a superellipse: an oval with fuller shoulders, so text clears the rim
    inside = lambda x, y, a, b: abs((x - SX) / a) ** OVAL_POWER + abs((y - SY) / b) ** OVAL_POWER <= 1.0  # noqa: E731
    for y in range(H):
        for x in range(38, W):
            if inside(x, y, rx, ry):
                rim = not inside(x, y, rx - 1.2, ry - 1.1) if rx > 3 and ry > 2.5 else True
                out[(x, y)] = "rim" if rim else "face"
    return out


def draw_sticker(c, scale, text, text_color, rim_color=C.RED, shine=None):
    cells = oval_cells(scale)
    for (x, y), kind in cells.items():
        col = rim_color if kind == "rim" else C.WHITE
        if shine is not None and abs(x - shine - (y - SY) * 0.6) <= 1.5:
            # a slanted glint: rim flashes white, face goes cyan
            col = C.WHITE if kind == "rim" else C.CYAN
        c.pixel(x, y, col)
    if text:
        width = Canvas.text_width(text, proportional=True)
        x0 = round(SX - width / 2) + 1
        c.text(text, x0, TEXT_Y, text_color, proportional=True)


def tall_text(c, text, x, y, color, upto=None):
    """5x7 glyphs stretched to double height (5x14), proportional spacing."""
    positions, _ = layout_text(text, proportional=True)
    shown = 0
    for char, cell_x in positions:
        if char == " ":
            continue
        if upto is not None and shown >= upto:
            break
        shown += 1
        bitmap = glyph(char)
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    for k in (0, 1):
                        px, py = x + cell_x + col, y + 2 * row + k
                        c.pixel(px, py, color(px, py) if callable(color) else color)


GO_WIDTH = layout_text(GO_VOTE, proportional=True)[1]
GO_X = round(SX - GO_WIDTH / 2) + 1
GO_Y = 1
STAR_SPOTS = [(40, 3), (40, 12), (93, 3), (93, 12), (43, 0), (90, 15), (55, 15), (78, 0), (67, 15), (50, 0)]


def draw_star(c, x, y, size, color):
    c.pixel(x, y, color)
    if size >= 1:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= y + dy < H and not (dy and (y in (0, 15))):
                c.pixel(x + dx, y + dy, color)


def main():
    rnd = random.Random(1103)
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        draw_flag(c, f)

        if f in SLAP:
            draw_sticker(c, SLAP[f], None, None)
            if f == 2:
                # dust puffs where it smacks down
                for p in ((39, 2), (39, 13), (95, 1), (95, 14)):
                    c.pixel(*p, C.YELLOW)
        elif SETTLED <= f < DID_YOU:
            text = None if f == SWAP_BLANK else I_VOTED
            shine = None
            if f in SHINE:
                i = f - SHINE.start
                shine = 36 + round(i * (W - 32) / (len(SHINE) - 1))
            draw_sticker(c, 1.0, text, C.BLUE, shine=shine)
        elif DID_YOU <= f < min(PEEL):
            draw_sticker(c, 1.0, DID_YOU_TEXT, C.RED)
        elif f in PEEL:
            draw_sticker(c, PEEL[f], None, None)
        elif f >= GO_START:
            n = f - GO_START + 1
            color = C.WHITE
            if f in GO_SHINE:
                head = GO_X - 2 + (f - GO_SHINE.start) * (GO_WIDTH + 4) // (len(GO_SHINE) - 1)
                color = lambda x, _y, h=head: C.YELLOW if abs(x - h) <= 2 else C.WHITE  # noqa: E731
            tall_text(c, GO_VOTE, GO_X, GO_Y, color, upto=n)
            if n >= 3:
                for i, (sx, sy) in enumerate(STAR_SPOTS):
                    r = rnd.random()
                    if r < 0.35:
                        continue
                    col = (C.YELLOW, C.WHITE, C.CYAN)[(i + f) % 3]
                    big = r > 0.8 and sx in (40, 93)
                    draw_star(c, sx, sy, 1 if big else 0, col)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/vote_i_voted.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
