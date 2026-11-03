#!/usr/bin/env python3
"""
Polls open -- a neon sign buzzes on, a line files through the booth.

A dark panel holds an unlit neon sign: a blue tube spelling POLLS OPEN in
a blue frame. It buzzes into life like a shop's OPEN sign -- the frame
catches cyan, then the letters stutter on in magenta one at a time, a
couple dropping out again, one sputtering white -- until the whole sign
burns steady.

Cut to the polling place: a voting booth with a white frame and a striped
blue-and-cyan curtain under a small VOTE sign, a little cyan-framed
magenta OPEN still glowing in the corner. A line of voters waits on the left: a man
in a green shirt, a tall woman in magenta walking a white dog, a
white-haired voter in cyan, and a parent in yellow pushing a red stroller.
One at a time each steps behind the curtain (feet showing underneath,
curtain twitching), and walks out the other side wearing a tiny red I VOTED
sticker on the chest that flashes as they emerge (white on the warm
shirts). Once the last voter is out, the curtain is drawn back: an empty
booth, a yellow shelf, a white ballot and a glinting pen.

To close, the first voter (waving) and the dog walker stand either side of
YOUR TURN / GO VOTE!, stickers blinking.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

DELAY = 140
W, H = 96, 16

# -- beat sheet (frame indexes) -------------------------------------------
SIGN_FRAMES = 13        # 0-12 the neon sign buzzes on and holds
SCENE_FRAMES = 28       # then the polling place
END_FRAMES = 12         # then YOUR TURN / GO VOTE!
FRAMES = SIGN_FRAMES + SCENE_FRAMES + END_FRAMES

# -- the neon sign ----------------------------------------------------------
SIGN_TEXT = "POLLS OPEN"
SIGN_TX = (W - Canvas.text_width(SIGN_TEXT)) // 2
SIGN_TY = 4
BOX_X, BOX_Y = SIGN_TX - 2, 1
BOX_W, BOX_H = Canvas.text_width(SIGN_TEXT) + 4, 13
LETTER_X = [SIGN_TX + 6 * i for i in range(len(SIGN_TEXT))]

# Per frame: frame state ('off', 'lit', 'flash') and which letters are lit.
# Letters are indexed into SIGN_TEXT; the space at 5 is never drawn.
NEON = [
    ("off", set()),
    ("lit", set()),
    ("off", set()),
    ("lit", {0, 1}),
    ("lit", {0, 1, 2, 3}),
    ("lit", {0, 1, 3, 4, 6}),
    ("lit", {0, 1, 2, 3, 4, 6, 7}),
    ("flash", {0, 1, 2, 3, 4, 6, 7, 8}),
    ("lit", {0, 1, 2, 3, 4, 6, 8, 9}),
    ("lit", set(range(10))),
    ("lit", set(range(10))),
    ("lit", set(range(10))),
    ("lit", set(range(10))),
]
SPUTTER = {7: 7, 8: 7}  # frame -> letter that sputters white
assert len(NEON) == SIGN_FRAMES

# -- the polling place ------------------------------------------------------
FLOOR = 15                      # feet stand on this row
BOOTH_X0, BOOTH_X1 = 40, 54     # outer posts
BOOTH_TOP = 6
CURTAIN_BOTTOM = 13             # curtain stops here; feet show below
VOTE_SIGN = "VOTE"
VOTE_X = (BOOTH_X0 + BOOTH_X1 + 1 - Canvas.small_text_width(VOTE_SIGN)) // 2
MINI_SIGN = "OPEN"
MINI_X = W - Canvas.small_text_width(MINI_SIGN) - 2
SPEED = 2
EXIT_SPEED = 3                  # a spring in the step once you've voted
HOLD = 2                        # scene frames before the line shuffles up
VOTE_TIME = 3                   # frames spent behind the curtain
GAP = 2                         # space kept between people in line
WAIT_FRONT = BOOTH_X0 - 1       # front of the line waits by the post

STICKER = C.RED


class Voter:
    def __init__(self, shirt, hair, pants, height, extra=None):
        self.x = 0              # left edge of the person themself
        self.shirt = shirt
        self.hair = hair
        self.pants = pants
        self.height = height
        self.extra = extra      # None, 'dog' or 'stroller', both out in front
        self.state = "queue"    # queue -> booth -> out
        self.timer = 0
        self.voted_at = None
        self.step = 0

    @property
    def lead(self):
        """Pixels the companion sticks out in front of the person."""
        return {"dog": 8, "stroller": 7}.get(self.extra, 0)

    @property
    def front(self):
        return self.x + 2 + self.lead


def make_line():
    # front of the line first
    people = [
        Voter(C.GREEN, C.RED, C.BLUE, 10),
        Voter(C.MAGENTA, C.YELLOW, C.BLUE, 11, extra="dog"),
        Voter(C.CYAN, C.WHITE, C.BLUE, 9),
        Voter(C.YELLOW, C.MAGENTA, C.BLUE, 10, extra="stroller"),
    ]
    front = WAIT_FRONT - 4
    for p in people:
        p.x = front - 2 - p.lead
        front = p.x - GAP - 1
    return people


def simulate():
    """Run the line; return per scene frame a snapshot of each voter."""
    people = make_line()
    shots = []
    for f in range(SCENE_FRAMES):
        busy = any(p.state == "booth" for p in people)
        ahead = None                        # the person in line in front
        prev = None                         # the voter before this one
        for p in people:
            moved = False
            if p.state == "queue":
                limit = WAIT_FRONT if busy else BOOTH_X0
                if ahead is not None:
                    limit = min(limit, ahead.x - GAP - 1)
                new_front = p.front if f < HOLD else min(p.front + SPEED, limit)
                if new_front != p.front:
                    p.x += new_front - p.front
                    moved = True
                if p.front >= BOOTH_X0:
                    p.state = "booth"       # slips behind the curtain
                    busy = True
                ahead = p if p.state == "queue" else None
            elif p.state == "booth":
                p.timer += 1
                # step out only once the last voter has cleared the doorway
                room = prev is None or prev.state != "out" or \
                    prev.x > BOOTH_X1 + 3 + p.lead + GAP + 4
                if p.timer >= VOTE_TIME and room:
                    p.state = "out"
                    p.voted_at = f
                    p.x = BOOTH_X1 + 1      # steps out the far side
                    moved = True
            else:
                p.x += EXIT_SPEED
                moved = True
            if moved:
                p.step += 1
            prev = p
        shots.append([(p.x, p.state, p.step, p.voted_at) for p in people])
    return make_line(), shots


def draw_person(c, x, p, step, voted, flash=False, wave=None):
    """A 3-wide person standing on FLOOR, facing right."""
    top = FLOOR - p.height + 1
    legs = 2
    body = p.height - 3 - legs          # rows of shirt
    c.hline(x, top, 3, p.hair)
    c.hline(x, top + 1, 3, C.YELLOW if p.hair != C.YELLOW else C.YELLOW)
    c.pixel(x, top + 1, p.hair)         # hair at the back of the head
    c.pixel(x + 2, top + 1, C.BLACK)    # and an eye looking ahead
    c.hline(x, top + 2, 3, C.YELLOW)
    for r in range(body):
        c.hline(x, top + 3 + r, 3, p.shirt)
    if voted:
        col = C.WHITE if flash else STICKER
        if p.shirt in (C.RED, C.MAGENTA):
            col = STICKER if flash else C.WHITE     # contrast on warm shirts
        c.pixel(x + 1, top + 4, col)
    if wave is not None:
        # an arm raised beside the head, flapping
        ax = x + 3 if wave >= 0 else x - 1
        c.pixel(ax, top + 3, p.shirt)
        c.pixel(ax, top + 2 - (abs(wave) % 2), C.YELLOW)
    ly = FLOOR - 1
    if step % 2:
        c.pixel(x, ly, p.pants)
        c.pixel(x + 2, ly, p.pants)
        c.pixel(x, ly + 1, p.pants)
        c.pixel(x + 2, ly + 1, p.pants)
    else:
        c.hline(x, ly, 3, p.pants)
        c.pixel(x + 1, ly + 1, p.pants)


DOG = [
    "W...WW.",
    ".WWWWWW",
]
DOG_LEGS = [".W..W..", "W....W."]


def draw_dog(c, x, step):
    """A small white dog, 7 wide, nose to the right, on rows 13-15."""
    for r, line in enumerate(DOG + [DOG_LEGS[step % 2]]):
        for k, ch in enumerate(line):
            if ch == "W":
                c.pixel(x + k, FLOOR - 2 + r, C.WHITE)
    return (x + 4, FLOOR - 2)                   # collar


def draw_stroller(c, x):
    """A red pram, 5 wide, with a cyan hood and a handle back to the parent."""
    c.hline(x, FLOOR - 4, 3, C.RED)
    c.pixel(x + 3, FLOOR - 5, C.CYAN)
    c.pixel(x + 4, FLOOR - 4, C.CYAN)
    c.pixel(x + 3, FLOOR - 4, C.CYAN)
    c.hline(x, FLOOR - 3, 5, C.RED)
    c.hline(x, FLOOR - 2, 5, C.RED)
    c.pixel(x, FLOOR, C.WHITE)                  # wheels
    c.pixel(x + 4, FLOOR, C.WHITE)
    c.vline(x - 1, FLOOR - 5, 3, C.WHITE)       # handle


def draw_voter(c, p, x, step, voted, flash=False):
    if p.extra == "dog":
        cx, cy = draw_dog(c, x + 4, step)
        c.line(x + 3, FLOOR - 5, cx - 1, cy - 1, C.RED)   # leash
    elif p.extra == "stroller":
        draw_stroller(c, x + 5)
        c.pixel(x + 3, FLOOR - 5, C.YELLOW)     # hand on the handle
    draw_person(c, x, p, step, voted, flash)


def draw_booth(c, f, inside, open_for=0):
    # the VOTE sign over the booth
    c.small_text(VOTE_SIGN, VOTE_X, 0, C.WHITE)
    # frame
    c.hline(BOOTH_X0, BOOTH_TOP, BOOTH_X1 - BOOTH_X0 + 1, C.WHITE)
    c.vline(BOOTH_X0, BOOTH_TOP, FLOOR - BOOTH_TOP + 1, C.WHITE)
    c.vline(BOOTH_X1, BOOTH_TOP, FLOOR - BOOTH_TOP + 1, C.WHITE)
    if open_for:
        # the curtain drawn back to both posts: an empty booth, a shelf
        # with a white ballot on it, waiting for whoever's next
        for x in (BOOTH_X0 + 1, BOOTH_X0 + 2, BOOTH_X1 - 2, BOOTH_X1 - 1):
            c.vline(x, BOOTH_TOP + 1, CURTAIN_BOTTOM - BOOTH_TOP,
                    C.CYAN if x % 2 else C.BLUE)
        c.hline(BOOTH_X0 + 3, 10, BOOTH_X1 - BOOTH_X0 - 5, C.YELLOW)
        c.rect(BOOTH_X0 + 5, 8, 4, 2, C.WHITE, fill=True)
        if open_for % 2:
            c.pixel(BOOTH_X0 + 10, 8, C.WHITE)   # the pen, glinting
            c.pixel(BOOTH_X0 + 9, 9, C.WHITE)
        else:
            c.pixel(BOOTH_X0 + 10, 8, C.RED)
            c.pixel(BOOTH_X0 + 9, 9, C.RED)
        return
    # curtain: stripes, which twitch while someone is inside
    shift = (f % 2) if inside else 0
    for x in range(BOOTH_X0 + 1, BOOTH_X1):
        col = C.CYAN if (x + shift) % 2 else C.BLUE
        bottom = CURTAIN_BOTTOM
        if inside and (x + f) % 5 == 0:
            bottom += 1             # a fold swinging lower
        c.vline(x, BOOTH_TOP + 1, bottom - BOOTH_TOP, col)


def draw_neon(c, f):
    state, lit = NEON[f]
    frame_col = {"off": C.BLUE, "lit": C.CYAN, "flash": C.WHITE}[state]
    c.rect(BOX_X, BOX_Y, BOX_W, BOX_H, frame_col)
    # little hanging chains up to the top edge
    c.pixel(BOX_X + 6, 0, C.WHITE if state != "off" else C.BLUE)
    c.pixel(BOX_X + BOX_W - 7, 0, C.WHITE if state != "off" else C.BLUE)
    for i, ch in enumerate(SIGN_TEXT):
        if ch == " ":
            continue
        if SPUTTER.get(f) == i:
            col = C.WHITE
        elif i in lit:
            col = C.MAGENTA
        else:
            col = C.BLUE            # the dead tube is still faintly visible
        c.text(ch, LETTER_X[i], SIGN_TY, col)


END_LINE1, END_LINE2 = "YOUR TURN", "GO VOTE!"
END_Y1, END_Y2 = 0, 9


def draw_end(c, k, people):
    n1 = min(len(END_LINE1), (k + 1) * 5)
    n2 = min(len(END_LINE2), k * 4)
    x1 = (W - Canvas.text_width(END_LINE1)) // 2
    x2 = (W - Canvas.text_width(END_LINE2)) // 2
    c.text(END_LINE1[:n1], x1, END_Y1, C.YELLOW)
    c.text(END_LINE2[:n2], x2, END_Y2, C.WHITE if k % 4 else C.CYAN)
    # two voters flank the words, waving, stickers blinking
    left, right = people[0], people[1]
    draw_person(c, 9, left, 0, True, flash=k % 2 == 0, wave=k + 1)
    draw_voter(c, right, W - 15, k // 2, True, flash=k % 2 == 1)


def main():
    anim = Animation(delay=DELAY)
    for f in range(SIGN_FRAMES):
        draw_neon(anim.frame(), f)

    people, shots = simulate()
    for f, shot in enumerate(shots):
        c = anim.frame()
        c.small_text(MINI_SIGN, MINI_X, 0, C.MAGENTA)
        c.rect(MINI_X - 2, -1, Canvas.small_text_width(MINI_SIGN) + 4, 7, C.CYAN)
        inside = any(s[1] == "booth" for s in shot)
        for p, (x, state, step, voted_at) in zip(people, shot):
            if state == "booth":
                continue
            voted = state == "out"
            flash = voted and f - voted_at < 2
            draw_voter(c, p, x, step, voted, flash)
        last = [s[3] for s in shot]
        open_for = 0
        if all(v is not None for v in last) and f - max(last) >= 2:
            open_for = f - max(last) - 1
        draw_booth(c, f, inside, open_for)
        # feet under the curtain while someone votes
        for p, (_x, state, _s, _v) in zip(people, shot):
            if state == "booth":
                x = (BOOTH_X0 + BOOTH_X1) // 2 - 1
                for y in (FLOOR - 1, FLOOR):
                    c.pixel(x, y, p.pants)
                    c.pixel(x + 2, y, p.pants)
                if p.extra == "dog":
                    c.pixel(x + 5, FLOOR, C.WHITE)
                    c.pixel(x + 7, FLOOR, C.WHITE)
                elif p.extra == "stroller":
                    c.pixel(x + 4, FLOOR, C.WHITE)
                    c.pixel(x + 7, FLOOR, C.WHITE)

    for k in range(END_FRAMES):
        draw_end(anim.frame(), k, people)

    assert len(anim) == FRAMES <= 53
    out = Path(__file__).resolve().parents[2] / "src/sample/vote_polls_open.jt"
    anim.save(out)
    print(f"{out.name}: {anim.describe()}")


if __name__ == "__main__":
    main()
