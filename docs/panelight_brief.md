<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: panelight-equiv -->
# `panelight` — design brief (URDRPNL1, T3.52, V1)

**Read**: 2026-08-04, the centrality-ordered READ pass — P15 of batch 3
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-AB** — three laws, three rows, no single
center. This resolution's second consecutive zero-arrival closed run 4. Reading grade:
**CONFIRMATION**.

## What it is

**The windowed loop — the first rung of the visible world.** Every prior terrain rung was a batch
fold: a whole command log in, a trajectory out. This is the same certified world driven as a live
interactive game — input → a fixed-timestep authority tick → the witness → a declared,
interpolated view → pixels, closed in a loop. The gate certifies everything except the pixels; the
window (`panelight.html`) is the declared depiction. The module mints its motion from `glide`
(compose, don't reimplement): a tick advances the avatar by exactly one command from a resumable
Q32.32 pose — the certified mover, clocked.

## The three laws (what the rows certify)

**INTERACTIVE == BATCH** (`panelight-equiv`): on a pure-move log the tick transcript equals
`glide.glide_cells` bit-for-bit — the interactive world IS the batch authority, the theorem that
lets a live game be trusted: playing it and folding it agree. **THE ACCUMULATOR**
(`panelight-accum`): real engines render at display rate and simulate at a fixed timestep; the
loop advances the authority on an integer-ms accumulator — alpha always in [0, TICK_MS); total
ticks == floor(Σdt / TICK_MS), no time lost or invented; each input consumed **exactly once** (a
schedule short of the input refuses — no silent skip); and the **decoupling law**: two different
dt-logs with the same total ticks land the identical authority witness — render cadence never
moves the authority. **THE INTERPOLATION FIREWALL** (`panelight-firewall`): a frame renders a
DECLARED pose interpolated between bracketing tick poses by alpha — exact integer lerp,
deterministic, outside the authority; the witness is over tick poses only, invariant to the frame
schedule. D15's firewall, now on time instead of space.

## The seam (P15's finding)

Identity, conservation, and police fused across three rows — the C-AB shape at its most explicit
(the freeze priced it 30 and it landed). The V-phase opens exactly the way the arc's discipline
demands: the live loop earns trust by *equalling* the batch authority, not by being tested
separately.

## does_not_show

Wall-clock dt is nondeterministic and lives OFF-GATE (the gate certifies the accumulator over a
pinned dt-log; the window feeds it real `performance.now()` deltas — the input→photon reading is
`bench.py` §3, a named-host claim not made here). The render is presentation behind the firewall.
Multiplayer ghosts are `ghostsnap` (V3). Cross-placement joins the frontier. `integrity ≠ truth`.

## Falsifier

This brief cites `panelight-equiv`: interactive == batch. If the tick transcript ever diverged
from the batch fold on a pure-move log, that row reddens and this brief's central claim dies with
it.
