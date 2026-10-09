#!/usr/bin/env python3
"""
Goose chase -- never make eye contact with a goose.

A man in a red hat strolls across a green park lawn munching a sandwich. A
white goose with a yellow beak and feet is grazing on the right. It looks up.
Its neck shoots forward, its wings flare, and HONK! fills the gap between
them. The man freezes, hands up, hat jumping on his head -- then bolts left,
legs a blur, dropping hat and sandwich, the goose flapping after him with
honks trailing and snatching the hat on the way past. Both exit. An empty
park, a distant AAAA. Then the goose struts back in wearing the red hat
with the sandwich in its beak, stops centre stage, and lets out one small,
smug "honk".
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
GROUND = 15

PALETTE = {"W": C.WHITE, "Y": C.YELLOW, "K": C.BLACK, "R": C.RED, "G": C.GREEN}

# Goose sprites, all facing right; feet on the last row.
GOOSE_STAND = [
    ".......WW..",
    ".......WKYY",
    ".......WW..",
    "........W..",
    "........W..",
    ".......WW..",
    "W.WWWWWWW..",
    "WWWWWWWWW..",
    ".WWWWWWW...",
    "...Y..Y....",
    "..YY.YY....",
]
GOOSE_GRAZE = [
    "W.WWWWWW....",
    "WWWWWWWWWW..",
    ".WWWWWWW.WW.",
    "...Y..Y..WKY",
    "..YY.YY.....",
]
GOOSE_ALERT = [
    ".......WW..",
    ".......WKYY",
    ".......WW..",
    ".......W...",
    ".......W...",
    ".......WW..",
    "W.WWWWWWW..",
    "WWWWWWWWW..",
    ".WWWWWWW...",
    "...Y..Y....",
    "..YY.YY....",
]
GOOSE_ANGRY = [  # wings up, neck thrust forward, beak open
    "..W....W......",
    "..WW..WW......",
    "...WWWW.......",
    "...WWWW...WW.Y",
    "WWWWWWWWWWWKY.",
    ".WWWWWWW.....Y",
    "..WWWWW.......",
    "...Y..Y.......",
    "..YY.YY.......",
]
GOOSE_FLAP_DOWN = [  # wings down, neck forward, beak open
    "..........WW.Y",
    "WWWWWWWWWWWKY.",
    ".WWWWWWWWW...Y",
    "WWWWWWWWW.....",
    "..WWWWW.......",
    "...Y..Y.......",
    "...YY.YY......",
]
GOOSE_RUN_UP = [  # wings up, legs mid-stride
    "..W....W......",
    "..WW..WW......",
    "...WWWW.......",
    "...WWWW...WW.Y",
    "WWWWWWWWWWWKY.",
    ".WWWWWWW.....Y",
    "..WWWWW.......",
    "..Y....Y......",
    ".YY.....YY....",
]
# Proud strut: chest out, head high, hat on, sandwich in beak.
GOOSE_PROUD_A = [
    "......RRR...",
    ".....RRRRR..",
    ".......WW...",
    ".......WKYG.",
    ".......WW.Y.",
    ".......WW...",
    ".......WWW..",
    "W.WWWWWWWW..",
    "WWWWWWWWWW..",
    ".WWWWWWWW...",
    "....Y.Y.....",
    "...YY.YY....",
]
GOOSE_PROUD_B = [  # high step: one foot raised
    "......RRR...",
    ".....RRRRR..",
    ".......WW...",
    ".......WKYG.",
    ".......WW.Y.",
    ".......WW...",
    ".......WWW..",
    "W.WWWWWWWW..",
    "WWWWWWWWWW..",
    ".WWWWWWWW...",
    "....Y..YY...",
    "...YY.......",
]


def sprite(frame, art, x, bottom, facing=1):
    """Draw ASCII art with its bottom row on ``bottom``; facing -1 mirrors."""
    height = len(art)
    width = max(len(row) for row in art)
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            col = c if facing > 0 else width - 1 - c
            frame.pixel(x + col, bottom - height + 1 + r, PALETTE[ch])


def person(frame, cx, facing, pose="walk", phase=0, hat=True, hat_lift=0,
           sandwich=True):
    """A little man centred on column cx, feet on row 14."""
    d = facing
    # Head and eye.
    frame.rect(cx - 1, 4, 3, 3, C.YELLOW, fill=True)
    if pose == "freeze":
        frame.pixel(cx, 5, C.BLACK)            # wide-eyed, mouth open below
        frame.pixel(cx + d, 5, C.BLACK)
        frame.pixel(cx + d, 6, C.BLACK)
    else:
        frame.pixel(cx + d, 5, C.BLACK)
    # Hat: brim then crown, optionally popped up off the head.
    if hat:
        frame.hline(cx - 2, 3 - hat_lift, 5, C.RED)
        frame.hline(cx - 1, 2 - hat_lift, 3, C.RED)
    # Body.
    frame.rect(cx - 1, 7, 3, 4, C.CYAN, fill=True)
    # Arms and legs by pose.
    if pose == "walk":
        # Front arm raised to the mouth with the sandwich; back arm swings.
        frame.pixel(cx + 2 * d, 7, C.CYAN)
        frame.pixel(cx + 2 * d, 6, C.CYAN)
        if sandwich:
            frame.pixel(cx + 2 * d, 4, C.YELLOW)
            frame.pixel(cx + 3 * d, 4, C.YELLOW)
            frame.pixel(cx + 2 * d, 5, C.GREEN)
            frame.pixel(cx + 3 * d, 5, C.GREEN)
            frame.pixel(cx + 3 * d, 6, C.YELLOW)
        frame.pixel(cx - 2 * d, 8 + (phase % 2), C.CYAN)
        if phase % 2 == 0:
            frame.vline(cx - 1, 11, 4, C.BLUE)
            frame.vline(cx + 1, 11, 4, C.BLUE)
        else:
            frame.vline(cx, 11, 2, C.BLUE)
            frame.line(cx, 12, cx - 2, 14, C.BLUE)
            frame.line(cx, 12, cx + 2, 14, C.BLUE)
    elif pose == "freeze":
        frame.line(cx - 2, 7, cx - 3, 4, C.CYAN)  # hands up
        frame.line(cx + 2, 7, cx + 3, 4, C.CYAN)
        if sandwich:
            frame.pixel(cx + 3 * d, 3, C.YELLOW)
            frame.pixel(cx + 3 * d, 2, C.GREEN)
            frame.pixel(cx + 3 * d, 1, C.YELLOW)
        frame.vline(cx - 1, 11, 4, C.BLUE)
        frame.vline(cx + 1, 11, 4, C.BLUE)
    elif pose == "run":
        # Arms flailing up, legs a blur of positions.
        frame.line(cx - 2, 7, cx - 3, 4 + phase % 2, C.CYAN)
        frame.line(cx + 2, 7, cx + 3, 5 - phase % 2, C.CYAN)
        frame.vline(cx, 11, 1, C.BLUE)
        for spread in (1, 3, 4):
            frame.line(cx, 12, cx + spread, 14, C.BLUE)
            frame.line(cx, 12, cx - spread, 14, C.BLUE)
        # Speed lines trailing behind.
        for k, row in enumerate((5, 8, 11)):
            frame.hline(cx - d * (5 + k % 2) - (3 if d > 0 else 0), row, 3, C.WHITE)


def dropped(frame, cx, falling=0):
    """The hat and sandwich left behind on the grass (``falling`` rows up)."""
    lift = max(0, falling) * 4
    frame.hline(cx - 2, 14 - lift, 5, C.RED)
    frame.hline(cx - 1, 13 - lift, 3, C.RED)
    frame.pixel(cx + 4, 14 - lift // 2, C.YELLOW)
    frame.pixel(cx + 5, 14 - lift // 2, C.YELLOW)
    frame.pixel(cx + 4, 13 - lift // 2, C.GREEN)
    frame.pixel(cx + 5, 13 - lift // 2, C.GREEN)


def ground(frame, offset=0):
    frame.hline(0, GROUND, 96, C.GREEN)
    for x in range(-2, 96, 7):
        frame.pixel(x + 3 + (x * 3) % 5, GROUND - 1, C.GREEN)  # grass tufts


def build():
    anim = Animation(delay=DELAY)
    goose_x = 74
    for i in range(FRAMES):
        f = anim.frame()
        ground(f)
        if i <= 13:
            # Stroll in from the left, eating. Goose grazing, pecking.
            cx = -4 + i * 3
            person(f, min(cx, 33), 1, "walk", phase=i)
            if i < 11:
                sprite(f, GOOSE_GRAZE, goose_x + (i % 3 == 0), GROUND - 1, facing=-1)
                if i % 4 == 1:
                    f.small_text("CHOMP", min(cx, 33) + 5, 0, C.WHITE)
            else:
                sprite(f, GOOSE_ALERT, goose_x, GROUND - 1, facing=-1)
                f.small_text("?", goose_x + 1, 0, C.WHITE)
        elif i <= 15:
            # Eye contact. A held beat.
            person(f, 33, 1, "walk", phase=0)
            sprite(f, GOOSE_ALERT, goose_x, GROUND - 1, facing=-1)
            f.text("!", goose_x + 1, 0, C.RED)
        elif i <= 22:
            # HONK! Wings flare, neck shoots forward.
            jolt = i <= 17
            person(f, 33, 1, "freeze", hat=True, hat_lift=(2 if i in (17, 18) else 1 if i in (16, 19) else 0))
            sprite(f, GOOSE_ANGRY, goose_x - 3, GROUND - 1, facing=-1)
            if i >= 17:
                f.text("HONK!", 41 + (i % 2), 1, C.WHITE if i % 2 else C.YELLOW)
            if jolt:
                f.small_text("!", 30, 0, C.WHITE)
                f.small_text("!", 37, 0, C.WHITE)
        elif i <= 24:
            # He turns to flee.
            person(f, 33 - (i - 23) * 2, -1, "run", phase=i, hat=False,
                   sandwich=False)
            sprite(f, GOOSE_ANGRY, goose_x - 3, GROUND - 1, facing=-1)
            dropped(f, 37, falling=24 - i)
            f.small_text("AAA!", 40, 0, C.WHITE)
        elif i <= 33:
            # Sprint left; goose gives chase, flapping and honking.
            t = i - 25
            cx = 29 - t * 8
            person(f, cx, -1, "run", phase=i, hat=False, sandwich=False)
            if cx > -4:
                f.small_text("AAA!", cx + 6, 0, C.WHITE)
            gx = goose_x - 3 - round(t * 7.5)
            art = GOOSE_RUN_UP if i % 2 else GOOSE_FLAP_DOWN
            if gx > 34:
                dropped(f, 37)
            else:
                # Snatched on the way past: the hat is now on the goose.
                top = 8 if art is GOOSE_RUN_UP else 7
                f.hline(gx + 1, top, 5, C.RED)
                f.hline(gx + 2, top - 1, 3, C.RED)
            art = GOOSE_RUN_UP if i % 2 else GOOSE_FLAP_DOWN
            sprite(f, art, gx, GROUND - 1, facing=-1)
            if i % 3 != 2 and gx > -6:
                f.small_text("HONK", gx + 2, 0, C.YELLOW)
            # Feathers left in the air.
            if t >= 1:
                f.pixel(gx + 16, 6 + t % 3, C.WHITE)
        elif i <= 38:
            # Empty park. A distant scream, then nothing.
            if i <= 36:
                f.small_text("AAAAAAA"[: 3 + (i - 34) * 2], 1, 3, C.CYAN)
        else:
            # The goose returns, strutting, hat on, sandwich in beak.
            t = i - 39
            gx = min(-12 + t * 6, 42)
            art = GOOSE_PROUD_B if (t % 2 and gx < 42) else GOOSE_PROUD_A
            sprite(f, art, gx, GROUND - 1, facing=1)
            if i >= 50:
                f.small_text("honk.", 56, 1, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/goose_chase.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
