<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: wardhom-tie -->
# `wardhom` — design brief (URDRWARDH1, T3.27, MMO Stage E)

**Read**: 2026-08-04, the centrality-ordered READ pass — P16 of batch 3
(`../exe_epistemics/PREDICTIONS.md`), post-closure. Outcome: **C-EQ** — the equivalence the role
line states outright, certified. Reading grade: **CONFIRMATION**.

## What it is

**The warden's β₀ IS the certified F2-homology β₀, cross-placed.** The warden's walkable field is
a graph — a vertex per cell, an undirected edge where the step is legal both ways — read as a
1-dimensional simplicial complex. Its homology is elementary and exact: β₀ = n₀ − rank(∂₁) = the
number of connected components — exactly `warden.betti0`, obtained by F2 boundary-matrix rank
instead of union-find; β₁ = n₁ − rank(∂₁) = the independent cycles of the walkable space.

## The keystone (what `wardhom-tie` certifies)

**Two independent methods agree**: `warden.betti0` (union-find) == URDRPD1 F2-rank β₀ on every
pinned world, including the 16×16 barrier. And the F2 computation is **cross-placed**: `wardhom_c/`
(C99) and `wardhom_rs/` (Rust) build the same walkable complex from the same field and reproduce
the URDRWARDH1 digest (MAGIC | name | n₀ | n₁ | rank | β₀ | β₁) bit-for-bit — the anti-cheat's
topological certificate is no longer a single implementation's count but the rank of a boundary
operator over F2, reproduced across three languages. Non-vacuity is pinned in the topology itself:
`barrier8` has β₀ = 3, `cliff8` has β₀ = 2 (|Δ| > MAX_STEP, undirected-disconnected), `flat8` has
β₀ = 1 with the most cycles — genuinely different worlds the digest must separate; the `--defect`
mode (dropping the rank subtraction) inflates β₀ and moves the digest.

## The seam (P16's finding)

The neutral-oracle equivalence, central — two computations neither of which reads the other,
agreeing on every world, with the agreement (not either count) as the certified object. This is
`nway`'s cross-check pattern applied to the anti-cheat's own foundation: `warden`'s refusals
(WARD-UNREACH) now rest on an invariant certified twice, three ways.

## does_not_show

β₂ and higher (the walkable graph is 1-dimensional by construction); PERSISTENCE (static homology,
not a filtration); torsion (F2 ranks only); weighted edges (a single MAX_STEP); wall-clock cost.
The homology is the walkable graph's, not a point cloud's — it uses URDRPD1's machinery verbatim,
so the two agree by construction where they overlap. `integrity ≠ truth`.

## Falsifier

This brief cites `wardhom-tie`: union-find == F2-rank on every world. If the two methods ever
disagreed on a β₀, that row reddens and this brief's central claim dies with it.
