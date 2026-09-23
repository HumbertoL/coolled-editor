#!/usr/bin/env python3
"""
Leeroy Jenkins (2005) -- the plan, and then the plan meeting reality.

Four tiny adventurers huddle on the left while the strategy types out
beside them: a 32.33 survival chance whose threes keep coming, (REPEATING).
A fifth, in gold armour, strolls in late and announces OK LET'S / DO THIS.
He crouches. Then he goes: across the whole panel in seven frames, sword
out, legs pumping, a dust trail boiling up behind him and the party left
with red ! over their heads. The name comes after him, stretching as it's
shouted -- L, LE, LEE, LEEEE, LEEEEROY -- and JENKINS!!! slams in at
double size, the panel shaking and the letters strobing.

The dust is a particle list: every frame of the charge drops a few puffs at
his heels, and each puff fades WHITE -> CYAN -> BLUE as it rises and
spreads, so the trail hangs in the air for a beat after he is gone.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C, layout_text  # noqa: E402
from jtkit.font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 3233
ODDS_AT, REPEAT_AT = 2, 8
ARRIVE_AT = 14          # Leeroy walks in
SAY_AT = 16             # OK LET'S / DO THIS
CROUCH_AT = 25
CHARGE_AT = 28
NAME_AT = 35            # LEEEEROY stretches out
JENKINS_AT = 45
GROUND = 15
TEXT_X = 34
PARTY = [(13, C.BLUE), (17, C.GREEN), (21, C.MAGENTA), (25, C.CYAN)]
NAME_STEPS = ["L", "LE", "LEE", "LEEE", "LEEEE", "LEEEER", "LEEEERO", "LEEEEROY"]

PERSON = [".H.", "BBB", "BBB", "BBB", ".B.", "B.B", "B.B"]
HERO_RUN = [
    [
        "...WWW......",
        "...WWWW.....",
        "...WYY....W.",
        "....Y....W..",
        "..YYYYY.W...",
        ".YYYYYYW....",
        "YY.YYY......",
        "...YYY......",
        "..YY.YY.....",
        ".YY...YY....",
        "YY.....YY...",
    ],
    [
        "...WWW......",
        "...WWWW.....",
        "...WYY....W.",
        "....Y....W..",
        "..YYYYY.W...",
        ".YYYYYYW....",
        "YY.YYY......",
        "...YYY......",
        "...YYY......",
        "...YY.Y.....",
        "..YY..YY....",
    ],
]
HERO_STAND = [
    ".WWW..",
    ".WWWW.",
    ".WYY..",
    "..Y...",
    "YYYYY.",
    "YYYYYY",
    "Y.YYY.",
    "..YYY.",
    "..Y.Y.",
    "..Y.Y.",
    ".YY.YY",
]
HERO_CROUCH = [
    ".WWW......",
    ".WWWW.....",
    ".WYY....W.",
    "..Y....W..",
    "YYYYY.W...",
    "YYYYYW....",
    ".YYYY.....",
    ".YY.YY....",
    "YY...YY...",
]
HERO_COLORS = {"H": C.WHITE, "S": C.YELLOW, "Y": C.YELLOW, "W": C.WHITE}


def sprite(canvas, rows, x, bottom, palette):
    top = bottom - len(rows) + 1
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in palette:
                canvas.pixel(x + c, top + r, palette[ch])


def big_text(canvas, text, x, y, color, scale=2):
    """The 5x7 font at ``scale``x, proportional."""
    positions, _ = layout_text(text, 1, proportional=True)
    for char, cell_x in positions:
        bitmap = glyph(char)
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            canvas.pixel(x + (cell_x + col) * scale + dx, y + row * scale + dy, color)


def big_width(text):
    return layout_text(text, 1, proportional=True)[1] * 2


def typed(text, since, index, per_frame=2):
    return text[: max(0, (index - since) * per_frame)]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    dust = []           # [x, y, age, drift]

    for index in range(FRAMES):
        scene = Canvas()
        if index < NAME_AT:
            scene.hline(0, GROUND, 96, C.BLUE)

        # The party. They jump and get red ! the moment he goes.
        startled = CHARGE_AT <= index < NAME_AT
        for n, (px, color) in enumerate(PARTY):
            hop = 1 if startled and (index + n) % 2 == 0 else 0
            if index < NAME_AT:
                sprite(scene, PERSON, px, GROUND - 1 - hop, {"H": C.WHITE, "B": color})
                if startled:
                    scene.vline(px + 1, GROUND - 13 - hop, 3, C.RED)
                    scene.pixel(px + 1, GROUND - 9 - hop, C.RED)

        # The plan.
        if ODDS_AT <= index < SAY_AT:
            # The threes never stop; they just run out of panel.
            shown = typed("32.33" + "3" * 20, ODDS_AT - 1, index)
            while layout_text(shown, 1, proportional=True)[1] > 96 - TEXT_X:
                shown = shown[:-1]
            scene.text(shown, TEXT_X, 0, C.WHITE, proportional=True)
            if index >= REPEAT_AT:
                scene.text(typed("(REPEATING)", REPEAT_AT, index, 3), TEXT_X, 9, C.CYAN, proportional=True)

        # Leeroy: arrives late, talks, crouches, goes.
        hero_palette = HERO_COLORS
        if ARRIVE_AT <= index < CROUCH_AT:
            x = min(3, -6 + (index - ARRIVE_AT) * 3)
            sprite(scene, HERO_STAND, x, GROUND - 1, hero_palette)
        elif CROUCH_AT <= index < CHARGE_AT:
            sprite(scene, HERO_CROUCH, 1, GROUND - 1, hero_palette)
        elif CHARGE_AT <= index < NAME_AT:
            k = index - CHARGE_AT
            x = 1 + k * 14
            bob = k % 2
            sprite(scene, HERO_RUN[k % 2], x, GROUND - 1 - bob, hero_palette)
            # Speed lines behind him.
            for row, length in ((GROUND - 9, 8), (GROUND - 6, 14), (GROUND - 3, 10)):
                scene.hline(x - length - 1, row - bob, length, C.WHITE if k % 2 else C.CYAN)
            for _ in range(8):
                dust.append([x + rng.randint(-12, 2), GROUND - 1, 0, rng.uniform(-0.8, 0.4)])

        if SAY_AT <= index < CHARGE_AT:
            scene.text(typed("OK LET'S", SAY_AT, index), TEXT_X, 0, C.YELLOW, proportional=True)
            if index >= SAY_AT + 4:
                scene.text(typed("DO THIS", SAY_AT + 4, index), TEXT_X, 9, C.YELLOW, proportional=True)

        # Dust: rises, spreads, fades down the glow ramp, and goes.
        for puff in dust:
            x, y, age, drift = puff
            color = C.WHITE if age < 2 else C.CYAN if age < 4 else C.BLUE
            if age < 6 and index < NAME_AT + 1:
                size = 1 if age < 1 else 2
                scene.rect(round(x), round(y) - size + 1, size, size, color, fill=True)
            puff[0] += drift
            puff[1] -= 0.6 if age < 5 else 0.2
            puff[2] += 1

        # The name.
        if index >= NAME_AT:
            strobe = [C.WHITE, C.YELLOW, C.RED][index % 3]
            if index < JENKINS_AT:
                text = NAME_STEPS[min(len(NAME_STEPS) - 1, index - NAME_AT)]
                color = C.WHITE if index - NAME_AT < len(NAME_STEPS) - 1 else strobe
            else:
                text = "JENKINS!!!"
                color = C.WHITE if index == JENKINS_AT else strobe
            big_text(scene, text, (96 - big_width(text)) // 2, 1, color)

        # Thundering feet during the charge; the slam shakes hardest.
        shake_x = shake_y = 0
        if CHARGE_AT <= index < NAME_AT:
            shake_y = rng.randint(-1, 1)
        elif index >= NAME_AT:
            # The words are 94px wide, so they shake mostly vertically.
            shake_x = rng.randint(-1, 1)
            shake_y = rng.choice((-1, 1)) if index in (NAME_AT + 7, JENKINS_AT, JENKINS_AT + 1) else rng.randint(-1, 1)
        frame = anim.frame()
        frame.blit(scene, shake_x, shake_y)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/leeroy_jenkins.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
