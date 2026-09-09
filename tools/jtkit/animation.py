"""
Frames in, ``.jt`` file out -- and back again.

The bit layout is the part worth stating carefully, because getting it wrong
produces a file that still displays but is subtly scrambled:

* Each LED holds 3 bits, one per channel, so a frame of 96x16 takes 576 bytes.
* The three color planes span the WHOLE animation, not each frame: every
  frame's red bits, then every frame's green, then every frame's blue.
* Within a plane the frames sit side by side, and within a frame each column is
  walked top to bottom before moving right.

So the bit for (frame, column, row) in a plane is at
``(frame * width + column) * height + row``.

This matches what the editor's ``parse_data.js`` reads and ``export_data.js``
writes, and it is what the vendor's own animation packs use.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

from .canvas import Canvas

#: Largest frame count seen in the vendor packs. Beyond this is untested on
#: real hardware -- the sign may refuse or truncate the transfer.
MAX_TESTED_FRAMES = 24

DEFAULT_DELAY_MS = 200


class Animation:
    """An ordered list of canvases sharing one frame delay."""

    def __init__(self, width=96, height=16, delay=DEFAULT_DELAY_MS):
        self.width = width
        self.height = height
        self.delay = delay
        self.frames = []

    def __len__(self):
        return len(self.frames)

    def __iter__(self):
        return iter(self.frames)

    def __getitem__(self, index):
        return self.frames[index]

    def frame(self):
        """Append a fresh blank canvas and return it for drawing."""
        canvas = Canvas(self.width, self.height)
        self.frames.append(canvas)
        return canvas

    def add(self, canvas):
        if (canvas.width, canvas.height) != (self.width, self.height):
            raise ValueError(
                f"Frame is {canvas.width}x{canvas.height}, "
                f"animation is {self.width}x{self.height}"
            )
        self.frames.append(canvas)
        return canvas

    def bytes_per_frame(self):
        return self.width * self.height * 3 // 8

    # -- encoding --------------------------------------------------------

    def pack(self):
        """Flatten to the byte list that goes in ``aniData``."""
        if not self.frames:
            raise ValueError("Nothing to pack: no frames")

        bits = []
        for channel in range(3):
            for canvas in self.frames:
                for column in range(self.width):
                    for row in range(self.height):
                        bits.append(
                            "1" if canvas.get(column, row)[channel] else "0"
                        )

        packed = bytearray()
        for start in range(0, len(bits), 8):
            packed.append(int("".join(bits[start : start + 8]), 2))

        expected = len(self.frames) * self.bytes_per_frame()
        if len(packed) != expected:
            raise AssertionError(
                f"Packed {len(packed)} bytes, expected {expected}"
            )
        return list(packed)

    def to_jt(self):
        """The parsed ``.jt`` structure: a one-element list, as the app writes."""
        if len(self.frames) > MAX_TESTED_FRAMES:
            warnings.warn(
                f"{len(self.frames)} frames exceeds the {MAX_TESTED_FRAMES} "
                "seen in vendor packs; the sign may refuse or truncate it.",
                stacklevel=2,
            )
        return [
            {
                "dataType": 0,
                "data": {
                    "aniType": 1,
                    "pixelHeight": self.height,
                    "pixelWidth": self.width,
                    "frameNum": len(self.frames),
                    "delays": self.delay,
                    "aniData": self.pack(),
                },
            }
        ]

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_jt()))
        return path

    def describe(self):
        total = len(self.frames) * self.delay
        return (
            f"{len(self.frames)} frames at {self.delay}ms "
            f"= {total / 1000:.1f}s loop, "
            f"{len(self.frames) * self.bytes_per_frame()} pixel bytes"
        )


def load_jt(path):
    """
    Read a ``.jt`` back into an Animation.

    Works on editor exports, files written here, and static (``graffitiData``)
    files, which come back as a single frame.
    """
    raw = json.loads(Path(path).read_text())
    data = raw[0]["data"] if isinstance(raw, list) else raw["data"]

    pixel_data = data.get("aniData")
    if pixel_data is None:
        pixel_data = data["graffitiData"]

    width = data.get("pixelWidth", 96)
    height = data.get("pixelHeight", 16)
    per_frame = width * height * 3 // 8
    # Trust the byte count over frameNum; some vendor entries disagree.
    frame_count = max(1, round(len(pixel_data) / per_frame))

    animation = Animation(width, height, data.get("delays", DEFAULT_DELAY_MS))
    plane_bits = frame_count * width * height

    def bit(index):
        byte_index = index >> 3
        if byte_index >= len(pixel_data):
            return 0
        return (pixel_data[byte_index] >> (7 - (index & 7))) & 1

    for frame_index in range(frame_count):
        canvas = animation.frame()
        for column in range(width):
            for row in range(height):
                offset = (frame_index * width + column) * height + row
                canvas.pixel(
                    column,
                    row,
                    (
                        bit(offset),
                        bit(plane_bits + offset),
                        bit(2 * plane_bits + offset),
                    ),
                )
    return animation


def round_trip_ok(path):
    """Decode a file and re-encode it; True if the bytes come back identical."""
    original = json.loads(Path(path).read_text())
    data = original[0]["data"]
    source = data.get("aniData") or data["graffitiData"]
    return load_jt(path).pack() == list(source)
