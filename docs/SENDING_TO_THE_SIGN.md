# Sending to the sign

How a `.jt` file gets from this repo onto the panel, and what goes wrong.
[README.md](../README.md) has the short version; this is the detail you need
when it fails.

## The pieces

- This editor exports `.jt`.
- [coolledx-driver](https://github.com/UpDryTwist/coolledx-driver), checked out
  at `~/workspace/coolledx-driver`, sends it over Bluetooth LE.
- A Python virtualenv at `~/workspace/coolledx-driver/.venv` with `bleak` and
  `pillow`.

```sh
cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python \
  utils/tweak_sign.py -jt ~/workspace/coolled-editor/src/sample/LFG.jt
```

`PYTHONPATH=src` is required: the package lives in `src/coolledx`, but a stale
empty `coolledx/` directory at the repo root shadows it whenever the working
directory is on `sys.path`.

## There is no pairing mode

The sign is an unbonded BLE peripheral speaking GATT on service `0xFFF0`. It
advertises continuously whenever powered, and there is no bonding step.
Consequences that cost real time if you don't know them:

- **It never appears in macOS Bluetooth settings.** That pane lists classic
  Bluetooth and bonded BLE HID devices. Nothing is wrong if it isn't there;
  `utils/scan.py` is the only place it shows up.
- **Force-quit the phone app first.** The sign accepts one connection at a
  time and stops advertising while the CoolLED1248 app holds it, so it is
  genuinely invisible to your Mac until you quit the app. Backgrounding is not
  enough.
- **Renaming the sign in the app does not change what it advertises.** It
  still broadcasts as `CoolLEDX`, which is the driver's default, so `-d` is
  usually unnecessary. (Our sign is named "ChaosCorner" in the app and still
  advertises as `CoolLEDX`.)

## macOS specifics

**Bluetooth permission belongs to the terminal, not to Python.** Run these
commands from **iTerm2**, which declares `NSBluetoothAlwaysUsageDescription`.
Terminal.app does not. Under a process without that entitlement, Python is
killed outright — `Abort trap: 6`, exit 134 — before it can scan. Every
framework Python re-execs into a `Python.app` bundle that lacks the key, so
switching interpreters does not help; the entitlement has to come from the
launching app.

This is why **an agent cannot send to the sign here**: an agent-run shell is
not attributed to an entitled app, so it always dies with `Abort trap: 6`. The
user has to run the send.

**Use `-d`, not `-a`, for addressing.** CoreBluetooth never exposes hardware
MACs; Bleak returns a per-host UUID instead, so the `XX:XX:XX:XX:XX:XX`
address in the driver's README is Linux/Windows-only. A macOS UUID will not
match what your phone or a Raspberry Pi reports for the same sign. The real
MAC is in the advertisement's manufacturer data, bytes 0–5, if you ever need
it.

## Required local driver fixes

Four bugs in `coolledx-driver` block this path. All four are fixed on the
local `local/all-fixes` branch; **without them nothing works at all.**

| Fix | Symptom without it | Upstream |
| --- | --- | --- |
| `hardware.py` imports `COLOR_TYPE_MONO` from `decoder`, not `commands` | `ImportError`: circular import — the package will not import | [PR #164](https://github.com/UpDryTwist/coolledx-driver/pull/164) |
| `Command` inherits `BasicProtocol` | `AttributeError: no attribute 'create_command'` on every non-raw command | [PR #164](https://github.com/UpDryTwist/coolledx-driver/pull/164) |
| `create_jt_payload` drops its 2-byte length prefix | Sends succeed but the image is scrambled — one column of shift | [PR #164](https://github.com/UpDryTwist/coolledx-driver/pull/164) |
| `write_raw` only requests write-with-response where the characteristic allows it | `BleakGATTProtocolError: (3, 'Write Not Permitted')` on macOS | [PR #165](https://github.com/UpDryTwist/coolledx-driver/pull/165) |

The third is the dangerous one: it corrupts output *silently*. The payload
layout is 24 zero bytes, a 1-byte frame count, a 16-bit delay, then the pixel
planes — no length prefix. The vendor's own payloads confirm it: a
single-frame 16x96 `sendData` entry is exactly 603 bytes.

The fourth is platform-specific rather than a regression. `fff1` grants
write-without-response and notify but not write; BlueZ quietly downgrades the
request, CoreBluetooth rejects it. An ATT write-with-response and the sign
sending a notification are unrelated things, and conflating them was the bug.

## Troubleshooting by error

| What you see | Cause |
| --- | --- |
| `python: command not found` | macOS has no bare `python`; use `python3` |
| `Abort trap: 6` / exit 134, no output | No Bluetooth entitlement — run it from iTerm2 |
| `scan.py` finds nothing | Phone app still connected, or the sign is off/out of range |
| Scan shows other devices but not the sign | Try `-a` to list everything; check it is powered |
| `ImportError: cannot import name 'COLOR_TYPE_MONO'` | Missing the driver fixes above |
| `AttributeError: ... 'create_command'` | Missing the driver fixes above |
| `Write Not Permitted` (error 3) | Missing the macOS write fix |
| Connection timeout | Phone reconnected; BLE allows one connection |
| Image displays but shifted a column | Missing the length-prefix fix |
| Multi-frame file shows colored fringing | Plane layout misread — see [CLAUDE.md](../CLAUDE.md) |
| `did not receive a notification within 1.0 seconds` | Sign slow to ack — raise `--command-timeout`, see below |

## Large files need a longer chunk timeout

A payload is split into chunks, and by default each one waits only **1.0s**
for the sign to acknowledge it. A 24-frame animation is 109 chunks; the
protocol maximum of 113 frames is 509. One slow ack anywhere in that sequence
raises `TimeoutError` and abandons the transfer part way, leaving a partial
animation on the panel.

So raise it for anything past a few frames:

```sh
cd ~/workspace/coolledx-driver && PYTHONPATH=src .venv/bin/python \
  utils/tweak_sign.py --command-timeout 8 -jt ~/workspace/coolled-editor/src/sample/plasma.jt
```

`--command-timeout` is a local addition (`a7ef7a2`); `Client` always accepted
`command_timeout` but nothing on the command line could set it. Not upstream
yet.

**This matters for reading the frame ladder.** A timeout and a genuine size
limit both leave a short animation on the panel, so they look alike. The
difference is that a timeout also prints an error, and the driver's handler
misattributes it as a connection timeout. So: if a ladder file stops early
*and* the command reported an error, retry with a larger
`--command-timeout` before concluding you found the sign's limit.

## Verified on hardware

A CoolLEDX 16x96, over CoreBluetooth on macOS:

- Single-frame `.jt` — `TEA_purpose.jt`, `Believe.jt` (603-byte payloads).
- Column and plane alignment — `column_markers.jt`, which renders red, green,
  blue, white across the first four columns and green, red in columns 95–96.
  Any shift or plane swap is immediately visible.
- Multi-frame animation — `LFG.jt`, 3 frames, 1755-byte payload.

Frame-ladder results, from `tools/animations/frame_ladder.py`:

| Frames | Payload | Chunks | Result |
| --- | --- | --- | --- |
| 24 | 13,851 | 109 | works reliably |
| 40 | 23,067 | 181 | works; failed once, succeeded on retry |
| 52 | 29,979 | 235 | works |
| **53** | **30,555** | **239** | **works — the maximum** |
| 54 | 31,131 | 243 | reports success, sign never applies it |
| 56 | 32,283 | 253 | as 54 |
| 60 | 34,587 | 271 | as 54 |
| 113 | 65,115 | 509 | as 54 |

**53 frames is the limit** on a 96x16 panel — far below the protocol's 113.
Treat 24 as the safe working figure, since 40 proved flaky and needed a
retry.

### It is a size limit, not a frame limit

The cap falls between 30,555 bytes (53 frames, works) and 31,131 (54, fails).
**30KB — 30,720 bytes — is the only round number in that window**, and it
predicts a maximum of exactly 53 frames: `(30720 - 27) // 576 = 53`. A 32KB
buffer would have allowed 56, which failed, so that is ruled out.

Reading it as a byte cap matters for other hardware: a 16x64 panel uses 384
bytes per frame, so the same 30KB would hold about 79 frames.

**But which byte count?** The payload is escaped before transmission, so the
bytes on the wire outnumber the payload. A second cap fits the boundary just
as well:

| | Payload | Wire | Result |
| --- | --- | --- | --- |
| 53 frames | 30,555 | 33,729 | works |
| 54 frames | 31,131 | 34,368 | fails |

30KB (30,720) sits between the payloads; 33KB (33,792) sits between the wire
sizes. Both predict the observed boundary exactly.

`tools/animations/wire_probe.py` writes `sparse_053.jt` to separate them: the
same 30,555-byte payload as the working file, nudged to 33,849 wire bytes,
just past the 33KB line, with no single packet any larger. If it applies, a
33KB total-wire cap is disproven and the 30KB payload cap stands.

## The driver mis-chunks escape-heavy content

A first attempt at that probe, `maxesc_053.jt`, was not a valid test and
revealed a separate bug instead.

`chop_up_data` splits the payload into 128-byte chunks and *then* each chunk
is escaped, so escaping inflates the packets after the split. For ordinary
content that hardly matters, but for a payload full of `0x01` bytes the
packets nearly double:

| | Largest packet | Total wire |
| --- | --- | --- |
| normal content | 148 B | 33,729 |
| escape-heavy (`maxesc_053`) | **269 B** | 61,492 |

A typical CoreBluetooth ATT payload is around 180 bytes, so those 269-byte
packets are too large. The sign stops acknowledging, the transfer aborts
part way on a notify timeout, and — unlike the oversized-animation case —
**the panel displays an error and falls back to a default animation**:

```
asyncio.exceptions.CancelledError
...
TimeoutError
2026-... - __main__ - ERROR - Connection timed out while trying to connect
```

Two things to note about that output. The driver reports it as a *connection*
timeout, which is misleading — the connection was fine and 8 seconds of
chunks had already gone through. And the command hex in the error names
chunk 0, because `truncated_command()` always prints the first chunk, not the
one that failed.

The fix is to split on the escaped length rather than the raw length. Content
that does not escape heavily would chunk identically, so it need not change
existing behaviour.

This is also a third distinct failure mode, alongside the other two:

| Symptom | Cause |
| --- | --- |
| Transfer succeeds, panel unchanged, no percent counter | Payload over ~30KB |
| Transfer aborts on a notify timeout, panel shows an error and falls back | Packets too large — escape-heavy content |
| Transfer succeeds, panel updates | Fine |

### What actually gets escaped

`escape_bytes` doubles only `0x01`, `0x02` and `0x03`. **`0x00` passes through
unescaped**, which is why mostly-black frames inflate far less than you would
expect. The unused `escape_byte` helper beside it documents the opposite rule
("bytes < 4 need to be escaped") and is dead code — nothing calls it. Worth
reporting upstream, since the two would disagree if anyone ever used it.

### Distinguishing an accepted transfer from a rejected one

The sign's own percent counter is the tell. On a file it accepts, the counter
runs after the last chunk as it commits the animation. On an oversized file
**the counter never appears at all** — the sign discards the data without
attempting to apply it. That is the only host-visible difference, since the
BLE traffic reports success either way.

## The transfer and the apply are separate phases

After the last chunk is acked, the sign runs **its own percent counter** to
commit the animation. That happens *after* the transfer, not during it. An
oversized file transfers fine and then fails at that commit step, so the
panel keeps showing whatever it had before.

The driver cannot see this, and will tell you it worked:

```python
# client.py, handle_notify
# TODO:  This isn't entirely accurate.  I just don't know how to
#        properly interpret the errors from the devices yet.
self.current_command.set_command_status(CommandStatus.ACKNOWLEDGED)
self.current_command.error_code = ErrorCode.SUCCESS
```

Every notification is recorded as success and the status byte the sign
returns is discarded, even though `ErrorCode` already enumerates
`TRANSMISSION_FAILED`, `DEVICE_ABNORMALITY`, `DATA_ERROR`,
`DATA_LENGTH_ERROR`, `DATA_ID_ERROR` and `DATA_CHECKSUM_ERROR`.

### The sign does not report the failure at all

It would be reasonable to assume the sign returns an error the driver is
throwing away. It does not. A full `-l DEBUG` capture of a failing 60-frame
send was decoded, and the sign acknowledges everything:

- **271 notifications for 271 chunks**, ids 0 to 270 with no gaps and none
  malformed.
- Every one carries status byte `0x00` in the same position — success.
- The driver logged no error and printed "LED sign update completed
  successfully".

The response format is `04 <status> <chunk_id:16> <trailing>`, where `04` is
the animation command byte. The trailing byte is `0x05` on every chunk except
the first, which is `0x04`; it does not look like a checksum of the preceding
bytes.

So the transfer genuinely succeeds at the protocol level and the animation is
dropped afterwards, during the commit the sign shows its own percent counter
for. Nothing about it reaches the host. Fixing `handle_notify` to parse the
status byte is still worth doing — it currently masks any real error — but it
would **not** catch this failure, because no error is sent.

Detecting it would need a status query after the transfer, if such a command
exists. None is known.
