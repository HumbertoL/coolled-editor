#!/usr/bin/env python3
"""
Autocorrect -- the phone knows better than you.

A thin blue phone frame with a green send button. On the typing line a
white cursor blinks and SEE YOU SOON types out a letter per frame. The
moment SOON completes it flashes red and snaps to SPOON, held, then
whooshes up into a green sent bubble. Frantic retyping: NO, SOON becomes
NO, SPOON. Sent. I MEANT... becomes I MEAT... Sent. UGH becomes HUG. Sent.
A held beat, cursor blinking. A magenta reply bubble slides in from the
other side: ? ? ?  then OK. HUG.  Button: the typing line reads DUCK THIS,
a little yellow duck waddles up beside it, and the send button lights up.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140

FRAME_COLOR = C.BLUE
TEXT_X = 2               # left edge of the typing line
TEXT_Y = 8               # 5x7 text occupies rows 8..14
BUBBLE_Y = 0             # bubbles occupy rows 0..6, a dark row, then the text
SEND_X = 87              # the send button, a green square at the right

DUCK = [
    ".##...",
    "###R..",
    ".#....",
    ".####.",
    "######",
    ".####.",
]


def phone(frame, send="idle"):
    # Sides and a bottom edge; the screen runs off the top of the panel.
    frame.vline(0, 0, 16, FRAME_COLOR)
    frame.vline(95, 0, 16, FRAME_COLOR)
    frame.hline(0, 15, 96, FRAME_COLOR)
    # Send button: a green square with a black up-arrow.
    color = C.WHITE if send == "flash" else C.GREEN
    frame.rect(SEND_X, 8, 7, 7, color, fill=True)
    cx = SEND_X + 3
    frame.pixel(cx, 9, C.BLACK)
    frame.pixel(cx - 1, 10, C.BLACK)
    frame.pixel(cx + 1, 10, C.BLACK)
    frame.vline(cx, 10, 4, C.BLACK)


def typed(frame, text, red_from=None, cursor=True, color=C.WHITE):
    """The typing line. ``red_from`` is a character index: that word and on is red."""
    if red_from is None:
        frame.text(text, TEXT_X, TEXT_Y, color)
    else:
        frame.text(text[:red_from], TEXT_X, TEXT_Y, color)
        frame.text(text[red_from:], TEXT_X + red_from * 6, TEXT_Y, C.RED)
    if cursor:
        x = TEXT_X + Canvas.text_width(text) + (1 if text else 0)
        frame.vline(x, TEXT_Y, 7, C.WHITE)


def bubble(frame, text, side, y=BUBBLE_Y, rim=C.GREEN, ink=C.WHITE):
    """A rounded speech bubble in the small font, hugging the left or right."""
    w = Canvas.small_text_width(text) + 4
    x = 93 - w if side == "right" else 3
    if y < -6 or y > 8:
        return
    # Rounded rect: corners left dark.
    frame.hline(x + 1, y, w - 2, rim)
    frame.hline(x + 1, y + 6, w - 2, rim)
    frame.vline(x, y + 1, 5, rim)
    frame.vline(x + w - 1, y + 1, 5, rim)
    frame.small_text(text, x + 2, y + 1, ink)


def duck(frame, x, y, bob=0):
    for r, line in enumerate(DUCK):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r + bob, C.YELLOW)
            elif ch == "R":
                frame.pixel(x + c, y + r + bob, C.RED)
    frame.pixel(x + 1, y + 1 + bob, C.BLACK)                 # eye


# Each message: (text typed, chars per frame, the word's start index,
# the autocorrected text). Typing frames show progressively more text.
MESSAGES = [
    ("SEE YOU SOON", 1, 8, "SEE YOU SPOON"),
    ("NO, SOON", 2, 4, "NO, SPOON"),
    ("I MEANT...", 2, 2, "I MEAT..."),
    ("UGH", 2, 0, "HUG"),
]


def typing_steps(text, per_frame):
    """Prefixes of ``text`` as it types; spaces ride along with the next letter."""
    steps = []
    letters = 0
    for count, ch in enumerate(text, 1):
        if ch == " ":
            continue
        letters += 1
        if letters % per_frame == 0 or count == len(text):
            steps.append(text[:count])
    return steps


def build():
    anim = Animation(delay=DELAY)
    # Script the frames as a list of (kind, payload) first, then draw.
    script = []
    for text, per, word, fixed in MESSAGES:
        steps = typing_steps(text, per)
        for s in steps:
            script.append(("type", s))
        if per == 1:
            script += [("flash", (text, word))] * 2
        script += [("fixed", (fixed, word))] * 3
        script.append(("whoosh", fixed))
    script += [("beat", None)] * 3
    script += [("reply", "? ? ?")] * 3
    script += [("reply2", "OK. HUG.")] * 3
    while len(script) < FRAMES:
        script.append(("button", len(script)))
    script = script[:FRAMES]
    assert len(script) == FRAMES, len(script)

    sent = None              # text of the latest sent bubble
    reply = None
    for index, (kind, payload) in enumerate(script):
        frame = anim.frame()
        blink = (index // 2) % 2 == 0
        phone(frame, send="flash" if kind == "whoosh" else "idle")
        if kind == "type":
            if sent:
                bubble(frame, sent, "right")
            typed(frame, payload, cursor=True)
        elif kind == "flash":
            text, word = payload
            if sent:
                bubble(frame, sent, "right")
            typed(frame, text, red_from=word, cursor=False)
        elif kind == "fixed":
            text, word = payload
            if sent:
                bubble(frame, sent, "right")
            typed(frame, text, red_from=word, cursor=False)
        elif kind == "whoosh":
            # The old bubble flies off the top; the new text is mid-flight.
            if sent:
                bubble(frame, sent, "right", y=BUBBLE_Y - 5)
            frame.text(payload, 85 - Canvas.text_width(payload), 2, C.GREEN)
            sent = payload
            typed(frame, "", cursor=True)
        elif kind == "beat":
            bubble(frame, sent, "right")
            typed(frame, "", cursor=blink)
        elif kind == "reply":
            bubble(frame, sent, "right")
            reply = payload
            bubble(frame, reply, "left", rim=C.MAGENTA, ink=C.WHITE)
            typed(frame, "", cursor=blink)
        elif kind == "reply2":
            bubble(frame, sent, "right")
            reply = payload
            bubble(frame, reply, "left", rim=C.MAGENTA, ink=C.WHITE)
            typed(frame, "", cursor=blink)
        elif kind == "button":
            bubble(frame, sent, "right")
            bubble(frame, reply, "left", rim=C.MAGENTA, ink=C.WHITE)
            typed(frame, "DUCK THIS", cursor=False)
            duck(frame, 60, 8, bob=(index % 2))
            first = next(i for i, (k, _) in enumerate(script) if k == "button")
            if index > first:
                frame.small_text("QUACK", 67, 9, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/autocorrect.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
