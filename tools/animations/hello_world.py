#!/usr/bin/env python3
"""
Hello, world -- seven ways.

The language on top, the line on the bottom, seven frames each: Python, C,
JavaScript, Ruby, Go, Bash and Java. The Java one is abbreviated, which is
also a joke about Java.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
PER = 7
LANGS = [
    ("PYTHON", 'print("hi")', C.YELLOW),
    ("C", 'printf("hi");', C.CYAN),
    ("JAVASCRIPT", 'console.log("hi")', C.YELLOW),
    ("RUBY", 'puts "hi"', C.RED),
    ("GO", 'fmt.Println("hi")', C.CYAN),
    ("BASH", "echo hi", C.GREEN),
    ("JAVA", 'out.println("hi");', C.RED),
]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        i = min(len(LANGS) - 1, index // PER)
        name, code, color = LANGS[i]
        k = index - i * PER
        frame.text(name, 2, 0, color, proportional=True)
        # The code types in over the first frames.
        typed = code[:min(len(code), (k + 1) * 4)]
        frame.text(typed, 2, 9, C.WHITE, proportional=True, fold_case=True)
        if len(typed) < len(code) or k % 2:
            cx = 2 + frame.text_width(typed, proportional=True) + 1
            frame.vline(cx, 9, 7, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hello_world.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
