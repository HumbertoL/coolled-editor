#!/usr/bin/env python3
"""
Candy bowl -- PLEASE TAKE ONE, an honour system on a porch at night.

A yellow crescent moon and a few stars, a blue porch floor, a cyan bowl
heaped with red, yellow, green, magenta and white candy, and beside it a
yellow-framed sign in the small font: PLEASE / TAKE ONE.

A little witch -- magenta pointy hat, green face, magenta robe, red pumpkin
bucket -- walks up, takes exactly one piece (it hops into her bucket), a
magenta heart pops up, and she walks off. Polite. A beat of empty porch.

Then a kid in a cyan hoodie arrives, reads the sign (a white "?"), takes one
and pockets it... then looks left, right, left. Out comes a white sack. He
hoists the bowl and pours: candy streams into the sack, which swells. The
bowl goes back down holding one sad piece. He pulls a black mask over his
eyes -- he was a burglar all along -- a yellow $ appears on the sack, and he
reaches over to the sign: a red line strikes through ONE, which becomes a
red ALL. He tiptoes off with the loot.

The witch comes back. She looks at the bowl, a red "!", then up at the sign
-- PLEASE TAKE ALL -- and the one last candy blinks in the empty bowl.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
W, H = 96, 16

FLOOR_Y = 15
BOWL_X, BOWL_Y = 45, 11        # rim's left end
KID_STOP = 34                  # where the witch stands to reach the bowl
KID2_STOP = 28                 # the hoodie kid stands back, room for a sack
SIGN_X = 59                    # left edge of the sign board
TEXT_X = SIGN_X + 2
ONE_X = TEXT_X + Canvas.small_text_width("TAKE ") + 1

BOWL = [
    "############",
    ".##########.",
    "..########..",
    "...######...",
]
# Candy heap above the rim, row by row: (y, x0, x1).
HEAP = [(10, 1, 10), (9, 2, 9), (8, 4, 7)]
CANDY_COLORS = [C.RED, C.YELLOW, C.GREEN, C.MAGENTA, C.WHITE]

# 'M' magenta, 'G' green, 'k' black, legs handled separately.
WITCH = [
    "...M...",
    "...MM..",
    "..MMM..",
    "..MMMM.",
    "MMMMMMM",
    ".GGGGG.",
    ".GGkGk.",
    ".GGGGG.",
    "..MMM..",
    ".MMMMM.",
]
# 'C' cyan hood, 'Y' face, 'k' eye, 'W' (mask) white eye.
HOODIE = [
    "..CCC..",
    ".CCCCC.",
    "CYYYYYC",
    "CYkYkYC",
    "CYYYYYC",
    "CCCCCCC",
    "CCCCCCC",
    ".CCCCC.",
]
LEGS = [[".#...#."], ["..#.#.."]]

# Beat sheet: (name, frames).
SCRIPT = [
    ("witch_in", 6),
    ("take1", 2),
    ("thanks", 2),
    ("witch_out", 3),
    ("empty", 2),
    ("kid_in", 5),
    ("read", 3),
    ("take2", 2),
    ("look", 3),
    ("dump", 6),
    ("mask", 2),
    ("edit", 2),
    ("sneak", 4),
    ("witch_back", 4),
    ("stare", 4),
    ("sign", 3),
]

COLOR = {"M": C.MAGENTA, "G": C.GREEN, "k": C.BLACK, "C": C.CYAN,
         "Y": C.YELLOW, "W": C.WHITE}


def sprite(c, rows, x, y, flip=False, recolor=None):
    for r, line in enumerate(rows):
        if flip:
            line = line[::-1]
        for k, ch in enumerate(line):
            if ch == ".":
                continue
            color = COLOR.get(ch, C.WHITE)
            if recolor and ch in recolor:
                color = recolor[ch]
            c.pixel(x + k, y + r, color)


def legs(c, x, y, step, color):
    for k, ch in enumerate(LEGS[step % 2][0]):
        if ch == "#":
            c.pixel(x + k, y, color)


def witch(c, x, step=0, face_left=False, bucket_candy=False, reach=False):
    rows = WITCH
    if face_left:
        rows = WITCH[:6] + [".kGkGG."] + WITCH[7:]
    sprite(c, rows, x, 4, flip=False)
    legs(c, x, 14, step, C.MAGENTA)
    # pumpkin bucket in the leading hand
    bx = x - 4 if face_left else x + 7
    if reach and not face_left:
        bx = x + 8
    c.rect(bx, 11, 3, 3, C.RED, fill=True)
    c.pixel(bx + 1, 12, C.YELLOW)          # its little face
    c.hline(bx, 10, 3, C.WHITE if bucket_candy else C.BLACK)
    c.pixel(bx - 1 if not face_left else bx + 3, 11, C.WHITE)  # handle
    if bucket_candy:
        c.pixel(bx + 1, 10, C.YELLOW)


def kid(c, x, step=0, look=0, mask=False, arm=None, marker=False):
    """Hoodie kid, 7 wide, rows 6..14. look: -1 left, 0 ahead, +1 right."""
    rows = list(HOODIE)
    eyes = {-1: "CkYkYYC", 0: "CYkYkYC", 1: "CYYkYkC"}[look]
    rows[3] = eyes
    if mask:
        # a black band with the eyes showing white through it
        rows[3] = eyes.replace("k", "W").replace("Y", "k")
        rows[2] = "CkkkkkC"
    # the head turns with the eyes, so the look reads from across the room
    sprite(c, rows[:5], x + look, 6)
    sprite(c, rows[5:], x, 11)
    legs(c, x, 14, step, C.BLUE)
    if arm:
        ax, ay = arm
        c.line(x + 6, 11, ax, ay, C.CYAN)
    if marker:
        # arm up, red marker aimed at the sign
        c.line(x + 7, 10, x + 13, 4, C.CYAN)
        c.line(x + 14, 3, x + 15, 2, C.RED)


def bowl(c, x, y, candies, tilt=False):
    """Bowl with its rim at (x, y); candies are (dx, dy, color) above it."""
    for r, line in enumerate(BOWL):
        shift = (r if tilt else 0)
        for k, ch in enumerate(line):
            if ch == "#":
                c.pixel(x + k + shift // 2, y + r - (k // 4 if tilt else 0), C.CYAN)
    if not tilt:
        for dx, dy, color in candies:
            c.pixel(x + dx, y + dy, color)


def full_heap():
    out = []
    n = 0
    for y, x0, x1 in HEAP:
        for dx in range(x0, x1 + 1):
            out.append((dx, y - BOWL_Y, CANDY_COLORS[(n * 3 + y) % 5]))
            n += 1
    return out


def sack(c, x, fill, dollar=False):
    """White sack, bottom at y 14, grows with fill (0..4)."""
    h = 4 + fill
    w = 5 + (fill + 1) // 2
    top = 15 - h
    c.rect(x, top + 1, w, h - 1, C.WHITE, fill=True)
    c.hline(x + 1, top, w - 2, C.WHITE)
    c.pixel(x + w // 2, top - 1, C.WHITE)  # the gathered neck
    if dollar:
        cx = x + w // 2 - 1
        c.small_text("$", cx, top + 1, C.YELLOW)


def sign(c, state="one"):
    c.rect(SIGN_X, 0, W - SIGN_X, 14, C.YELLOW)
    c.vline(SIGN_X + 4, 14, 1, C.YELLOW)
    c.vline(W - 5, 14, 1, C.YELLOW)
    c.small_text("PLEASE", TEXT_X, 2, C.WHITE)
    c.small_text("TAKE", TEXT_X, 8, C.WHITE)
    if state == "one":
        c.small_text("ONE", ONE_X, 8, C.WHITE)
    elif state == "strike":
        c.small_text("ONE", ONE_X, 8, C.WHITE)
        c.hline(ONE_X - 1, 10, Canvas.small_text_width("ONE") + 2, C.RED)
    else:
        c.small_text("ALL", ONE_X, 8, C.RED)


def scenery(c):
    # crescent moon
    for y, x0, x1 in ((1, 3, 4), (2, 2, 3), (3, 2, 2), (4, 2, 3), (5, 3, 4)):
        c.hline(x0, y, x1 - x0 + 1, C.YELLOW)
    for x, y in ((11, 2), (20, 0), (29, 3), (40, 1)):
        c.pixel(x, y, C.WHITE)
    c.hline(0, FLOOR_Y, W, C.BLUE)


def main():
    beats = []
    for name, count in SCRIPT:
        beats.extend((name, k) for k in range(count))
    assert len(beats) == FRAMES, len(beats)
    assert ONE_X + Canvas.small_text_width("ONE") < W - 1

    heap = full_heap()
    # the piece the witch takes, the piece the kid takes, the sad last piece
    first_take = heap.index(max(heap, key=lambda p: (-p[1], p[0])))
    anim = Animation(delay=DELAY)
    candies = list(heap)
    sad = None

    for f, (beat, k) in enumerate(beats):
        c = anim.frame()
        scenery(c)
        sign_state = "one"
        bowl_drawn = False

        if beat == "witch_in":
            x = -8 + (k + 1) * (KID_STOP + 8) // 6
            witch(c, x, step=k)
        elif beat == "take1":
            if k == 0:
                taken = candies.pop(first_take)
                witch(c, KID_STOP, reach=True)
                c.pixel(KID_STOP + 10, 9, taken[2])     # in her hand
            else:
                witch(c, KID_STOP, bucket_candy=True)
        elif beat == "thanks":
            witch(c, KID_STOP, bucket_candy=True)
            c.glyph("+HEART", KID_STOP + 9, 1 - k, C.MAGENTA)
        elif beat == "witch_out":
            x = KID_STOP - (k + 1) * 15
            witch(c, x, step=k, face_left=True, bucket_candy=True)
        elif beat == "empty":
            pass
        elif beat == "kid_in":
            x = -8 + (k + 1) * (KID2_STOP + 8) // 5
            kid(c, x, step=k)
        elif beat == "read":
            kid(c, KID2_STOP)
            c.text("?", KID2_STOP + 9, 0 + (k % 2), C.WHITE)
        elif beat == "take2":
            if k == 0:
                taken = candies.pop()                  # top of the heap
                kid(c, KID2_STOP, arm=(BOWL_X + 1, 9))
                c.pixel(BOWL_X + 1, 8, taken[2])
            else:
                kid(c, KID2_STOP)
        elif beat == "look":
            kid(c, KID2_STOP, look=[-1, 1, -1][k])
        elif beat == "dump":
            # sack out, bowl up, pour, bowl down with one piece
            sx = KID2_STOP + 8
            if k == 0:
                kid(c, KID2_STOP)
                sack(c, sx, 0)
            elif k == 1:
                kid(c, KID2_STOP, arm=(BOWL_X - 1, 5))
                sack(c, sx, 0)
                bowl(c, BOWL_X - 2, 5, [(dx, dy, col) for dx, dy, col in candies])
                bowl_drawn = True
            elif k < 5:
                kid(c, KID2_STOP, arm=(BOWL_X - 1, 4))
                sack(c, sx, k)
                bowl(c, BOWL_X - 1, 3, [], tilt=True)
                bowl_drawn = True
                # the stream, from the bowl's low lip into the sack
                for i in range(6):
                    yy = 3 + i + (f % 2)
                    xx = BOWL_X - 2 - i // 2
                    c.pixel(xx, yy, CANDY_COLORS[(i + f) % 5])
                    if i % 2:
                        c.pixel(xx + 1, yy, CANDY_COLORS[(i + f + 2) % 5])
            else:
                sad = (5, -1, C.GREEN)
                candies = [sad]
                kid(c, KID2_STOP)
                sack(c, sx, 4)
        elif beat == "mask":
            kid(c, KID2_STOP, mask=True)
            sack(c, KID2_STOP + 8, 4, dollar=k >= 1)
        elif beat == "edit":
            sack(c, KID2_STOP + 8, 4, dollar=True)
            kid(c, KID2_STOP, mask=True, marker=True)
            sign_state = "strike" if k == 0 else "all"
        elif beat == "sneak":
            sign_state = "all"
            x = KID2_STOP - (k + 1) * 12
            kid(c, x, step=k, look=-1, mask=True)
            sack(c, x - 9, 4, dollar=True)
        elif beat == "witch_back":
            sign_state = "all"
            x = -8 + (k + 1) * (KID_STOP + 8) // 4
            witch(c, x, step=k, bucket_candy=True)
        elif beat == "stare":
            sign_state = "all"
            witch(c, KID_STOP, bucket_candy=True)
            if k >= 1:
                c.text("!", KID_STOP + 9, 0 if k % 2 else 1, C.RED)
        elif beat == "sign":
            sign_state = "all"
            # she reads the new sign... and obeys it, as always
            if k == 0:
                witch(c, KID_STOP, bucket_candy=True)
                c.small_text("?", KID_STOP + 9, 1, C.WHITE)
            elif k == 1:
                candies = []
                witch(c, KID_STOP, reach=True, bucket_candy=True)
                c.pixel(KID_STOP + 10, 9, sad[2])
            else:
                witch(c, KID_STOP, bucket_candy=True)
                c.glyph("+HEART", KID_STOP + 9, 1, C.MAGENTA)

        if not bowl_drawn:
            bowl(c, BOWL_X, BOWL_Y, candies)
        sign(c, sign_state)

    assert len(anim) == FRAMES
    out = Path(__file__).resolve().parents[2] / "src/sample/candy_bowl.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
