# AI-created animations

Which of the animations in `src/sample/` were made by an AI model, by which
model, and when. Each has a matching script in `tools/animations/` that
regenerates it. Dates are the date of the commit that added the file.

Frame counts: 24 unless noted; **53** is the measured device maximum.

The previews in `docs/gifs/` are rendered from the committed `.jt` files at
3x, with the real frame delays. Regenerate one after changing its script:

```sh
python3 tools/preview_jt.py src/sample/NAME.jt --gif docs/gifs/NAME.gif --scale 3
```

## Claude Fable 5.1

Created 2026-09-09.

### Free choice

| Animation | Preview | Description |
| --- | --- | --- |
| `lorenz` | ![lorenz](gifs/lorenz.gif) | The Lorenz attractor tracing itself, oldest path blue, head white; the tail expires so it never fills to a slab. 53 frames. |
| `julia` | ![julia](gifs/julia.gif) | Julia set morphing as c circles the origin; seamless. 53 frames. |
| `tunnel` | ![tunnel](gifs/tunnel.gif) | Demoscene checkered-pipe flythrough; parity kept even so it loops. |
| `lissajous` | ![lissajous](gifs/lissajous.gif) | 3:2 Lissajous figure turning in phase, sparse blue ghost, comet running two laps. |
| `cubes` | ![cubes](gifs/cubes.gif) | Three wireframe cubes tumbling with perspective, blue back-edges. |
| `rule30` | ![rule30](gifs/rule30.gif) | Wolfram's rule 30 from a single seed, two generations a frame, scrolling up. |
| `orbit` | ![orbit](gifs/orbit.gif) | Five planets with integer periods passing behind and in front of the sun. |
| `heartbeat` | ![heartbeat](gifs/heartbeat.gif) | ECG monitor sweep with a blank gap ahead of the cursor; the heart beats on each spike. |
| `fireworks` | ![fireworks](gifs/fireworks.gif) | Eight shells, particles cooling through three colours, two-shell finale. 53 frames. |
| `lightning` | ![lightning](gifs/lightning.gif) | Random-walk bolts with afterglow; one flickers. |
| `bounce` | ![bounce](gifs/bounce.gif) | Balls with periods 12/8/6 that realign once per loop, squash frame, shadows. |
| `pong` | ![pong](gifs/pong.gif) | Four crossings, then the left player misses and the score ticks over. 53 frames. |
| `tetris` | ![tetris](gifs/tetris.gif) | Sideways, gravity left, on a board built from real tetrominoes; six pieces drop in, two rotate in flight and one is steered, five columns clear. Sequence found by search. 53 frames. |
| `invaders` | ![invaders](gifs/invaders.gif) | The 1978 crab marching, legs alternating; the cannon shoots one. |
| `rocket` | ![rocket](gifs/rocket.gif) | T-3 countdown, flame, smoke, LIFTOFF. |
| `eyes` | ![eyes](gifs/eyes.gif) | A pair of eyes: glances, blinks, a thinking look, a sideways squint. 53 frames. |
| `flag` | ![flag](gifs/flag.gif) | Rainbow flag rippling on a pole, amplitude growing from the hoist. |
| `hourglass` | ![hourglass](gifs/hourglass.gif) | Three hourglasses out of phase; sand drains, then a card-flip turns each over. |
| `aquarium` | ![aquarium](gifs/aquarium.gif) | Fish both ways with tail flicks, bubbles, swaying weed; seamless. 53 frames. |
| `pendulum_wave` | ![pendulum_wave](gifs/pendulum_wave.gif) | Ten bobs end-on at consecutive whole cycles per loop: line, wave, chaos, line. 53 frames. |
| `night_drive` | ![night_drive](gifs/night_drive.gif) | Skyline with flickering windows, stars, cars passing both lanes; seamless. 53 frames. |
| `dominoes` | ![dominoes](gifs/dominoes.gif) | Sixteen tiles tipping in turn, each reaching the next as it starts to go. 53 frames. |
| `newtons_cradle` | ![newtons_cradle](gifs/newtons_cradle.gif) | One sine drives both end balls; the middle three hold and flash on the click. 53 frames. |
| `sorting` | ![sorting](gifs/sorting.gif) | Bubble sort on 24 bars, swaps sampled to fit, then the green done-sweep. 53 frames. |
| `donut_dvd` | ![donut_dvd](gifs/donut_dvd.gif) | The bouncing DVD logo as a donut; triangle-wave path so it loops seamlessly despite 53 being prime, grazing a corner by one pixel. 53 frames. |
| `clawd` | ![clawd](gifs/clawd.gif) | The Claude Code mascot trots in, blinks at a prompt with a blinking cursor, trots off. 53 frames. |

### Text-Em-All and desk statuses

| Animation | Preview | Description |
| --- | --- | --- |
| `rebrand` | ![rebrand](gifs/rebrand.gif) | CALL-EM-ALL flips letter by letter into TEXT-EM-ALL, then a shine. |
| `sms_bubbles` | ![sms_bubbles](gifs/sms_bubbles.gif) | A texting thread: outgoing green, incoming blue, typing dots, scroll. |
| `tests_passing` | ![tests_passing](gifs/tests_passing.gif) | Sixteen specs run; one fails red, retries, passes; ALL 16 PASS. |
| `pairing` | ![pairing](gifs/pairing.gif) | Bluetooth SEARCHING... then CONNECTED with a tick. |
| `status_on_a_call` | ![status_on_a_call](gifs/status_on_a_call.gif) | Rattling handset, ON A CALL in red, blinking dot. |
| `status_focus` | ![status_focus](gifs/status_focus.gif) | Headphones with a small equaliser, FOCUS MODE with a shine. |
| `status_brb` | ![status_brb](gifs/status_brb.gif) | BE RIGHT BACK while a stick figure walks off the right edge. |
| `humberto` | ![humberto](gifs/humberto.gif) | The name at 2x font, letters dropping in, then a rainbow ripple. |
| `sgla_welcome` | ![sgla_welcome](gifs/sgla_welcome.gif) | For the Small Giants Leadership Academy graduation visit: WELCOME / SGLA, CONGRATS, / Y'ALL! with a tossed mortarboard, CLASS OF 2026, under confetti. 53 frames. |

### Dungeon Crawler Carl

All 53 frames, red and yellow after the book covers.

| Animation | Preview | Description |
| --- | --- | --- |
| `dcc_loot_box` | ![dcc_loot_box](gifs/dcc_loot_box.gif) | A chest rattles, the lid lifts, light fans out, GOLD BOX! |
| `dcc_boss_battle` | ![dcc_boss_battle](gifs/dcc_boss_battle.gif) | WARNING, then BOSS BATTLE with a red-eyed skull and a strobing border. |
| `dcc_collapse` | ![dcc_collapse](gifs/dcc_collapse.gif) | COLLAPSE IN over a real-time ten-second countdown, red bars closing in. |
| `dcc_level_up` | ![dcc_level_up](gifs/dcc_level_up.gif) | XP bar fills, 27 rolls up and 28 slides in, LEVEL UP! |
| `dcc_goddammit_donut` | ![dcc_goddammit_donut](gifs/dcc_goddammit_donut.gif) | Typed out with a cursor while Donut blinks, flicks an ear and swishes her tail. |
| `dcc_followers` | ![dcc_followers](gifs/dcc_followers.gif) | A live follower count with a heart that beats on each batch. |

### Dungeons & Dragons

All 53 frames.

| Animation | Preview | Description |
| --- | --- | --- |
| `d20_nat20` | ![d20_nat20](gifs/d20_nat20.gif) | A wireframe icosahedron tumbles in and stops; the near face fills gold, NAT 20! |
| `d20_nat1` | ![d20_nat1](gifs/d20_nat1.gif) | The same roll from the same code, landing on 1: red face, CRIT FAIL. |
| `dnd_fireball` | ![dnd_fireball](gifs/dnd_fireball.gif) | Eight 5x5 d6 tumble and settle under FIREBALL!, total counts to 34. |
| `dnd_dragon` | ![dnd_dragon](gifs/dnd_dragon.gif) | A dragon beats its wings, breathes a cone of fire, then ROLL INITIATIVE! |
| `dnd_hp` | ![dnd_hp](gifs/dnd_hp.gif) | A hit-point bar taking damage in chunks, one heal, ending at 3/58. |

### Reworked, not created

These existed before; Fable 5.1 changed them on 2026-09-09. The original
author should list them under their own model.

| Animation | Preview | Change |
| --- | --- | --- |
| `dcc_new_achievement` | ![dcc_new_achievement](gifs/dcc_new_achievement.gif) | 24 frames at 230ms to 53 at 100ms; yellow-on-blue to red and yellow. |
| `life` | ![life](gifs/life.gif) | 24 generations to 53; seed 11 to 16, chosen as the one still busiest at the end. |
