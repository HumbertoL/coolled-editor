# About

This app was created to preview and edit data on a 16x96 LED panel

# Sending to the sign from your machine

You don't need the phone or the CoolLED1248 app. Click **Send to sign** in the
toolbar for the copy-paste commands, with the filename of your last export
filled in automatically. The pieces:

- This editor exports a `.jt` file (the format documented below).
- [coolledx-driver](https://github.com/UpDryTwist/coolledx-driver) sends it to
  the panel over Bluetooth LE, via `utils/tweak_sign.py -jt <file>`. Pass
  `--command-timeout 8` for anything past a few frames — the default 1s
  per-chunk wait can abandon a large transfer part way.

Assuming the driver is checked out at `~/workspace/coolledx-driver` with a venv
holding `bleak` and `pillow`:

```sh
# Confirm the sign is visible (expect: CoolLEDX, Height: 16, Width: 96)
cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python utils/scan.py -t 15

# Send an exported .jt
cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python utils/tweak_sign.py --command-timeout 8 -jt ~/Downloads/your-export.jt
```

Things that will otherwise cost you an afternoon:

- **There is no pairing mode, and the sign never shows up in macOS Bluetooth
  settings.** It's an unbonded BLE peripheral speaking GATT on service `0xFFF0`,
  so `scan.py` is the only place it appears. Nothing is wrong if Bluetooth
  settings doesn't list it.
- **Force-quit the phone app first.** The sign takes one connection at a time
  and stops advertising while the app holds it, so it's invisible to your Mac
  until you actually quit CoolLED1248.
- **macOS Bluetooth permission belongs to the terminal**, not to Python. iTerm2
  declares the entitlement; Terminal.app does not. Run the commands from a
  terminal directly — under anything lacking it, Python is killed outright with
  `Abort trap: 6` before it can scan.
- **`PYTHONPATH=src` is required.** The driver package lives in `src/coolledx`,
  but a stale empty `coolledx/` directory at the repo root shadows it whenever
  the working directory is on `sys.path`.
- **Renaming the sign in the app doesn't change what it advertises.** It still
  broadcasts as `CoolLEDX`, which is the driver's default, so `-d` isn't needed.
- On macOS, `-a` takes a CoreBluetooth UUID, not the MAC address the driver's
  README shows. That identifier is per-host, so it won't match what your phone
  or a Raspberry Pi reports. Prefer `-d`.

Sending to the panel needs [three fixes to coolledx-driver](https://github.com/UpDryTwist/coolledx-driver)
that aren't upstream yet — without them the driver can't import, can't encode a
command, and can't write to the characteristic on macOS.
# Setting text

**Add text** in the toolbar sets a string in the CoolLED1248 app's own 16px
bitmap font, extracted from its APK -- so accented Latin, Greek, Cyrillic,
Kana and CJK all work, not just ASCII. Alignment, tracking and a
monospace/proportional toggle are there, with a live preview and a column
count so you can see what fits in 96.

The result is stamped into the current frame as ordinary pixels, editable
afterwards like anything you drew.

The glyph pages live in `public/fonts/` and are regenerated with
`node scripts/extract-font.mjs`. See
[docs/VENDOR_DATA.md](docs/VENDOR_DATA.md) for the font's layout and where it
came from.

# Samples and the vendor's data

The editor ships with the `.jt` files under `src/sample`, and the **Samples**
tab (`#/samples`) also serves two vendor animation packs and the CoolLED1248
app's whole material catalog -- 1526 items across Driving, Business, Creative,
Emoji, Festival and more.

Where all of that comes from, how the vendor's CDN is laid out, and how to
refresh it: [docs/VENDOR_DATA.md](docs/VENDOR_DATA.md).

# Data Format

This repo is using a reverse engineered data format that is used by the vendor.

Data is saved in .jt files. There's two types of files:

- Graffiti (static images)
- Animations

Both use essentially the same format.

Data is stored in a large array, split into individual bytes. For example:

```
[192, 15, 64, ...]
```

A static image with dimensions of 16x96 will have an array of 576 bytes. Note that this means each pixel is represented by 3 bits.

To interpret the data, first we convert each number in the array to an 8 bit binary number and build up a string.

```
110000001100000000001111000011110100000001000000...
```

Then we split the binary string into pieces that represent each column of pixels. Each column is 16 pixels tall and represented in 6 bytes.

```
11000000 11000000 00001111 00001111 01000000 01000000
```

We split the bytes representing the column into three evenly sized sections.

```
[1100000011000000, 0000111100001111, 0100000001000000]
```

For static image with dimensions of 16x96, there will be 96 columns, each 6 bytes. Each group represents one column.

These three parts of the group represent the red bits, the green bits and the blue bits.

So in this example, we take the first bit of each section:

| 1   | 0   | 0   |
| --- | --- | --- |
| R   | G   | B   |
| FF  | 00  | 00  |

This gives us the first pixel, which is the color #FF0000 aka red.

The second pixel is made up of the second bit in each array and so forth.

Each of those pixels is converted into a color in the same way:

| Binary | Hex    | Name    |
| ------ | ------ | ------- |
| 000    | 000000 | Black   |
| 001    | 0000FF | Blue    |
| 010    | 00FF00 | Green   |
| 011    | 00FFFF | Cyan    |
| 100    | FF0000 | Red     |
| 101    | FF00FF | Magenta |
| 110    | FFFF00 | Yellow  |
| 111    | FFFFFF | White   |

To convert the pixels to an image, we render starting at the top left, then moving down the column. Once the bottom of a column is reached, it starts at the top of the next column, like so:

| 1   | 4   | 7   |
| --- | --- | --- |
| 2   | 5   | 8   |
| 3   | 6   | 9   |

That'll look like:

| 100 | 000 | 010 |
| --- | --- | --- |
| 101 | 010 | 010 |
| 000 | 010 |     |

This process is continued using a height of 16 pixels and width of 96 pixels.

To represent multiple frames in an animation, each entire frame is stored in the binary data, one at a time:

[ `[576 bytes of frame 1 data]`, `[576 bytes of frame 2 data]`, `[576 bytes of frame 3 data]` ]

Note that the data is one continuous blob. Each frame is not an element in the array. We have to know to divide it up first, then process each subset of data with the process described above.
