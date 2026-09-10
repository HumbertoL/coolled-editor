#!/usr/bin/env python3
"""
Natural 1 -- the same roll as d20_nat20, landing badly.

Identical tumble, identical stop; the face fills red instead of gold and the
banner reads CRIT FAIL. Kept as its own file so the Samples page lists both.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jtkit import colors as C  # noqa: E402
from d20_nat20 import build  # noqa: E402

if __name__ == "__main__":
    animation = build(result="1", banner="CRIT FAIL", accent=C.RED, flash=C.WHITE,
                      number_x=30, banner_x=46)
    out = Path(__file__).resolve().parents[2] / "src/sample/d20_nat1.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
