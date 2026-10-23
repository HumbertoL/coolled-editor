#!/usr/bin/env python3
"""
The treadmill.

A jogger trots on a treadmill belt, the belt ticking past under its feet.
The console on the right reads SPEED 3.0 over BRISK JOG. A hand comes
down and taps the + button, and the speed climbs: 5.0, 8.0, 12.0, 16.0,
20.0. The jogger's legs blur, sweat flies, the belt tears past, and its head
turns red; the BRISK JOG line never changes. At 20 the jogger is flung off the
back of the belt and skids out the left edge. The console: SPEED 20.0, BRISK
JOG. Button: an empty, roaring belt and the + button pressed once more:
SPEED 25.0.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

BELT_X0, BELT_X1 = 12, 54           # belt spans these columns on row 14-15
POST_X = 54                         # the console post rises here
JOG_X = 28
CONSOLE_X = 59                      # text starts here

SPEEDS = [3.0, 5.0, 8.0, 12.0, 16.0, 20.0, 25.0]
TAPS = [8, 14, 20, 26, 32, 48]      # frames where the hand taps +
FLING = 38
GONE = 44

RUN = [
    ["..HH...", "..HH...", "A.SS.A.", ".SSSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", ".ASS...", "..SSA..", "..SS...", "..LL...", ".L.L..."],
    ["..HH...", "..HH...", ".ASS.A.", "..SSS..", "..SS...", ".L..L..", "L....L."],
    ["..HH...", "..HH...", "..SSA..", ".ASS...", "..SS...", "..LL...", "..L.L.."],
]
BLUR = ["..HH...", "..HH...", "AASSAA.", ".SSSS..", "..SS...", "LLLLLL.", "LLLLLL."]
TUMBLE = [".L...L.", "..L.L..", "..SSS..", ".SSSSH.", "..SS.H.", ".A..A..", "......."]
HAND = ["..W..", "..W..", "WWWW.", "WWWWW", ".WWWW"]


def sprite(frame, art, x, y, palette):
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != ".":
                frame.pixel(x + c, y + r, palette[ch])


def draw_treadmill(frame, scroll, speed_index):
    # The belt: a scrolling dash pattern, two rows, in blue with white ticks.
    for x in range(BELT_X0, BELT_X1):
        frame.pixel(x, 14, C.BLUE)
        frame.pixel(x, 15, C.WHITE if (x + scroll) % 6 == 0 else C.BLUE)
    frame.pixel(BELT_X0 - 1, 15, C.BLUE)
    # The post and console.
    frame.vline(POST_X, 4, 12, C.WHITE)
    frame.vline(POST_X + 1, 4, 12, C.WHITE)
    frame.hline(POST_X, 3, 4, C.WHITE)
    # The + button, lit green, on a stalk off the post's left.
    frame.hline(POST_X - 2, 3, 2, C.WHITE)
    frame.pixel(POST_X - 3, 1, C.GREEN)
    frame.hline(POST_X - 4, 2, 3, C.GREEN)
    frame.pixel(POST_X - 3, 3, C.GREEN)
    speed = SPEEDS[speed_index]
    frame.small_text(f"SPEED {speed:.1f}", CONSOLE_X, 2, C.CYAN)
    frame.small_text("BRISK JOG", CONSOLE_X, 9, C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    scroll = 0
    speed_index = 0
    for i in range(FRAMES):
        f = anim.frame()
        if i in TAPS:
            speed_index = min(len(SPEEDS) - 1, TAPS.index(i) + 1)
        scroll += 1 + speed_index
        draw_treadmill(f, scroll, speed_index)

        # The hand drops in to tap +, then lifts away.
        for tap in TAPS:
            if tap - 3 <= i <= tap + 1:
                dy = -3 + min(3, i - (tap - 3)) if i <= tap else -1
                for r, row in enumerate(HAND):
                    for c, ch in enumerate(row):
                        if ch == "W":
                            f.pixel(POST_X - 5 + c, dy + r - 4 + 1, C.CYAN)
                if i == tap:
                    f.pixel(POST_X - 6, 0, C.WHITE)
                    f.pixel(POST_X - 6, 4, C.WHITE)

        head = C.YELLOW if speed_index < 3 else C.RED
        palette = {"H": head, "S": C.GREEN, "A": C.WHITE, "L": C.WHITE}
        if i < FLING:
            fast = speed_index >= 4
            art = BLUR if fast and i % 2 else RUN[(scroll // 2) % 4]
            sprite(f, art, JOG_X, 7, palette)
            if speed_index >= 2:
                # Sweat: drops thrown up and back, cycling with the frame.
                for k in range(speed_index - 1):
                    f.pixel(JOG_X - 1 - k * 2 - (i % 3), 7 + (i + k) % 4, C.CYAN)
            if fast:
                for k in range(3):
                    f.hline(JOG_X - 4 - k * 3, 9 + k * 2, 2, C.CYAN)
        elif i < GONE:
            t = i - FLING
            x = JOG_X - t * 6
            y = 7 - (3 - abs(t - 2)) if t < 5 else 8
            sprite(f, TUMBLE, x, y, palette)
            f.small_text("!", JOG_X + 2, 2, C.RED)
            for k in range(3):
                f.hline(x + 8 + k * 2, 10 + k, 2, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/brisk_treadmill.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
