#!/usr/bin/env python3
"""
Dad joke -- with rimshot.

Two little white skeletons stand at either end of the panel while the setup
types out between them in the small font: WHY DON'T SKELETONS / FIGHT EACH
OTHER? It holds long enough to read, the skeletons blink, then a beat of
nothing but three dots. The punchline lands in yellow: THEY DON'T HAVE /
THE GUTS. A drum kit is waiting on the right -- a red snare on its stand and
a yellow cymbal on a pole. Sticks hit: BA, DUM, a pause with the stick
raised high, then TSS! -- the cymbal flashes white and rocks back and forth,
throwing sparks. The words clear, the cymbal wobbles to rest, a green
cricket chirps into the silence, and the panel lets out a magenta GROAN.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

DELAY = 150
SETUP = ("WHY DON'T SKELETONS", "FIGHT EACH OTHER?")
PUNCH = ("THEY DON'T HAVE", "THE GUTS.")

SKELETON = [
    "..###..",
    ".#####.",
    ".#.#.#.",
    ".#####.",
    "..#.#..",
    "...#...",
    "#######",
    "#.###.#",
    "#..#..#",
    "#.###.#",
    "...#...",
    "..###..",
    "..#.#..",
    "..#.#..",
    "..#.#..",
    ".##.##.",
]

CRICKET = [
    "#...#",
    ".#.#.",
    ".###.",
    "#####",
    "#.#.#",
]

# Beat sheet: (name, frames). Holding a pose is just repeating it.
SCRIPT = (
    [("type1", 2), ("setup", 14), ("blink", 1), ("setup", 2)]
    + [("dots", 3)]
    + [("punch", 13)]
    + [("ba", 2), ("dum", 2), ("windup", 1)]
    + [("tss", 6)]
    + [("settle", 2), ("cricket", 3), ("groan", 1), ("groan2", 1)]
)


def sprite(canvas, rows, x, y, color, blink=False):
    for r, line in enumerate(rows):
        for c, cell in enumerate(line):
            if cell == "#":
                canvas.pixel(x + c, y + r, color)
    if blink:
        canvas.hline(x + 1, y + 2, 5, color)


def lines(canvas, pair, x, color, upto=None):
    first, second = pair
    if x == "center":
        canvas.small_text(first, "center", 2, color)
        if upto is None:
            canvas.small_text(second, "center", 9, color)
    else:
        canvas.small_text(first, x, 2, color)
        canvas.small_text(second, x, 9, color)


def drum_kit(canvas, snare_hit=False, tilt=0, flash=False, stick=None):
    """Snare at x 70..79, cymbal on a pole at x 88."""
    # Snare.
    canvas.hline(70, 8, 10, C.WHITE if not snare_hit else C.YELLOW)
    canvas.rect(70, 9, 10, 3, C.RED, fill=True)
    canvas.hline(70, 10, 10, C.WHITE)                       # lug band
    canvas.hline(70, 12, 10, C.WHITE)
    canvas.vline(74, 13, 3, C.CYAN)
    canvas.pixel(72, 15, C.CYAN)
    canvas.pixel(76, 15, C.CYAN)
    if snare_hit:
        canvas.pixel(69, 7, C.YELLOW)
        canvas.pixel(80, 7, C.YELLOW)
        canvas.pixel(74, 6, C.YELLOW)
    # Cymbal stand.
    canvas.vline(88, 5, 11, C.CYAN)
    canvas.pixel(86, 15, C.CYAN)
    canvas.pixel(87, 14, C.CYAN)
    canvas.pixel(89, 14, C.CYAN)
    canvas.pixel(90, 15, C.CYAN)
    color = C.WHITE if flash else C.YELLOW
    canvas.line(82, 4 - tilt, 94, 4 + tilt, color)
    canvas.pixel(88, 3, color)
    if flash:
        for x0, y0, x1, y1 in ((81, 1, 80, 0), (95, 1, 95, 0), (84, 7, 83, 8),
                               (93, 7, 94, 8), (88, 0, 88, 0)):
            canvas.line(x0, y0, x1, y1, C.WHITE)
    # Sticks (yellow wood, white tips).
    left, right = {
        None: ((64, 2, 69, 6), (86, 9, 81, 6)),
        "ba": ((64, 5, 71, 7), (86, 9, 81, 6)),
        "dum": ((64, 2, 69, 6), (85, 11, 78, 7)),
        "windup": ((64, 2, 69, 6), (78, 0, 80, 5)),
        "tss": ((64, 2, 69, 6), (77, 1, 83, 3)),
    }[stick]
    for x0, y0, x1, y1 in (left, right):
        canvas.line(x0, y0, x1, y1, C.YELLOW)
        canvas.pixel(x1, y1, C.WHITE)


def build():
    beats = [name for name, count in SCRIPT for _ in range(count)]
    anim = Animation(delay=DELAY)
    tss_tilts = [2, -2, 2, -1, 1, -1]
    tss_count = 0
    for index, beat in enumerate(beats):
        frame = anim.frame()
        if beat in ("type1", "setup", "blink"):
            sprite(frame, SKELETON, 0, 0, C.WHITE, blink=beat == "blink")
            sprite(frame, SKELETON, 89, 0, C.WHITE, blink=beat == "blink")
            lines(frame, SETUP, "center", C.WHITE,
                  upto=1 if beat == "type1" else None)
        elif beat == "dots":
            sprite(frame, SKELETON, 0, 0, C.BLUE)
            sprite(frame, SKELETON, 89, 0, C.BLUE)
            k = beats[:index].count("dots") + 1
            for d in range(k):
                frame.rect(40 + d * 6, 10, 2, 2, C.WHITE, fill=True)
        elif beat == "punch":
            lines(frame, PUNCH, 2, C.YELLOW)
            drum_kit(frame)
        elif beat in ("ba", "dum", "windup"):
            drum_kit(frame, snare_hit=beat != "windup", stick=beat)
            frame.text("BA", 2, 4, C.WHITE)
            if beat != "ba":
                frame.text("DUM", 18, 4, C.WHITE)
        elif beat == "tss":
            tilt = tss_tilts[tss_count]
            flash = tss_count % 2 == 0
            tss_count += 1
            drum_kit(frame, tilt=tilt, flash=flash,
                     stick="tss" if tss_count <= 2 else None)
            frame.text("BA", 2, 4, C.WHITE)
            frame.text("DUM", 18, 4, C.WHITE)
            frame.text("TSS!", 40, 4 + (tss_count % 2), C.YELLOW if flash else C.WHITE)
        elif beat == "settle":
            k = beats[:index].count("settle")
            drum_kit(frame, tilt=(1 if k == 0 else 0))
        elif beat == "cricket":
            k = beats[:index].count("cricket")
            drum_kit(frame)
            hop = 1 if k == 1 else 0
            sprite(frame, CRICKET, 4, 11 - hop, C.GREEN)
            if k != 1:
                frame.small_text("CHIRP", 12, 4 + 4 * (k // 2), C.GREEN)
        elif beat in ("groan", "groan2"):
            drum_kit(frame)
            sprite(frame, CRICKET, 4, 11, C.GREEN)
            frame.text("GROAN", 20, 4 + (beat == "groan2"), C.MAGENTA)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dad_joke.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
