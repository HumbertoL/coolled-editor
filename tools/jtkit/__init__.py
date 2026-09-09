"""
jtkit -- author and inspect CoolLEDX ``.jt`` files.

    from jtkit import Animation, colors as C

    anim = Animation(delay=200)
    for step in range(8):
        frame = anim.frame()
        frame.text("HELLO", x="center", y=4, color=C.YELLOW)
        frame.pixel(step * 12, 14, C.CYAN)
    anim.save("hello.jt")

See ``tools/README.md`` for the format notes and the verification habit that
catches packing mistakes.
"""

from . import colors, font, preview
from .animation import (
    DEFAULT_DELAY_MS,
    MAX_TESTED_FRAMES,
    Animation,
    load_jt,
    round_trip_ok,
)
from .canvas import (
    Canvas,
    gradient,
    highlight,
    vertical_wipe,
    wipe,
)

__all__ = [
    "Animation",
    "Canvas",
    "DEFAULT_DELAY_MS",
    "MAX_TESTED_FRAMES",
    "colors",
    "font",
    "gradient",
    "highlight",
    "load_jt",
    "preview",
    "round_trip_ok",
    "vertical_wipe",
    "wipe",
]
