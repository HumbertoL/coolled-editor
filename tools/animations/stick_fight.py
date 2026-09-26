#!/usr/bin/env python3
"""
Stick Fight -- a Flash-era stick-figure brawl, then the winner tries to leave.

A homage to the old Xiao Xiao animations. A white and a red stick figure
square off in guard, bobbing. They step in: red throws a punch that white
blocks, white lands one on red's jaw, red answers with a side kick to the
chest. White crouches and launches a flying kick -- a big yellow burst -- and
red cartwheels backwards clean out through the right edge of the panel.

White pumps both fists in victory, then strolls right to follow... and bonks
face-first into the edge as if it were glass, which flashes cyan. Dazed
stars. White points up, crouches and jumps for the top: the top edge flashes
where his head hits it. So he turns and sprints the whole width left, speed
lines behind him, and splats into the left edge with an even bigger flash,
falling flat on his back. He sits up, slumps, and a little blue
rain cloud settles over his head.

The figures are skeletons: every pose is a set of joint angles (torso lean,
upper arm, forearm, thigh, shin) turned into lines, so poses can be mirrored,
rotated for a tumble, and their fists and feet located for the sparks.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16
FLOOR = 15  # the floor line; feet stand on row 14
HIP_Y = 8.0

TORSO, SHOULDER = 4.0, 3.4  # hip->neck length, hip->shoulder
HEAD = 1.6  # neck->head centre
UPPER, FORE = 2.6, 2.4
THIGH, SHIN = 3.0, 3.0

HERO, FOE = C.WHITE, C.RED


# -- the skeleton ---------------------------------------------------------


def pose(torso=0, front_arm=(15, 5), back_arm=(-15, -5), front_leg=(12, 0), back_leg=(-12, 0), drop=0):
    """
    Angles in degrees for a figure facing right. The torso angle is measured
    from straight up, limbs from straight down; positive always means towards
    the way the figure faces. ``drop`` lowers the hip, for bent knees.
    """
    return dict(torso=torso, fa=front_arm, ba=back_arm, fl=front_leg, bl=back_leg, drop=drop)


STAND = pose()
GUARD = pose(8, (55, 150), (25, 140), (28, 12), (-28, -8), drop=0.6)
GUARD2 = pose(10, (60, 155), (30, 145), (32, 14), (-30, -10), drop=1.2)
PUNCH = pose(18, (95, 95), (20, 150), (35, 20), (-35, -15), drop=0.8)
BLOCK = pose(-8, (55, 178), (25, 150), (22, 10), (-32, -18), drop=0.6)
KICK = pose(-35, (60, 120), (-60, -30), (100, 98), (-8, 0))
CROUCH = pose(30, (-45, -70), (-60, -90), (70, -25), (35, -45), drop=2.2)
FLY = pose(-20, (40, 110), (-80, -100), (96, 94), (-70, 15))
RECOIL = pose(-28, (-80, -130), (-40, -80), (30, 20), (-22, -10))
SPLAYED = pose(0, (100, 110), (-100, -110), (35, 35), (-35, -35))
VICTORY = pose(0, (125, 150), (-125, -150), (18, 0), (-18, 0))
PUMP = pose(0, (95, 175), (-95, -175), (22, 5), (-22, -5), drop=0.5)
WALK_A = pose(4, (-25, -10), (25, 30), (25, 12), (-25, -12))
WALK_B = pose(4, (15, 30), (-15, -5), (-20, -40), (10, 5))
BONKED = pose(12, (-30, -20), (40, 60), (15, 5), (-15, -5))
POINT_UP = pose(-8, (135, 150), (-20, -10), (12, 0), (-12, 0))
JUMP = pose(0, (-60, -40), (60, 40), (10, 0), (-10, 0))
SQUAT = pose(10, (80, 95), (-80, -95), (60, -30), (-50, 30), drop=2.0)
RUN_A = pose(25, (70, 150), (-70, -20), (75, 15), (-45, -100))
RUN_B = pose(25, (-70, -20), (70, 150), (-45, -100), (75, 15))
TURN = pose(5, (40, 120), (10, 90), (20, 5), (-20, -5))
LYING = pose(0, (60, 70), (-40, -20), (10, 0), (-10, 0))
SITTING = pose(28, (15, 35), (-5, 20), (90, 90), (84, 96))


def unit_down(angle, facing):
    a = math.radians(angle)
    return facing * math.sin(a), math.cos(a)


def unit_up(angle, facing):
    a = math.radians(angle)
    return facing * math.sin(a), -math.cos(a)


def skeleton(x, hip_y, p, facing=1, rot=0):
    """Joint positions for pose ``p``. ``rot`` spins the whole body forward."""
    hip = (x, hip_y + p["drop"])
    tx, ty = unit_up(p["torso"] + rot, facing)
    neck = (hip[0] + tx * TORSO, hip[1] + ty * TORSO)
    shoulder = (hip[0] + tx * SHOULDER, hip[1] + ty * SHOULDER)
    head = (hip[0] + tx * (TORSO + HEAD), hip[1] + ty * (TORSO + HEAD))
    j = dict(hip=hip, neck=neck, shoulder=shoulder, head=head)
    for key, root, l1, l2 in (
        ("fa", shoulder, UPPER, FORE),
        ("ba", shoulder, UPPER, FORE),
        ("fl", hip, THIGH, SHIN),
        ("bl", hip, THIGH, SHIN),
    ):
        a1, a2 = p[key]
        ux, uy = unit_down(a1 - rot, facing)
        mid = (root[0] + ux * l1, root[1] + uy * l1)
        vx, vy = unit_down(a2 - rot, facing)
        end = (mid[0] + vx * l2, mid[1] + vy * l2)
        j[key] = (root, mid, end)
    return j


def rnd(pt):
    return int(round(pt[0])), int(round(pt[1]))


def seg(frame, a, b, colour):
    (x0, y0), (x1, y1) = rnd(a), rnd(b)
    frame.line(x0, y0, x1, y1, colour)


def draw_figure(frame, x, hip_y, p, colour, facing=1, rot=0):
    j = skeleton(x, hip_y, p, facing, rot)
    for key in ("bl", "ba", "fl", "fa"):
        root, mid, end = j[key]
        seg(frame, root, mid, colour)
        seg(frame, mid, end, colour)
    seg(frame, j["hip"], j["neck"], colour)
    hx, hy = rnd(j["head"])
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        frame.pixel(hx + dx, hy + dy, colour)
    return j


# -- effects --------------------------------------------------------------


def spark(frame, pt, big=False):
    x, y = rnd(pt)
    frame.pixel(x, y, C.WHITE)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        frame.pixel(x + dx, y + dy, C.YELLOW)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        frame.pixel(x + 2 * dx, y + 2 * dy, C.YELLOW)
        if big:
            frame.pixel(x + dx, y + dy, C.YELLOW)
            frame.pixel(x + 3 * dx, y + 3 * dy, C.RED)
    if big:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            frame.pixel(x + 2 * dx, y + 2 * dy, C.YELLOW)


def dazed(frame, head, f):
    hx, hy = rnd(head)
    ring = [(-2, -1), (0, -2), (2, -1), (0, 0)]
    for k in range(3):
        dx, dy = ring[(f + k) % 4]
        if dy == 0:
            continue
        frame.pixel(hx + dx, hy - 1 + dy, C.YELLOW)


def edge_flash(frame, side, y, strength):
    """``side`` is 'left', 'right' or 'top'; strength 2 = impact, 1 = afterglow."""
    if side == "top":
        for x in range(W):
            d = abs(x - y)
            frame.pixel(x, 0, C.WHITE if d < 2 and strength == 2 else C.CYAN if d < 18 * strength else C.BLUE)
            if strength == 2 and d < 5:
                frame.pixel(x, 1, C.CYAN if d < 3 else C.BLUE)
        return
    x = W - 1 if side == "right" else 0
    inward = -1 if side == "right" else 1
    for row in range(H):
        d = abs(row - y)
        frame.pixel(x, row, C.WHITE if d < 2 and strength == 2 else C.CYAN if strength == 2 or d < 5 else C.BLUE)
    if strength == 2:
        for row in range(H):
            if abs(row - y) < 4:
                frame.pixel(x + inward, row, C.CYAN if abs(row - y) < 2 else C.BLUE)
        frame.pixel(x + 2 * inward, y, C.BLUE)


def speed_lines(frame, x, facing, f):
    for k, row in enumerate((5, 8, 11)):
        length = 5 + ((f + k) % 3) * 2
        start = x - facing * 4
        for i in range(length):
            frame.pixel(start - facing * i, row, C.BLUE if i > 2 else C.CYAN)


def rain_cloud(frame, head, f):
    hx, hy = rnd(head)
    cy = max(0, hy - 7)
    frame.hline(hx - 1, cy, 3, C.BLUE)
    frame.hline(hx - 3, cy + 1, 7, C.BLUE)
    for k, dx in enumerate((-2, 0, 2)):
        frame.pixel(hx + dx, cy + 2 + (f + k) % 3, C.CYAN)


# -- the choreography -----------------------------------------------------

# Each frame: (hero spec, foe spec, effects). A spec is
# (x, hip_y, pose, facing, rot) or None.


def script():
    s = {}

    def put(f, hero=None, foe=None, fx=()):
        s[f] = (hero, foe, list(fx))

    # 0-3 face-off, bobbing out of phase
    for f in range(4):
        put(f, (38, HIP_Y, GUARD if f % 2 else GUARD2, 1, 0), (72, HIP_Y, GUARD2 if f % 2 else GUARD, -1, 0))
    # 4-5 step in
    put(4, (42, HIP_Y, WALK_A, 1, 0), (68, HIP_Y, WALK_A, -1, 0))
    put(5, (46, HIP_Y, GUARD, 1, 0), (62, HIP_Y, GUARD2, -1, 0))
    # 6-7 red punches, white blocks
    put(6, (48, HIP_Y, BLOCK, 1, 0), (56, HIP_Y, PUNCH, -1, 0), [("spark", "foe", "fa")])
    put(7, (48, HIP_Y, BLOCK, 1, 0), (56, HIP_Y, PUNCH, -1, 0))
    # 8-9 white punches red in the face
    put(8, (51, HIP_Y, PUNCH, 1, 0), (58, HIP_Y, RECOIL, -1, 0), [("spark", "hero", "fa")])
    put(9, (51, HIP_Y, PUNCH, 1, 0), (60, HIP_Y, RECOIL, -1, 0))
    # 10-11 red side-kicks white in the chest
    put(10, (52, HIP_Y, RECOIL, 1, 0), (58, HIP_Y, KICK, -1, 0), [("spark", "foe", "fl")])
    put(11, (49, HIP_Y, RECOIL, 1, 0), (59, HIP_Y, KICK, -1, 0))
    # 12 reset, 13 white crouches
    put(12, (48, HIP_Y, GUARD2, 1, 0), (62, HIP_Y, GUARD, -1, 0))
    put(13, (48, HIP_Y, CROUCH, 1, 0), (63, HIP_Y, GUARD2, -1, 0))
    # 14-16 flying kick
    put(14, (51, 7.0, FLY, 1, 0), (63, HIP_Y, GUARD, -1, 0))
    put(15, (55, 6.5, FLY, 1, 0), (63, HIP_Y, GUARD2, -1, 0))
    put(16, (58, 6.5, FLY, 1, 0), (64, HIP_Y, RECOIL, -1, 0), [("bigspark", "hero", "fl")])
    # 17-20 red cartwheels out through the right edge
    put(17, (60, 7.5, FLY, 1, 0), (72, 7.0, SPLAYED, -1, -90))
    put(18, (61, HIP_Y, SQUAT, 1, 0), (82, 6.5, SPLAYED, -1, -180))
    put(19, (61, HIP_Y, STAND, 1, 0), (92, 7.0, SPLAYED, -1, -270))
    put(20, (61, HIP_Y, STAND, 1, 0), (103, 8.0, SPLAYED, -1, -360))
    # 21-24 victory
    put(21, (61, HIP_Y, VICTORY, 1, 0))
    put(22, (61, HIP_Y, PUMP, 1, 0))
    put(23, (61, HIP_Y, VICTORY, 1, 0))
    put(24, (61, HIP_Y, PUMP, 1, 0))
    # 25-28 stroll right to follow
    for k, f in enumerate(range(25, 29)):
        put(f, (67 + k * 6, HIP_Y, WALK_A if k % 2 == 0 else WALK_B, 1, 0))
    # 29-31 bonk into the right edge
    put(29, (92, HIP_Y, BONKED, 1, 0), fx=[("flash", "right", 2)])
    put(30, (89, HIP_Y, RECOIL, 1, 0), fx=[("flash", "right", 1), ("dazed",)])
    put(31, (89, HIP_Y, STAND, 1, 0), fx=[("dazed",)])
    # 32-37 the top: point, crouch, hop, bonk, fall, land
    put(32, (89, HIP_Y, POINT_UP, 1, 0))
    put(33, (89, HIP_Y, CROUCH, 1, 0))
    put(34, (89, 7.4, JUMP, 1, 0))
    put(35, (89, 6.6, JUMP, 1, 0), fx=[("flash", "top", 2)])
    put(36, (89, 7.4, RECOIL, 1, 0), fx=[("flash", "top", 1)])
    put(37, (89, HIP_Y, SQUAT, 1, 0), fx=[("dazed",)])
    # 38 turn, 39-44 sprint left
    put(38, (88, HIP_Y, TURN, -1, 0))
    for k, f in enumerate(range(39, 45)):
        put(f, (76 - k * 14, HIP_Y, RUN_A if k % 2 == 0 else RUN_B, -1, 0), fx=[("speed",)])
    # 45 splat into the left edge, 46-48 flat on his back, dazed
    put(45, (2, HIP_Y, BONKED, -1, 0), fx=[("flash", "left", 2)])
    put(46, (5, 10.0, RECOIL, -1, -50), fx=[("flash", "left", 1)])
    put(47, (7, 13.5, LYING, -1, -90), fx=[("dazed",)])
    put(48, (7, 13.5, LYING, -1, -90), fx=[("dazed",)])
    # 49-52 sits up and slumps; a little rain cloud arrives
    put(49, (9, 13.5, SITTING, -1, -35))
    for f in range(50, 53):
        put(f, (9, 13.5, SITTING, -1, 0), fx=[("cloud",)])
    return s


def main():
    anim = Animation(delay=DELAY)
    s = script()
    assert sorted(s) == list(range(FRAMES)), sorted(set(range(FRAMES)) - set(s))
    for f in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, FLOOR, W, C.BLUE)
        hero, foe, fx = s[f]
        joints = {}
        if foe:
            x, y, p, facing, rot = foe
            joints["foe"] = draw_figure(frame, x, y, p, FOE, facing, rot)
        if hero:
            x, y, p, facing, rot = hero
            if any(e[0] == "speed" for e in fx):
                speed_lines(frame, x, facing, f)
            joints["hero"] = draw_figure(frame, x, y, p, HERO, facing, rot)
        for e in fx:
            kind = e[0]
            if kind in ("spark", "bigspark"):
                end = joints[e[1]][e[2]][2]
                spark(frame, end, big=kind == "bigspark")
            elif kind == "flash":
                h = joints["hero"]
                edge_flash(frame, e[1], rnd(h["head"])[0] if e[1] == "top" else rnd(h["head"])[1], e[2])
            elif kind == "dazed":
                dazed(frame, joints["hero"]["head"], f)
            elif kind == "cloud":
                rain_cloud(frame, joints["hero"]["head"], f)
        if any(e[0] == "flash" for e in fx):
            # the figure stays in front of the glowing edge it hit
            x, y, p, facing, rot = hero
            draw_figure(frame, x, y, p, HERO, facing, rot)
    out = Path(__file__).resolve().parents[2] / "src/sample/stick_fight.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
