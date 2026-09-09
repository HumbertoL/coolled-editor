"""
A single frame you can draw on.

Every drawing method takes a ``color`` that may be either a plain ``(r, g, b)``
triple or a callable ``f(x, y) -> color``. The callable form is what makes
effects like a travelling highlight or a left-to-right wipe one-liners: the
color becomes a function of position, so the same ``text()`` call renders
differently each frame.
"""

from __future__ import annotations

from . import colors
from .font import FONT_5X7, GLYPH_HEIGHT, GLYPH_WIDTH, glyph

DEFAULT_TRACKING = 1

#: Advance for a space when spacing proportionally, since it has no ink.
BLANK_ADVANCE = 3


def glyph_ink(char, fold_case=True):
    """First and last cell column containing ink, or None for a blank glyph."""
    bitmap = glyph(char, fold_case=fold_case)
    columns = [
        column
        for column in range(GLYPH_WIDTH)
        if any(row[column] == "#" for row in bitmap)
    ]
    if not columns:
        return None
    return columns[0], columns[-1]


def layout_text(text, tracking=DEFAULT_TRACKING, proportional=False, fold_case=True):
    """
    Work out where each glyph goes, and how wide the string is.

    With ``proportional``, each glyph advances by its own ink width instead of
    the full 5-pixel cell, and its side bearings are trimmed. That matters for
    narrow glyphs: '!' is a single column of ink in a 5-wide cell, so fixed
    spacing leaves a 3px hole before it and 2 dead columns after -- which also
    throws off centring, since the nominal width counts space that is never
    inked.

    Returns ``([(char, cell_x)], width)``, where ``cell_x`` is where the
    glyph's cell origin goes; for a trimmed glyph that is left of its ink.
    """
    positions = []
    x = 0
    for char in text:
        ink = glyph_ink(char, fold_case=fold_case) if proportional else None
        if not proportional:
            positions.append((char, x))
            advance = GLYPH_WIDTH
        elif ink is None:
            positions.append((char, x))
            advance = BLANK_ADVANCE
        else:
            first, last = ink
            # Shift the cell so the glyph's ink starts exactly at x.
            positions.append((char, x - first))
            advance = last - first + 1
        x += advance + tracking
    return positions, max(0, x - tracking)


class Canvas:
    """A width x height grid of palette colors. Unset pixels read as black."""

    def __init__(self, width=96, height=16):
        self.width = width
        self.height = height
        self._pixels = {}

    # -- basics ----------------------------------------------------------

    def clone(self):
        copy = Canvas(self.width, self.height)
        copy._pixels = dict(self._pixels)
        return copy

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x, y):
        return self._pixels.get((x, y), colors.BLACK)

    def pixel(self, x, y, color):
        x, y = int(x), int(y)
        if not self.in_bounds(x, y):
            return self
        resolved = _resolve(color, x, y)
        if resolved == colors.BLACK:
            self._pixels.pop((x, y), None)
        else:
            self._pixels[(x, y)] = resolved
        return self

    def clear(self):
        self._pixels.clear()
        return self

    def fill(self, color):
        for y in range(self.height):
            for x in range(self.width):
                self.pixel(x, y, color)
        return self

    def lit(self):
        """Coordinates of every non-black pixel."""
        return list(self._pixels)

    def is_blank(self):
        return not self._pixels

    # -- text ------------------------------------------------------------

    @staticmethod
    def text_width(text, tracking=DEFAULT_TRACKING, font=FONT_5X7, proportional=False):
        del font
        if not text:
            return 0
        return layout_text(text, tracking, proportional)[1]

    def center_x(self, text, tracking=DEFAULT_TRACKING, proportional=False):
        return (self.width - self.text_width(text, tracking, proportional=proportional)) // 2

    def text(
        self,
        text,
        x=0,
        y=0,
        color=colors.WHITE,
        tracking=DEFAULT_TRACKING,
        fold_case=True,
        proportional=False,
    ):
        """
        Draw ``text`` with its top-left at (x, y).

        ``x`` may be ``"center"`` to centre the string horizontally.
        ``proportional`` trims each glyph's side bearings -- see
        :func:`layout_text`.
        """
        if x == "center":
            x = self.center_x(text, tracking, proportional=proportional)
        positions, _ = layout_text(text, tracking, proportional, fold_case)
        for char, cell_x in positions:
            bitmap = glyph(char, fold_case=fold_case)
            for row in range(GLYPH_HEIGHT):
                for col in range(GLYPH_WIDTH):
                    if bitmap[row][col] == "#":
                        self.pixel(x + cell_x + col, y + row, color)
        return self

    def glyph(self, name, x=0, y=0, color=colors.WHITE, fold_case=True):
        """
        Draw one glyph by name, for the symbol entries in the font.

        ``text()`` iterates over characters, so passing it "+ARROW_U" spells
        that out literally. Use this for the named symbols instead.
        """
        bitmap = glyph(name, fold_case=fold_case)
        if x == "center":
            x = (self.width - GLYPH_WIDTH) // 2
        for row in range(GLYPH_HEIGHT):
            for col in range(GLYPH_WIDTH):
                if bitmap[row][col] == "#":
                    self.pixel(x + col, y + row, color)
        return self

    # -- shapes ----------------------------------------------------------

    def hline(self, x, y, length, color):
        for offset in range(int(length)):
            self.pixel(x + offset, y, color)
        return self

    def vline(self, x, y, length, color):
        for offset in range(int(length)):
            self.pixel(x, y + offset, color)
        return self

    def rect(self, x, y, width, height, color, fill=False):
        if fill:
            for row in range(int(height)):
                self.hline(x, y + row, width, color)
            return self
        self.hline(x, y, width, color)
        self.hline(x, y + height - 1, width, color)
        self.vline(x, y, height, color)
        self.vline(x + width - 1, y, height, color)
        return self

    def line(self, x0, y0, x1, y1, color):
        """Bresenham, so diagonals stay evenly spaced."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx - dy
        while True:
            self.pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return self
            doubled = 2 * error
            if doubled > -dy:
                error -= dy
                x0 += sx
            if doubled < dx:
                error += dx
                y0 += sy

    def blit(self, source, dx=0, dy=0, transparent=True):
        """Copy another canvas in at an offset."""
        for (x, y), color in source._pixels.items():
            self.pixel(x + dx, y + dy, color)
        if not transparent:
            for y in range(source.height):
                for x in range(source.width):
                    if (x, y) not in source._pixels:
                        self.pixel(x + dx, y + dy, colors.BLACK)
        return self

    def map(self, function):
        """Recolor in place: ``function(x, y, color) -> color``."""
        for (x, y), color in list(self._pixels.items()):
            self.pixel(x, y, function(x, y, color))
        return self

    def each(self, function):
        """Set every pixel from ``function(x, y) -> color``. Good for fields."""
        for y in range(self.height):
            for x in range(self.width):
                self.pixel(x, y, function(x, y))
        return self


def _resolve(color, x, y):
    if callable(color):
        return color(x, y)
    return color


# -- effect helpers ------------------------------------------------------
#
# Each returns a callable suitable for passing as `color`.


def highlight(base, accent, head, half_width=2):
    """A band of ``accent`` centred on column ``head``, over ``base``."""

    def color_at(x, _y):
        return accent if abs(x - head) <= half_width else base

    return color_at


def wipe(lit, unlit, edge):
    """``lit`` left of column ``edge``, ``unlit`` from there on."""

    def color_at(x, _y):
        return lit if x < edge else unlit

    return color_at


def vertical_wipe(lit, unlit, edge):
    """``lit`` above row ``edge``, ``unlit`` below."""

    def color_at(_x, y):
        return lit if y < edge else unlit

    return color_at


def gradient(sequence, axis="x", period=None, phase=0.0, size=96):
    """Cycle a ramp along an axis -- handy for barber-pole style motion."""
    span = period or size

    def color_at(x, y):
        position = (x if axis == "x" else y) / span + phase
        return colors.ramp(sequence, position % 1.0)

    return color_at
