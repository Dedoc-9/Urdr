<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: gaze-properties -->
# `gaze` — design brief (URDRGAZE1, T3.10, Slice 2)

**Read**: 2026-08-04, the centrality-ordered READ pass — P14 of batch 2
(`../exe_epistemics/PREDICTIONS.md`), the batch's genuine discrimination: the promoted basis read
the observer police-first, the challenger identity-first, and the rows chose. Outcome: **C-R** —
B-M's win, weights 0.73/0.27. Reading grade: **CONFIRMATION**.

## What it is

**The certified first-person observer**: a view of the walking actor is ADMITTED iff it
reconstructs to the authoritative pose, else REFUSED. `stance` earns the trajectory; this is the
observer that watches it — the D7–D10 observability construct (exact-integer Kálmán observability)
specialized to the terrain pose `[x, y, ground_height, facing]`. An axis-selection chart observes
a subset of pose coordinates; an atlas is **covering** iff every coordinate is observed by some
chart (the trivial-kernel / full-column-rank condition); a covering atlas reconstructs the pose
from a frame; a frame is admitted iff its reconstruction's digest equals the **current**
authority's.

## The admit law (what `gaze-properties` certifies)

Pure — admit reads the authority, never mutates it (the membrane). NON-COVERING → refuse
`GAZE-NONCOVER` (a frame that does not observe every axis cannot pin the state; the atlas kernel
is nontrivial). LAUNDERING → refuse `GAZE-LAUNDER` (a covering frame whose reconstruction's digest
differs from the authority's — a *substituted* pose or a *stale* one: **one mechanism, two threat
models**). Else ADMIT, bound to the current authority. `gaze-selftest` pins the advancing
authority as load-bearing: advance pose[j] → pose[k] by a real walk step and the once-valid
pose[j] frame — still covering, still an honest reconstruction of *a* pose — now refuses: **the
same frame that admits at its own pose refuses at the advanced one**. Replay caught by
construction; if a wiring bug ever anchored on a stale pose, the scene reddens.

## The seam (P14's finding)

**Police × representation, confirmed** — the warden pattern pointed at observers: what is
adjudicated is a *view's claim* to depict the authority, and the criterion is reconstruction
against canonical state, certificate-independent. The rank condition is the unnamed gem: coverage
decided by linear algebra (full column rank = trivial kernel), admissibility as an observability
criterion. gaze certifies WHERE; composing with the lockstep transcript (`drive`) certifies WHERE
AND WHEN — the temporal-replay gap each names is closed by the pair.

## does_not_show

Visual localization (recovering the pose from the terrain *seen* is a nonlinear inversion — not
this linear observer). A true perspective projection (axis-selection charts only). Temporal replay
of a *spatially identical* pose (identity is content; same-where-different-when needs a sequence —
the netcode stack binds it). The render (pixels never measured). The kernel `world_host`
cross-check (a clean next step). `integrity ≠ truth`.

## Falsifier

This brief cites `gaze-properties`: genuine admits, exact reconstruction by a covering atlas, and
the membrane. If a non-covering frame admitted, a covering frame stopped reconstructing exactly,
or admit mutated the authority, that row reddens and this brief's central claim dies with it.
