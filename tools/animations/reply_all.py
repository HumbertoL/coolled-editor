#!/usr/bin/env python3
"""
Reply all -- one click, four thousand recipients.

A white inbox envelope with a red unread badge at 1 and a quiet subject line,
LUNCH?. A cursor drifts over to a REPLY ALL button, hesitates, and clicks.
TO: ALL STAFF. The badge starts doubling -- 2, 4, 16, 128, 512, 999+ -- while
the subject stacks up RE: RE: RE: and little envelopes rain in and pile up
across the panel. Then it all shakes: PLS REMOVE ME, STOP REPLYING ALL,
UNSUBSCRIBE and +1 flash over the pile, the badge strobing red and yellow.
A white flash, a held black beat, and the panel is empty -- until one last
envelope slides in: RE: RE: RE: THANKS! The badge ticks to 2.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 4812

BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H = 52, 8, 42, 8
CLICK = 9                   # frame the button is pressed
CHAOS = 24                  # shaking starts
FLASH = 41                  # white-out
FINAL = 44                  # last email starts arriving

ARROW = [
    "#....",
    "##...",
    "###..",
    "####.",
    "##...",
    "..#..",
]


def envelope(canvas, x, y, color):
    """Big 13x10 inbox envelope."""
    canvas.rect(x, y, 13, 10, color)
    canvas.line(x, y, x + 6, y + 5, color)
    canvas.line(x + 12, y, x + 6, y + 5, color)


def mini(canvas, x, y, color):
    """A 7x5 envelope for the pile."""
    canvas.rect(x, y, 7, 5, color, fill=True)
    canvas.line(x, y, x + 3, y + 2, C.BLACK)
    canvas.line(x + 6, y, x + 3, y + 2, C.BLACK)


def badge(canvas, label, color=C.RED):
    width = Canvas.small_text_width(label) + 2
    x = 17 - width
    canvas.rect(x, 0, width, 7, color, fill=True)
    canvas.small_text(label, x + 1, 1, C.WHITE if color != C.YELLOW else C.RED)


def arrow(canvas, x, y):
    for row, line in enumerate(ARROW):
        for col, cell in enumerate(line):
            if cell == "#":
                canvas.pixel(x + col, y + row, C.WHITE)
    canvas.pixel(x - 1, y - 1, C.BLACK)


def boxed(canvas, text, y, color, small=True):
    """Text on a black plate, centred over the pile region (x 17..95)."""
    width = Canvas.small_text_width(text) if small else Canvas.text_width(text)
    height = 5 if small else 7
    x = 17 + (79 - width) // 2
    canvas.rect(x - 2, y - 1, width + 4, height + 2, C.BLACK, fill=True)
    canvas.rect(x - 2, y - 1, width + 4, height + 2, C.RED)
    if small:
        canvas.small_text(text, x, y, color)
    else:
        canvas.text(text, x, y, color)


def counter(index):
    steps = [(CLICK + 3, "2"), (CLICK + 5, "4"), (CLICK + 7, "16"),
             (CLICK + 9, "128"), (CLICK + 11, "512"), (CLICK + 13, "999+")]
    label = "1"
    for start, text in steps:
        if index >= start:
            label = text
    return label


def plan_pile(rng):
    """Envelopes: (spawn frame, x, landing y, color). Stacked in columns."""
    columns = list(range(18, 90, 8))
    heights = {cx: 16 for cx in columns}
    pile = []
    spawn = CLICK + 3
    rate = 1
    palette = [C.WHITE, C.YELLOW, C.CYAN, C.WHITE]
    while spawn < FLASH:
        for _ in range(rate):
            cx = rng.choice(columns)
            heights[cx] -= 5
            pile.append((spawn, cx + rng.randint(-1, 1), heights[cx],
                         rng.choice(palette)))
        spawn += 1
        if spawn in (CLICK + 7, CLICK + 11, CHAOS, CHAOS + 6):
            rate += 1
    return pile


def build():
    rng = random.Random(SEED)
    pile = plan_pile(rng)
    anim = Animation(delay=DELAY)
    messages = [
        (CHAOS, CHAOS + 3, "REMOVE ME!!", False, C.YELLOW),
        (CHAOS + 3, CHAOS + 6, "STOP REPLYING ALL", True, C.WHITE),
        (CHAOS + 6, CHAOS + 9, "UNSUBSCRIBE", False, C.CYAN),
        (CHAOS + 9, CHAOS + 11, "+1", False, C.GREEN),
        (CHAOS + 11, CHAOS + 14, "WHO IS BOB??", True, C.YELLOW),
        (CHAOS + 14, FLASH, "STOP!!!", False, C.RED),
    ]
    for index in range(FRAMES):
        frame = anim.frame()
        if index == FLASH:
            frame.fill(C.WHITE)
            continue
        if FLASH < index < FINAL:
            continue
        if index >= FINAL:
            # The aftermath: one envelope, one last reply.
            envelope(frame, 1, 6, C.WHITE)
            badge(frame, "1" if index < FRAMES - 3 else "2")
            slide = max(0, (FINAL + 3 - index)) * 22
            subject = "RE: RE: RE: THANKS!"
            mini(frame, 20 + slide, 9, C.YELLOW)
            if index >= FINAL + 3:
                frame.small_text(subject, 30, 9, C.WHITE)
            frame.small_text("FROM: BOB", 20, 2, C.CYAN)
            if index >= FRAMES - 3:
                frame.text("+1", 82, 1, C.GREEN)
            continue

        scene = Canvas()
        envelope(scene, 1, 6, C.WHITE)
        rre = 0 if index < CLICK + 2 else min(6, (index - CLICK) // 2)
        # Envelopes raining into the pile.
        for spawn, x, land, color in pile:
            if index < spawn:
                continue
            y = min(land, -5 + (index - spawn) * 7)
            mini(scene, x, y, color)

        if index < CLICK + 3:
            end = scene.small_text("BOB:", 20, 2, C.CYAN)
            scene.small_text("LUNCH?", end + 4, 2, C.WHITE)
            pressed = index >= CLICK
            fill = C.RED if pressed else C.BLUE
            scene.rect(BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H, fill, fill=True)
            if index >= CLICK - 3:
                scene.rect(BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H, C.WHITE)
            label = "REPLY ALL"
            lx = BUTTON_X + 2
            scene.small_text(label, lx, BUTTON_Y + 2 - (0 if pressed else 0),
                             C.WHITE if not pressed else C.YELLOW)
            # Cursor glides in, hovers, then clicks.
            path = [(70, 15), (78, 14), (84, 13), (88, 12), (90, 12),
                    (90, 12), (91, 12), (90, 12), (90, 12)]
            cx, cy = path[min(index, len(path) - 1)]
            if index >= CLICK:
                cx, cy = 90, 13
            arrow(scene, cx, cy)
            if index >= CLICK + 1:
                scene.rect(19, 0, 77, 7, C.BLACK, fill=True)
                scene.small_text("TO: ALL", 20, 1, C.RED)
                scene.rect(19, 8, 34, 7, C.BLACK, fill=True)
                scene.small_text("4812!", 20, 9, C.YELLOW)
        elif index < CHAOS:
            subject = "RE: " * rre + "LUNCH?"
            width = Canvas.small_text_width(subject)
            scene.rect(17, 0, 79, 6, C.BLACK, fill=True)
            scene.small_text(subject, min(19, 95 - width), 0, C.WHITE)
            scene.rect(0, 0, 19, 6, C.BLACK, fill=True)    # clip the left
        else:
            for start, end, text, small, color in messages:
                if start <= index < end:
                    blink = color if (index - start) % 2 == 0 else C.WHITE
                    boxed(scene, text, 5 if small else 4, blink, small)

        # Badge on top of everything.
        label = counter(index)
        color = C.RED
        if index >= CHAOS and index % 2:
            color = C.YELLOW
        badge(scene, label, color)

        if index >= CHAOS:
            amp = 1 if index < CHAOS + 8 else 2
            dx = rng.randint(-amp, amp)
            dy = rng.choice((-1, 0, 1))
        elif index >= CLICK + 11:
            dx, dy = rng.choice((-1, 1)), 0
        else:
            dx = dy = 0
        frame.blit(scene, dx, dy)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/reply_all.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
