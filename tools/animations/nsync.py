#!/usr/bin/env python3
"""
NSYNC, Bye Bye Bye -- five marionettes, and then the strings go.

The video's conceit, at 96x16: five figures hang from strings and jerk
through the puppet choreography, each one a quarter-beat behind the last so
the move travels down the line. Poses snap between fixed positions rather
than easing -- a puppet has no in-betweens, and the jerk is the joke. Then
the strings part in a flash of white, whip back up out of frame, and the
five dance free before the panel gives them the last word, one BYE per beat.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

# Scene beats, by frame index.
SNAP_AT = 28        # the strings part
FREE_AT = 32        # dancing without them
BYE_AT = 42         # BYE ... BYE BYE ... BYE BYE BYE

MEMBERS = [(9, C.WHITE), (26, C.CYAN), (43, C.YELLOW), (60, C.MAGENTA), (77, C.GREEN)]
HEAD_Y = 6
GROUND = 15
#: (left arm rise, right arm rise, stance width) -- four poses, no tweening.
POSES = [(-2, 2, 2), (2, -2, 3), (3, 3, 1), (0, 0, 3)]
BYE_X, BYE_Y = 15, 5


def draw_member(frame, cx, top, pose, color):
    left_arm, right_arm, stance = POSES[pose]
    frame.rect(cx - 1, top, 3, 3, color, fill=True)
    frame.pixel(cx, top + 1, C.BLACK)
    torso_top, torso_bottom = top + 3, top + 6
    frame.vline(cx, torso_top, torso_bottom - torso_top + 1, color)
    shoulder = torso_top + 1
    frame.line(cx - 1, shoulder, cx - 3, shoulder - left_arm, color)
    frame.line(cx + 1, shoulder, cx + 3, shoulder - right_arm, color)
    frame.line(cx, torso_bottom, cx - stance, GROUND, color)
    frame.line(cx, torso_bottom, cx + stance, GROUND, color)
    return shoulder, left_arm, right_arm


def draw_strings(frame, cx, top, shoulder, left_arm, right_arm, cut):
    """Head and wrist strings. ``cut`` is how far they have whipped back."""
    for x, y in ((cx, top), (cx - 3, shoulder - left_arm), (cx + 3, shoulder - right_arm)):
        if cut is None:
            frame.vline(x, 0, y, C.BLUE)
        elif cut < y:
            frame.vline(x, 0, max(0, y - cut * 4), C.BLUE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index >= BYE_AT:
            beat = index - BYE_AT
            words = min(3, beat // 3 + 1)
            fresh = beat % 3 == 0
            frame.text(" ".join(["BYE"] * words), BYE_X, BYE_Y, C.WHITE if fresh else C.MAGENTA)
            if fresh:
                frame.hline(0, 0, 96, C.CYAN)
                frame.hline(0, 15, 96, C.CYAN)
            continue

        free = index >= FREE_AT
        for order, (cx, color) in enumerate(MEMBERS):
            if free:
                # Off the strings: faster, and they get some air.
                pose = (index + order) % len(POSES)
                top = HEAD_Y - (1 if (index + order) % 3 == 0 else 0)
            else:
                pose = (index // 2 + order) % len(POSES)
                top = HEAD_Y + (1 if (index // 2 + order) % 2 else 0)
            shoulder, left_arm, right_arm = draw_member(frame, cx, top, pose, color)

            if index < SNAP_AT:
                draw_strings(frame, cx, top, shoulder, left_arm, right_arm, None)
            elif index < FREE_AT:
                cut = index - SNAP_AT
                draw_strings(frame, cx, top, shoulder, left_arm, right_arm, cut)
                if cut == 0:
                    for x in (cx, cx - 3, cx + 3):
                        frame.vline(x, 0, top, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/nsync.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
