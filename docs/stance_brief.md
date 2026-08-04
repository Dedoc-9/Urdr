<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: stance-properties -->
# `stance` — design brief (URDRSTANCE1, T3.9)

**Read**: 2026-08-04, the centrality-ordered READ pass — the **third brief written blind against a
frozen pre-registration** (P3, `../exe_epistemics/PREDICTIONS.md`), under the freeze-before-history rule
(L59). Outcome: **LOCAL-SURPRISE** — the ledger's first residual: the predicted predicate held, the
predicted refusal semantics did not (refuse ≠ measure, below). Reading grade: **CONFIRMATION** — the
module is what its rows certify; the surprise is the prediction's, not the module's.

## What it is

The **measured foundation of first-person movement**: an exact, integer, grounded walk across the
certified heightfield — the solid-ground sibling of `buoyancy` (waterline on the wavefield) and
`crossing` (agent through the wavefield), and the opener of the movement chain
(`stance` → `gaze` → `drive` → `traj`). Two exact facts, no float, no `/` `//` `%`:

- **GROUNDED** — at cell (x, y) the actor's feet rest at the exact ground height `heights[y][x]`;
  standing IS reading the field.
- **STEP GATE** — a cardinal step is traversable iff its rise `heights[B] − heights[A] ≤ MAX_STEP`:
  the integer collapse of a character controller's two knobs (step-offset and slope-limit — on a unit
  grid a slope over one cell IS a rise). Descending is always traversable; a rise above `MAX_STEP` is
  a wall.

The declared walk is a start cell plus a string of cardinal moves; the measured event is the **first
step blocked** by an unclimbable rise, else the full path length. `MAX_STEP` is load-bearing and
pinned as such: `ridge_clear` and `ridge_blocked` share one path and differ only in `MAX_STEP` (40
clears, 20 walls at step 8) — the terrain decides where the walk ends, not the model.

## The core law (what `stance-properties` certifies)

The profile is the exact ground under the path; the result is the **first** wall; `MAX_STEP` is
load-bearing. Around it: `stance:scenes` pins three walks to URDRSTANCE1 digests (×2, binding both the
blocking event and the footing); `stance-selftest` proves the gate can redden — a planted
walk-through-walls defect (`blind=True`, which ignores the step gate) changes where a walled walk ends;
`stance-refusal` is the domain boundary — 8/8 typed `STANCE-REFUSE` (off-grid start, path leaving the
grid, unknown move, negative step, non-positive actor, empty path, bool, non-int start): refuse, never
clamp the path or invent a footing.

## The seam (P3's finding — the first residual)

The prediction froze "an admission seam: a per-step admissibility predicate over canonical terrain,
with a typed refusal for wall-crossing steps." The rows confirm the **predicate** and refute the
**refusal semantics**: a wall does not refuse — blocking is a *measured event*, and the typed refusal
guards only the *domain*. The residual (delta: REFUSE → MEASURE, a class neither pre-named risk
covered) names a distinction the seam vocabulary did not have: **admission of the question** (domain
membership — refuses, totally and typed) is separated from **the answer** (a measured event — never
refused). `jurisdiction` refuses inadmissible claims; `stance` measures where terrain blocks. The
movement MODEL is DECLARED; the walk is MEASURED; the heightfield it reads is the authority.

## does_not_show

The walked path is a state trajectory; the observer that certifies a *view* of it (the D7–D10
observability seam, `world_host`/`atlas_*`) is deferred — this module earns the trajectory, not the
camera. Diagonals are excluded by construction (no exact integer length; one cell per move keeps the
gate exact). Cross-placement is deferred (asserted division-free; Python reference until a placement
reproduces the digests). Wall-clock is `bench.py` territory. And the brief does not upgrade the model:
"an actor climbs at most MAX_STEP" is DECLARED — the gate certifies the walk against it, never that
real locomotion obeys it. `integrity ≠ truth`.

## Falsifier

This brief cites `stance-properties`: the row certifying the exact ground profile, the first-wall
result, and the load-bearing `MAX_STEP`. If the profile stopped matching the field, the result stopped
being the first wall, or one path stopped clearing high while walling low, that row reddens and this
brief's central claim dies with it.
