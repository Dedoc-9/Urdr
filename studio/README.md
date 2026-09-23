<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `studio/` — the studio arc

A deterministic 1080p game-rendering studio with a measurable low-latency presentation path — that is the
target, stated as what can be measured rather than as a claim. "Competitive latency" is earned through
measurements or not stated; software can time the renderer and the present queue, and input-to-photon needs
the physical boundary (`latchain`: input_transport, present_wait and panel need capture hardware).

This folder is where the arc's own artifacts live: the driver, the records, the charter. The certified game
and its renderer stay where they are — `Urðr` is the immutable source of semantic truth, frozen at a tag, and
the studio consumes it as a sealed oracle. Nothing here mints authority; nothing here changes `mantle`,
`vista`, `voxray` or `raster`. The native placement of the tile path (`tools/terrain/mantle_rs/`) stays with
the gate that re-verifies it live, because that is what makes it a placement rather than a port.

## The shape (ratified)

    Urðr — certified Python reference oracle
      ├── exact frame / pixel witnesses
      ├── CORE authority
      └── VIEW geometry / material semantics
            ↓ frozen tag (urdr-oracle-1)
    Studio — native kernel → window/present shell → 1080p output

The gauntlet every optimisation rung answers, with two instruments that are never fused: the placement rows
(bit-exact against the oracle, in the gate, seconds) and the bench (wall-clock, off-gate, on a named host).
Faster *and* the same witnesses passes; faster with one pixel moved is not an optimisation until the changed
semantics are re-earned.

## Files

| File | What it is |
|---|---|
| `studio0.py` | the STUDIO-0 driver: `--oracle` writes the cross-repo contract; `--bench N --host NAME` compiles the placement in release, checks its witnesses against the Python modules, and records per-phase p50/p95/p99/max on the named host |
| `attest/studio-oracle-1.json` | the frozen contract: the view, `D_0`, the URDRFB1 frame digest, the identity picture's pixel sha256, the oriented picture and tile digest, the identity laws, the camera, the index layout, the corpus goldens, the kernel input format, the Python witnessed |
| `attest/studio0-bench-<host>.json` | one bench record per named host; the verdict against 60 / 144 / 240 Hz is renderer time, never latency |
| `STUDIO-0.md` | the measurement that precedes the repository decision: the fat, the closure classified, the placement, the first number, the decision rule |

## Running

    python studio/studio0.py --oracle                      # rewrite the contract from the live modules
    python studio/studio0.py --bench 200 --warm 20 --host $env:COMPUTERNAME     # PowerShell; needs rustc

## What decides the next step

The owner's bench record. p99 under 16,667 µs unoptimised means 1080p60 is reached before the first gauntlet
rung and the studio kernel's first row already exists (reproduce the oracle's three hashes natively against
the tag); otherwise the first gauntlet rung — the incremental floor cast, since the texel pass is two thirds
of the frame — is measured here, in this repo, under the same rows, before any repository is created.
