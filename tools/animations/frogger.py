#!/usr/bin/env python3
"""
Frogger -- one frog, two lanes of traffic, one lily pad.

The panel is the road seen from above: cars stream left in the upper lane and
right in the lower one, and a frog starts on the bottom verge, waits for the
gaps, and hops up to the pond at the top. The hop frames are found by
searching the same traffic the frames draw for windows where the frog's
column stays clear for its *entire* stay in each lane -- so it provably never
shares a pixel with a car.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110

FROG_X = 46  # column the frog climbs
CAR_LENGTH = 11
CAR_PERIOD = 26  # spacing of the traffic pattern, in pixels
CAR_SPEED = 2  # px per frame

# (top row, direction, phase offset, color). Cars fill rows top..top+2 --
# exactly the rows the frog occupies when it sits in that lane.
LANE_FAST = (3, -1, 0, C.YELLOW)
LANE_SLOW = (8, +1, 13, C.RED)

#: Frog top row at each rung: verge, lower lane, upper lane, pond.
RUNGS = [13, 8, 3, 0]


def car_columns(lane, frame_index):
    """Set of x columns any car in this lane covers at this frame."""
    _top, direction, phase, _color = lane
    offset = (phase + direction * CAR_SPEED * frame_index) % CAR_PERIOD
    columns = set()
    for start in range(-CAR_PERIOD, 96 + CAR_PERIOD, CAR_PERIOD):
        left = start + offset
        for x in range(int(left), int(left) + CAR_LENGTH):
            if 0 <= x < 96:
                columns.add(x)
    return columns


def lane_safe(lane, frame_index, margin=2):
    """True if the frog's column (plus margin either side) is clear."""
    columns = car_columns(lane, frame_index)
    return all(FROG_X + d not in columns for d in range(-margin, margin + 1))


def plan_hops():
    """
    (enter_slow, enter_fast, enter_pond) frames such that the slow lane is
    clear for the whole [enter_slow, enter_fast] stay and the fast lane for
    [enter_fast, enter_pond].
    """
    for h1 in range(16, 34):
        for h2 in range(h1 + 3, 42):
            if not all(lane_safe(LANE_SLOW, f) for f in range(h1, h2 + 1)):
                continue
            for h3 in range(h2 + 3, 50):
                if all(lane_safe(LANE_FAST, f) for f in range(h2, h3 + 1)):
                    return h1, h2, h3
    raise RuntimeError("No safe crossing in this traffic; retime the lanes")


def frog_row(index, hops):
    rung = sum(1 for h in hops if index >= h)
    row = RUNGS[min(rung, len(RUNGS) - 1)]
    if index in hops:
        # Mid-leap: halfway between the rung it left and the one it enters.
        row = (RUNGS[rung - 1] + row) // 2
    return row


def build():
    anim = Animation(delay=DELAY)
    hops = plan_hops()

    for index in range(FRAMES):
        frame = anim.frame()

        # Pond shimmer and the lily pad.
        for x in range(96):
            if (x + index) % 4 == 0:
                frame.pixel(x, 0, C.BLUE)
        frame.hline(FROG_X - 3, 1, 7, C.GREEN)
        frame.hline(FROG_X - 2, 2, 5, C.GREEN)

        # Road furniture: dashed centre line, solid verge line.
        for x in range(0, 96, 6):
            frame.hline(x + (index % 6), 6, 2, C.BLUE)
        frame.hline(0, 12, 96, C.BLUE)

        # Traffic.
        for lane in (LANE_FAST, LANE_SLOW):
            top, _direction, _phase, color = lane
            for x in car_columns(lane, index):
                frame.vline(x, top, 3, color)
                if x % CAR_PERIOD in (2, 3):
                    frame.pixel(x, top + 1, C.WHITE)

        # The frog: 3x3 with white eyes.
        row = frog_row(index, hops)
        frame.rect(FROG_X - 1, row, 3, 3, C.GREEN, fill=True)
        frame.pixel(FROG_X - 1, row, C.WHITE)
        frame.pixel(FROG_X + 1, row, C.WHITE)

        # Made it: a short victory blink on the pad.
        if 0 < index - hops[-1] <= 9 and row == RUNGS[-1] and index % 4 < 2:
            frame.rect(FROG_X - 3, row, 7, 4, C.YELLOW)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/frogger.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
