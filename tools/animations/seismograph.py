#!/usr/bin/env python3
"""
seismograph -- a drum recorder through a quake.

Paper scrolls left under a pen on a pivoting arm, with blue minute ticks
along the bottom edge moving with it. The green trace is quiet at first, a
pixel of jitter now and then; then the P-waves arrive, small and fast; then
the S and surface waves, swinging nearly the full sixteen rows, and a long
exponential decay back to the line. Each sample is joined to the last with a
vertical run, so the fast wiggles read as a solid band rather than dots. A
little building on the right sways in proportion to the pen -- sheared, so
its roof moves further than its base -- and a magnitude readout in a 3x5
mini-font climbs to M6.8 once the S-wave hits. The paper is periodic --
the quake is written only into samples the first frame never shows, and
tapered out before they wrap -- so the record scrolls off the left edge and
the last frame runs seamlessly into the first.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 1906

PEN_X = 78          # where the pen touches the paper
PIVOT = (84, 3)     # top of the pen arm
BASE = 8            # rest row of the trace
SCROLL = 3          # samples (= pixels) per frame
PERIOD = 53 * SCROLL          # samples in one loop of paper
P_AT, S_AT = 86, 100          # arrivals; frame 0 shows samples 0..78
QUAKE_END = PERIOD - 4        # quiet again before the paper wraps
READOUT_OFF = 44              # frame the magnitude clears, before the loop
HOUSE_X, HOUSE_W, HOUSE_TOP = 88, 7, 5

MINI = {
    "M": ["#.#", "###", "###", "#.#", "#.#"],
    ".": ["...", "...", "...", "...", ".#."],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "##.", "..#", "##."],
    "6": [".##", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "##."],
}


def mini_text(frame, text, x, y, colour):
    for char in text:
        rows = MINI[char]
        width = 1 if char == "." else 3
        start = 1 if char == "." else 0
        for r, line in enumerate(rows):
            for c in range(width):
                if line[start + c] == "#":
                    frame.pixel(x + c, y + r, colour)
        x += width + 1
    return x


def signal(rng):
    """
    Displacement in rows for one loop's worth of samples, rounded to the pixel.

    The paper is periodic: sample t and t + PERIOD are the same, so the last
    frame scrolls straight into the first. The quake is confined to the
    samples frame 0 does not show, and tapered to nothing before it wraps.
    """
    out = []
    for t in range(PERIOD):
        v = 0.0
        if rng.random() < 0.08:
            v += rng.choice((-1, 1)) * 0.6
        quake = 0.0
        taper = max(0.0, min(1.0, (QUAKE_END - t) / 14))
        if t >= P_AT:
            k = t - P_AT
            envelope = 2.2 * min(1, k / 4) * math.exp(-k / 30)
            quake += envelope * math.sin(k * 2.3) + rng.uniform(-0.4, 0.4)
        if t >= S_AT:
            k = t - S_AT
            envelope = 10.0 * min(1, k / 5) * math.exp(-k / 14)
            quake += envelope * math.sin(k * 0.95 + 0.4 * math.sin(k * 0.3)) + rng.uniform(-0.6, 0.6)
        out.append(max(-7, min(7, round(v + quake * taper))))
    return out


def build():
    rng = random.Random(SEED)
    history = PEN_X + 1
    loop = signal(rng)
    samples = [loop[t % PERIOD] for t in range(history + FRAMES * SCROLL + 1)]
    anim = Animation(delay=DELAY)
    peak = 0
    for index in range(FRAMES):
        frame = anim.frame()
        now = history + index * SCROLL  # sample under the pen
        # Minute ticks on the paper, scrolling with it.
        for x in range(PEN_X + 1):
            t = (now - (PEN_X - x)) % PERIOD
            if (t * 13) % PERIOD < 13:  # 13 ticks per loop, so they wrap too
                frame.pixel(x, 15, C.BLUE)
        # The trace.
        prev = None
        for x in range(PEN_X + 1):
            t = now - (PEN_X - x)
            y = BASE - samples[t]
            if prev is None:
                frame.pixel(x, y, C.GREEN)
            else:
                frame.vline(x, min(prev, y), abs(prev - y) + 1, C.GREEN)
            prev = y
        pen_y = BASE - samples[now]
        frame.line(PEN_X + 1, pen_y, PIVOT[0], PIVOT[1], C.WHITE)
        frame.pixel(PEN_X, pen_y, C.RED)
        frame.rect(PIVOT[0], PIVOT[1] - 1, 2, 2, C.YELLOW, fill=True)

        # The building, sheared by the shaking.
        recent = max(abs(s) for s in samples[now - 3 : now + 1])
        sway = 0
        if recent >= 3:
            sway = (1 if samples[now] > 0 else -1) * (2 if recent >= 6 else 1)
        for row in range(HOUSE_TOP, 15):
            lean = round(sway * (15 - row) / (15 - HOUSE_TOP))
            for col in range(HOUSE_W):
                x = HOUSE_X + col + lean
                wall = col in (0, HOUSE_W - 1) or row == HOUSE_TOP
                window = col in (2, 4) and row in (7, 10) and not wall
                if wall:
                    frame.pixel(x, row, C.WHITE)
                elif window:
                    frame.pixel(x, row, C.YELLOW)
        frame.hline(PIVOT[0] - 1, 15, 96 - PIVOT[0] + 1, C.RED)

        # Magnitude readout, masked out of the paper.
        if now >= S_AT + 3:
            peak = min(68, peak + 9)
        elif now >= P_AT + 2:
            peak = max(peak, 21)
        if peak and index < READOUT_OFF:
            frame.rect(0, 0, 16, 6, C.BLACK, fill=True)
            colour = C.RED if peak >= 60 and index % 2 else C.YELLOW
            mini_text(frame, f"M{peak // 10}.{peak % 10}", 0, 0, colour)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/seismograph.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
