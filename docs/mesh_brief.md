<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: mesh-law -->
# `mesh` — design brief (URDRMSH1, Phase M, rung M3)

**Read**: 2026-08-04, the centrality-ordered READ pass — P25 of batch 6
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ** (the identity the role states, certified;
the bases agreed). Reading grade: **CONFIRMATION**.

## What it is

**The meshed simulation — the capstone ∀-law MESH == MONOLITH.** N authorities own regions of one
world and migrate authority between each other over time; a meshed simulation of concurrent per-tick
writes composes to the *same* world witness a single monolithic authority would compute —
bit-for-bit — or refuses. Not a best-effort convergence: **a theorem, re-derived in bytes.**

## The core law (what `mesh-law` certifies)

For any schedule of ticks — each a set of concurrent writes by the current stewards on
pairwise-disjoint regions, followed by authority migrations — the meshed world witness equals the
monolith of the same writes, bit-for-bit. It is a **composition**, not a new mechanism: `nway` (M1)
schedules the concurrent writes as one independence round (an overlapping batch is not schedulable —
the tick refuses whole); `migrate` (M2) moves authority between ticks, witness-neutral, gating every
write through steward-checked conjunctive admission (lease AND custody chain); and `terraform` is the
**monolith oracle / neutral ruler** — it applies the same writes globally *ignoring custody
entirely*, never consulting a steward or lease, so a bug in the meshed tick cannot hide inside its
own answer (Goodhart resistance built into the check's structure). This generalizes `regionprop`'s
reunify == monolith from a static partition to a *migrating* one: the partition of work is fixed
(the chunk grid), the partition of authority migrates, and the witness is invariant to both.
Reject-whole refusal: a non-steward write, an overlapping concurrent batch, and a theft migration
each refuse the whole tick typed `MESH-REFUSE`.

## The seam (P25's finding)

The neutral-oracle equivalence at simulation scale — the `nway`/`hand`/`wardhom` bit-identity
pattern lifted to the whole meshed world, with a migrating authority partition. Both bases priced
C-EQ; not a discrimination. The unnamed gem is the oracle's *structural* neutrality: the ruler
cannot be gamed because it is denied the very inputs (custody, leases) a meshed bug would exploit.

## does_not_show

Throughput / per-tick cost of the mesh (NOT_MEASURED — correctness is measured, scale is a design
target); non-disjoint concurrent writes (rejected by construction — one independence round only);
the network transport of writes and migrations; wall-clock. `integrity ≠ truth`.

## Falsifier

This brief cites `mesh-law`: mesh == monolith under migration, reject-whole. If a meshed tick ever
diverged from the monolith of the same writes, or a partial world admitted, that row reddens and
this brief's central claim dies with it.
