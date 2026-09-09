# Samples and the vendor's data

Everything the **Samples** tab (`#/samples`) shows, and where it comes from.
Each card previews on a 96x16 canvas, animations play on hover, and every card
gives you a `.jt` download plus the exact command to push it to the sign.

Three sources, in the order the tabs appear:

| Tab | Items | Origin |
|-----|------:|--------|
| In this repo | 27 | `.jt` / `.json` committed under `src/sample` |
| Vendor static / animations | 209 | the app's bundled `animation_update_data` packs |
| Material catalog | 1526 | the app's runtime material CDN, converted from GIFs |

Everything not already in `src/sample` is vendored into `public/samples/` and
fetched on demand, rather than bundled into the JS.

# The bundled animation packs

62 static images and 147 animations, from:

http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/data1696_static.json

http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/data1696_dynamic.json

Their entries hold a ready-made `sendData` payload rather than a `.jt` body:
24 zero bytes, a frame count, a 16-bit frame delay, then the pixel planes. The
Samples page converts that back into a `.jt` on the fly, which round-trips
exactly -- re-encoding all 209 of them through the driver reproduces the
original payload byte for byte.

Other sizes and the dynamic/static split, from the app's source:

    private static final String UPDATE_JSON_FILE_URL_1248 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1248/";
    private static final String UPDATE_JSON_FILE_URL_1616 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1616/";
    private static final String UPDATE_JSON_FILE_URL_1632 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1632/";
    private static final String UPDATE_JSON_FILE_URL_1664 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1664/";
    private static final String UPDATE_JSON_FILE_URL_1696 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/1696/";
    private static final String UPDATE_JSON_FILE_URL_3232 = "http://coolledx.com/appDownload/CoolLED1248/animation_update_data/3232/";

        private static final String DYNAMIC_ANIMATION_FILE_NAME_1248 = "data1248_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1616 = "data1616_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1632 = "data1632_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1664 = "data1664_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_1696 = "data1696_dynamic.json";
    private static final String DYNAMIC_ANIMATION_FILE_NAME_3232 = "data3232_dynamic.json";

# The material catalog (Driving, Business, Creative, Emoji, Festival, ...)

The `animation_update_data` packs above are the *bundled* library. The
categories the current app shows under "Material" come from a second, separate
CDN tree that is discovered at runtime. Reverse engineered from
`CoolLED1248 v2.7.7` (`com.jtkj.led1248`), in
`com.jtkj.led1248.base.OkHttpUtils`.

## How the app finds it

1. **Device config.** On connect the app fetches
   `http://www.coolledx.com/CoolLEDX/<BLE device name>/config.json` —
   for our sign that's `.../CoolLEDX/CoolLEDX/config.json`. It returns the
   base URLs, all of which are currently the same for every device name:

   ```json
   {
     "material_url": "http://www.coolledx.com/CoolLED1248/material",
     "banner_url":   "http://www.coolledx.com/CoolLED1248/banner",
     "ota_url":      "http://www.coolledx.com/CoolLED1248/ota",
     "guide_url":    "http://www.coolledx.com/CoolLED1248/guide"
   }
   ```

2. **Category list.**
   `{material_url}/{colorDir}/{rows}x{cols}/category.json`

   `colorDir` is derived from the device's color type — byte 20 of the BLE scan
   record (`DeviceManager.getDeviceColorTye`):

   | color type | dir  |
   |-----------|------|
   | 0         | `oc` |
   | 1         | `sc` |
   | 2, 3, 4   | `fc` |

   `rows`/`cols` come from scan-record bytes 17 and 18–19. Our panel is
   `16x96`. So a single-color 16x96 sign asks for
   `http://www.coolledx.com/CoolLED1248/material/sc/16x96/category.json`.

   The response is a list of categories, each with its localized names and its
   own base URL:

   ```json
   {"category": [
     {"name": {"en": "Driving", "zh-CN": "驾驶", "ja": "運転", ...},
      "url": "http://www.coolledx.com/CoolLED1248/material/sc/16x96/driving"},
     ...
   ]}
   ```

3. **Items in a category.** `{category url}/list_{language}.json`, e.g.
   `.../sc/16x96/driving/list_en.json`. Every language tag from the `name` map
   works (`en`, `zh-CN`, `zh-TW`, `ja`, `ko`, `fr`, `de`, `it`, `pt`, `es`,
   `ru`, `vi`, `th`, and on `fc` also `tr`, `ar`, `hi`, `he`, `ro`, `tl`). The
   list itself is identical across languages:

   ```json
   {"baseUrl": "http://www.coolledx.com/CoolLED1248/material/sc/16x96/driving",
    "list": ["sc_16x96_2_51.gif", "sc_16x96_2_50.gif", ...]}
   ```

   Fetch an item at `{baseUrl}/{name}`.

4. **DevilEyes is also served on its own tree**, at
   `{devileyes_url}/{colorDir}/{rows}x{cols}/list.json` (no `category.json`,
   and `list` is a list of *pairs* — left eye, right eye):

   ```
   http://www.coolledx.com/CoolLED1248/devileyes/fc/16x96/list.json
   {"baseUrl": ".../devileyes/fc/16x96",
    "list": [["fc_16x96_200_250.gif", "fc_16x96_200_249.gif"], ...]}
   ```

## The `.gif` files are obfuscated GIFs

Each item is a real GIF (96x16 for our panel) whose **first 32 bytes are XOR'd
with `0xDA`** — see `com.jtkj.led1248.glide.DptModelLoader`, which does exactly
`b[i] ^ 218` for `i < 32` before handing the stream to Glide. `file(1)` reports
"data" until you undo it:

```sh
curl -s -o item.gif http://www.coolledx.com/CoolLED1248/material/fc/16x96/driving/fc_16x96_2_142.gif
python3 -c "
b = bytearray(open('item.gif','rb').read())
for i in range(32): b[i] ^= 0xDA
open('item_decoded.gif','wb').write(b)"
file item_decoded.gif   # GIF image data, version 89a, 96 x 16
```

Note these are GIFs, not `.jt` bodies and not `sendData` payloads — the app
rasterizes/quantizes them on import, so pulling them into this editor means
decoding the GIF frames yourself rather than reusing the vendor's pixel planes.

## What actually exists on the CDN

Probed 2026-09-09. Not every `colorDir`/size combination is published; a
missing one 404s.

| dir  | size    | categories |
|------|---------|------------|
| `oc` | 12x48   | DevilEyes, Creative, Default |
| `sc` | 16x16   | Dynamic, Static |
| `sc` | 16x32   | Business, Creative, Emoji, Festival |
| `sc` | 16x64   | Driving, Business, Creative, Emoji, Festival |
| `sc` | 16x96   | Driving, Business, Creative, Emoji, Festival |
| `sc` | 32x32   | Dynamic, Static |
| `fc` | 16x16   | Dynamic, Static |
| `fc` | 16x32   | Trending, DevilEyes, Driving, Business, Creative, Emoji, Festival, Default, Sport, Flag, Rideshare, Life |
| `fc` | 16x64   | DevilEyes, Driving, Business, Creative, Emoji, Festival, Default, Sport, Flag, Rideshare |
| `fc` | 16x96   | DevilEyes, Driving, Business, Creative, Emoji, Festival, Default, Sport, Flag |
| `fc` | 16x192  | Business, DevilEyes, Festival |
| `fc` | 32x32   | Dynamic, Static |

Item counts for our panel (16x96):

| category  | slug        | `sc` | `fc` |
|-----------|-------------|-----:|-----:|
| Driving   | `driving`   |   41 |   96 |
| Business  | `business`  |   61 |   94 |
| Creative  | `creative`  |  104 |  110 |
| Emoji     | `emoji`     |   66 |   51 |
| Festival  | `festival`  |   68 |  112 |
| DevilEyes | `devileyes` |    — |  522 |
| Default   | `default`   |    — |  100 |
| Sport     | `sport`     |    — |   18 |
| Flag      | `flag`      |    — |   83 |
| **total** |             | **340** | **1186** |

# Getting the catalog into this editor

The CDN serves plain HTTP with no `Access-Control-Allow-Origin`, so the browser
cannot read any of it directly -- not from `localhost` and certainly not from
the https deploy, where it would also be blocked as mixed content. So the
catalog is vendored, the same way the animation packs are:

```bash
node scripts/fetch-material.mjs
```

That walks `config.json` -> `category.json` -> `list_en.json`, downloads every
GIF, un-XORs it, converts it to the panel's packed pixel format, and writes
`public/samples/material/`:

- one `material-<dir>-<slug>.json.gz` per category, holding
  `{ name, file, frameNum, delays, data }` per item, where `data` is base64 of
  the packed colour planes -- exactly the bytes a `.jt` carries in `aniData`
- an `index.json` the Samples page reads to build its tabs

The packs are gzipped on disk because the packed planes are extremely
repetitive: 2.1MB for all 1526 items, against 25MB raw. The page inflates them
with `DecompressionStream`. If `index.json` is missing the catalog tabs just
don't render, so the script is optional for anyone who only wants the editor.

Useful flags:

```bash
node scripts/fetch-material.mjs --dir fc --only emoji,festival
node scripts/fetch-material.mjs --size 16x64        # centred/cropped to 16x96
```

## GIF to panel pixels

`src/helpers/gif_utils.js` does the conversion, and the same code runs when you
drop a `.gif` on the editor. Two things it has to get right:

- **A GIF frame is a patch, not a picture.** It can be smaller than the canvas,
  sit at an offset, and leave pixels transparent so the previous frame shows
  through. About a third of the frames in this catalog are partial, so frames
  have to be composited cumulatively; reading each frame's patch as if it were
  the whole canvas shifts and smears them. Disposal methods 0 and 1 are what
  the vendor uses; 2 and 3 are handled for arbitrary GIFs.
- **The panel is 3 bits per pixel**, one on/off per channel, so every colour
  reduces to one of eight. A channel lights up if it carries at least half of
  the pixel's dominant channel, which keeps hue: `(120, 20, 20)` stays red,
  `(120, 110, 100)` goes white, and anything near-black or mostly transparent
  goes dark.

A GIF the size of the panel lands 1:1; anything else is centred, and anything
larger is cropped rather than scaled. `.jt` carries one delay for the whole
animation while GIF stores one per frame, so the delay most frames use wins.

Round-tripping is verified both ways: all 27 committed samples re-pack to their
original bytes, and material items parse back to the same packed planes they
were written with.

# Other endpoints in the same app

```
http://www.coolledx.com/CoolLEDX/<device name>/config.json    device base URLs
{banner_url}/bannerinfo.json                                  in-app banner carousel
{ota_url}/<firmware>.json                                     firmware OTA manifest
http://coolledx.com/appDownload/CoolLED1248/apk/update.json   app self-update manifest
```

# Redoing the reverse engineering

Everything above came out of `CoolLED1248 v2.7.7` (`com.jtkj.led1248`). An APK
is a zip, and [jadx](https://github.com/skylot/jadx) turns its dex files into
readable Java:

```bash
jadx -d out --no-res --no-debug-info CoolLED1248.apk
grep -rn 'category.json' out/sources        # -> base/OkHttpUtils.java
```

The interesting classes:

| Class | What it holds |
|-------|---------------|
| `com.jtkj.led1248.base.OkHttpUtils` | every URL and how it is assembled |
| `com.jtkj.led1248.light.device.DeviceManager` | scan-record parsing: colour type, rows, columns |
| `com.jtkj.led1248.light.device.DeviceConfigManager` | the JSON models the responses are parsed into |
| `com.jtkj.led1248.glide.DptModelLoader` | the 32-byte XOR on catalog images |

One thing to know reading `OkHttpUtils`: the size in a catalog path is built as
`row + LanguageTag.PRIVATEUSE + column`, and `PRIVATEUSE` is just `"x"`. Also
several fragments call `getMaterialCategoryFromServer` with the row twice
instead of column-and-row, which is why `16x16` paths exist on a CDN tree whose
panels are 16x96.

# What else is in the APK

Things found while pulling the catalog out, kept here because they answer
questions the `.jt` format alone doesn't.

## `mode`, `speed` and `stayTime`

A graffiti `.jt` carries `graffitiType`, `mode`, `speed` and `stayTime`
alongside the pixels. `mode` is the panel's **display effect**, and the values
come straight from the app's `mode_string` array:

| `mode` | Effect |
|-------:|--------|
| 1 | Static |
| 2 | Left |
| 3 | Right |
| 4 | Up |
| 5 | Down |
| 6 | Snowflake |
| 7 | Picture |
| 8 | Laser |

Which is exactly `coolledx.Mode` in the driver, arrived at independently.

The app's own defaults for a new graffiti item are `graffitiType 1, mode 1,
speed 247, stayTime 2`. This editor had `mode` and `speed` transposed --
`mode: 247` is not a valid effect. Fixed; it never mattered for sending,
because `create_jt_payload` in the driver reads only the pixel data and
`delays`, but it does matter if a file is opened in the app.

Brightness and speed are separate BLE commands, not file fields: both are
0-255, with the app defaulting brightness to 255 and speed to 127.

## BLE command bytes

`Light1696Utils` builds every command as
`01 <length> <payload...> 03`, where the payload's first byte selects the
command and any byte in `01..03` inside it is escaped as `02` followed by
`byte ^ 0x04`:

| Byte | Command |
|-----:|---------|
| `01` | music / rhythm data |
| `02` | text |
| `03` | draw (graffiti and animation pixels) |
| `05` | icon |
| `06` | mode (the table above) |
| `07` | speed |
| `08` | brightness |
| `09` | power on/off |
| `0a` | begin transfer |
| `0d` | check password |

The driver already implements this framing; it is recorded here because the
escaping is easy to miss when reading a capture.

## Bundled bitmap fonts

The app does not download fonts -- `font_url` exists in the config model but
the live `config.json` omits it. Instead the fonts ship in the APK's `assets/`,
as flat arrays indexed directly by Unicode code point, with no header and no
index:

| Asset | Glyph | Bytes/glyph | Offset |
|-------|-------|------------:|--------|
| `8_small`, `8_large` | 8x8 | 8 | `cp * 8` |
| `UNICODE12`, `UNICODE12_BOLD` | 12x16 | 24 | `cp * 24` |
| `UNICODE16`, `UNICODE16_bold` | 16x16 | 32 | `cp * 32` |
| `32_16_small`/`_large`, `32_24_*`, `32_32_*` | 32 rows | 32-128 | `cp * n` |

Each covers the whole Basic Multilingual Plane -- `UNICODE16` is exactly
65536 x 32 bytes -- so CJK, Cyrillic and Greek are all present.

The layout is **the same column-major, MSB-at-top packing the panel uses**:
for a 16x16 glyph, 16 columns of 2 bytes, first byte rows 0-7, bit 7 topmost.
Verified by decoding `U+0041` and `U+4E2D`. So glyph bytes drop into a `.jt`
plane with no transformation, and a 16-row font matches this panel's height
exactly.

Glyphs are stored full-width; the app trims blank leading and trailing columns
per glyph to space text proportionally.

Nothing in this repo uses them yet. A text tool is mostly a matter of reading
the right 32 bytes per character -- worth knowing before writing a rasteriser
against a TTF instead. The fonts appear to be rasterised from the Noto faces
that ship alongside them in `assets/`.

## Emoji and icon sets

`assets/emoji_<size>.json` holds small inline icons, in the same `sendData`
shape as the animation packs (24 zero bytes, frame count, 16-bit delay, then
planes). `emoji_1696.json` -- the one for this panel -- has 151 single-frame
entries, but each is **16x16**, not 16x96: 96 bytes of pixel data, three
planes of 16 columns. They are stamps meant to be placed inline in text, so
they need positioning on the 96-wide canvas rather than loading as samples.

Each entry also carries a `showData` field: 32 bytes, the same 16x16 glyph
packing, used for the picker thumbnail.

## Other assets worth knowing about

- `data<size>_static.json` / `data<size>_dynamic.json` for 1248, 1616, 1632,
  1664, 1696, 3232 and `CooledA` -- the same packs the `animation_update_data`
  URLs serve, bundled as a fallback. `data1696_*` are byte-identical to what
  this repo vendors.
- `coolledu.bin`, and `apphtml/` for the in-app help pages.
