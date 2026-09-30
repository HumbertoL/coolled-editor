#!/usr/bin/env python3
"""
Rickroll (2007) -- the bait and the switch.

A sober CLICK FOR FREE WIFI dialog fills its progress bar, a cursor arrives
to click it, and the panel glitches into a trench-coated, quiffed dancer
doing the step while NEVER / GONNA / GIVE / YOU / UP lands one word per beat.
A second glitch drops back to the loading bar for the loop.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 100
SEED = 2007
BAIT = 18
GLITCH = 2
BEAT = 6
WORDS = ["NEVER", "GONNA", "GIVE", "YOU", "UP"]
DANCE = BEAT * len(WORDS)
FRAMES = BAIT + GLITCH + DANCE + GLITCH + 1


def dancer(f, x, beat):
    """A 9px-wide figure. `beat` 0..3 picks the pose."""
    bob = beat % 2                       # body drops on odd beats
    top = 0 + bob
    # quiff and head
    f.rect(x + 2, top, 5, 2, C.RED, fill=True)
    f.pixel(x + 6, top - 1 if top else top, C.RED)
    f.pixel(x + 7, top, C.RED)
    f.rect(x + 2, top + 2, 5, 3, C.WHITE, fill=True)
    f.pixel(x + 3, top + 3, C.BLACK)
    f.pixel(x + 5, top + 3, C.BLACK)
    # trench coat
    f.rect(x + 2, top + 5, 5, 5, C.YELLOW, fill=True)
    f.vline(x + 4, top + 5, 5, C.RED)     # tie / lapel line
    # arms by pose
    if beat == 0:      # right arm up (point), left down
        f.line(x + 7, top + 5, x + 8, top + 1, C.YELLOW)
        f.pixel(x + 8, top, C.WHITE)
        f.line(x + 1, top + 6, x, top + 9, C.YELLOW)
    elif beat == 1:    # both arms out
        f.line(x + 1, top + 6, x - 1, top + 5, C.YELLOW)
        f.line(x + 7, top + 6, x + 9, top + 5, C.YELLOW)
    elif beat == 2:    # left arm up
        f.line(x + 1, top + 5, x, top + 1, C.YELLOW)
        f.pixel(x, top, C.WHITE)
        f.line(x + 7, top + 6, x + 8, top + 9, C.YELLOW)
    else:              # pumping fists
        f.line(x + 1, top + 6, x - 1, top + 8, C.YELLOW)
        f.line(x + 7, top + 6, x + 9, top + 8, C.YELLOW)
    # legs: alternate kicks
    ly = top + 10
    if beat in (0, 2):
        f.vline(x + 3, ly, 16 - ly, C.BLUE)
        f.vline(x + 5, ly, 16 - ly, C.BLUE)
    elif beat == 1:
        f.vline(x + 3, ly, 16 - ly, C.BLUE)
        f.line(x + 5, ly, x + 8, ly + 2, C.BLUE)
        f.hline(x + 3, 15, 2, C.WHITE)
    else:
        f.vline(x + 5, ly, 16 - ly, C.BLUE)
        f.line(x + 3, ly, x, ly + 2, C.BLUE)
        f.hline(x + 5, 15, 2, C.WHITE)


def cursor(f, x, y):
    for r, row in enumerate(["#.", "##", "###", "####", "##.#", "#..#"][:5]):
        for c, ch in enumerate(row):
            if ch == "#":
                f.pixel(x + c, y + r, C.WHITE)
    f.pixel(x, y, C.WHITE)


def bait(f, i):
    f.rect(0, 0, 96, 16, C.BLUE)
    f.rect(1, 1, 94, 14, C.BLACK, fill=True)
    f.text("FREE WIFI", "center", 2, C.WHITE, proportional=True)
    f.small_text("CLICK", 2, 2, C.CYAN)
    f.small_text("HERE", 75, 2, C.CYAN)
    f.rect(12, 11, 72, 3, C.CYAN)
    fill = min(70, round(70 * (i + 1) / (BAIT - 4)))
    f.rect(13, 12, fill, 1, C.GREEN, fill=True)
    if i >= BAIT - 5:                       # cursor arrives and clicks
        t = i - (BAIT - 5)
        cursor(f, 84 - t * 9, 6 + t) if t < 3 else cursor(f, 66, 8)
        if i == BAIT - 1:
            f.rect(1, 1, 94, 14, C.YELLOW)


def glitch(f, rng, pattern):
    for y in range(16):
        if rng.random() < 0.5:
            x = rng.randrange(0, 80)
            f.hline(x, y, rng.randrange(6, 40), rng.choice([C.RED, C.CYAN, C.MAGENTA, C.WHITE]))
    f.text("ERROR" if pattern else "LOADING", "center", 4, C.WHITE)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for i in range(BAIT):
        bait(anim.frame(), i)
    for g in range(GLITCH):
        glitch(anim.frame(), rng, g)
    for i in range(DANCE):
        f = anim.frame()
        beat = (i // 3) % 4
        w = i // BEAT
        k = i % BEAT
        col = [C.YELLOW, C.WHITE][k % 2] if k < 4 else C.CYAN
        word = WORDS[w]
        if w == 4:
            col = [C.RED, C.YELLOW, C.WHITE][k % 3]
        f.text(word, 22 + (72 - Animation_w(f, word)) // 2, 1, col, proportional=True)
        # ticker of the full lyric on the bottom, small text
        line = "NEVER GONNA GIVE YOU UP   "
        x = 22 - (i * 3) % (f.small_text_width(line) + 2)
        f.small_text(line + line, x, 10, C.MAGENTA)
        f.rect(0, 0, 19, 16, C.BLACK, fill=True)
        dancer(f, 4, beat)
    for g in range(GLITCH):
        glitch(anim.frame(), rng, g + 1)
    anim.frame()  # blank beat before the bar restarts
    return anim


def Animation_w(f, word):
    return f.text_width(word, proportional=True)


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rickroll.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
