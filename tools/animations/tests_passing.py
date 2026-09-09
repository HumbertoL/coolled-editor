#!/usr/bin/env python3
"""
Tests passing -- an acceptance suite running.

Sixteen spec dots along the bottom, one per column of the panel. Each goes
from blue (queued) through yellow (running) to green (passed). One fails --
red -- and gets retried after the rest finish, blinking yellow, then passes,
because that is how a flaky end-to-end run actually goes. The counter at the
top keeps score and the whole thing ends on ALL PASS.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 160

SPECS = 16
FLAKY = 9
RETRY_START = 16
RETRY_PASS = 18
DONE = 19


def spec_state(i, index):
    if i == FLAKY:
        if index < i:
            return "queued"
        if index == i:
            return "running"
        if index < RETRY_START:
            return "failed"
        if index < RETRY_PASS:
            return "running"
        return "passed"
    if index < i:
        return "queued"
    if index == i:
        return "running"
    return "passed"


COLORS = {"queued": C.BLUE, "running": C.YELLOW, "failed": C.RED, "passed": C.GREEN}


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        states = [spec_state(i, index) for i in range(SPECS)]
        for i, state in enumerate(states):
            color = COLORS[state]
            if state == "running" and index % 2:
                color = C.WHITE
            frame.rect(2 + i * 6, 11, 3, 3, color, fill=True)

        passed = states.count("passed")
        failed = states.count("failed")
        if index >= DONE:
            frame.text("ALL 16 PASS", "center", 1, C.GREEN if index % 4 else C.WHITE)
            continue
        frame.text("E2E", 2, 1, C.CYAN)
        frame.text(f"{passed:2d}/{SPECS}", 62, 1, C.GREEN if passed else C.WHITE)
        if failed:
            frame.text(f"{failed} FAIL", 24, 1, C.RED)
        elif index >= RETRY_START:
            frame.text("RETRY", 24, 1, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tests_passing.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
