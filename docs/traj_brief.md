<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: traj-properties -->
# `traj` — design brief (URDRTRAJ1, T3.12, FPS-over-terrain slice 3b)

**Read**: 2026-08-04, the centrality-ordered READ pass — P31 of batch 8
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-R** — the second of the batch's two leading-class
misses (author priced C-REP 32, C-R 25; the partition was frozen deliberately near-flat because the
observer family had split before). Reading grade: **CONFIRMATION**.

## What it is

**The certified trajectory observer — a HORIZON observer where `gaze` is a SNAPSHOT one.** A
*sequence* of partial views is admitted iff every frame reconstructs to the pose the dynamics predict
at that tick. It couples the deterministic dynamics Φ (`drive.step`) with the axis-selection
observation H (`gaze`'s Chart/Atlas) across n steps, which buys two things `gaze` structurally cannot
do: PARTIAL COVERAGE becomes admissible (a frame need not see every axis — over the horizon the
dynamics carry unobserved axes into observed ones, so position-only frames reconstruct the full pose,
where `gaze` refuses each one `GAZE-NONCOVER`), and TEMPORAL REPLAY is caught.

## The core law (what `traj-properties` certifies)

**Admit iff every innovation is exactly zero.** For each tick the residual ν(k) = image(k) −
H(k)·trajectory(k) is formed in EXACT INTEGERS; the witness admits iff every ν is the zero vector,
else the first nonzero tick is a typed REFUSE (`traj-refusal`). Zero divides nothing — the verdict is
a divisibility-free equality, so it is confirmed or fought, never rounded. The load-bearing structural
choice: the observer reconstructs the authoritative trajectory ITSELF, folding the lockstep inputs
from the start with the same law the authority runs (`drive.drive`), so a frame is checked against a
LOCALLY-DERIVED truth rather than a trusted one. Facing is recovered from motion (the direction of the
position delta), and ground is a pure function of position — which is why partial frames suffice.

## The seam (P31's finding)

**Police, not representation — and a neutral ruler underneath.** The prediction leaned C-REP (a
trajectory transcript, the `drive` pattern); the rows certify an ADMISSION verdict with typed refusals
— the `gaze` pattern extended over a horizon. The gem the partition did not name is the
SAME-WHERE-DIFFERENT-**WHEN** catch: a frame that is entirely content-valid — a faithful view of a
pose the actor genuinely held at *another* tick, which is precisely `gaze`'s own `does_not_show`
("identity is content") — is REFUSED here, because Φ predicts a different pose at this tick and the
innovation is nonzero. The sequence IS Φ, and it closes a gap `gaze` explicitly deferred. The
locally-derived truth is the neutral-ruler pattern again (`mesh`'s monolith oracle, `wardhom`'s
cross-language identity): the checker is denied the option of trusting the thing it checks.

## does_not_show

Facing UNOBSERVABLE-from-position when the actor is BLOCKED (a stationary step needs the facing axis
observed, or the input); input INFERENCE (the inputs are lockstep-known, not inferred from frames);
visual localization (recovering pose from the terrain *seen* is a nonlinear field inversion — the
`gaze` barrier); continuous / fixed-point Φ (the Q32.32 regime is the slice-4 enrichment); the kernel
`world_host` cross-check. The general linear Kálmán observability matrix and its rank test are
DECLARED — `drive.step` is input-driven and terrain-gated, NOT an LTI operator, so horizon
observability is computed OPERATIONALLY and the linear matrix is the MODEL, not the measured object.
An admitted trajectory is not a TRUE one — it is one consistent with the dynamics. `integrity ≠ truth`.

## Falsifier

This brief cites `traj-properties`: admit iff every innovation ν is exactly zero, with the
replay/teleport discrimination (a witness whose every frame is content-valid yet is REFUSED). If a
nonzero-innovation sequence ever admitted, or a genuine partial-coverage trajectory were refused, that
row reddens and this brief's central claim dies with it.
