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
| 56 | 32,283 | 253 | reports success, sign never applies it |
| 60 | 34,587 | 271 | reports success, sign never applies it |
| 113 | 65,115 | 509 | reports success, sign never applies it |

**The hardware limit is between 52 and 56 frames** — roughly 30KB of payload
— far below the protocol's 113. Treat 24 as the safe working figure, since
even 40 proved flaky.

A 32KB buffer would have allowed 56 frames, so that is ruled out. 30KB caps
at 53 frames and 31KB at 55, so the exact boundary distinguishes them.

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
