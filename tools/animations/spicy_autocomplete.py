#!/usr/bin/env python3
"""
Spicy autocomplete -- how this sentence got written.

The sentence grows a word at a time along the top. For each new word, three
candidates flick past on the bottom line with a bar for how likely each is,
the winner flashes and jumps up to join the sentence, and the process
repeats. The final word is the one this whole thing is: AUTOCOMPLETE.

The probabilities are made up, but the mechanism is the honest one.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
# (candidates in the order they flick past, with percent). Winner is first.
STEPS = [
    ("AM", 71, [("WAS", 18), ("THINK", 9)]),
    ("A", 64, [("NOT", 22), ("JUST", 8)]),
    ("SPICY", 37, [("LARGE", 35), ("HELPFUL", 20)]),
    ("AUTOCOMPLETE", 88, [("AUTOMATON", 7), ("AUTOMOBILE", 3)]),
]
PER_STEP = 11
SHOW = 3           # frames each candidate is shown


def bar(frame, x, y, percent, color):
    frame.hline(x, y, max(1, round(percent * 30 / 100)), color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        step = min(len(STEPS), index // PER_STEP)
        sentence = ["I"] + [s[0] for s in STEPS[:step]]
        done = step >= len(STEPS)
        top = " ".join(sentence if not done else sentence[:-1])
        frame.text(top, 2, 0, C.WHITE, proportional=True)
        if done:
            k = index - len(STEPS) * PER_STEP
            frame.text(STEPS[-1][0], 2, 9, C.YELLOW if k % 4 < 2 else C.WHITE, proportional=True)
            continue

        winner, win_pct, others = STEPS[step]
        k = index % PER_STEP
        order = [others[0], others[1], (winner, win_pct)]
        if k < SHOW * 3:
            word, pct = order[k // SHOW]
            color = C.CYAN if k // SHOW < 2 else C.YELLOW
            frame.text(word, 2, 9, color, proportional=True)
            bar(frame, 62, 12, pct, color)
            frame.hline(62, 11, 30, C.BLUE)
        else:
            # Winner chosen: flash, then it is drawn rising into the sentence.
            last = step == len(STEPS) - 1
            rise = 9 if last else 9 - 4 * (k - SHOW * 3)
            x = 2 if rise == 9 else 2 + frame.text_width(top, proportional=True) + 3
            frame.text(winner, x, rise, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/spicy_autocomplete.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
