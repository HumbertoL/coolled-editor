#!/usr/bin/env python3
"""
git log -- a commit graph growing, with the messages you would expect.

Commits land on main as white dots joined by a line. A feature branch forks
off upward in cyan, takes a few commits of its own, and merges back down in
a gold merge commit. The latest message shows along the top -- FIX, FIX FIX,
REVERT, FINAL, FINAL2 -- because it always goes like that.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
MAIN_Y, BRANCH_Y = 12, 6
EVERY = 4
# (lane, message). Lanes: m = main, b = branch, M = merge on main.
COMMITS = [
    ("m", "INIT"), ("m", "ADD SIGN"), ("m", "FIX TYPO"), ("b", "WIP"), ("m", "FIX"),
    ("b", "WIP 2"), ("b", "ACTUALLY WORKS"), ("m", "FIX FIX"), ("M", "MERGE FEATURE"),
    ("m", "REVERT"), ("m", "FINAL"), ("m", "FINAL2"), ("m", "FINAL FINAL"),
]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shown = min(len(COMMITS), index // EVERY + 1)
        x = 4
        last_main = None
        last_branch = None
        fork_x = None
        message = ""
        for i in range(shown):
            lane, message = COMMITS[i]
            if lane == "b":
                if last_branch is None:
                    fork_x = last_main
                    frame.line(last_main, MAIN_Y, x, BRANCH_Y, C.CYAN)
                else:
                    frame.hline(last_branch, BRANCH_Y, x - last_branch, C.CYAN)
                frame.rect(x - 1, BRANCH_Y - 1, 3, 3, C.CYAN, fill=True)
                last_branch = x
            else:
                if last_main is not None:
                    frame.hline(last_main, MAIN_Y, x - last_main, C.WHITE)
                if lane == "M" and last_branch is not None:
                    frame.line(last_branch, BRANCH_Y, x, MAIN_Y, C.CYAN)
                    last_branch = None
                frame.rect(x - 1, MAIN_Y - 1, 3, 3, C.YELLOW if lane == "M" else C.WHITE, fill=True)
                last_main = x
            x += 7
        if shown == len(COMMITS) and index % 2:
            frame.rect(last_main - 1, MAIN_Y - 1, 3, 3, C.GREEN, fill=True)
        frame.text(message, 2, 0, C.WHITE if index % EVERY else C.YELLOW, proportional=True)
        del fork_x
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/git_log.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
