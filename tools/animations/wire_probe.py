#!/usr/bin/env python3
"""
Wire-size probe: is the sign's limit on the payload or on the bytes sent?

Measurement put the limit between 53 frames (30,555-byte payload) and 54
(31,131). Two caps fit that boundary exactly:

* a **30KB payload** cap -- 30,720, the only round number in the window
* a **33KB wire** cap -- 33,792, which also falls between the two files'
  transmitted sizes of 33,729 and 34,368

They differ because the payload is escaped before transmission: the protocol
turns 0x01, 0x02 and 0x03 into two bytes each. Notably **0x00 is not
escaped** (`escape_bytes` in coolledx/commands.py handles only those three,
despite the unused `escape_byte` helper next to it claiming everything below
0x04), so mostly-black frames do not inflate much.

This script writes files that separate the hypotheses by pushing the wire
size around while holding the payload fixed:

``maxesc_053``
    53 frames, so the payload matches the file already known to work. Lights
    only the last row of each 8-row byte group, making nearly every plane
    byte 0x01 -- which doubles on the wire. Payload 30,555, wire ~61,500.

    Applies  -> the cap is on the decoded payload; wire size is irrelevant.
    Fails    -> the cap involves the transmitted size.

``dense_054``
    54 frames, filled so almost nothing escapes. The counterpart test, though
    a weak one: the wire size only drops to ~34,200, still above 33,792.

Both draw a frame counter, so the panel shows whether they applied.
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
        ("maxesc_053", build_max_escape()),
        ("dense_054", build_dense()),
    ]:
        path = animation.save(out_dir / f"{name}.jt")
        print(f"{path}  {len(animation)} frames, payload {animation.payload_bytes():,}")

    print()
    print("Send maxesc_053 first -- it is the decisive one:")
    print("  applies -> the cap is the decoded payload (~30KB)")
    print("  fails   -> the cap involves the transmitted size")

    return 0


if __name__ == "__main__":
    sys.exit(main())
