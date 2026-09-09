"""
The panel's palette.

Each LED stores 3 bits -- one per channel -- so there are exactly 8 colors and
no brightness levels. A color here is a ``(r, g, b)`` triple of 0/1.

Because there is no brightness, BLUE -> CYAN -> WHITE is the closest thing to a
dim -> mid -> bright ramp, and it is what the effects in this package use to
fake a glow.
"""

from __future__ import annotations

BLACK = (0, 0, 0)
BLUE = (0, 0, 1)
GREEN = (0, 1, 0)
CYAN = (0, 1, 1)
RED = (1, 0, 0)
MAGENTA = (1, 0, 1)
YELLOW = (1, 1, 0)
WHITE = (1, 1, 1)

ALL = [BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE]

BY_NAME = {
    "black": BLACK,
    "blue": BLUE,
    "green": GREEN,
    "cyan": CYAN,
    "red": RED,
    "magenta": MAGENTA,
    "pink": MAGENTA,
    "yellow": YELLOW,
    "white": WHITE,
}

NAME_OF = {
    BLACK: "black",
    BLUE: "blue",
    GREEN: "green",
    CYAN: "cyan",
    RED: "red",
    MAGENTA: "magenta",
    YELLOW: "yellow",
    WHITE: "white",
}

#: Stand-in for a brightness ramp, dimmest first.
GLOW = [BLACK, BLUE, CYAN, WHITE]

#: A cyclic ramp that reads as a smooth hue rotation on the panel.
SPECTRUM = [BLUE, CYAN, GREEN, YELLOW, RED, MAGENTA]


def parse(value):
    """Accept a name, a ``#rrggbb`` string, or an ``(r, g, b)`` triple."""
    if isinstance(value, tuple):
        return value
    text = str(value).strip().lower()
    if text in BY_NAME:
        return BY_NAME[text]
    if text.startswith("#"):
        return from_hex(text)
    raise ValueError(f"Unknown color: {value!r}")


def from_hex(text):
    """Quantize a ``#rrggbb`` string to the nearest panel color."""
    text = text.lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"Not a hex color: #{text}")
    return quantize(
        int(text[0:2], 16),
        int(text[2:4], 16),
        int(text[4:6], 16),
    )


def quantize(r, g, b, threshold=128):
    """Reduce 0-255 channels to the panel's 1-bit-per-channel palette."""
    return (
        1 if r >= threshold else 0,
        1 if g >= threshold else 0,
        1 if b >= threshold else 0,
    )


def ramp(sequence, position):
    """
    Sample a color ramp with ``position`` in [0, 1).

    Wraps, so it is safe to drive from an angle that crosses 1.0 -- which is
    what makes a seamless loop possible.
    """
    if not sequence:
        raise ValueError("Empty ramp")
    index = int(position * len(sequence)) % len(sequence)
    return sequence[index]
