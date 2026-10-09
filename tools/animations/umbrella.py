#!/usr/bin/env python3
"""
Umbrella -- the weather is watching.

Rain: blue and cyan drops falling in staggered columns across the whole
panel under a cloud line along the top. A man walks in from the left with
a closed umbrella, drops bouncing off his head. He opens it -- a wide red
dome -- and the rain stops instantly; a yellow sun appears top right. He
looks up. ? He closes it: rain, no sun. Opens it: sun. Closes it: rain.
Faster and faster, his face getting more annoyed. He gives up and stands
in the downpour with the umbrella shut, drenched, a puddle growing under
him and drips coming off his nose. Then the rain everywhere else stops and
the sun comes out, but one tiny cloud stays directly over his head, still
raining only on him. He shuffles right; it follows. TYPICAL.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
GROUND = 15

SUN = [
    "....#....",
    ".#.###.#.",
    "..#####..",
    "#.#####.#",
    "..#####..",
    ".#.###.#.",
    "....#....",
]
SUN_X, SUN_Y = 85, 0

# Script: (first frame, umbrella open?, raining?, annoyance level, eye)
# Frames not in a cue inherit the previous one.
CUES = [
    (0, False, True, 0, "front"),
    (9, False, True, 0, "front"),      # stopped, getting rained on
    (11, True, False, 0, "front"),     # open: rain stops, sun
    (13, True, False, 0, "up"),        # looks up
    (16, False, True, 1, "front"),     # close: rain
    (19, True, False, 1, "up"),        # open: sun
    (21, False, True, 1, "front"),
    (23, True, False, 2, "up"),
    (24, False, True, 2, "front"),
    (25, True, False, 2, "up"),
    (26, False, True, 2, "front"),
    (27, False, True, 2, "front"),     # gives up
    (33, False, "own", 2, "front"),    # sun out, one cloud over him
    (36, False, "own", 2, "right"),    # glances at the sun
    (38, False, "own", 2, "front"),
]
WALK_END = 8            # last walking frame
STAND_X = 40
SHUFFLE = range(39, 43)  # steps right, the cloud following
CAPTION_FROM = 45


def cue_for(i):
    current = CUES[0]
    for cue in CUES:
        if cue[0] <= i:
            current = cue
    return current


def draw_rain(f, i, columns=None, top=2, bottom=15):
    """Drops in staggered columns. ``columns`` limits them (the tiny cloud)."""
    cols = columns if columns is not None else range(0, 96, 3)
    span = bottom - top + 1
    for k, x in enumerate(cols):
        y = top + (k * 5 + i * 4) % span
        head = C.CYAN if k % 3 else C.BLUE
        f.pixel(x, y, head)
        for tail in (1, 2):
            if y - tail >= top:
                f.pixel(x, y - tail, C.BLUE)


def draw_cloud_line(f):
    f.hline(0, 0, 96, C.BLUE)
    for x in range(0, 96, 7):
        f.hline(x + 2, 1, 3, C.BLUE)


def draw_sun(f):
    for r, row in enumerate(SUN):
        for c, ch in enumerate(row):
            if ch == "#":
                f.pixel(SUN_X + c, SUN_Y + r, C.YELLOW)


def draw_small_cloud(f, cx, i):
    """A cloud wider than the umbrella was, with drips under it."""
    f.hline(cx - 5, 0, 13, C.WHITE)
    f.hline(cx - 7, 1, 15, C.WHITE)
    f.pixel(cx - 7, 0, C.BLUE)
    f.pixel(cx + 7, 0, C.BLUE)
    for k, x in enumerate((cx - 2, cx, cx + 2)):
        f.pixel(x, 2 + (i + k) % 2, C.CYAN)          # drops between cloud and head


def draw_person(f, cx, phase=0, walking=False, annoyed=0, eye="front",
                umbrella="closed", drenched=False, splash=False):
    # Head and face.
    f.rect(cx - 1, 4, 4, 5, C.YELLOW, fill=True)
    if drenched:
        f.hline(cx - 1, 4, 4, C.CYAN)                # hair plastered flat
    if eye == "up":
        f.pixel(cx + 1, 5, C.BLACK)
    elif eye == "right":
        f.pixel(cx + 2, 6, C.BLACK)
    else:
        f.pixel(cx + 1, 6, C.BLACK)
    if annoyed >= 1 and eye != "up":
        f.pixel(cx, 5, C.BLACK)                      # furrowed brow
    if annoyed >= 2:
        f.hline(cx, 8, 2, C.BLACK)                   # mouth set
    # Body.
    f.rect(cx - 1, 9, 4, 4, C.GREEN, fill=True)
    # Legs.
    if walking and phase % 2:
        f.line(cx, 13, cx - 2, 15, C.BLUE)
        f.line(cx + 1, 13, cx + 3, 15, C.BLUE)
    else:
        f.vline(cx - 1, 13, 3, C.BLUE)
        f.vline(cx + 2, 13, 3, C.BLUE)
    # Back arm.
    swing = (phase % 2) if walking else 0
    f.vline(cx - 2, 9 + swing, 3, C.GREEN)
    # Front arm and the umbrella.
    if umbrella == "closed":
        f.pixel(cx + 3, 10, C.GREEN)
        f.pixel(cx + 3, 11, C.YELLOW)                # hand
        f.vline(cx + 4, 11, 4, C.RED)                # furled, hanging down
        f.pixel(cx + 4, 15, C.WHITE)
    else:
        f.pixel(cx + 3, 9, C.GREEN)
        f.pixel(cx + 3, 8, C.YELLOW)                 # hand up
        f.vline(cx + 3, 3, 5, C.RED)                 # shaft, held above the head
        f.hline(cx, 0, 7, C.RED)                     # dome: 13 wide, 3 deep
        f.hline(cx - 2, 1, 11, C.RED)
        f.hline(cx - 3, 2, 13, C.RED)
        f.pixel(cx + 3, 0, C.WHITE)                  # ferrule
    if splash:
        if phase % 2:
            f.pixel(cx - 2, 4, C.WHITE)
            f.pixel(cx + 3, 4, C.WHITE)
        else:
            f.pixel(cx - 1, 3, C.WHITE)
            f.pixel(cx + 2, 3, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        _, is_open, rain, annoyed, eye = cue_for(i)

        if i <= WALK_END:
            cx = i * 5
            walking = i < WALK_END
        elif i in SHUFFLE:
            cx = STAND_X + (i - SHUFFLE.start + 1) * 2
            walking = True
        elif i >= SHUFFLE.stop:
            cx = STAND_X + len(SHUFFLE) * 2
            walking = False
        else:
            cx = STAND_X
            walking = False

        # Weather first, so the man stands in front of it.
        if rain is True:
            draw_cloud_line(f)
            draw_rain(f, i)
        else:
            draw_sun(f)

        if rain == "own":
            # One tiny cloud, raining only on him; he stands in front of it.
            draw_rain(f, i, columns=(cx - 6, cx - 4, cx + 5, cx + 7), top=2, bottom=14)
            draw_small_cloud(f, cx, i)

        drenched = i >= 27
        draw_person(f, cx, phase=i, walking=walking, annoyed=annoyed, eye=eye,
                    umbrella="open" if is_open else "closed", drenched=drenched,
                    splash=(rain and not is_open and i >= 2))

        if i in (14, 15):
            f.small_text("?", cx + 12, 0, C.WHITE)

        if drenched:
            # Puddle widening under him, drips off the nose.
            width = min(2 + (i - 27), 8)
            f.hline(cx - width // 2, GROUND, width + 3, C.CYAN)
            f.pixel(cx + 3, 7 + (i % 3), C.CYAN)
            f.pixel(cx - 2, 9 + ((i + 1) % 3), C.CYAN)

        if i >= CAPTION_FROM:
            f.small_text("TYPICAL.", 58, 6, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/umbrella.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
