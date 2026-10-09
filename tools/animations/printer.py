#!/usr/bin/env python3
"""
Printer -- one page. One. Page.

An office printer (a squat blue box with a white lid, a little status
window and a status LED) sits on the left; a person in a magenta shirt
stands beside it, empty-handed, waiting. The display narrates: PRINT 1
PAGE, then WARMING UP... with the dots ticking and the LED blinking green
for a long, long time. PAPER JAM, in red: the person lifts the lid, there
is nothing inside, closes it. LOW MAGENTA: the person throws both hands up
(IT'S B&W!). PC LOAD LETTER: ??? Then a fist comes down on the lid --
BONK -- and the printer squashes a pixel. The LED turns green, PRINTING,
and a page rolls slowly out of the slot while the person backs off, then
leans in to read it. The page says NO. in big letters. Button: the display
reads OUT OF PAPER.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150

BODY = C.BLUE
LID = C.WHITE
SKIN = C.YELLOW
SHIRT = C.MAGENTA
LEGS = C.WHITE

PRINTER_RIGHT = 23          # last blue column of the printer body
SLOT_X = 24                 # the page emerges from here
MSG_X = 42                  # display messages are spelt out up here
PAGE_W, PAGE_TOP, PAGE_H = 20, 6, 9

# Beats (first frame of each).
WARMING, JAM, MAGENTA, LETTER, WHACK, PRINTING, LEAN, NO, OUT = (
    5, 13, 20, 26, 32, 35, 41, 43, 48,
)


def draw_printer(frame, squash=0, lid="closed", led=None, display=C.CYAN,
                 msg=""):
    """The printer, feet on row 15. ``squash`` presses the top down a row."""
    top = 4 + squash
    # Body: a dark blue box with little feet.
    frame.rect(0, top, PRINTER_RIGHT + 1 + squash, 15 - top, BODY, fill=True)
    frame.hline(1, 15, 2, BODY)
    frame.hline(PRINTER_RIGHT - 2, 15, 2, BODY)
    # Rounded top corners.
    frame.pixel(0, top, C.BLACK)
    frame.pixel(PRINTER_RIGHT + squash, top, C.BLACK)
    # Lid.
    if lid == "closed":
        frame.hline(2, top - 1, PRINTER_RIGHT - 3, LID)
    else:
        # Lifted at the right-hand end; the inside is hollow and empty.
        frame.rect(3, top, PRINTER_RIGHT - 5, 3, C.BLACK, fill=True)
        frame.line(2, top - 1, 20, 0, LID)
    # Status window with a hint of text in it.
    frame.rect(2, 8, 8, 4, C.BLACK, fill=True)
    if msg:
        pattern = ("#.##.#", ".#.##.") if len(msg) % 2 else ("##.#.#", "#.##.#")
        for r, row in enumerate(pattern):
            for c, ch in enumerate(row):
                if ch == "#":
                    frame.pixel(3 + c, 9 + r, display)
    # Status LED.
    if led is not None:
        frame.hline(19, 9, 2, led)
    # Output slot on the right face.
    frame.vline(SLOT_X, PAGE_TOP + 1, PAGE_H - 2, C.BLACK)
    if msg:
        frame.small_text(msg, MSG_X, 0, display)


def draw_person(frame, cx, eye="left", arms="rest", lean=0):
    """Facing the printer (left), feet on row 15."""
    hx = cx - lean
    frame.rect(hx - 1, 5, 3, 3, SKIN, fill=True)
    if eye == "left":
        frame.pixel(hx - 1, 6, C.BLACK)
    elif eye == "front":
        frame.pixel(hx, 6, C.BLACK)
    elif eye == "wide":
        frame.pixel(hx - 1, 6, C.BLACK)
        frame.pixel(hx, 6, C.BLACK)
    elif eye == "shut":
        frame.hline(hx - 1, 6, 2, C.BLACK)
    frame.rect(cx - 1, 8, 3, 4, SHIRT, fill=True)
    if lean:
        frame.pixel(cx - 1, 8, C.BLACK)
        frame.pixel(cx - 2, 8, SHIRT)
    frame.vline(cx - 1, 12, 4, LEGS)
    frame.vline(cx + 1, 12, 4, LEGS)
    if arms == "rest":
        frame.vline(cx - 2, 8, 3, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)
    elif arms == "up":
        frame.line(cx - 2, 8, cx - 4, 4, SKIN)
        frame.line(cx + 2, 8, cx + 4, 4, SKIN)
    elif arms == "shrug":
        frame.line(cx - 2, 9, cx - 4, 7, SKIN)
        frame.line(cx + 2, 9, cx + 4, 7, SKIN)
    elif arms == "reach":
        frame.hline(cx - 5, 8, 4, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)
    elif arms == "lid":
        frame.line(cx - 2, 8, cx - 6, 2, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)
    elif arms == "wind":
        frame.line(cx - 2, 8, cx - 1, 2, SKIN)
        frame.pixel(cx - 2, 2, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)
    elif arms == "whack":
        frame.line(cx - 2, 8, PRINTER_RIGHT - 3, 4, SKIN)
        frame.pixel(PRINTER_RIGHT - 4, 4, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)
    elif arms == "lean":
        frame.line(cx - 2, 8, cx - 4, 10, SKIN)
        frame.vline(cx + 2, 8, 3, SKIN)


def draw_page(frame, width, text=False):
    frame.rect(SLOT_X, PAGE_TOP, width, PAGE_H, C.WHITE, fill=True)
    if text:
        x = SLOT_X + (PAGE_W - Canvas.text_width("NO.")) // 2
        frame.text("NO.", x, PAGE_TOP + 1, C.BLACK)


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        f = anim.frame()
        blink = C.GREEN if i % 2 else None
        if i < WARMING:
            draw_printer(f, led=C.GREEN, msg="PRINT 1 PAGE")
            draw_person(f, 28)
        elif i < JAM:
            dots = "." * (1 + (i - WARMING) % 3)
            draw_printer(f, led=blink, msg="WARMING UP" + dots)
            eye = "shut" if i in (9, 10) else "left"
            draw_person(f, 28, eye=eye)
        elif i < MAGENTA:
            t = i - JAM
            lid = "open" if 2 <= t <= 4 else "closed"
            arms = "reach" if t in (1, 5) else "lid" if lid == "open" else "rest"
            draw_printer(f, lid=lid, led=C.RED, display=C.RED, msg="PAPER JAM")
            draw_person(f, 28, arms=arms)
            if t in (3, 4):
                f.small_text("?", 31, 0, C.WHITE)
        elif i < LETTER:
            t = i - MAGENTA
            draw_printer(f, led=C.RED, display=C.RED, msg="LOW MAGENTA")
            draw_person(f, 28, arms="up" if t >= 1 else "rest",
                        eye="wide" if t >= 1 else "left")
            if t >= 2:
                f.small_text("IT'S B&W!", 44, 9, C.WHITE)
        elif i < WHACK:
            t = i - LETTER
            draw_printer(f, led=C.RED, display=C.RED, msg="PC LOAD LETTER")
            draw_person(f, 28, arms="shrug" if t >= 1 else "rest",
                        eye="front" if t >= 2 else "left")
            if t >= 1:
                f.small_text("???", 23, 0, C.WHITE)
        elif i < PRINTING:
            t = i - WHACK
            if t == 0:
                draw_printer(f, led=C.RED, display=C.RED, msg="PC LOAD LETTER")
                draw_person(f, 28, arms="wind", eye="wide")
            elif t == 1:
                draw_printer(f, squash=1, led=None)
                draw_person(f, 28, arms="whack", eye="wide")
                f.small_text("BONK", 29, 0, C.YELLOW)
            else:
                draw_printer(f, led=C.GREEN)
                draw_person(f, 34, arms="rest", eye="wide")
                f.small_text("BONK", 29, 0, C.WHITE)
        elif i < LEAN:
            t = i - PRINTING
            draw_printer(f, led=blink, msg="PRINTING")
            cx = (42, 48)[min(t, 1)]
            draw_person(f, cx, eye="left")
            draw_page(f, (3, 6, 10, 13, 17, 20)[t])
        elif i < NO:
            draw_printer(f, led=C.GREEN, msg="PRINTING")
            draw_person(f, 48, arms="lean", lean=2)
            draw_page(f, PAGE_W)
        elif i < OUT:
            draw_printer(f, led=C.GREEN)
            draw_person(f, 48, arms="lean", lean=2, eye="wide")
            draw_page(f, PAGE_W, text=True)
        else:
            draw_printer(f, led=C.RED, display=C.RED, msg="OUT OF PAPER")
            draw_person(f, 48, arms="rest", eye="front")
            draw_page(f, PAGE_W, text=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/printer.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
