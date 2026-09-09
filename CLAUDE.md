# CLAUDE.md

Editor and preview tool for a 16x96 CoolLEDX LED panel. React (CRA) app for
drawing, plus a Python toolkit in `tools/` for generating animations, plus a
route to push files to real hardware over Bluetooth.

## Read on demand

| Doc | When |
| --- | --- |
| [README.md](README.md) | What the app is, sending to the sign, the `.jt` data format |
| [tools/README.md](tools/README.md) | Generating `.jt` files in Python, the bit layout, frame limits |
| [docs/SENDING_TO_THE_SIGN.md](docs/SENDING_TO_THE_SIGN.md) | Driver setup, macOS Bluetooth, error-by-error troubleshooting |
| [docs/VENDOR_DATA.md](docs/VENDOR_DATA.md) | The vendor's CDN endpoints and material catalog |

## The one rule that will bite you

**The three color planes span the whole animation, not each frame.** Every
frame's red bits, then every frame's green, then every frame's blue. Within a
plane the frames sit side by side, and within a frame each column is walked
top to bottom before moving right:

```
bit index in plane = (frame * width + column) * height + row
```

Getting this wrong produces a file that still *displays* — subtly scrambled —
and it looks completely correct for single-frame files, because with one frame
the two layouts coincide. This has already caused one real bug (`fd25d08`),
found only by testing a 3-frame file.

`src/helpers/parse_data.js` reads this layout and `src/helpers/export_data.js`
writes it. They are the authority; follow them rather than inferring from the
format description in README.md, which describes a single frame.

## Verify against artifacts, not intentions

A packing bug hides easily, because the same wrong assumption both writes and
reads the data. So:

- Verify a file **loaded from disk**, not the in-memory structure you built.
  `python3 tools/preview_jt.py FILE --verify` decodes and re-encodes, checking
  the bytes come back identical.
- Render previews **from the written file**. A GIF made from your in-memory
  canvas proves nothing about what you saved.
- Cross-check against an independent decoder where one exists — the driver's
  `create_jt_payload`, or the vendor's own `sendData` payloads.
- None of that proves the *sign* agrees. Only hardware does, and only the user
  can run that. Say plainly which parts are hardware-confirmed and which are
  not.

## Conventions

- **`python3`, never `python`.** macOS ships no bare `python`; `python`
  fails with `command not found`.
- **Prettier: always pass `--single-quote`.** There is no Prettier config, so
  its default is double quotes while the codebase uses single. Running it bare
  reformats every string in the file you touch.
- **Build with `npx react-scripts build`, not `CI=true`.** There are
  pre-existing lint warnings (`FrameControls.js`, `SamplesPage.js`); `CI=true`
  promotes warnings to errors, so the build fails for reasons unrelated to
  your change. Check that you added no *new* warnings.
- No router: routing is a small hash router in `App.js`, so static hosting
  needs no rewrite rules. New views go through the same `route` check.
- Palette is **3 bits per pixel** — 8 colors, no brightness levels.
  `BLUE -> CYAN -> WHITE` is the only available dim-to-bright ramp and is what
  the effects use to fake a glow.

## Repo layout worth knowing

- `src/sample/*.jt` — samples. The Samples page enumerates this directory at
  build time via `require.context`, so **dropping a `.jt` file in is enough**;
  no registration. Files without a `.jt`/`.json` extension are ignored.
- `public/samples/` — the vendor packs and material catalog, fetched at
  runtime rather than bundled. Keeps a few MB out of the JS bundle.
  Regenerate the catalog with `yarn fetch-material`.
- `tools/out/` — generated diagnostics, gitignored. Large and reproducible.
- `tools/jtkit/` — the Python authoring library. Not installed; scripts find
  it by relative path, so any Python 3 interpreter works.

## Frame limits

24 frames is the largest the vendor's own packs use, so it is the most that is
known-good. The protocol's hard ceiling is **113 frames** — the driver writes
the payload length in two bytes, so past 65535 bytes it raises `OverflowError`
before anything reaches the sign. What the *hardware* accepts is still
unmeasured; `tools/animations/frame_ladder.py` exists to measure it.

Large sends also need `--command-timeout 8` or so: the per-chunk
acknowledgement timeout defaults to 1.0s, and a 24-frame animation is 109
chunks. A timeout abandons the transfer part way and looks identical to the
sign truncating.

Frame-based scrolling is impractical: a 20-character message needs ~54 frames
of travel. The sign has native scroll modes for this, via the `mode` field
that `coolledx-driver` currently ignores.

## Working with the user

- **This repo often has uncommitted work in flight.** Stage your own files by
  path; never `git add -A` or `git commit -a`. Deletions and edits you did not
  make show up mid-task — surface them, don't absorb them into your commit.
- Sending to the sign is always the user's action: Bluetooth is blocked for
  agent-run processes here (see the troubleshooting doc). Hand over an exact
  command rather than reporting a send as done.
