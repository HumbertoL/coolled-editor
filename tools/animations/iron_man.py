#!/usr/bin/env python3
"""
Iron Man -- arc reactor, faceplate, repulsor.

Three beats in the suit's own order. The arc reactor kindles alone in the
dark, rings pushing outward as it climbs the only brightness ramp the panel
has: blue, cyan, white. The helmet drops over it -- faceplate first, a
one-frame clank of white on the seam -- and the eye slits come up. Then the
suit slides aside, a gauntlet charges in the middle of the panel, and the
repulsor fires the length of the sign with a shockwave off the palm. Red and
gold is one of the few real-world liveries this eight-colour palette can
actually hit.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

# Scene beats, by frame index.
HELMET_AT = 12      # the faceplate starts to fall
CLANK_AT = 18       # it seats, with a flash on the seam
SLIDE_AT = 28       # the suit steps aside for the gauntlet
CHARGE_AT = 36      # the palm spins up
FIRE_AT = 43        # and lets go
FIRE_TIMES = (43, 48)  # two shots, so the panel ends hot

REACTOR_X, REACTOR_Y = 48, 8
HELMET_HOME_X, HELMET_Y = 41, 3
HELMET_LEFT_X = 3
PALM_X, PALM_Y = 24, 4
HELMET = [
    "..RRRRRRRRR..",
    ".RRYYYYYYYRR.",
    "RRYYYYYYYYYRR",
    "RRY.......YRR",
    "RRY.......YRR",
    "RRYYYYYYYYYRR",
    "RRYYYYYYYYYRR",
    ".RY.......YR.",
    ".RYY.Y.Y.YYR.",
    "..RYYYYYYYR..",
    "...RRRRRRR...",
]
HELMET_COLORS = {"R": C.RED, "Y": C.YELLOW}
#: The faceplate's eye recess is drawn black; these light up inside it.
EYE_ROW = 3
EYE_SLITS = ((3, 5), (7, 9))
#: The forearm, then the fist, with the repulsor recessed in the palm.
GAUNTLET = [
    "..RRR..",
    ".RYYYR.",
    "RYYYYYR",
    "RYY.YYR",
    "RY...YR",
    "RYY.YYR",
    "RYYYYYR",
    ".RYYYR.",
    "..RRR..",
]
FOREARM_ROWS = (3, 4, 5)


def draw_reactor(frame, glow, rings):
    """The chest light: a ring, a triangle core, and expanding shockwaves."""
    for angle_step in range(24):
        angle = 2 * math.pi * angle_step / 24
        frame.pixel(
            REACTOR_X + round(3 * math.cos(angle)),
            REACTOR_Y + round(3 * math.sin(angle)),
            glow,
        )
    for offset in (-1, 0, 1):
        frame.pixel(REACTOR_X + offset, REACTOR_Y + 1, glow)
    frame.pixel(REACTOR_X, REACTOR_Y - 1, C.WHITE if glow == C.WHITE else glow)

    for radius in rings:
        for angle_step in range(48):
            angle = 2 * math.pi * angle_step / 48
            frame.pixel(
                REACTOR_X + round(radius * math.cos(angle)),
                REACTOR_Y + round(radius * 0.5 * math.sin(angle)),
                C.BLUE,
            )


def draw_helmet(frame, x, y, eyes):
    for row, line in enumerate(HELMET):
        for column, cell in enumerate(line):
            if cell in HELMET_COLORS:
                frame.pixel(x + column, y + row, HELMET_COLORS[cell])
    if eyes:
        for first, last in EYE_SLITS:
            frame.hline(x + first, y + EYE_ROW, last - first + 1, eyes)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index < HELMET_AT:
            # Kindling: the core climbs the ramp, rings leave every 4 frames.
            glow = (C.BLUE, C.CYAN, C.WHITE)[min(2, index // 4)]
            rings = [
                4 + (index - launch) * 3
                for launch in range(0, HELMET_AT, 4)
                if 0 <= index - launch < 5
            ]
            draw_reactor(frame, glow, rings)
            continue

        if index < SLIDE_AT:
            x = HELMET_HOME_X
            if index < CLANK_AT:
                # The faceplate falls in, easing out as it seats.
                t = (index - HELMET_AT) / (CLANK_AT - HELMET_AT)
                y = round(HELMET_Y - 16 * (1 - t) ** 2)
            else:
                y = HELMET_Y
            eyes = None
            if index == CLANK_AT:
                frame.hline(x - 2, y + len(HELMET), 17, C.WHITE)
            elif index > CLANK_AT:
                eyes = C.CYAN if index < CLANK_AT + 3 else C.WHITE
            draw_helmet(frame, x, y, eyes)
            continue

        # The suit steps left, and the gauntlet comes up.
        slide = min(1.0, (index - SLIDE_AT) / 6)
        x = round(HELMET_HOME_X + (HELMET_LEFT_X - HELMET_HOME_X) * slide)
        recoil = 1 if any(shot <= index <= shot + 1 for shot in FIRE_TIMES) else 0
        draw_helmet(frame, x - recoil, HELMET_Y, C.WHITE)

        if index < CHARGE_AT:
            continue
        palm_x = PALM_X - recoil
        for row in FOREARM_ROWS:
            frame.hline(x + 13, PALM_Y + row, palm_x - x - 12, C.RED)
        frame.hline(x + 13, PALM_Y + FOREARM_ROWS[0] - 1, palm_x - x - 12, C.YELLOW)
        for row, line in enumerate(GAUNTLET):
            for column, cell in enumerate(line):
                if cell != ".":
                    frame.pixel(palm_x + column, PALM_Y + row, HELMET_COLORS[cell])

        core_x, core_y = palm_x + 3, PALM_Y + 4
        if index < FIRE_AT:
            spin = index - CHARGE_AT
            glow = (C.BLUE, C.CYAN, C.WHITE)[min(2, spin // 3)]
            frame.pixel(core_x, core_y, glow)
            if spin >= 3:
                for offset in (-1, 1):
                    frame.pixel(core_x, core_y + offset, glow)
            if spin >= 5:
                for angle_step in range(16):
                    angle = 2 * math.pi * (angle_step / 16 + spin / 8)
                    frame.pixel(
                        core_x + round(4 * math.cos(angle)),
                        core_y + round(3 * math.sin(angle)),
                        C.CYAN,
                    )
            continue

        # Firing. Each shot decays over four frames rather than cutting.
        age = index - max(shot for shot in FIRE_TIMES if shot <= index)
        strength = max(0, 4 - age)
        if strength:
            frame.hline(core_x, core_y, 96 - core_x, C.WHITE)
            for offset in (-1, 1):
                frame.hline(core_x + 4, core_y + offset, 96, C.YELLOW)
            if strength >= 3:
                for offset in (-2, 2):
                    frame.hline(core_x + 8, core_y + offset, 96, C.RED)
            # Shockwave off the palm, one ring per frame.
            radius = 4 + age * 3
            for angle_step in range(32):
                angle = 2 * math.pi * angle_step / 32
                frame.pixel(
                    core_x + round(radius * math.cos(angle)),
                    core_y + round(radius * 0.6 * math.sin(angle)),
                    C.CYAN,
                )
        else:
            frame.pixel(core_x, core_y, C.CYAN if age % 2 else C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/iron_man.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
