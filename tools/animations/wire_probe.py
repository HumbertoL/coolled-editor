#!/usr/bin/env python3
"""
Wire-size probe: is the sign's limit on the payload or on the bytes sent?

RESOLVED: the sign's limit is on the decoded payload, ~30KB. maxesc_053
applied on hardware with a 30,555-byte payload and 61,492 wire bytes, so the
transmitted size does not matter. These files are kept as reproducers.

The limit sits between 53 frames (30,555-byte payload) and 54 (31,131). Two
caps initially fit that boundary:

* a **30KB payload** cap -- 30,720, the only round number in the window
  (confirmed)
* a **33KB wire** cap -- 33,792, which also fell between the two files'
  transmitted sizes of 33,729 and 34,368 (disproven)

They differ because the payload is escaped before transmission: the protocol
turns 0x01, 0x02 and 0x03 into two bytes each. Notably **0x00 is not
escaped** (`escape_bytes` in coolledx/commands.py handles only those three,
despite the unused `escape_byte` helper next to it claiming everything below
0x04), so mostly-black frames do not inflate much.

This script writes files that separate the hypotheses by pushing the wire
size around while holding the payload fixed:

``sparse_053`` -- the clean discriminator
    53 frames, payload 30,555: identical to the file known to work. Draws
    only a counter, so slightly more of the payload escapes and the total
    wire size reaches 33,849, just past the 33,792 line. Crucially the
    largest single packet is 146 bytes, no bigger than the working file's
    148, so nothing else changes.

    Applies  -> a 33KB total-wire cap is disproven; the 30KB payload cap
                stands.
    Fails    -> the total transmitted size is what matters.

``maxesc_053`` -- demonstrates a driver bug, NOT a size cap
    Lights only the last row of each 8-row byte group so nearly every plane
    byte is 0x01, doubling the wire size to 61,492. This was written as a
    discriminator and is not one: ``chop_up_data`` splits on the *unescaped*
    length (128 bytes), and escaping then inflates each packet afterwards, so
    the largest packet reaches **269 bytes** against ~148 for normal content.
    The sign stops acknowledging, the transfer times out part way, and the
    panel shows an error and falls back to a default animation.

    It is kept because it reproduces that bug on demand.

``dense_054``
    54 frames, filled so almost nothing escapes. A weak counterpart test: the
    wire size only drops to ~34,200, still above 33,792.

All three draw a frame counter, so the panel shows whether they applied.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, FrameCountWarning, colors as C  # noqa: E402

DELAY = 120


def counter(frame, number, total, color):
    label = f"{number}/{total}"
    frame.text(
        label,
        x=(frame.width - Canvas.text_width(label)) // 2,
        y=0,
        color=color,
    )


def build_sparse(total=53):
    """
    Same payload as a working file, nudged just past the 33KB wire line
    without making any single packet bigger.
    """
    anim = Animation(delay=DELAY)
    for index in range(total):
        number = index + 1
        frame = anim.frame()
        counter(frame, number, total, C.YELLOW if number == total else C.WHITE)
    return anim


def build_max_escape(total=53):
    """Same payload as a working file, roughly double the wire size."""
    anim = Animation(delay=DELAY)
    for index in range(total):
        frame = anim.frame()
        # Bottom row of each 8-row byte group -> plane bytes of 0x01, all escaped.
        for column in range(anim.width):
            frame.pixel(column, 7, C.WHITE)
            frame.pixel(column, 15, C.WHITE)
        counter(frame, index + 1, total, C.YELLOW if index + 1 == total else C.CYAN)
    return anim


def build_dense(total=54):
    """Same payload as a failing file, with as little escaping as possible."""
    anim = Animation(delay=DELAY)
    for index in range(total):
        number = index + 1
        frame = anim.frame()
        frame.fill(C.WHITE)
        counter(frame, number, total, C.BLUE if number < total else C.RED)
        filled = round(anim.width * number / total)
        frame.rect(0, 10, anim.width, 3, C.GREEN, fill=True)
        frame.rect(0, 10, filled, 3, C.MAGENTA, fill=True)
    return anim


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[1] / "out"),
        help="where to write the files (default: tools/out, gitignored)",
    )
    args = parser.parse_args()

    # Exceeding the frame guidance is the point of these probes.
    warnings.filterwarnings("ignore", category=FrameCountWarning)

    out_dir = Path(args.out_dir)
    for name, animation in [
        ("sparse_053", build_sparse()),
        ("maxesc_053", build_max_escape()),
        ("dense_054", build_dense()),
    ]:
        path = animation.save(out_dir / f"{name}.jt")
        print(f"{path}  {len(animation)} frames, payload {animation.payload_bytes():,}")

    print()
    print("Send sparse_053 -- it is the clean discriminator:")
    print("  applies -> a 33KB total-wire cap is disproven; 30KB payload stands")
    print("  fails   -> the total transmitted size is what matters")
    print()
    print("maxesc_053 reproduces the chunking bug: packets reach 269 bytes")
    print("because chop_up_data splits before escaping. Expect a timeout.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
