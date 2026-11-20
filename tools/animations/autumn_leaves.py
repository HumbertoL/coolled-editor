#!/usr/bin/env python3
"""
Autumn leaves -- GIVE THANKS under a fall of maple leaves.

GIVE THANKS sits in white across the middle of a dark panel while red,
yellow and magenta maple leaves tumble down over it. Each leaf spins about
its own vertical axis as it falls -- full face, narrowing, edge-on, back
again -- and sways from side to side on its own phase. About half the
leaves are drawn behind the lettering and half in front, so they pass
both ways across the words.

Halfway through the loop a gust comes through: thin cyan and blue streaks
of wind race across the panel and every leaf is swept a full panel-width to
the right, slowing to a drift again as the wind dies.

Seamless: every motion is periodic in the loop. Each leaf falls a whole
number of drops per loop, its tumble period divides the frame count, and
the gust carries every leaf exactly one panel-width, so it wraps back to
where it started.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 110
W, H = 96, 16

TEXT = "GIVE THANKS"
TEXT_Y = 4
TEXT_COLOR = C.WHITE

# Tumble sprites, drawn centred on the leaf's position. A maple leaf turning
# about its vertical axis: full face, narrower, edge-on, narrower.
FULL = [
    "..#..",
    "#.#.#",
    "#####",
    ".###.",
    "..#..",
]
NARROW = [
    ".#.",
    "###",
    "###",
    ".#.",
]
EDGE = [
    "#",
    "#",
    "#",
    "#",
]
# a smaller oak-ish leaf for variety
SMALL_FULL = [
    ".#.",
    "###",
    ".#.",
]
SMALL_EDGE = [
    "#",
    "#",
    "#",
]
BIG_CYCLE = [FULL, FULL, NARROW, EDGE, NARROW]
SMALL_CYCLE = [SMALL_FULL, SMALL_FULL, SMALL_EDGE]

LEAF_COLORS = (C.RED, C.YELLOW, C.MAGENTA)
DROP = H + 8          # vertical travel for one fall, top edge to below the panel


def gust_offset(f):
    """Horizontal displacement from the gust: 0 -> W over the loop, steepest mid-loop."""
    t = f / FRAMES
    # a raised-cosine pulse of wind centred on t = 0.5
    return W * (t - math.sin(2 * math.pi * t) / (2 * math.pi))


def gust_strength(f):
    t = f / FRAMES
    return 1 - math.cos(2 * math.pi * t)   # 0..2


def make_leaves():
    rnd = random.Random(1126)
    leaves = []
    n = 20
    for i in range(n):
        big = i % 3 != 2
        cycle = BIG_CYCLE if big else SMALL_CYCLE
        leaves.append({
            "x0": (i * W / n + rnd.uniform(-2, 2)) % W,
            "phase": rnd.random(),
            "falls": rnd.choice((1, 1, 2)),
            "sway_amp": rnd.uniform(1.5, 3.5),
            "sway_n": rnd.choice((2, 3, 4)),
            "sway_p": rnd.random(),
            "color": LEAF_COLORS[i % 3],
            "cycle": cycle,
            "tumble_n": rnd.choice((4, 6)) if big else rnd.choice((6, 8)),
            "tumble_p": rnd.randrange(FRAMES),
            "front": i % 4 in (0, 1),
        })
    return leaves


LEAVES = make_leaves()


def sprite_at(leaf, f):
    """Tumble sprite for frame f: tumble_n full turns per loop, so seamless."""
    cyc = leaf["cycle"]
    pos = ((f + leaf["tumble_p"]) * leaf["tumble_n"] * len(cyc) / FRAMES) % len(cyc)
    return cyc[int(pos)]


def leaf_pos(leaf, f):
    t = f / FRAMES
    y = ((leaf["phase"] + t * leaf["falls"]) % 1.0) * DROP - 5
    sway = leaf["sway_amp"] * math.sin(2 * math.pi * (leaf["sway_n"] * t + leaf["sway_p"]))
    x = (leaf["x0"] + sway + gust_offset(f)) % W
    return x, y


def draw_leaf(c, leaf, f):
    x, y = leaf_pos(leaf, f)
    spr = sprite_at(leaf, f)
    h, w = len(spr), len(spr[0])
    x0 = round(x) - w // 2
    y0 = round(y) - h // 2
    for r, row in enumerate(spr):
        for col, ch in enumerate(row):
            if ch == "#":
                # wrap horizontally so a leaf crossing the edge stays whole
                c.pixel((x0 + col) % W, y0 + r, leaf["color"])


def draw_wind(c, f, rnd):
    s = gust_strength(f)
    if s < 1.6:
        return
    n = 2
    for _ in range(n):
        y = rnd.randrange(H)
        length = rnd.randint(6, 12)
        x = rnd.randrange(W)
        for i in range(length):
            c.pixel((x + i) % W, y, C.CYAN if i > length // 2 else C.BLUE)


def main():
    rnd = random.Random(2026)
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        draw_wind(c, f, rnd)
        for leaf in LEAVES:
            if not leaf["front"]:
                draw_leaf(c, leaf, f)
        c.text(TEXT, "center", TEXT_Y, TEXT_COLOR)
        for leaf in LEAVES:
            if leaf["front"]:
                draw_leaf(c, leaf, f)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/autumn_leaves.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
