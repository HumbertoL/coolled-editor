#!/usr/bin/env python3
"""
Harlem Shake (2013) -- one helmeted dancer, then everybody.

A lone figure in a shiny helmet flails in the middle of the panel while four
bystanders stand there with their backs to him, dim and unmoved. Then the
bass drops: a white flash, and the room goes wild -- five costumed dancers,
each with a different hat, thrashing under strobing blue, magenta and green.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

DELAY = 90
LONE = 22
FLASH = 2
WILD = 27
FRAMES = LONE + FLASH + WILD
STROBE = [C.BLUE, C.MAGENTA, C.GREEN]


def figure(f, x, top, pose, skin, body, hat=None, helmet=False, wild=True):
    """A figure ~5px wide, 13 tall, feet at top+12. pose 0..3."""
    squat = pose in (1, 3) and wild
    t = top + (2 if squat else 0)
    # head
    if helmet:
        f.rect(x, t, 5, 3, C.WHITE, fill=True)
        f.hline(x + 1, t + 2, 3, C.CYAN)       # visor
        f.pixel(x + 2, t - 1, C.RED)
        t += 3
    else:
        f.rect(x + 1, t, 3, 3, skin, fill=True)
        if hat == "spike":
            f.pixel(x + 2, t - 2, C.RED); f.pixel(x + 1, t - 1, C.RED); f.pixel(x + 2, t - 1, C.RED); f.pixel(x + 3, t - 1, C.RED)
        elif hat == "cone":
            f.pixel(x + 2, t - 2, C.YELLOW); f.hline(x + 1, t - 1, 3, C.YELLOW)
        elif hat == "wide":
            f.hline(x - 1, t - 1, 7, C.RED); f.hline(x + 1, t - 2, 3, C.RED)
        elif hat == "band":
            f.hline(x + 1, t, 3, C.RED); f.pixel(x, t + 1, C.RED); f.pixel(x + 4, t + 1, C.RED)
        elif hat == "horn":
            f.pixel(x, t - 1, C.WHITE); f.pixel(x + 4, t - 1, C.WHITE); f.pixel(x + 2, t - 1, C.WHITE)
        t += 3
    f.rect(x + 1, t, 3, 4, body, fill=True)
    # arms
    if wild:
        if pose == 0:
            f.line(x + 1, t, x - 1, t - 3, body); f.line(x + 3, t, x + 5, t - 3, body)
        elif pose == 1:
            f.line(x, t + 1, x - 2, t + 3, body); f.line(x + 4, t + 1, x + 6, t + 3, body)
        elif pose == 2:
            f.line(x + 1, t, x - 1, t - 3, body); f.line(x + 3, t + 1, x + 5, t + 3, body)
        else:
            f.line(x + 1, t + 1, x - 1, t + 3, body); f.line(x + 3, t, x + 5, t - 3, body)
    else:
        f.vline(x, t + 1, 4, body); f.vline(x + 4, t + 1, 4, body)
    ly = t + 4
    end = top + 13
    if wild and pose in (0, 2):
        f.line(x + 1, ly, x - 1, end - 1, body)
        f.line(x + 3, ly, x + 5, end - 1, body)
    else:
        f.vline(x + 1, ly, end - ly, body)
        f.vline(x + 3, ly, end - ly, body)


HATS = ["spike", "cone", "wide", "band", "horn"]
BODIES = [C.YELLOW, C.WHITE, C.CYAN, C.RED, C.YELLOW]
SKINS = [C.WHITE, C.YELLOW, C.WHITE, C.CYAN, C.WHITE]


def build():
    anim = Animation(delay=DELAY)
    for i in range(LONE):
        f = anim.frame()
        for x in (8, 22, 68, 82):
            figure(f, x, 2, 0, C.BLUE, C.BLUE, wild=False)
        pose = (i // 2) % 4
        top = 1 + (i % 2)
        figure(f, 45, top - 1, pose, C.WHITE, C.GREEN, helmet=True)
        f.hline(0, 15, 96, C.BLUE)
    for g in range(FLASH):
        f = anim.frame()
        if g == 0:
            f.fill(C.WHITE)
        else:
            f.text("DROP", "center", 4, C.WHITE)
    for i in range(WILD):
        f = anim.frame()
        bg = STROBE[i % 3]
        if i % 2 == 0:
            f.fill(bg)
        else:
            f.rect(0, 0, 96, 16, C.BLACK, fill=True)
        for n, x in enumerate((6, 24, 45, 66, 84)):
            pose = (i + n) % 4
            bob = (i + n * 2) % 2
            figure(f, x, 1 + bob, pose, SKINS[n], BODIES[n], hat=HATS[n] if n != 2 else None, helmet=(n == 2))
        if i % 2 == 0:
            f.hline(0, 15, 96, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/harlem_shake.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
