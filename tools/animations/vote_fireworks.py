#!/usr/bin/env python3
"""
Vote fireworks -- an Election Day show that spells VOTE in fireworks.

A night sky of twinkling blue, cyan and white stars. Four rockets climb from
the bottom on yellow-and-red tails, one under each letter, and burst in turn
-- red, white, blue, red -- each with a white flash and a crackle of yellow
sparkle. Every spark then curves inward to its own spot, and together they
lock into a huge "VOTE" fourteen rows tall: the 5x7 letters scaled 3x2, so
each spark becomes a chunky block, striped red and white like a flag.

A white highlight travels across VOTE while it holds. The blocks then slide
apart and regroup into "TODAY!" in white, which holds briefly with red and
blue sparkles twinkling round it, before the letters burst back into sparks
that fall and cool to blue embers -- just as the next rockets leave the
ground.

Nonpartisan by design: no parties, no candidates, just go vote.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.font import FONT_5X7  # noqa: E402

FRAMES = 53            # device maximum
DELAY = 110
SEED = 1103            # Nov 3
W, H = 96, 16

# Beat sheet (frame numbers)
RISE = 5               # frames a rocket spends climbing
LAUNCHES = [0, 1, 2, 3]
EXPLODE = 3            # frames the burst flies outward before homing in
SETTLED = 17           # VOTE complete
SWEEP_END = 31         # highlight has crossed VOTE
MORPH = (31, 35)       # blocks slide from VOTE to TODAY!
TODAY_END = 43         # TODAY! holds until here
BURST_LIFE = FRAMES - TODAY_END

BURST_COLORS = [C.RED, C.WHITE, C.BLUE, C.RED]
STRIPES = [C.RED, C.WHITE]   # alternate per glyph row in VOTE
TODAY_COLOR = C.WHITE

GRAVITY = 0.28


def layout(word, cw, ch, gap, y):
    """Cells (x, y, w, h) for a word in the 5x7 font scaled cw x ch."""
    glyphs = []
    for c in word:
        rows = FONT_5X7[c]
        if c == "!":                      # trim to its single ink column
            rows = [r[2] for r in rows]
        glyphs.append(rows)
    total = sum(len(g[0]) * cw for g in glyphs) + gap * (len(glyphs) - 1)
    x0 = (W - total) // 2
    cells, letters = [], []
    x = x0
    for li, rows in enumerate(glyphs):
        for r, row in enumerate(rows):
            for k, bit in enumerate(row):
                if bit == "#":
                    cells.append((x + k * cw, y + r * ch, cw, ch, li, r))
        letters.append(x + len(rows[0]) * cw / 2)
        x += len(rows[0]) * cw + gap
    return cells, letters, total


VOTE_CELLS, VOTE_CENTERS, VOTE_W = layout("VOTE", 3, 2, 4, 1)
TODAY_CELLS, _, TODAY_W = layout("TODAY!", 2, 2, 3, 1)
assert VOTE_W <= W and TODAY_W <= W


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    stars = [(rng.randrange(W), rng.randrange(H), rng.randrange(6),
              rng.choice([C.BLUE, C.BLUE, C.CYAN, C.WHITE]))
             for _ in range(30)]

    rockets = []
    for li, launch in enumerate(LAUNCHES):
        x = round(VOTE_CENTERS[li])
        apex = 4 + (li % 2)
        rockets.append((launch, x, apex, BURST_COLORS[li]))

    # One spark per VOTE cell, launched from its letter's rocket.
    sparks = []
    for cell in VOTE_CELLS:
        cx, cy, cw, chh, li, r = cell
        launch, rx, apex, color = rockets[li]
        ang = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(1.6, 2.6)
        sparks.append({
            "burst": launch + RISE, "origin": (rx, apex),
            "vel": (math.cos(ang) * speed * 1.6, math.sin(ang) * speed * 0.7),
            "target": (cx, cy), "size": (cw, chh),
            "color": color, "final": STRIPES[r % 2],
            "twinkle": rng.random(),
        })

    # Decorative sparks that just fall and fade.
    crackle = []
    for launch, rx, apex, color in rockets:
        for _ in range(8):
            ang = rng.uniform(0, 2 * math.pi)
            sp = rng.uniform(1.0, 2.2)
            crackle.append((launch + RISE, rx, apex, math.cos(ang) * sp * 1.8,
                            math.sin(ang) * sp * 0.8,
                            rng.choice([C.YELLOW, C.WHITE, color])))

    # VOTE -> TODAY! morph pairing, matched left-to-right.
    vote_sorted = sorted(VOTE_CELLS, key=lambda c: (c[0], c[1]))
    today_sorted = sorted(TODAY_CELLS, key=lambda c: (c[0], c[1]))
    morph_pairs = []
    for i, dst in enumerate(today_sorted):
        src = vote_sorted[i * len(vote_sorted) // len(today_sorted)]
        morph_pairs.append((src, dst))

    # TODAY! burst-out velocities, away from the word's centre.
    out_sparks = []
    for cx, cy, cw, chh, li, r in TODAY_CELLS:
        dx, dy = cx + 1 - W / 2, cy + 1 - H / 2
        ang = math.atan2(dy * 2.2, dx) + rng.uniform(-0.4, 0.4)
        sp = rng.uniform(1.4, 2.6) + abs(dx) / 30
        out_sparks.append((cx, cy, math.cos(ang) * sp * 1.8,
                           math.sin(ang) * sp * 0.8 - 0.6,
                           rng.choice([C.RED, C.WHITE, C.BLUE, C.WHITE])))

    def halo(cells):
        """Pixels within one of a word, kept starless so letters read cleanly."""
        out = set()
        for cx, cy, cw, chh, *_ in cells:
            for x in range(cx - 1, cx + cw + 1):
                for y in range(cy - 1, cy + chh + 1):
                    out.add((x, y))
        return out

    vote_halo, today_halo = halo(VOTE_CELLS), halo(TODAY_CELLS)

    for f in range(FRAMES):
        frame = anim.frame()
        quiet = (vote_halo if SETTLED - 1 <= f < MORPH[0] else
                 vote_halo | today_halo if f < MORPH[1] and f >= MORPH[0] else
                 today_halo if MORPH[1] <= f <= TODAY_END else set())

        # Stars twinkle on a 6-frame cycle, each with its own phase.
        for sx, sy, phase, color in stars:
            if (sx, sy) in quiet:
                continue
            p = (f + phase) % 6
            if p == 0:
                frame.pixel(sx, sy, C.WHITE)
            elif p < 4:
                frame.pixel(sx, sy, color)

        # Rockets climbing.
        for launch, x, apex, color in rockets:
            age = f - launch
            if 0 <= age < RISE:
                y = round(15 - (15 - apex) * age / RISE)
                frame.pixel(x, y + 2, C.RED)
                frame.pixel(x, y + 1, C.YELLOW)
                frame.pixel(x, y, C.WHITE)

        # Crackle: falls under gravity, cools through blue, gone.
        for start, rx, apex, vx, vy, color in crackle:
            age = f - start
            if 0 < age < 8:
                px = rx + vx * age
                py = apex + vy * age + 0.5 * GRAVITY * age * age
                c = color if age < 4 else C.BLUE
                if age < 4 and (age + int(px)) % 3 == 0:
                    c = C.YELLOW
                frame.pixel(round(px), round(py), c)

        # Main sparks: explode out, home in on VOTE, settle as blocks.
        if f < MORPH[0]:
            for s in sparks:
                age = f - s["burst"]
                if age < 0:
                    continue
                ox, oy = s["origin"]
                vx, vy = s["vel"]
                tx, ty = s["target"]
                cw, chh = s["size"]
                if age <= EXPLODE:
                    px, py = ox + vx * age, oy + vy * age
                    frame.pixel(round(px), round(py), s["color"])
                    if age == 0:
                        frame.rect(ox - 1, oy - 1, 3, 3, C.WHITE, fill=True)
                    continue
                ex, ey = ox + vx * EXPLODE, oy + vy * EXPLODE
                span = SETTLED - (s["burst"] + EXPLODE)
                t = ease((age - EXPLODE) / span)
                px, py = ex + (tx - ex) * t, ey + (ty - ey) * t
                if t >= 1:
                    color = s["final"]
                    if f < SWEEP_END:
                        head = 4 + (f - SETTLED) * (W - 8) / (SWEEP_END - SETTLED - 1)
                        d = abs(tx + 1 - head)
                        if d <= 4:
                            color = C.WHITE
                        elif d <= 7:
                            color = C.YELLOW
                    else:
                        head = None
                    frame.rect(tx, ty, cw, chh, color, fill=True)
                elif t > 0.75:
                    frame.rect(round(px), round(py), cw, chh, s["color"], fill=True)
                else:
                    c = s["color"]
                    if (f + int(s["twinkle"] * 4)) % 4 == 0:
                        c = C.YELLOW
                    frame.pixel(round(px), round(py), c)
                    frame.pixel(round(px) + 1, round(py), c)

        # Morph VOTE blocks into TODAY! blocks.
        elif f < MORPH[1]:
            t = ease((f - MORPH[0] + 1) / (MORPH[1] - MORPH[0] + 1))
            for src, dst in morph_pairs:
                px = src[0] + (dst[0] - src[0]) * t
                py = src[1] + (dst[1] - src[1]) * t
                c = STRIPES[src[5] % 2] if t < 0.5 else TODAY_COLOR
                frame.rect(round(px), round(py), 2, 2, c, fill=True)

        # TODAY! holds with sparkles.
        elif f < TODAY_END:
            for cx, cy, cw, chh, li, r in TODAY_CELLS:
                frame.rect(cx, cy, cw, chh, TODAY_COLOR, fill=True)
            for i in range(5):
                sx = rng.randrange(W)
                sy = rng.choice([0, 15, rng.randrange(H)])
                if frame.get(sx, sy) == C.BLACK:
                    frame.pixel(sx, sy, rng.choice([C.RED, C.BLUE, C.YELLOW]))

        # TODAY! bursts back into falling sparks.
        else:
            age = f - TODAY_END
            if age == 0:
                for cx, cy, cw, chh, li, r in TODAY_CELLS:
                    frame.rect(cx, cy, cw, chh, C.WHITE, fill=True)
                continue
            for cx, cy, vx, vy, color in out_sparks:
                px = cx + vx * age
                py = cy + vy * age + 0.5 * GRAVITY * age * age
                c = color if age < 4 else C.BLUE if age < 7 else None
                if c is None:
                    continue
                frame.pixel(round(px), round(py), c)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/vote_fireworks.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
