#!/usr/bin/env python3
"""
Word Ladder -- get from COLD to WARM changing one letter at a time.

The challenge holds for most of the loop: a big icy-CYAN COLD on the left, a
big RED WARM on the right, and between them a little ladder of three empty
rungs, each a question mark that lights up in turn like someone thinking it
through. Underneath, the rule: ONE LETTER AT A TIME.

Then the answer. The panel cuts to the whole ladder in small type, rails
and all, with COLD and WARM at either end, and the rungs fill in one by one:
CORD, WORD, WORM, WARM. On each rung the letter that changed scrambles
through a couple of random letters and lands in YELLOW, so the path of
changes stays traced across the finished ladder -- and each of the four
letters changes exactly once. A green shine runs along the solved ladder
before the loop returns to the question.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
W, H = 96, 16

LADDER = ["COLD", "CORD", "WORD", "WORM", "WARM"]
START_C, END_C, MID_C, CHANGE_C = C.CYAN, C.RED, C.WHITE, C.YELLOW
RAIL_C = C.BLUE

CHALLENGE_END = 27  # frames 0..26: the question
STEP_FRAMES = 5  # per rung in the reveal
REVEAL_AT = CHALLENGE_END + 2  # two frames of blank ladder first
SOLVED_AT = REVEAL_AT + STEP_FRAMES * (len(LADDER) - 2) + 3  # 47: goal landed

# Small-type ladder layout: words separated by 3px gaps with a post in the middle.
GAP = 3
TEXT_Y = 6
RAIL_TOP, RAIL_BOT = 3, 12


def changed_index(a, b):
    diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert len(a) == len(b) and len(diffs) == 1, (a, b)
    return diffs[0]


CHANGES = [changed_index(a, b) for a, b in zip(LADDER, LADDER[1:])]


def word_positions():
    xs, x = [], 0
    for word in LADDER:
        xs.append(x)
        x += Canvas.small_text_width(word) + GAP
    total = x - GAP
    offset = (W - total) // 2
    return [p + offset for p in xs], total


WORD_X, LADDER_W = word_positions()


def small_word(frame, word, x, colors):
    """Draw a 3x5 word letter by letter, each with its own colour."""
    for ch, col in zip(word, colors):
        if col is not None:
            x = frame.small_text(ch, x, TEXT_Y, col) + 1
        else:
            x += Canvas.small_text_width(ch) + 1


def draw_ladder(frame, rail=RAIL_C):
    left = WORD_X[0] - 1
    right = WORD_X[-1] + Canvas.small_text_width(LADDER[-1])
    frame.hline(left, RAIL_TOP, right - left + 1, rail)
    frame.hline(left, RAIL_BOT, right - left + 1, rail)
    for i in range(1, len(LADDER)):
        post = WORD_X[i] - 2
        frame.vline(post, RAIL_TOP, RAIL_BOT - RAIL_TOP + 1, rail)


def challenge(frame, index):
    # Big start and goal words.
    frame.text("COLD", 1, 1, START_C)
    frame.text("WARM", W - 24, 1, END_C)
    # Mini ladder of three empty rungs between them.
    left, right = 27, 68
    frame.hline(left, 0, right - left + 1, RAIL_C)
    frame.hline(left, 8, right - left + 1, RAIL_C)
    posts = [left, left + 14, left + 27, right]
    for p in posts:
        frame.vline(p, 0, 9, RAIL_C)
    thinking = (index // 3) % 4  # 0,1,2 light a slot; 3 is a pause
    for slot in range(3):
        cx = (posts[slot] + posts[slot + 1]) // 2 - 2
        frame.text("?", cx, 1, C.WHITE if slot == thinking else C.BLUE)
    frame.small_text("ONE LETTER AT A TIME", "center", 10, C.GREEN)


def reveal(frame, index, rnd):
    solved = index >= SOLVED_AT
    shine = (index - SOLVED_AT) * 24 - 4 if solved else None
    draw_ladder(frame, C.CYAN if solved and index % 2 else RAIL_C)
    for i, word in enumerate(LADDER):
        base = START_C if i == 0 else END_C if i == len(LADDER) - 1 else MID_C
        colors = [base] * 4
        if i > 0:
            colors[CHANGES[i - 1]] = CHANGE_C
        appear = REVEAL_AT + (i - 1) * STEP_FRAMES
        shown = word
        if 0 < i < len(LADDER) - 1:
            if index < appear:
                # Empty rung: four dim dashes.
                x = WORD_X[i]
                for _ in word:
                    frame.hline(x, TEXT_Y + 4, 3, C.BLUE)
                    x += 4
                continue
        if i > 0 and index < appear + 2 and index >= appear:
            # The changing letter scrambles before it lands.
            k = CHANGES[i - 1]
            shown = word[:k] + rnd.choice("ABEHKLNPSTUXZ") + word[k + 1:]
            colors[k] = C.MAGENTA
        if i == len(LADDER) - 1 and index < appear:
            colors = [END_C] * 4  # the goal sits plain until reached
        if shine is not None:
            colors = [
                C.GREEN if abs(WORD_X[i] + 4 * n - shine) < 7 else c
                for n, c in enumerate(colors)
            ]
        small_word(frame, shown, WORD_X[i], colors)


def main():
    rnd = random.Random(4)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < CHALLENGE_END:
            challenge(frame, index)
        else:
            reveal(frame, index, rnd)
    out = Path(__file__).resolve().parents[2] / "src/sample/word_ladder.jt"
    anim.save(out)
    print(anim.describe())


if __name__ == "__main__":
    main()
