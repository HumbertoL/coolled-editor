#!/usr/bin/env python3
"""
Blue wave tide -- a rising tide that floods the panel and floats a message.

A calm horizon: a yellow sun hangs over a low blue sea whose surface is a
thin line of drifting cyan ripples, with a glint of yellow reflection under
the sun. Then three swells roll in from the left, one after another, each
with a white foam cap, and behind each one the water settles a few rows
higher than before.

A final huge wave rears up past the top of the panel, its face cyan and its
curling crest white, and sweeps right across, swallowing the sun and leaving
the whole panel flooded blue with cyan currents streaking through it. Out of
the flood "BLUE WAVE" surfaces in white, each letter bobbing on its own part
of the swell while a cyan shimmer travels along the word. It holds, sinks
back under, and the water drains down to the calm start for a clean loop.

Pure scenery: no results, no parties, no candidates.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402
from jtkit.canvas import layout_text  # noqa: E402

FRAMES = 53            # device maximum
DELAY = 110
SEED = 1104
W, H = 96, 16

# Beat sheet (frame numbers, end-exclusive)
CALM_END = 5
SWELLS = [(5, 13.0, 11.0), (10, 11.0, 8.5), (15, 8.5, 6.0)]  # (start, from, to)
SWELL_LEN = 5
BIG = (20, 27)         # the huge wave crosses
RISE = (27, 32)        # text surfaces
HOLD_END = 45          # text holds (bobbing) until here
SINK_END = 48          # text sinks back under
# remaining frames: water drains back to CALM_LEVEL

CALM_LEVEL = 13.0
FLOOD_LEVEL = -1.0
SUN_X, SUN_Y = 80, 4

WORD = "BLUE WAVE"
WORD_W = Canvas.text_width(WORD)
WORD_X = (W - WORD_W) // 2
WORD_Y = 4
assert WORD_X >= 0 and WORD_X + WORD_W <= W


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def sigmoid(v):
    return 1 / (1 + math.exp(-v))


def ripple(x, f, amp=0.6):
    """Small travelling ripple; whole cycles per loop so it is seamless."""
    p = 2 * math.pi * f / FRAMES
    return amp * (math.sin(x * 0.45 - p * 6) * 0.6 + math.sin(x * 0.17 + p * 3) * 0.4)


def surface(f):
    """Per-column surface height (row of the water top) and crest strength."""
    heights, crest = [], []
    for x in range(W):
        level, bump = CALM_LEVEL, 0.0
        if f < CALM_END:
            level = CALM_LEVEL
        elif f < BIG[0]:
            for start, old, new in SWELLS:
                if f < start:
                    break
                t = (f - start + 0.5) / SWELL_LEN
                cx = -12 + t * (W + 24)
                if t <= 1:
                    level = old + (new - old) * sigmoid((cx - x) / 5)
                    bump = 3.2 * math.exp(-((x - cx) / 7) ** 2)
                else:
                    level = new
        elif f < BIG[1]:
            t = (f - BIG[0] + 0.5) / (BIG[1] - BIG[0])
            cx = -14 + t * (W + 30)
            old = SWELLS[-1][2]
            level = old + (FLOOD_LEVEL - old) * sigmoid((cx - x) / 3)
            # tall face in front of the crest, long back behind it
            d = x - cx
            if d > 0:
                bump = 9 * math.exp(-(d / 6) ** 2)
            else:
                bump = 9 * math.exp(-(d / 14) ** 2)
        elif f < SINK_END:
            level = FLOOD_LEVEL
        else:
            t = ease((f - SINK_END + 1) / (FRAMES - SINK_END))
            level = FLOOD_LEVEL + (CALM_LEVEL - FLOOD_LEVEL) * t
        heights.append(level - bump + ripple(x, f))
        crest.append(bump)
    return heights, crest


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    # Cyan currents streaking through the flood: (y, x0, length, speed)
    currents = [(rng.randrange(1, H), rng.randrange(W), rng.randrange(4, 9),
                 rng.choice([3, 4, 5])) for _ in range(9)]
    bubbles = [(rng.randrange(W), rng.randrange(H), rng.randrange(8))
               for _ in range(14)]

    for f in range(FRAMES):
        frame = anim.frame()
        heights, crest = surface(f)

        # Sun (drawn first; water paints over it).
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy * 1.0 <= 6.5:
                    frame.pixel(SUN_X + dx, SUN_Y + dy, C.YELLOW)

        # Water body.
        for x in range(W):
            s = heights[x]
            top = math.ceil(s - 0.5)
            for y in range(max(top, 0), H):
                frame.pixel(x, y, C.BLUE)
            if 0 <= top < H:
                if crest[x] > 1.6:
                    frame.pixel(x, top, C.WHITE)
                    if crest[x] > 2.6 and top + 1 < H:
                        frame.pixel(x, top + 1, C.CYAN)
                elif crest[x] > 0.7:
                    frame.pixel(x, top, C.CYAN)
                elif (x + f) % 5 < 2 or abs(s - round(s)) > 0.3:
                    frame.pixel(x, top, C.CYAN)
            # spray just above the tallest crests
            if crest[x] > 2.9 and top - 1 >= 0 and (x * 7 + f) % 3 == 0:
                frame.pixel(x, top - 1, C.WHITE)
            # sun glint on calm water
            if crest[x] < 0.3 and abs(x - SUN_X) <= 5 and top + 1 < H and 0 <= top:
                if (x + f) % 3 == 0 and heights[x] > 9:
                    frame.pixel(x, top + 1, C.YELLOW)

        # Steep faces: fill the jump between a column and its lower right
        # neighbour with white foam, so the wall reads as a breaking face.
        tops = [math.ceil(h - 0.5) for h in heights]
        for x in range(W - 1):
            if crest[x] > 1.2 and tops[x + 1] - tops[x] > 1:
                for y in range(max(tops[x], 0), min(tops[x + 1], H)):
                    frame.pixel(x, y, C.WHITE)
                    if x + 1 < W and y > max(tops[x], 0):
                        frame.pixel(x + 1, y, C.CYAN)

        # Curl of the big wave: white lip thrown forward of the crest.
        if BIG[0] <= f < BIG[1]:
            t = (f - BIG[0] + 0.5) / (BIG[1] - BIG[0])
            cx = round(-14 + t * (W + 30))
            for k in range(8):
                lx, ly = cx + k, (k * k) // 10
                frame.pixel(lx, ly, C.WHITE)
                frame.pixel(lx, ly + 1, C.WHITE if k > 5 else C.CYAN)
            for k in range(1, 4):
                frame.pixel(cx - k * 3, 0, C.WHITE)

        # Text phase: where the word sits this frame (None if absent).
        word_y = None
        if RISE[0] <= f < SINK_END:
            if f < RISE[1]:
                t = ease((f - RISE[0] + 1) / (RISE[1] - RISE[0]))
                word_y = H + (WORD_Y - H) * t
            elif f < HOLD_END:
                word_y = WORD_Y
            else:
                t = ease((f - HOLD_END + 1) / (SINK_END - HOLD_END + 1))
                word_y = WORD_Y + (H - WORD_Y) * t

        # Currents and bubbles in deep water (kept clear of the word).
        def clear_of_word(x, y):
            if word_y is None:
                return True
            return not (WORD_X - 2 <= x <= WORD_X + WORD_W + 1
                        and word_y - 2 <= y <= word_y + 9)

        for cy, x0, length, speed in currents:
            hx = (x0 + f * speed) % (W + 20) - 10
            for k in range(length):
                x = int(hx - k)
                if 0 <= x < W and cy > heights[x] + 1 and clear_of_word(x, cy):
                    frame.pixel(x, cy, C.CYAN)
        for bx, by, phase in bubbles:
            age = (f + phase) % 8
            y = by - age
            if 0 <= y < H and y > heights[bx] + 1 and clear_of_word(bx, y):
                frame.pixel(bx, y, C.CYAN if age < 6 else C.WHITE)

        # The word, each letter bobbing on its own part of the swell.
        if word_y is not None:
            shimmer = WORD_X - 6 + (f - RISE[0]) * 4.5
            positions, _ = layout_text(WORD)
            for i, (ch, cell_x) in enumerate(positions):
                if ch == " ":
                    continue
                bob = 0
                if f >= RISE[1] - 1:
                    bob = round(0.9 * math.sin(2 * math.pi * f / 8 - i * 0.8))
                frame.text(ch, WORD_X + cell_x, round(word_y) + bob,
                           lambda x, _y: C.CYAN if abs(x - shimmer) <= 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/blue_wave_tide.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
