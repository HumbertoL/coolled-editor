#!/usr/bin/env python3
"""
Treadmill -- one more tap on the + button.

A gym. A treadmill on the left with its belt stripes rolling, a console post
at the front reading SPD 3 in small text, and a jogger on the belt in a cyan
vest, legs alternating, arms pumping. A finger comes down and taps the +
button: SPD 5, the legs quicken. Tap: SPD 8. Tap: SPD 12 -- the jogger leans
back, arms flailing, legs a blur. Tap: SPD 99 in red, a frozen wide-eyed
beat, and the jogger is launched backwards off the belt, tumbling end over
end across the floor, and slams into the far right wall -- WHAM!, the wall
shaking -- then slides down it into a heap. The belt keeps rolling happily.
Button: the console readout changes to CAL 3.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
FLOOR = 15                      # the floor line
BELT_X0, BELT_X1, BELT_Y = 22, 50, 13
POST_X = 20                     # console post column
BUTTON_X, BUTTON_Y = 23, 9      # centre of the + button
WALL_X = 93
RUNNER_X = 36                   # jogger's hip column while on the belt
IMPACT_X = 89                   # where the tumbling body meets the wall

# Speed stages: (first frame, readout, belt pixels per frame, leg frames).
STAGES = [
    (0, "SPD 3", 1, 2),
    (8, "SPD 5", 2, 1),
    (15, "SPD 8", 3, 1),
    (21, "SPD 12", 4, 1),
    (28, "SPD 99", 6, 1),
]
TAPS = {7, 14, 20, 27}          # the finger is on the button
LAUNCH = 30                     # first airborne frame
IMPACT = 37
SLIDE_END = 42
CAPTION_FROM = 46

PALETTE = {"Y": C.YELLOW, "C": C.CYAN, "B": C.BLUE, "K": C.BLACK, "W": C.WHITE}

# Tumbling poses (head yellow, vest cyan, legs blue), rotating clockwise.
TUMBLE = [
    [   # upright, arms and legs flung out
        "..YYY..",
        "..YYY..",
        "C.YYY.C",
        ".CCCCC.",
        "..CCC..",
        "..CCC..",
        ".B...B.",
        "B.....B",
    ],
    [   # on the side, head to the right
        "..B.C..",
        "...CC..",
        "B.CCCYYY",
        "..CCCYYY",
        "...CCYYY",
        "..B.C...",
    ],
    [   # inverted
        "B.....B",
        ".B...B.",
        "..CCC..",
        "..CCC..",
        ".CCCCC.",
        "C.YYY.C",
        "..YYY..",
        "..YYY..",
    ],
    [   # on the side, head to the left
        "..C.B..",
        "..CC...",
        "YYYCCC.B",
        "YYYCCC..",
        "YYYCC...",
        "...C.B..",
    ],
]
SPLAT = [   # flat against the wall, limbs spread, eyes crossed
    "..YYY",
    "C.YWY",
    ".CYYY",
    ".CCC.",
    "CCCC.",
    ".CCC.",
    ".CCC.",
    "B.B..",
    "B..B.",
    "B..B.",
]
HEAP = [    # a pile at the foot of the wall, one leg still in the air
    "........B",
    ".......B.",
    "....CCCB.",
    "YYY.CCCC.",
    "YYYCCCCC.",
    "YYYCCCCB.",
]


def sprite(frame, art, x, y):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, PALETTE[ch])


def draw_gym(frame, belt_offset, shake=0):
    # Floor and the far wall; the wall jolts sideways on impact.
    frame.hline(0, FLOOR, WALL_X + shake, C.WHITE)
    for y in range(0, FLOOR):
        frame.vline(WALL_X + shake, y, 1, C.CYAN)
        frame.vline(WALL_X + 1 + shake, y, 1, C.BLUE if y % 3 == 1 else C.CYAN)
        frame.vline(WALL_X + 2 + shake, y, 1, C.CYAN)
    # Belt: blue deck with white stripe marks rolling backwards (rightwards).
    width = BELT_X1 - BELT_X0 + 1
    frame.rect(BELT_X0, BELT_Y, width, 2, C.BLUE, fill=True)
    for k in range(width):
        if (k - belt_offset) % 5 == 0:
            frame.pixel(BELT_X0 + k, BELT_Y, C.WHITE)
    frame.hline(BELT_X0 - 1, BELT_Y + 2, width + 2, C.CYAN)   # the frame
    # Console post rising from the front of the belt, with the + button.
    frame.vline(POST_X, 6, BELT_Y - 6, C.CYAN)
    frame.vline(POST_X + 1, 6, BELT_Y - 6, C.CYAN)
    frame.hline(BUTTON_X - 1, BUTTON_Y, 3, C.YELLOW)
    frame.vline(BUTTON_X, BUTTON_Y - 1, 3, C.YELLOW)
    # Readout panel on top of the post.
    frame.hline(0, 6, POST_X + 2, C.CYAN)


def draw_readout(frame, label, color):
    frame.small_text(label, 1, 0, color)


def draw_finger(frame, down):
    """A finger coming in from the upper right to the button."""
    tip_y = BUTTON_Y if down else BUTTON_Y - 3
    frame.line(BUTTON_X + 7, tip_y - 6, BUTTON_X + 2, tip_y - 1, C.YELLOW)
    frame.line(BUTTON_X + 8, tip_y - 6, BUTTON_X + 3, tip_y - 1, C.YELLOW)
    frame.pixel(BUTTON_X + 1, tip_y, C.WHITE)
    frame.pixel(BUTTON_X + 2, tip_y, C.WHITE)
    if down:
        frame.pixel(BUTTON_X - 2, BUTTON_Y, C.WHITE)   # the button lights
        frame.pixel(BUTTON_X, BUTTON_Y + 2, C.WHITE)


def draw_runner(frame, cx, phase, lean=0, panic=False, frozen=False):
    """Jogger facing left, feet on the belt. ``lean`` tilts the top back."""
    top = BELT_Y - 10
    hx = cx + lean                       # head column shifts back with the lean
    frame.rect(hx - 1, top, 3, 3, C.YELLOW, fill=True)
    if frozen:
        frame.pixel(hx - 1, top + 1, C.WHITE)
        frame.pixel(hx, top + 1, C.BLACK)
    else:
        frame.pixel(hx - 1, top + 1, C.BLACK)          # eye, looking ahead
    # Body: a vest, bending back for the lean.
    for r in range(4):
        bx = cx + (lean if r < 2 else lean // 2)
        frame.hline(bx - 1, top + 3 + r, 3, C.CYAN)
    # Arms.
    if panic:
        up = phase % 2
        frame.line(hx - 2, top + 3, hx - 4, top - 1 + up, C.CYAN)
        frame.line(hx + 2, top + 3, hx + 4, top - 2 + (1 - up), C.CYAN)
    elif frozen:
        frame.line(hx - 2, top + 3, hx - 3, top, C.CYAN)
        frame.line(hx + 2, top + 3, hx + 3, top, C.CYAN)
    else:
        f = phase % 2
        frame.pixel(cx - 2, top + 4 - f, C.CYAN)         # front arm pumping
        frame.pixel(cx - 3, top + 4 - f, C.CYAN)
        frame.pixel(cx + 2, top + 4 + f, C.CYAN)         # back arm
        frame.pixel(cx + 3, top + 4 + f, C.CYAN)
    # Legs from the hip at (cx, top + 7) down to the belt.
    hip = top + 7
    if frozen:
        frame.vline(cx - 1, hip, 3, C.BLUE)
        frame.vline(cx + 1, hip, 3, C.BLUE)
        return
    stride = 3 if panic else 2
    if phase % 2 == 0:
        frame.line(cx, hip, cx - stride, hip + 2, C.BLUE)
        frame.line(cx, hip, cx + stride, hip + 2, C.BLUE)
    else:
        frame.line(cx, hip, cx - 1, hip + 2, C.BLUE)
        frame.line(cx, hip, cx + 1, hip + 2, C.BLUE)
    if panic:
        # Motion blur: ghost legs either side.
        frame.pixel(cx - stride - 1, hip + 2, C.BLUE)
        frame.pixel(cx + stride + 1, hip + 2, C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    belt = 0
    for i in range(FRAMES):
        f = anim.frame()

        stage = max(k for k, (start, *_rest) in enumerate(STAGES) if i >= start)
        _start, label, belt_speed, leg_every = STAGES[stage]
        belt = (belt + belt_speed) % 5
        shake = 0
        if IMPACT <= i <= IMPACT + 3:
            shake = (1, -1, 1, 0)[i - IMPACT]
        draw_gym(f, belt, shake)

        # Readout: red at 99, and the calorie count for the button.
        if i >= CAPTION_FROM:
            draw_readout(f, "CAL 3", C.GREEN)
        else:
            draw_readout(f, label, C.RED if label == "SPD 99" else C.GREEN)

        if i in TAPS:
            draw_finger(f, down=True)
        elif i + 1 in TAPS:
            draw_finger(f, down=False)

        if i < LAUNCH:
            phase = i // leg_every
            lean = 0
            if stage == 3:
                lean = 2
            elif stage == 4:
                lean = 3
            draw_runner(f, RUNNER_X, phase, lean=lean, panic=stage >= 3,
                        frozen=stage == 4)
            if stage == 4 and i >= LAUNCH - 2:
                f.small_text("!", RUNNER_X + 8, 0, C.RED)
        elif i < IMPACT:
            # Launched backwards: an arc from the belt to the wall, rotating.
            t = i - LAUNCH                     # 0..6
            n = IMPACT - LAUNCH
            x = RUNNER_X + (IMPACT_X - RUNNER_X) * t / (n - 1)
            arc = -5.0 * (1 - ((t - 3) / 3) ** 2)
            y = 7 + arc
            pose = TUMBLE[t % 4]
            sprite(f, pose, round(x) - len(pose[0]) // 2, round(y) - len(pose) // 2)
            # A couple of motion streaks behind the body.
            f.hline(round(x) - 7, round(y), 3, C.WHITE)
            if t == 0:
                f.small_text("!", RUNNER_X + 8, 0, C.RED)
        elif i <= IMPACT + 3:
            # WHAM. Flat against the wall, the wall jolting.
            sprite(f, SPLAT, WALL_X + shake - 5, 2)
            for dx, dy in ((-7, 1), (-8, 5), (-7, 12), (-9, 3), (-9, 8)):
                f.pixel(WALL_X + shake + dx, dy, C.YELLOW if i % 2 else C.WHITE)
            f.text("WHAM!", 54 - (i == IMPACT), 2, C.RED if i % 2 else C.YELLOW)
        elif i <= SLIDE_END:
            # Sliding down the wall.
            t = i - IMPACT - 4                 # 0..1
            sprite(f, SPLAT, WALL_X - 5, 4 + 2 * t)
            f.text("WHAM!", 54, 2, C.YELLOW)
        else:
            sprite(f, HEAP, WALL_X - 9, FLOOR - len(HEAP))
            # Dizzy stars orbiting over the heap.
            orbit = ((0, 0), (2, 1), (4, 0), (2, -1))
            for k in range(2):
                dx, dy = orbit[(i + 2 * k) % 4]
                f.pixel(WALL_X - 8 + dx, 6 + dy, C.YELLOW if k else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/treadmill.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
