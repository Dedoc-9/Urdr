<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: fpcap-collision -->
# `fpcap` — design brief (URDRCAP1, T3.16, the capsule/body seam)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P42 of batch 12
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**; the author priced C-R 30 against C-EQ 25 and
missed. Reading grade: **CONFIRMATION**.

## What it is

**The seam binding a collision capsule to the body it stands for.** A first-person avatar is a set of
joints for animation purposes and a capsule for collision purposes, and those two descriptions must
not drift apart — a capsule that fails to contain its own joints is a hitbox that disagrees with the
thing it represents. This rung binds the capsule to the joints, to the terrain underfoot, and to the
pose above it.

## The core law (what `fpcap-collision` certifies)

**The capsule COVERS its joints, with the boundary exact and load-bearing.** A point just inside the
radius is covered and one just outside is not — decided by `fppose`'s exact division-free certificate,
so the containment has a sharp edge rather than a tolerance — and **a shrunk radius uncovers a joint**,
which is the non-vacuity witness: a capsule that covered everything regardless of radius would certify
nothing (L61). Supporting: `fpcap-terrain` binds downward, the foot resting at the exact ground · ONE
with `stance`'s step law biting at the exact `rise > MAX_STEP` boundary (E/S walls, N/W walkable at a
ridge cell); `fpcap-pose` binds upward, upright and 90° cardinal pitch EXACT while ~45° mouse-look
pitch ROUNDS — the exactness boundary stated rather than blurred — with 5/5 typed `CAP-REFUSE`
(off-grid · height<1 · radius<1 · bool · negative step).

## The seam (P42's finding)

**A containment certified with a strict witness, which is `interest`'s shape rather than `warden`'s.**
The prediction read "seam" as a joint that gets POLICED (C-R 30) and the rows instead certify a
CONTAINMENT with a non-vacuity witness — capsule ⊇ joints, strict somewhere — which is precisely the
broad-phase soundness pattern `interest` (P24) resolved C-EQ. The refusals here guard the domain, not
the answer. What the module adds beyond `interest` is that it is a THREE-WAY binding: the capsule
answers to the joints below it, the terrain beneath it, and the pose above it, and the gate checks all
three seams rather than the one the module is named for. The pitch clause is the quiet honesty — the
cardinal cases are exact and the interpolated ones round, said plainly instead of being absorbed into
an "exact integer" claim the module could not support.

## does_not_show

Animation, skinning, or joint dynamics (joints are inputs here, not modelled); non-capsule collision
volumes; multi-body collision or capsule-vs-capsule (this binds ONE capsule to ONE body); sub-cell
terrain beneath the foot; continuous pitch exactness (explicitly rounded, and bounded); wall-clock. A
capsule that covers its joints is CONSISTENT with the body, never a claim that the body pose is
truthful. `integrity ≠ truth`.

## Falsifier

This brief cites `fpcap-collision`: the capsule covers its joints, a point just inside the radius is
covered and one just outside is not, and a shrunk radius uncovers. If a joint ever escaped its own
capsule, or the coverage survived shrinking the radius (making the containment vacuous), that row
reddens and this brief's central claim dies with it.
