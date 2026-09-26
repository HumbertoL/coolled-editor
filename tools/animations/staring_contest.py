#!/usr/bin/env python3
"""
Staring contest -- the sign challenges you, and loses.

"STARING CONTEST" in yellow, then a big green "GO!", then a pair of huge
eyes fills the panel: white sclera, cyan irises, black pupils with a white
glint, yellow eyebrows, staring straight out. They hold. Then they widen --
brows shoot up, pupils shrink -- the right lower lid twitches, red veins
creep in from the corners, blue tears well up along the bottom lids and the
left upper lid starts to quiver, faster and faster...

...and it blinks: the eyes slam shut into a squeezed ">  <" with the brows
crunched down and tears squirting out of the corners. The payoff is a small,
bloodshot, half-lidded pair of eyes looking at the floor beside "YOU WIN.",
then "BEST OF 3?".
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16

EYE_X = [30, 66]
RX = 13.5
BROW = C.YELLOW
IRIS = C.CYAN
LID = C.MAGENTA

# Beats, as frame ranges.
TITLE = range(0, 6)
GO = range(6, 9)
STARE = range(9, 17)
WIDEN = range(17, 20)
STRAIN = range(20, 36)     # twitch, veins, tears, quiver -- all escalating
BLINK = range(36, 40)
YOU_WIN = range(40, 46)
BEST_OF = range(46, 53)


def make_veins(seed):
    """Random-walk veins from the left and right corners, in growth order."""
    rnd = random.Random(seed)
    pixels = []
    for side in (-1, 1):
        for start_dy in (-2, 0, 2):
            x, y = side * 13, start_dy
            path = []
            for _ in range(8):
                path.append((x, y))
                x -= side
                if rnd.random() < 0.45:
                    y += rnd.choice((-1, 1))
                    y = max(-4, min(4, y))
            # a little branch halfway along
            bx, by = path[4]
            branch = []
            for k in range(1, 3):
                branch.append((bx - side * k, by + (k if start_dy >= 0 else -k)))
            pixels.append(path + branch)
    # interleave so all veins grow together
    order = []
    for step in range(max(len(p) for p in pixels)):
        for p in pixels:
            if step < len(p):
                order.append(p[step])
    return order


VEINS = [make_veins(3), make_veins(11)]


def draw_eye(c, i, cy, ry, lid_top=0.0, lid_bot=0.0, pupil=2.2, iris=4.2,
             veins=0.0, tears=0.0, look=(0, 0)):
    cx = EYE_X[i]
    top = cy - ry + lid_top
    bot = cy + ry - lid_bot
    vein_set = set(VEINS[i][: int(veins * len(VEINS[i]))])
    px, py = cx + look[0], cy + look[1]
    for y in range(H):
        yc = y + 0.5
        for x in range(int(cx - RX) - 1, int(cx + RX) + 2):
            xc = x + 0.5
            if ((xc - cx) / RX) ** 2 + ((yc - cy) / ry) ** 2 > 1.0:
                continue
            if yc < top:
                c.pixel(x, y, LID)          # the upper lid, pulled down
                continue
            if yc > bot:
                c.pixel(x, y, LID)
                continue
            color = C.WHITE
            if (x - cx, y - int(cy)) in vein_set:
                color = C.RED
            d2 = (xc - px) ** 2 + (yc - py) ** 2
            if d2 <= iris * iris:
                color = IRIS
            if d2 <= pupil * pupil:
                color = C.BLACK
            # tears pool along the bottom lid, deepest in the middle
            if tears > 0:
                edge = min(bot, cy + ry * (1 - ((xc - cx) / RX) ** 2) ** 0.5)
                depth = tears * (1.0 - 0.6 * abs(xc - cx) / RX)
                if yc > edge - depth:
                    color = C.CYAN if yc < edge - depth + 1 else C.BLUE
            c.pixel(x, y, color)
    # glint
    if pupil >= 1.4 and top < py - 1:
        c.pixel(int(px - 1), int(py - 1), C.WHITE)


def draw_brow(c, i, y, tilt=0, arch=0):
    """Thick brow over eye ``i``. tilt>0 drops the inner end (angry/scrunched)."""
    cx = EYE_X[i]
    inner = 1 if i == 0 else -1
    for k in range(-9, 10):
        t = k * inner / 9.0            # -1 outer .. +1 inner
        yy = y + round(tilt * (t + 1) / 2) - round(arch * (1 - t * t))
        c.pixel(cx + k, yy, BROW)
        c.pixel(cx + k, yy + 1, BROW)


def title_frame(c, f):
    c.text("STARING CONTEST", x="center", y=4, color=C.YELLOW)


def go_frame(c, f):
    c.text("GO!", x="center", y=4, color=C.GREEN)
    # tiny starting-flag ticks either side
    for x in (34, 60):
        c.pixel(x, 2, C.GREEN)
        c.pixel(x, 12, C.GREEN)


def stare_frame(c, f):
    for i in range(2):
        draw_eye(c, i, 9.5, 5.5)
        draw_brow(c, i, 1)


def widen_frame(c, f):
    k = f - WIDEN.start               # 0,1,2
    ry = [6.0, 6.7, 6.5][k]
    pupil = [1.9, 1.4, 1.4][k]
    for i in range(2):
        draw_eye(c, i, 9.0, ry, pupil=pupil, iris=3.4)
        draw_brow(c, i, 0, arch=1)


def strain_frame(c, f):
    s = f - STRAIN.start               # 0..15
    p = s / (len(STRAIN) - 1)
    veins = max(0.0, min(1.0, (s - 2) / 10))
    tears = max(0.0, min(3.2, (s - 5) * 0.32))
    for i in range(2):
        lid_top = 0.0
        lid_bot = 0.0
        brow_y = 0
        # twitch: right lower lid jumps on frames 0-1 and again at 7
        if i == 1 and s in (1, 7, 12):
            lid_bot = 2.0
            brow_y = 1
        # quiver: left upper lid shakes, getting worse
        if i == 0 and s >= 8:
            pattern = [0, 2, 0, 3, 1, 4, 1.5, 5]
            lid_top = pattern[s - 8]
        draw_eye(c, i, 9.0, 6.5, lid_top=lid_top, lid_bot=lid_bot,
                 pupil=1.3 + 0.2 * (s % 2) * (p > 0.6), iris=3.4,
                 veins=veins, tears=tears)
        draw_brow(c, i, brow_y + (1 if lid_top >= 2 else 0), arch=1)


def blink_frame(c, f):
    k = f - BLINK.start
    for i, cx in enumerate(EYE_X):
        d = 1 if i == 0 else -1        # > points right, < points left
        tip = cx + d * 7
        back = cx - d * 7
        c.line(back, 4, tip, 9, C.WHITE)
        c.line(back, 5, tip, 10, C.WHITE)
        c.line(back, 15, tip, 10, C.WHITE)
        c.line(back, 14, tip, 9, C.WHITE)
        draw_brow(c, i, 1, tilt=2)
        # tears squirting out of the outer corners
        ox = back - d * 1
        for j in range(3):
            t = k + 1 - j * 0.8
            if t <= 0:
                continue
            x = ox - d * int(t * 2.5)
            y = int(9 + (t - 1.2) ** 2 * 1.2 - 1)
            col = C.CYAN if j == 0 else C.BLUE
            c.pixel(x, y, col)
            c.pixel(x, y + 1, col)
            c.pixel(x - d, y, col)
    # squeeze lines between the eyes
    if k % 2 == 0:
        c.pixel(47, 8, C.YELLOW)
        c.pixel(48, 9, C.YELLOW)
        c.pixel(48, 11, C.YELLOW)
        c.pixel(47, 12, C.YELLOW)


def small_eyes(c, f, drip):
    """Sheepish: small, half-lidded, bloodshot, looking down at the floor."""
    for cx in (7, 20):
        for y in range(H):
            for x in range(cx - 6, cx + 7):
                xc, yc = x + 0.5 - cx, y + 0.5 - 9.0
                if (xc / 5.8) ** 2 + (yc / 4.0) ** 2 > 1 or yc < -0.5:
                    continue
                color = C.WHITE
                if (xc + 1.5) ** 2 + (yc - 2.0) ** 2 <= 5.0:
                    color = C.CYAN
                if (xc + 1.5) ** 2 + (yc - 2.5) ** 2 <= 1.6:
                    color = C.BLACK
                c.pixel(x, y, color)
        # heavy lid
        c.hline(cx - 5, 8, 11, C.YELLOW)
        # a vein each
        c.pixel(cx + 4, 10, C.RED)
        c.pixel(cx + 5, 10, C.RED)
        c.pixel(cx + 3, 11, C.RED)
    # a tear trickling down from the left eye
    ty = 13 + drip % 3
    c.pixel(3, ty, C.BLUE)
    if drip % 3 == 0:
        c.pixel(3, 12, C.CYAN)


def payoff_frame(c, f):
    if f in YOU_WIN:
        small_eyes(c, f, f - YOU_WIN.start)
        c.text("YOU WIN.", 33, 5, C.WHITE)
    else:
        small_eyes(c, f, f - BEST_OF.start)
        c.text("BEST OF 3?", 32, 5, C.YELLOW)


def main():
    anim = Animation(delay=DELAY)
    for f in range(FRAMES):
        c = anim.frame()
        if f in TITLE:
            title_frame(c, f)
        elif f in GO:
            go_frame(c, f)
        elif f in STARE:
            stare_frame(c, f)
        elif f in WIDEN:
            widen_frame(c, f)
        elif f in STRAIN:
            strain_frame(c, f)
        elif f in BLINK:
            blink_frame(c, f)
        else:
            payoff_frame(c, f)
    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/staring_contest.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
