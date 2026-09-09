#!/usr/bin/env python3
"""
Inspect any .jt file: the editor's exports, these tools' output, or the
vendor sample packs.

    python3 tools/preview_jt.py src/sample/LFG.jt --ascii
    python3 tools/preview_jt.py src/sample/LFG.jt --gif /tmp/lfg.gif
    python3 tools/preview_jt.py src/sample/LFG.jt --frames 0,4,8 --ascii

--gif and --sheet need Pillow; --ascii and --verify need nothing extra.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jtkit import load_jt, preview, round_trip_ok  # noqa: E402


def parse_frames(text, count):
    if not text:
        return None
    if text == "all":
        return range(count)
    return [int(part) for part in text.split(",") if part.strip() != ""]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help=".jt file to inspect")
    parser.add_argument("--ascii", action="store_true", help="print frames as text")
    parser.add_argument("--frames", help="comma-separated indexes, or 'all'")
    parser.add_argument("--columns", help="crop as START:END, e.g. 20:70")
    parser.add_argument("--gif", help="write an animated GIF here")
    parser.add_argument("--sheet", help="write a stacked PNG of all frames here")
    parser.add_argument("--scale", type=int, default=7, help="image scale factor")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="re-encode and confirm the bytes come back identical",
    )
    args = parser.parse_args()

    animation = load_jt(args.file)
    print(f"{args.file}: {animation.describe()}")

    lit = sum(len(frame.lit()) for frame in animation)
    print(f"  {animation.width}x{animation.height}, {lit} lit pixels total")

    if args.verify:
        ok = round_trip_ok(args.file)
        print(f"  round-trip re-encode identical: {ok}")
        if not ok:
            return 1

    columns = None
    if args.columns:
        start, _, end = args.columns.partition(":")
        columns = (int(start) if start else None, int(end) if end else None)

    if args.ascii:
        indexes = parse_frames(args.frames, len(animation))
        preview.print_frames(animation, indexes, columns=columns)

    if args.gif:
        print("  wrote", preview.to_gif(animation, args.gif, scale=args.scale))
    if args.sheet:
        print("  wrote", preview.to_sheet(animation, args.sheet, scale=args.scale))

    return 0


if __name__ == "__main__":
    sys.exit(main())
