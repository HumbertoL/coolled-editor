#!/usr/bin/env python3
"""
Ouija HR -- the spirit you summoned works in Human Resources.

A Ouija board fills the left two thirds of the panel inside a blue frame:
YES and the letters A to M on the top row, N to Z and NO on the bottom, all
in yellow 3x5 type. To the right, past a blue divider, is a readout with a
blinking cursor. The planchette is a white lens: wherever it sits, the
letter underneath shows through it in black.

It twitches, then glides letter to letter -- one frame of travel, two of
dwell -- and the readout spells out the message in cyan: HI ITS / HR (it
wobbles off and back for the double I, as planchettes do). A held beat.
The readout clears and somebody at the table asks, in white: PTO? The
planchette rockets straight to NO and rattles there, the lens flashing red,
NO appearing in red under the question. Then, slowly and deliberately, it
spells L, O, L.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

DELAY = 130
W, H = 96, 16

ROW_Y = (2, 9)
BOARD_RIGHT = 69          # frame's right edge; readout starts after it
READ_X = 72
LETTER = C.YELLOW
FRAME = C.BLUE
SPIRIT = C.CYAN

# Where every target on the board sits: name -> (x, y, width).
TARGETS = {}


def _lay_out(items, x, y):
    for item in items:
        width = Canvas.small_text_width(item)
        TARGETS[item] = (x, y, width)
        x += width + (1 if len(item) == 1 else 3)


_lay_out(["YES"] + list("ABCDEFGHIJKLM"), 2, ROW_Y[0])
_lay_out(list("NOPQRSTUVWXYZ"), 2, ROW_Y[1])
TARGETS["NO"] = (BOARD_RIGHT - 1 - 8, ROW_Y[1], 8)

# Park the planchette between the rows, mid-board.
PARK = (32, 5.5)


def centre(name):
    x, y, w = TARGETS[name]
    return (x + (w - 1) / 2, y + 2)


def board(c):
    c.rect(0, 0, BOARD_RIGHT + 1, H, FRAME)
    for corner in ((0, 0), (BOARD_RIGHT, 0), (0, H - 1), (BOARD_RIGHT, H - 1)):
        c.pixel(*corner, C.BLACK)
    for name, (x, y, _) in TARGETS.items():
        c.small_text(name, x, y, LETTER)


def planchette(c, cx, cy, width=3, color=C.WHITE):
    """A rounded lens, 2px wider than the letter, inverting what is under it."""
    x0 = round(cx - (width - 1) / 2) - 1
    y0 = round(cy - 2) - 1
    w, h = width + 2, 7
    for dx in range(w):
        for dy in range(h):
            if (dx in (0, w - 1)) and (dy in (0, h - 1)):
                continue                       # round the corners off
            x, y = x0 + dx, y0 + dy
            lit = c.get(x, y) == LETTER
            c.pixel(x, y, C.BLACK if lit else color)


def readout(c, lines, cursor=None):
    for (text, color), y in zip(lines, ROW_Y):
        c.small_text(text, READ_X, y, color)
    if cursor is not None:
        x, y = cursor
        c.hline(x, y + 5, 3, C.WHITE)


def spell(word, glide=1, dwell=2):
    """Beats for the planchette spelling `word`; spaces just add to the text."""
    beats = []
    prev = None
    for ch in word:
        if ch == " ":
            continue
        for k in range(glide):
            beats.append(("glide", ch, (k + 1) / (glide + 1), ch == prev))
        for _ in range(dwell):
            beats.append(("dwell", ch, None, False))
        prev = ch
    return beats


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def main():
    anim = Animation(delay=DELAY)

    message1 = "HI ITS HR"
    message2 = "LOL"
    # Beat sheet: frames in order.
    beats = (
        [("park", None, 0, False)] * 2
        + [("park", None, 1, False)]                    # a twitch
        + spell(message1)
        + [("hold1", None, None, False)] * 4
        + [("ask", None, k, False) for k in range(4)]
        + [("race", None, None, False)]
        + [("slam", None, k, False) for k in range(8)]
        + spell(message2, glide=1, dwell=2)
        + [("end", None, None, False)] * 3
    )
    assert len(beats) == 53, len(beats)

    pos = PARK
    width = 3
    typed1 = ""            # what the readout has spelled so far
    line1_full = message1.split(" ")
    shown2 = ""
    for f, (kind, ch, t, repeat) in enumerate(beats):
        c = anim.frame()
        board(c)
        lines = []
        cursor = None
        lens_color = C.WHITE

        if kind == "park":
            pos = (PARK[0] + t, PARK[1])
            cursor = (READ_X, ROW_Y[0]) if f % 2 == 0 else None
            planchette(c, *pos)
        elif kind in ("glide", "dwell") and f < 30:
            target = centre(ch)
            if kind == "glide":
                if repeat:
                    # off and back: a little loop below the letter
                    draw = (target[0] + 2, target[1] + 2)
                else:
                    draw = lerp(pos, target, 0.5)
                planchette(c, *draw, width=width)
            else:
                if beats[f - 1][0] == "glide":
                    typed1 = message1[: message1.index(ch, len(typed1)) + 1]
                pos = target
                width = TARGETS[ch][2]
                planchette(c, *pos, width=width)
            words = typed1.split(" ")
            lines = [(" ".join(words[:2]), SPIRIT)]
            if len(words) > 2:
                lines.append((words[2], SPIRIT))
        elif kind == "hold1":
            planchette(c, *pos, width=width)
            lines = [(" ".join(line1_full[:2]), SPIRIT), (line1_full[2], SPIRIT)]
        elif kind == "ask":
            planchette(c, *pos, width=width)
            text = "PTO?"[: t + 1]
            lines = [(text, C.WHITE)]
            cursor = (READ_X + Canvas.small_text_width(text) + 2, ROW_Y[0])
        elif kind == "race":
            target = centre("NO")
            # motion streak along the way
            a, b = pos, target
            for k in range(1, 6):
                px, py = lerp(a, b, k / 6)
                c.pixel(round(px), round(py), C.WHITE)
            planchette(c, *lerp(a, b, 0.75), width=3)
            lines = [("PTO?", C.WHITE)]
        elif kind == "slam":
            target = centre("NO")
            jitter = [(1, 0), (-1, 0), (0, -1), (1, 0), (-1, 0), (0, 0),
                      (1, 0), (0, 0)][t]
            pos = target
            width = 8
            lens_color = C.RED if t % 2 == 0 and t < 6 else C.WHITE
            planchette(c, target[0] + jitter[0], target[1] + jitter[1],
                       width=8, color=lens_color)
            lines = [("PTO?", C.WHITE), ("NO", C.RED)]
        elif kind in ("glide", "dwell"):
            target = centre(ch)
            if kind == "glide":
                draw = (lerp(pos, target, 0.5) if ch != "L" or not shown2
                        else (target[0], target[1] + 3))
                planchette(c, *draw, width=width)
            else:
                if beats[f - 1][0] == "glide":
                    shown2 = message2[: len(shown2) + 1]
                pos = target
                width = TARGETS[ch][2]
                planchette(c, *pos, width=width)
            lines = [("PTO?", C.WHITE), ("NO " + shown2, C.RED)]
        else:  # end
            planchette(c, *pos, width=width)
            lines = [("PTO?", C.WHITE), ("NO LOL", C.RED)]

        readout(c, lines, cursor)

    out = Path(__file__).resolve().parents[2] / "src/sample/ouija_hr.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
