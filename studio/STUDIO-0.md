<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# STUDIO-0 — measurement before a repository

Patch 0155 on 9ec9229 (the studio arc's own folder, `studio/`). Two full gates, byte-identical.
Nothing in `mantle`, `vista`, `voxray` or `raster` changed. The question, as ratified: *can the intended native
kernel actually hit the target on your hardware?* — asked with an instrument, not a plan.

## 1. The oracle is frozen — `studio/attest/studio-oracle-1.json`

Computed live from the modules a studio would consume, at the view (0xABCDE, depth 1, (34, 28), facing W):

| Witness | Value |
|---|---|
| `D_0` (statecanon, the player at pos) | `7d8d02e119b230a91f67c649cb0ded73e6a406b2bb69639bf267b47318888c58` |
| URDRFB1 frame digest | `9bb45bf393a6340af432c080b87e9a85e57810a7b46deb792247e11b633e18cf` |
| identity picture pixel sha256 | `0bef7c1ee0a299bed50df62c0d81f5daf39e34cb981a4e9dc87fa94b1ee72d35` |
| oriented picture pixel sha256 + tile digest | in the record |
| frame law | `URDRFB1 \| w \| h \| channels \| indices` → sha256; picture identity = sha256 of RGB bytes, never a PNG |
| camera, index layout, sign table, corpus goldens, kernel input format, Python witnessed | in the record |

The tag `urdr-oracle-1` goes on the commit that carries this file (your box does it). Python witnessed: CPython
3.11.15 on Linux here; your Windows CPython joins by its `--snapshot` line, which already printed the same three
hashes.

## 2. The closure, classified

| Class | Modules (lines) |
|---|---|
| CORE (12) | enact 542, rerun 539, gamegen 525, savegame 488, rngstream 457, loot 448, actionlog 388, move 377, descent 371, statecanon 354, descend 344, entity 288 |
| VIEW (3) | mantle 692, vista 594, cue 456 |
| certified substrate, untagged | voxray 725, voxref 563, raster 213, intla ×6 (573) |
| OBSERVER / off-gate | play 388 (driver), pngio 141 (codec) |

26 modules, 9,466 lines — one fortieth of the 382k-line tree. The **minimum native rendering closure** is
smaller than the kernel: voxray's traversal (~60 lines of the 725), vista's strip and floor, mantle's
coordinates and emission, raster's digest. The level, eye, facing, colour table, per-band maps and tiles are
*inputs* from the modules that own them, so the port is exactly the per-frame work and nothing about the world.

## 3. The placement — `tools/terrain/mantle_rs/mantle.rs`

Std-only Rust, its own SHA-256, one binary: read a scene, print `frame` and `pixels`. Exactness without big
integers: voxray carries t unreduced (denominators reach 1920¹⁵ on the corpus, Python big ints); the port carries
the same rational reduced — on axis i the crossing parameter is (k·Q − eye_i)/|d_i| with a fixed denominator
≤ 1920 — and every quantity vista and mantle derive from t is a floor of a rational, invariant under the
representation; every product stays under 2³⁶, i64 throughout.

Result: **all twenty witnesses reproduced on the first compile** — four corpus scenes × two tile sets + the
witness view, frame digest and pixel sha both, twice. Gate rows `mantle-placement` (live recompile, live
comparison) and `mantle-placement-selftest` (a mirrored sign table moves every oriented picture and no frame
digest and no identity picture — the two witnesses are distinct quantities). Both rows SKIP without rustc.

## 4. The number — `studio/attest/studio0-bench-linux-xeon-2p1ghz-cloud.json`

Off-gate, `-C opt-level=3`, 200 samples after 20 warm-ups, no window, no present, no disk; witnesses checked
before any number is printed. Host: Linux x86_64, Intel Xeon @ 2.10 GHz (a shared cloud core — a weak host).

| Phase (identity tiles) | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| traversal + strip + floor fill (the frame) | 5,871 µs | 7,988 | 9,221 | 14,139 |
| texel pass (the picture) | 10,789 µs | 14,488 | 17,023 | 17,664 |
| **total per frame** | **16,675 µs** | 23,357 | **25,263** | 27,218 |

Oriented tiles: total p50 17,286, p99 26,101. Budgets: 60 Hz 16,667 µs · 144 Hz 6,944 · 240 Hz 4,167.
**Verdict on this host: p99 OVER all three; p50 sits on the 60 Hz line** — single-threaded, unoptimised,
seventy-five times the 1.26-second Python frame.

What it does and does not say. It says the naive port is within one 60 Hz budget of the target on a slow core
before any optimisation, and that the texel pass (two integer divisions per floor pixel, one per wall pixel)
is two thirds of the cost. It does not say anything about your host — that is the record your box writes —
and it is renderer time, never input-to-photon: `latchain`'s boundary stands (input_transport, present_wait
and panel need capture hardware). No number here is a latency claim.

## 5. The gauntlet, as it now exists

Two disjoint instruments, never fused: the placement rows (bit-exact, in the gate, seconds) and the bench
(wall-clock, off-gate, on a named host). An optimisation rung passes both or neither: faster *and* the same
twenty witnesses. The first rungs are visible in the profile — the incremental floor cast (the floor point is
linear in the column at fixed row, so two divisions per pixel become one addition, exact by Bresenham-style
carry), row-parallel emission, then layout — each measured against the same oracle.

## 6. What decides the repository

Your host's `studio/studio0.py --bench` record. If the p99 is under 16,667 µs unoptimised, 1080p60 is reached before
the first gauntlet rung and the studio kernel's first row already exists (the cross-repo witness: reproduce
the oracle's three hashes natively against the tag). If it is not, the first gauntlet rung is measured here,
in this repo, under these rows, before any repository is created — and that is still a number, not a plan.
