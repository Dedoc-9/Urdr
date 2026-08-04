<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: drive-properties -->
# `drive` — design brief (URDRDRIVE1, T3.11, Slice 3a)

**Read**: 2026-08-04, the centrality-ordered READ pass — P9 of the first batch freeze
(`../exe_epistemics/PREDICTIONS.md`), the interface instrument's first high-Γ cell. Outcome:
**P9-C-REP** — transcript identity central, B-A′'s prediction confirmed. This resolution's second
consecutive zero-arrival closed run 3. Reading grade: **CONFIRMATION**.

## What it is

**The certified movement transcript**: the authoritative trajectory as a pure, exact-integer
function of (initial pose, input log) over the certified terrain. `stance` walks a *declared* path;
`drive` drives the actor from an *input log* — the netcode lockstep spine specialized to terrain.
Each input is a direction with a **gait**: lowercase = walk (1 cell), UPPERCASE = sprint (2 cells);
the actor turns to face the command (free), then advances gait cells, each cell gated by `stance`'s
step law (climb ≤ MAX_STEP); a cell off-grid or too high stops the actor at the last good cell. No
float, no `/` `//` `%`.

## The core law (what `drive-properties` certifies)

Drive is **the pure fold of step**: replaying the same (start, input log) reproduces the trajectory
bit-for-bit — state is a pure fold over the input, the lockstep witness on terrain. Sprint covers
2× walk; a cell is entered iff its rise ≤ MAX_STEP — stance's law, inherited per cell (composition,
not new mechanism). And **tamper-evidence** (`drive-selftest`): the transcript digest binds
(start, input log, trajectory), so a forged, replayed, or reordered *command* moves the digest —
input integrity is a digest equality, not a promise. Sprint is gated by the terrain (a stride whose
second cell is a wall moves one cell and stops). `drive:scenes` pins the walks to URDRDRIVE1
digests; `drive-refusal` is the typed domain battery (unknown command, empty log, off-grid start,
negative step, non-int).

## The seam (P9's finding)

**Representation — transcript identity — confirmed.** The module's two *novel* facts are both
identity facts (determinism; digest-bound input integrity); the measurement content is inherited
from stance, and gait is derived *in the input* (not a pose axis, not a velocity). Where `warden`
polices claimed *trajectories*, `drive` makes the *input log itself* tamper-evident — anti-cheat
moved one layer down, to the command stream. Each trajectory pose is `[x, y, ground, facing]` —
exactly what `gaze` observes: `drive` certifies WHEN (the tick's correct derivation), `gaze`
certifies WHERE (a view reconstructs to it).

## does_not_show

Continuous position and fixed-point rotation (mouse-look is the Q32.32 regime — `fpquat`/`fppose`,
not this exact-integer grid); diagonal moves; the kernel lockstep cross-check; velocity as a pose
axis (the declared next regime). The movement MODEL (turn-then-advance, rise > MAX_STEP walls) is
DECLARED, like buoyancy/crossing/stance. `integrity ≠ truth`.

## Falsifier

This brief cites `drive-properties`: the pure-fold, determinism, gait, and step-law row. If replay
stopped reproducing the trajectory bit-for-bit, sprint stopped covering 2× walk, or a cell entered
against the step law, that row reddens and this brief's central claim dies with it.
