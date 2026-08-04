<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: wavefield-properties -->
# `wavefield` — design brief (URDRWAV1, T3.3)

**Read**: 2026-08-04, the centrality-ordered READ pass — P12 of batch 2
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-AB** — canon identity fused with the exact
superposition invariant; the newly frozen tie-pricing rule paid on its first outing. Reading grade:
**CONFIRMATION**.

## What it is

**The authority half of the wave seam**: an exact, division-free integer traveling field. The
presentation renders a pretty sinusoidal Gerstner surface in float on the GPU (DECLARED); the
authority certifies a deterministic height field a view displaces and gameplay consumers
(`buoyancy`, `crossing`) read. Two grades, never conflated. Two design commitments make the
authority the strongest grade available: **no trig** — a periodic parabolic profile in pure
integers, amplitude and curvature tied by 8A = cP², running exactly +A → −A → +A; and **no
division operator** — every `/`, `//`, `%` is removed from the profile, the phase wrap, and the
exactness check alike, and the test suite *tokenizes the file* to assert none exists. Integer
division disagrees across languages on negative operands (Python floors, C99/Rust truncate);
removing the operators makes cross-placement parity **structural**, not a documented caveat. The
curvature and phase wrap are computed by shift-based doubling (`<<`, `>>`, `+`, `−`,
comparisons) — exact, no rounding, O(log).

## The core law (what `wavefield-properties` certifies)

Cells bounded within Σ|A|; a swell travels while a still component is static; and **superposition
is exact**: field(Σ components) == Σ field(component), no rounding — linearity as a certified
structural law, not a float approximation. `wavefield:scenes` pins the canon: same components +
tick → same bytes on every host. `wavefield-selftest` plants the defect variant; `wavefield-refusal`
is the typed battery (non-exact (A,P), odd/short period, zero direction, negative speed, non-int
including bool, bad dims/tick): refuse, never approximate.

## The seam (P12's finding)

Representation fused with structural invariant — the heightfield canon pattern lifted to a
time-varying field, carrying its linearity as a law. The unnamed structure worth keeping: the
doubling arithmetic (a Q16 reciprocal would *round* — the bounded regime — and could not claim
EXACT), and the tokenizer assertion as proof-of-absence: operator variance eliminated structurally
rather than warned about.

## does_not_show

The render (pixels are never measured — the Gerstner surface is DECLARED presentation, off-gate);
wall-clock; cross-placement (the winding_rs recipe applies; a clean next step). `integrity ≠ truth`.

## Falsifier

This brief cites `wavefield-properties`: bound, travel, and exact superposition. If a cell exceeded
Σ|A|, a still component moved, or superposition acquired a rounding error, that row reddens and
this brief's central claim dies with it.
