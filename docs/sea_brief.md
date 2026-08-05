<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: sea-conservation -->
# `sea` — design brief (URDRFLD1, S1/S2, the terrain sea as certified field state)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P53 of batch 15
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 16**. Outcome: **C-INV**, the
author's leading credence (44) correct — and disclosed in advance as an EASY call, since the row is
named `sea-conservation` and the name leaks its class. Reading grade: **CONFIRMATION**.

## What it is

**Water as certified state rather than decoration.** The sea evolves on the same integer lattice as
the terrain, and it must do so without leaking onto land or quietly gaining and losing volume — because
everything downstream (`buoyancy`'s waterline, `crossing`'s overtop tick) reads this field as
authority.

## The core law (what `sea-conservation` certifies)

**Total mass EXACT across 40 masked ticks — and the field genuinely moved.** Both halves matter: exact
conservation is the law, and "the field genuinely moved" is the non-vacuity witness (L61) that stops a
frozen field from satisfying conservation trivially. `sea-coast` binds the domain: land is identically
zero at init and after evolution, and **an all-sea mask is bit-for-bit identical to the frozen step**,
so masking adds no drift where there is nothing to mask. `sea-selftest` makes the mask load-bearing —
the UNMASKED evolution wets land cells and diverges. `sea-refusal` is total and typed (4/4: empty sea ·
drop on land · bool depth `TERRAIN-REFUSE`; grid/mask mismatch `FIELD-REFUSE`).

## The seam (P53's finding) — and a MARANGONI implementation already in the arc

The conservation law is what the row name promised, so the interesting content is elsewhere: **`sea`
already carries a Marangoni transport law.** `sea-marangoni` certifies **mass EXACT + monotone 30/30
ticks (audited, not estimated) + the peak persists above pure diffusion + land dry — surface tension on
the masked domain.** The "peak persists above pure diffusion" clause is the Marangoni signature proper:
surface-tension-driven transport sustaining a concentration peak that diffusion alone would flatten.
And `sea-marangoni-selftest` makes the stability bound load-bearing rather than decorative — **the
over-bound κ overshoots negative yet CONSERVES MASS**, which is the sharp case: a defect that preserves
the headline invariant while violating physicality would pass a conservation-only check, so the CFL
bound is tested by a plant that conservation cannot catch.

That last point is the module's methodological contribution: **an invariant that a defect can satisfy
is not sufficient evidence**, and the plant is chosen to be exactly such a defect. It is the same
reasoning `magicdiv` used (a multiplier that stays correct for powers of two) and `divergence` used
(two perturbations with identical rate), now applied to a physical bound.

## does_not_show

Real hydrodynamics — the field is a DECLARED model, as `wavefield`'s is, and only its computation is
measured; sub-cell water; wetting/drying dynamics beyond the mask; the rendered surface (behind the D15
firewall); wall-clock; that the Marangoni parameters correspond to any real fluid. Exact mass
conservation is a property of this model computed exactly. `integrity ≠ truth`.

## Falsifier

This brief cites `sea-conservation`: total mass exact across 40 masked ticks, with the field genuinely
moving. If mass ever drifted under masked evolution — or if the scene went vacuous, the field not
moving so that conservation held trivially — that row reddens and this brief's central claim dies with
it.
