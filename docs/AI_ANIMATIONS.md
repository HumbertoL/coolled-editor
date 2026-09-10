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

## Claude Opus 5

Created 2026-09-09, all 24 frames. These were the first batch, written before
the 53-frame device maximum had been measured, so they were all built to the
24 frames the vendor's own packs use.

### Free choice

| Animation | Preview | Description |
| --- | --- | --- |
| `plasma` | ![plasma](gifs/plasma.gif) | Three interfering sine fields banded into the 8-colour palette; the quantization is the point, turning a smooth gradient into moving topography. Seamless. |
| `rain` | ![rain](gifs/rain.gif) | Three-pixel streaks for motion blur, splashes on the floor, and one lightning strike where the sky fills blue for a single frame behind a white bolt. |
| `starfield` | ![starfield](gifs/starfield.gif) | Three parallax layers; speed and streak length both carry depth, since the palette has no brightness to spare. Seamless. |
| `fire` | ![fire](gifs/fire.gif) | Heat field rising and cooling through red-yellow-white, with sparse floor hotspots so tongues form instead of a slab. |
| `equalizer` | ![equalizer](gifs/equalizer.gif) | Spectrum bars coloured by height like a real VU meter, peak markers on a slower wave so they lag. Seamless. |
| `sonar` | ![sonar](gifs/sonar.gif) | Rings expanding on a horizontally stretched ellipse, age setting the colour. Seamless. |
| `matrix` | ![matrix](gifs/matrix.gif) | Font glyphs cascading, each column at its own speed, the character changing as it falls. |
| `hazard` | ![hazard](gifs/hazard.gif) | Diagonal warning stripes from `(x + y + offset) mod period`, with cyan pinstripes. Seamless. |
| `helix` | ![helix](gifs/helix.gif) | Two strands a half-period apart; the front one is drawn white and they swap at each crossing, so the ladder reads as twisting. Seamless. |
| `metaballs` | ![metaballs](gifs/metaballs.gif) | Inverse-square fields summed and thresholded into contour bands, so blobs bulge toward each other and fuse. Seamless. |
| `snake` | ![snake](gifs/snake.gif) | A serpentine route whose length divides the frame count, so it closes exactly; body fades back from the head, pellet always just ahead. |
| `wave` | ![wave](gifs/wave.gif) | Two sine components summing into a crest that changes shape rather than sliding, with a reflection above the surface. Seamless. |

### Text-Em-All and personal

| Animation | Preview | Description |
| --- | --- | --- |
| `tea_broadcast` | ![tea_broadcast](gifs/tea_broadcast.gif) | One sender, wavefronts sweeping right, recipients turning green as each is reached, then all pulsing together. |
| `tea_wordmark` | ![tea_wordmark](gifs/tea_wordmark.gif) | TEXT-EM-ALL with a shine passing over it. Deliberately plain — a name is the one thing on a sign that should not be hard to read. |
| `tea_delivered` | ![tea_delivered](gifs/tea_delivered.gif) | A percentage counting up with a filling bar, then SENT and a tick. |
| `chaos_corner` | ![chaos_corner](gifs/chaos_corner.gif) | The sign's own name, steady while the margins misbehave: sparks, glitched letters, the odd bad-connection streak. |
| `konami` | ![konami](gifs/konami.gif) | The code entered one input at a time, then flashing green. Guessed at from the Pac-Man, Animal Well and party parrot files already in the repo. |

### Later reworked by another model

Both were created here and have since been changed; see
[Reworked, not created](#reworked-not-created) for what changed. Note the
previews below show the *current* files, since previews are rendered from
what is committed — not the versions described in the last column.

| Animation | Preview | As created |
| --- | --- | --- |
| `dcc_new_achievement` | ![dcc_new_achievement](gifs/dcc_new_achievement.gif) | "Neeewwww achievement" in the narrator's voice, two beats: a highlight sweeps the top line, then the bottom lights up left to right as the payoff. 24 frames at 230ms, yellow on blue. |
| `life` | ![life](gifs/life.gif) | Conway's Life on a 96x16 torus, four gliders fired into random soup, cells coloured by age so you can see where the computation is still happening. 24 generations, seed 11. |

Not in these tables: `column_markers.jt`, a single-frame diagnostic from the
same session that renders red, green, blue, white across the first four
columns and green, red in columns 95-96. It has no script in
`tools/animations/` because it was generated ad hoc to catch plane and column
misalignment, which is what it was for.

## Claude Opus 4.7

Created 2026-09-09.

### Free choice

| Animation | Preview | Description |
| --- | --- | --- |
| `slot_machine` | ![slot_machine](gifs/slot_machine.gif) | Three reels spin random symbols, lock left-to-right onto 7 7 7, then the cabinet border strobes gold/red for the jackpot. |
| `sunrise` | ![sunrise](gifs/sunrise.gif) | A full day/night cycle: sun arcs across, moon rises on the opposite side, sky flushes red at the horizon at the extremes, water shimmers under whichever body is up. Seamless. 53 frames. |
| `pipes` | ![pipes](gifs/pipes.gif) | The Windows 95 screensaver on a 96x16: four coloured pipes grow one segment per frame with an 18% turn chance, respawning on collision. Wipes on the last frame so the loop is clean. 53 frames. |
| `hyperspace` | ![hyperspace](gifs/hyperspace.gif) | Radial starfield with geometric acceleration; each star draws a streak from its previous position to its new one, colour stepping blue → cyan → white with distance. Ends in a warp flash. |

### Text-Em-All and personal

| Animation | Preview | Description |
| --- | --- | --- |
| `retro_pager` | ![retro_pager](gifs/retro_pager.gif) | The sign as an amber pager LCD: idle "TEXT-EM-ALL" branding, then a buzz (shake + flashing red LEDs), then "HI HUMBERTO" typed one letter at a time with a blinking cursor, ending on a pulsing heart. A nod to Text-Em-All's roots in mass messaging. |
| `campaign_sent` | ![campaign_sent](gifs/campaign_sent.gif) | A broadcast counter easing from 0 to 250,000 with a filling progress bar and a "SENDING..." label that flips to "SENT!" with a check when the count settles. |

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

## Claude Opus 4.6

Created 2026-09-09, all 53 frames.

### Free choice

| Animation | Preview | Description |
| --- | --- | --- |
| `aurora` | ![aurora](gifs/aurora.gif) | Northern lights: overlapping sine waves drive curtain height and sway, GLOW brightness from leading edge up, hue drifting across the width via SPECTRUM. Seamless. 53 frames at 120ms. |
| `maze` | ![maze](gifs/maze.gif) | Recursive backtracker carving a 48×8-cell maze in real time. Blue walls, black passages, white carver head with a cyan trail. 53 frames at 80ms. |
| `ripples` | ![ripples](gifs/ripples.gif) | Seven staggered water drops sending concentric ring ripples that interfere constructively; brightness quantized through the GLOW ramp. Seamless. 53 frames at 80ms. |
| `flock` | ![flock](gifs/flock.gif) | ~30 boids with cohesion, separation, and alignment rules swarming as a murmuration; density-based coloring (white clusters, cyan medium, blue sparse). 53 frames at 90ms. |
| `sand` | ![sand](gifs/sand.gif) | Falling-sand simulation: colored grains drop from random positions and pile up following diagonal-slide physics. 53 frames at 80ms. |
| `fireflies` | ![fireflies](gifs/fireflies.gif) | ~12 fireflies drifting over an irregular green grass silhouette, each pulsing independently through the GLOW ramp. Seamless. 53 frames at 120ms. |
| `waveform` | ![waveform](gifs/waveform.gif) | Oscilloscope: a three-sine composite waveform morphing each frame, blue dot grid, dashed center line, phosphor persistence trail fading green → cyan → blue. Seamless. 53 frames at 60ms. |
| `coral` | ![coral](gifs/coral.gif) | Diffusion-limited aggregation growing branching coral structures from the bottom up; growth front white, recent cyan, established blue. 53 frames at 100ms. |

### Text-Em-All

| Animation | Preview | Description |
| --- | --- | --- |
| `tea_heartbeat` | ![tea_heartbeat](gifs/tea_heartbeat.gif) | Company pulse: a beating heart glyph synced with a messages-per-second counter, "TEA" steady in the center. 53 frames at 100ms. |
| `tea_network` | ![tea_network](gifs/tea_network.gif) | Mass messaging as a network effect: one sender's message cascades exponentially through four columns of recipients, each generation a different color, ending with a synchronized pulse. 53 frames at 90ms. |
| `tea_uptime` | ![tea_uptime](gifs/tea_uptime.gif) | Service uptime monitor: "99.99%" types in, a 30-day status row fills (mostly green, a couple yellow), then "ALL SYSTEMS GO" wipes in. 53 frames at 100ms. |
