#!/usr/bin/env python3
"""
Frame-ladder diagnostic: find out how many frames the sign actually accepts.

Each frame displays its own number as "N/TOTAL" plus a progress bar, so a
truncated transfer is readable directly off the panel. Send a ladder file and
watch the counter:

* It reaches TOTAL and the last frame turns yellow -> the sign took all of it.
* It cycles but stops at some lower number -> that is where it truncated, and
  the highest number you see is the usable frame count.
* Nothing renders, or the send errors -> that size was refused outright.

Work down the ladder until one displays fully, then use --frames to bisect
between that and the next one up.

    python tools/animations/frame_ladder.py                 # the default ladder
    python tools/animations/frame_ladder.py --frames 48     # one specific size
    python tools/animations/frame_ladder.py --frames 30,34,38

Note that frame count and payload size are not the same question, and the
sign more likely cares about the latter. The table printed on each run gives
both.

Hard ceiling: 113 frames. coolledx-driver writes the payload length as two
bytes, so anything over 65535 bytes raises OverflowError before it reaches
the sign -- see chop_up_data in coolledx/commands.py.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, Canvas, colors as C  # noqa: E402

# 27-byte header, and the length field that caps the whole payload.
HEADER_BYTES = 27
MAX_PAYLOAD_BYTES = 0xFFFF
BYTES_PER_FRAME = 576

MAX_FRAMES = (MAX_PAYLOAD_BYTES - HEADER_BYTES) // BYTES_PER_FRAME  # 113

DEFAULT_LADDER = [24, 40, 60, 80, MAX_FRAMES]
DEFAULT_DELAY = 120  # slow enough to read the counter, quick enough to sit through

COUNTER_Y = 0
BAR_Y = 10
BAR_HEIGHT = 3


def build(total, delay=DEFAULT_DELAY):
    """A ladder animation of ``total`` frames, each labelled with its index."""
    if total < 1:
        raise ValueError("Need at least one frame")
    if total > MAX_FRAMES:
        raise ValueError(
            f"{total} frames is {HEADER_BYTES + total * BYTES_PER_FRAME} bytes, "
            f"past the {MAX_PAYLOAD_BYTES}-byte payload field. "
            f"The most the protocol can carry is {MAX_FRAMES} frames."
        )

    anim = Animation(delay=delay)

    for index in range(total):
        number = index + 1
        final = number == total
        frame = anim.frame()

        label = f"{number}/{total}"
        frame.text(
            label,
            x=(anim.width - Canvas.text_width(label)) // 2,
            y=COUNTER_Y,
            color=C.YELLOW if final else C.WHITE,
        )

        # Progress bar: how far through the animation this frame is. If the
        # sign truncates, the bar visibly never fills.
        filled = round(anim.width * number / total)
        frame.rect(0, BAR_Y, anim.width, BAR_HEIGHT, C.BLUE, fill=True)
        frame.rect(
            0,
            BAR_Y,
            filled,
            BAR_HEIGHT,
            C.WHITE if final else C.CYAN,
            fill=True,
        )

        # Quarter marks, to judge the bar without counting pixels.
        for fraction in (0.25, 0.5, 0.75):
            frame.pixel(round(anim.width * fraction), BAR_Y + BAR_HEIGHT + 1, C.MAGENTA)

    return anim


def parse_ladder(text):
    if not text:
        return DEFAULT_LADDER
    return [int(part) for part in text.split(",") if part.strip()]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--frames",
        help=f"comma-separated frame counts (default: {','.join(map(str, DEFAULT_LADDER))})",
    )
    parser.add_argument(
        "--delay", type=int, default=DEFAULT_DELAY, help="ms per frame"
    )
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[1] / "out"),
        help="where to write the files (default: tools/out, gitignored)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    counts = parse_ladder(args.frames)

    # Animation.to_jt() warns above 24 frames, which is exactly what this
    # tool exists to exceed -- the warning would be noise on every run.
    # filterwarnings anchors the pattern at the start of the message.
    warnings.filterwarnings(
        "ignore", message=".*exceeds.*vendor packs.*", category=UserWarning
    )

    print(f"{'frames':>7} {'payload':>9} {'loop':>7}  file")
    written = []
    for total in counts:
        try:
            animation = build(total, delay=args.delay)
        except ValueError as error:
            print(f"{total:>7} {'-':>9} {'-':>7}  skipped: {error}")
            continue

        path = out_dir / f"ladder_{total:03d}.jt"
        animation.save(path)
        payload = HEADER_BYTES + total * BYTES_PER_FRAME
        loop = total * args.delay / 1000
        print(f"{total:>7} {payload:>9} {loop:>6.1f}s  {path}")
        written.append(path)

    if written:
        print()
        print("Send the largest first; if it fails, work down. For each one:")
        print("  cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python \\")
        print(f"    utils/tweak_sign.py -jt {written[-1]}")
        print()
        print("Then read the highest counter value the panel reaches.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
