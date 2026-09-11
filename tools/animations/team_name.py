#!/usr/bin/env python3
"""
Team name -- DONUT HOLES becomes WAFFLING DONUT$, and back, seamlessly.

Forward: the old name flips out letter by letter from the left -- each glyph
squashes to a line and vanishes -- and the new one flips in the same way
behind it, while the team icon turns over from a frosted ring to a waffle
grid. A shine passes over the new name.

Back: the names sit on a vertical carousel. WAFFLING DONUT$ eases up out of
the panel while DONUT HOLES eases in from below, like a departure board
turning over. The loop closes on a hold of DONUT HOLES, so there is no cut.

MODE picks the return transition: "slide" (the default), "wipe" (an eraser
bar clears the new name and a reveal bar draws the old one), "dissolve"
(pixels swap at random) or "flip" (the forward cascade run backwards). Pass a mode on the command line to
write that variant to tools/out/ for comparison.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, font, layout_text  # noqa: E402

FRAMES = 53
DELAY = 150
MODE = "slide"

OLD, NEW = "DONUT HOLES", "WAFFLING DONUT$"
TEXT_X, TEXT_Y = 9, 4
HOLD_OLD_END, OUT_END, IN_END, SHINE_AT, SHINE_END, BACK_START, BACK_END = 4, 11, 20, 24, 30, 32, 48
LETTERS_PER_FRAME = 2

DONUT = [".#####.", "#######", "##...##", "##...##", "##...##", "#######", ".#####."]
WAFFLE = ["#######", "#.#.#.#", "#######", "#.#.#.#", "#######", "#.#.#.#", "#######"]
ICON_X, ICON_Y = 0, 4


def squashed(canvas, char, x, y, scale, color):
    bitmap = font.glyph(char)
    for row in range(font.GLYPH_HEIGHT):
        dest = y + 3 + int((row - 3) * scale)
        for col in range(font.GLYPH_WIDTH):
            if bitmap[row][col] == "#":
                canvas.pixel(x + col, dest, color)


def icon(canvas, rows, color, scale=1.0, dy=0):
    for r, line in enumerate(rows):
        dest = ICON_Y + dy + 3 + int((r - 3) * scale)
        for c, ch in enumerate(line):
            if ch == "#":
                canvas.pixel(ICON_X + c, dest, color)


def full_name(word, color, rows, dy=0):
    """The finished name with its icon, as an offscreen canvas."""
    canvas = Canvas(96, 16)
    canvas.text(word, TEXT_X, TEXT_Y + dy, color, proportional=True)
    icon(canvas, rows, color if rows is WAFFLE else C.MAGENTA, dy=dy)
    return canvas


def cascade(canvas, word, color, progress, direction):
    """Letters flipping in (direction +1) or out (-1); progress in letters."""
    positions, _ = layout_text(word, proportional=True)
    for i, (char, cell_x) in enumerate(positions):
        x = TEXT_X + cell_x
        phase = progress - i
        if direction < 0:
            phase = -phase + len(positions)
        # phase: <0 not yet, 0 squashed, 1 line, >=2 done (for "in"); mirrored for "out".
        if direction > 0:
            if phase >= 2:
                canvas.text(char, x, TEXT_Y, color)
            elif phase >= 1:
                squashed(canvas, char, x, TEXT_Y, 0.5, color)
            elif phase >= 0:
                canvas.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
        else:
            if phase >= 2:
                canvas.text(char, x, TEXT_Y, color)
            elif phase >= 1:
                squashed(canvas, char, x, TEXT_Y, 0.5, color)
            elif phase >= 0:
                canvas.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)


def build(mode=MODE):
    rng = random.Random(7)
    anim = Animation(delay=DELAY)
    old_canvas = full_name(OLD, C.MAGENTA, DONUT)
    new_canvas = full_name(NEW, C.YELLOW, WAFFLE)
    threshold = {(x, y): rng.random() for x in range(96) for y in range(16)}
    assert TEXT_X + Canvas.text_width(NEW, proportional=True) <= 96

    for index in range(FRAMES):
        frame = anim.frame()

        if index < HOLD_OLD_END or index >= BACK_END:
            frame.blit(old_canvas)

        elif index < OUT_END:
            k = index - HOLD_OLD_END
            progress = k * LETTERS_PER_FRAME
            # Letters vanish from the left: letter i is gone once progress > i + 1.
            positions, _ = layout_text(OLD, proportional=True)
            for i, (char, cell_x) in enumerate(positions):
                gone = progress - i
                x = TEXT_X + cell_x
                if gone <= 0:
                    frame.text(char, x, TEXT_Y, C.MAGENTA)
                elif gone == 1:
                    squashed(frame, char, x, TEXT_Y, 0.5, C.MAGENTA)
                elif gone == 2:
                    frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
            icon(frame, DONUT, C.MAGENTA, 1.0 if k < 4 else 0.4)

        elif index < IN_END:
            k = index - OUT_END
            progress = k * LETTERS_PER_FRAME
            positions, _ = layout_text(NEW, proportional=True)
            for i, (char, cell_x) in enumerate(positions):
                arrived = progress - i
                x = TEXT_X + cell_x
                if arrived >= 2:
                    frame.text(char, x, TEXT_Y, C.YELLOW)
                elif arrived == 1:
                    squashed(frame, char, x, TEXT_Y, 0.5, C.YELLOW)
                elif arrived == 0:
                    frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
            icon(frame, WAFFLE, C.YELLOW, 0.4 if k < 2 else 1.0)

        elif index < BACK_START:
            frame.blit(new_canvas)
            if SHINE_AT <= index < SHINE_END:
                head = TEXT_X - 3 + (index - SHINE_AT) * 16
                for x, y in list(frame.lit()):
                    if abs(x - head) <= 2 and x >= TEXT_X:
                        frame.pixel(x, y, C.WHITE)

        else:
            k = index - BACK_START
            span = BACK_END - BACK_START
            if mode == "wipe":
                half = span // 2
                if k < half:
                    # Eraser sweeping right to left over the new name.
                    bar = 96 - (96 * (k + 1)) // half
                    for (x, y), color in new_canvas._pixels.items():
                        if x < bar:
                            frame.pixel(x, y, color)
                    frame.rect(bar - 1, 0, 2, 16, C.WHITE, fill=True)
                else:
                    # Reveal bar sweeping left to right, drawing the old name.
                    j = k - half
                    bar = (96 * (j + 1)) // half
                    for (x, y), color in old_canvas._pixels.items():
                        if x < bar:
                            frame.pixel(x, y, color)
                    if bar < 96:
                        frame.rect(bar - 1, 0, 2, 16, C.WHITE, fill=True)
            elif mode == "slide":
                t = min(1.0, k / 12)
                ease = 3 * t * t - 2 * t * t * t          # ease in and out
                shift = round(12 * ease)
                frame.blit(full_name(NEW, C.YELLOW, WAFFLE, dy=-shift))
                frame.blit(full_name(OLD, C.MAGENTA, DONUT, dy=12 - shift))
            elif mode == "dissolve":
                t = (k + 1) / span
                for (x, y), color in new_canvas._pixels.items():
                    if threshold[(x, y)] > t:
                        frame.pixel(x, y, color)
                for (x, y), color in old_canvas._pixels.items():
                    if threshold[(x, y)] <= t:
                        frame.pixel(x, y, color)
            elif mode == "flip":
                half = 8
                if k < half:
                    progress = k * LETTERS_PER_FRAME
                    positions, _ = layout_text(NEW, proportional=True)
                    n = len(positions)
                    for i, (char, cell_x) in enumerate(positions):
                        gone = progress - (n - 1 - i)          # from the right
                        x = TEXT_X + cell_x
                        if gone <= 0:
                            frame.text(char, x, TEXT_Y, C.YELLOW)
                        elif gone == 1:
                            squashed(frame, char, x, TEXT_Y, 0.5, C.YELLOW)
                        elif gone == 2:
                            frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
                    icon(frame, WAFFLE, C.YELLOW, 1.0 if k < 6 else 0.4)
                else:
                    progress = (k - half) * LETTERS_PER_FRAME
                    positions, _ = layout_text(OLD, proportional=True)
                    n = len(positions)
                    for i, (char, cell_x) in enumerate(positions):
                        arrived = progress - (n - 1 - i)
                        x = TEXT_X + cell_x
                        if arrived >= 2:
                            frame.text(char, x, TEXT_Y, C.MAGENTA)
                        elif arrived == 1:
                            squashed(frame, char, x, TEXT_Y, 0.5, C.MAGENTA)
                        elif arrived == 0:
                            frame.hline(x, TEXT_Y + 3, font.GLYPH_WIDTH, C.WHITE)
                    icon(frame, DONUT, C.MAGENTA, 0.4 if k - half < 2 else 1.0)
    return anim


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else MODE
    animation = build(mode)
    root = Path(__file__).resolve().parents[2]
    out = root / "src/sample/team_name.jt" if mode == MODE else root / f"tools/out/team_name_{mode}.jt"
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
