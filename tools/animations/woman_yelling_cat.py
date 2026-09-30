#!/usr/bin/env python3
"""
Woman Yelling at a Cat (2019) -- the two-panel argument.

Left panel: a woman with her arm thrust out yells, shaking, red anger marks
flicking around her head. Right panel: a white cat with green eyes sits behind
a plate of vegetables at a table and stares back, unimpressed, blinking slowly.
The two alternate twice, then the table goes over in a spray of greens. The
cat does not move.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100

PAL = {"B": C.BLUE, "F": C.YELLOW, "K": C.BLACK, "R": C.RED, "W": C.WHITE,
       "G": C.GREEN, "C": C.CYAN, "M": C.MAGENTA}
WOMAN = [
    "..BBBBBB..",
    ".BBBBBBBB.",
    ".BFFFFFFB.",
    ".BRFFFFRB.",
    ".BFKFFKFB.",
    ".BFFFFFFB.",
    ".BFKKKKFB.",
    "..FKRRKF..",
    "...FFFF...",
]
WOMAN_CLOSED = WOMAN[:6] + [".BFFKKFFB.", "..FFFFFF..", "...FFFF..."]
TORSO = [
    "..WWWWWW..",
    ".WWWWWWWW.",
    "WWWWWWWWWW",
    "WWWWWWWWWW",
    "WWWWWWWWWW",
    "WWWWWWWWWW",
]
CAT = [
    "WW..........WW",
    "WWW........WWW",
    "WWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWW",
    "WWGGGWWWWGGGWW",
    "WWGKGWWWWGKGWW",
    "WWGGGWWWWGGGWW",
    "WWWWWWRRWWWWWW",
    ".WWWWWWWWWWWW.",
    "..WWWWWWWWWW..",
]
CAT_LID = [
    "WW..........WW",
    "WWW........WWW",
    "WWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWW",
    "WWGGGWWWWGGGWW",
    "WWWWWWWWWWWWWW",
    "WWWWWWRRWWWWWW",
    ".WWWWWWWWWWWW.",
    "..WWWWWWWWWW..",
]
CAT_SHUT = [r if k not in (4, 5, 6) else "WWKKKWWWWKKKWW" if k == 5
            else "WWWWWWWWWWWWWW" for k, r in enumerate(CAT_LID)]
VEG = [(61, "G"), (63, "R"), (65, "G"), (67, "Y"), (69, "G"), (71, "R"), (73, "G")]
VEG_COL = {"G": C.GREEN, "R": C.RED, "Y": C.YELLOW}
PHASES = [(0, 12, "yell"), (12, 22, "stare"), (22, 34, "yell"),
          (34, 44, "stare"), (44, 53, "flip")]


def spr(f, rows, x, y, pupil=0):
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "K" and rows is CAT:
                c += pupil
            f.pixel(x + c, y + r, PAL[ch])


def phase_of(i):
    for a, b, name in PHASES:
        if a <= i < b:
            return name, i - a
    return "stare", 0


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        name, k = phase_of(i)
        yelling = name in ("yell", "flip") and not (name == "flip" and k > 6)
        dx = (1 if i % 2 else -1) if yelling else 0
        dy = 1 if yelling and i % 3 == 0 else 0
        # left panel
        spr(f, TORSO, 5 + dx, 10)
        spr(f, WOMAN if (i % 2 == 0 or not yelling) and yelling else WOMAN_CLOSED,
            5 + dx, 1 + dy)
        arm_y = 10 + dy if name != "flip" else 8 + dy
        f.rect(15 + dx, arm_y, 8, 2, C.WHITE, fill=True)
        f.rect(23 + dx, arm_y, 12, 2, C.YELLOW, fill=True)
        f.rect(35 + dx, arm_y - 1, 3, 4, C.YELLOW, fill=True)
        if yelling:
            if i % 2:
                for p in ((17, 2), (18, 3), (19, 4), (17, 4), (19, 2)):
                    f.pixel(p[0] + dx, p[1], C.RED)
            else:
                f.small_text("!!", 20, 1, C.RED)
                f.pixel(16, 1, C.RED)
        f.vline(45, 0, 16, C.BLUE)
        # right panel
        if name == "stare":
            cyc = k % 10
            cat = CAT_SHUT if cyc in (4,) else CAT_LID if cyc in (3, 5) else CAT
        else:
            cat = CAT_LID if i % 2 and name == "yell" else CAT
        spr(f, cat, 60, 1, pupil=-1)
        t = k
        if name == "flip":
            tilt = min(t * 3, 18)
            if t < 5:
                for x in range(48, 96):
                    y = 14 - tilt * (x - 48) // 47
                    f.pixel(x, y, C.YELLOW)
                    f.pixel(x, y + 1, C.YELLOW)
            if t >= 6:
                f.hline(48, 14, 48, C.YELLOW)
                f.hline(48, 15, 48, C.YELLOW)
            if t >= 7:
                pass
            for n, (vx, vc) in enumerate(VEG):
                drift = ((n % 3) - 1) * (t + 1) // 2
                y = 12 - round(6 * t - 1.1 * t * t) + (n % 2)
                if y < 16:
                    f.pixel(vx + drift, y, VEG_COL[vc])
            py = 13 - round(5 * t - 1.0 * t * t)
            if py < 16 and t < 6:
                f.hline(58 + t, py, 16, C.CYAN)
        else:
            f.hline(48, 14, 48, C.YELLOW)
            f.hline(48, 15, 48, C.YELLOW)
            f.hline(58, 13, 16, C.CYAN)
            for vx, vc in VEG:
                f.pixel(vx, 12, VEG_COL[vc])
                f.pixel(vx + 1, 12, VEG_COL[vc])
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/woman_yelling_cat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
