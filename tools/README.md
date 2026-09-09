# tools

Author and inspect `.jt` files from Python. The editor is for drawing pixels;
this is for anything driven by timing, maths, or a simulation — sweeps, wipes,
fades, generated fields.

## Layout

```
tools/
  jtkit/            the library
    colors.py       the 8-color palette, quantizing, ramps
    font.py         5x7 bitmap font, editable as ASCII art
    canvas.py       one frame: pixels, text, shapes, effect helpers
    animation.py    frames <-> .jt bytes, and loading files back
    preview.py      ASCII, GIF and contact-sheet rendering
  preview_jt.py     CLI to inspect any .jt
  animations/       one script per animation
```

## Writing an animation

```python
from jtkit import Animation, colors as C

anim = Animation(delay=200)              # 96x16 by default
for step in range(12):
    frame = anim.frame()
    frame.text("HELLO", x="center", y=4, color=C.YELLOW)
    frame.pixel(step * 8, 14, C.CYAN)
anim.save("src/sample/hello.jt")
```

Run any of the existing scripts to write its `.jt` into `src/sample/`, where
the editor's Samples page will pick it up:

```sh
python tools/animations/plasma.py
```

### Colors as functions

Every drawing call accepts either a `(r, g, b)` triple or a callable
`f(x, y) -> color`. That is what makes effects short — the color becomes a
function of position, so one `text()` call renders differently each frame:

```python
from jtkit import highlight, wipe

frame.text(word, x, y, highlight(C.YELLOW, C.WHITE, head=cursor))  # travelling shine
frame.text(word, x, y, wipe(C.WHITE, C.BLUE, edge=cursor))         # reveal L->R
```

`canvas.each(f)` fills the whole frame from a function, which is how
`plasma.py` works.

## The format

- Each LED stores **3 bits**, one per channel. Eight colors, no brightness
  levels. `BLUE -> CYAN -> WHITE` is the closest thing to a dim-to-bright ramp
  and is what these effects use to fake a glow.
- A 96x16 frame is **576 bytes**.
- The three color planes span the **whole animation**, not each frame: every
  frame's red bits, then every frame's green, then every blue. Within a plane
  the frames sit side by side, and within a frame each column is walked top to
  bottom before moving right. The bit for `(frame, column, row)` lives at
  `(frame * width + column) * height + row`.

That last point is the one that bites. Getting it wrong yields a file that
still displays but is subtly scrambled, and it looks *correct* for
single-frame files, because with one frame the two layouts coincide.

## Verify what you wrote, not what you meant

A packing bug can hide when the same wrong assumption both writes and reads
the data. So check a file you loaded **from disk**:

```sh
python tools/preview_jt.py src/sample/plasma.jt --verify --ascii --frames 0,12
python tools/preview_jt.py src/sample/plasma.jt --gif /tmp/plasma.gif
```

`--verify` decodes and re-encodes, confirming the bytes come back identical.
`--gif` and `--sheet` need Pillow (the coolledx-driver virtualenv has it);
`--ascii` and `--verify` need nothing beyond Python.

The CLI reads any `.jt` — editor exports and the vendor packs included — so it
doubles as a way to inspect samples you did not make.

Worth doing once against real hardware too, since none of the above proves the
sign agrees with you.

## Limits

- **Keep it to 24 frames.** That is the largest frame count in the vendor
  packs, so it is the most that is known-good; `Animation.to_jt()` warns past
  it. 24 frames is ~13.8KB, and the sign may refuse or truncate more.
- **Frame-based scrolling is impractical.** A 20-character message is ~119px
  wide, so scrolling it across a 96px panel needs ~215px of travel — 54 frames
  at a smooth 4px per frame, well past the ceiling. This is presumably why the
  sign has its own scroll modes, via the `mode` field in a `.jt` that
  `coolledx-driver` currently ignores. For long messages, drive the sign with
  `tweak_sign.py -t "text"` and a `-m` mode instead of building frames.
- The font is uppercase only; lowercase input is folded automatically. Add
  glyphs to `FONT_5X7` as 7 rows of 5 characters.

## How many frames will the sign take?

Unknown, and worth establishing. Three different ceilings are in play:

| Level | Limit | Basis |
| --- | --- | --- |
| Format | 255 frames | the frame count is a single byte |
| Driver / protocol | **113 frames** | measured; see below |
| Known-good | 24 frames | the largest in the vendor packs |
| Sign hardware | unknown | never tested |

113 is a hard ceiling: `coolledx-driver` writes the payload length as two
bytes in `chop_up_data`, so anything over 65535 bytes raises `OverflowError`
before it ever reaches the sign. 113 frames is 65115 bytes across 509 BLE
chunks, each awaiting a notification, so expect a slow transfer even if it
works.

`frame_ladder.py` measures the last row. Each frame displays its own number
as `N/TOTAL` plus a progress bar, so a truncated transfer can be read
straight off the panel:

```sh
python tools/animations/frame_ladder.py            # 24, 40, 60, 80, 113
python tools/animations/frame_ladder.py --frames 48
```

Files land in `tools/out/` (gitignored -- they are large and regenerate on
demand). Send the largest, then read the highest counter the panel reaches:
if it cycles but never passes 61, that is your limit. Bisect with `--frames`
from there.

Note that frame count and payload size are different questions, and the sign
more likely cares about the latter; the table the script prints gives both.

## Sending to the sign

```sh
cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python \
  utils/tweak_sign.py -jt ~/workspace/coolled-editor/src/sample/plasma.jt
```

Force-quit the phone app first, and run it from a terminal that has Bluetooth
permission. See the main README for the full set of traps.
