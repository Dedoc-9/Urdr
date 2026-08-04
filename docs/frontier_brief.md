<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: frontier-law -->
# `frontier` — design brief (URDRFRN1)

**Read**: 2026-08-04, the centrality-ordered READ pass — P13 of batch 2
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **R-O** — the first residual since P3, minting the
**approximation axis's first sighting**: both rival bases predicted an equivalence law and the
module is a verified sound-incomplete abstraction instead. Reading grade: **CONFIRMATION** — the
module is what its rows certify; the surprise is the bases', not the module's.

## What it is

**The admission accelerator**: routing work between a cheap structural certificate and an
expensive semantic check, with the residue tracked as an explicit **obligation signature** rather
than left implicit. `disjoint` decides commutation for prefix-disjoint edits in one integer
comparison — sound and incomplete — which is exactly what a two-tier scheduler wants: route the
decided pairs to a fast path needing no check, and reserve `commute`/`rannull`/`nway` for the
FRONTIER, the pairs the structural certificate cannot settle. The prior art is scoped with unusual
honesty (scalable commutativity, filter/refinement, broadphase/narrowphase, conflict-graph
serializability, and — "the closest framework of all" — abstract interpretation, Cousot & Cousot
1977; every one explicitly NOT claimed).

## The core law (what `frontier-law` certifies)

**The frontier is a Galois connection, verified rather than asserted**: with α mapping edit-pair
sets to block-prefix footprints and γ concretizing back, the adjunction α(P) ≤ O ⟺ P ≤ γ(O) holds
on 63 of 63 tested pairs — sound (P ≤ γ(α(P))), reductive (α(γ(O)) ≤ O), and NOT complete, with
measured precision loss. That loss is not an error margin: γ(α(P)) ∖ P **is** the obligation set —
the headroom a sound over-approximation needs to stay authoritative without doing proof work — and
it is counted. The row certifies: edits in different connected components of the conflict graph
commute, **checked against the commutation semantics rather than the predicate that built the
graph** (so the theorem is not true by construction); the obligation signature **conserves**
(proved + obligations == total — nothing silently dropped, which is the failure an accelerator
invites, because a fast path that discards what it cannot handle looks exactly like one that
handles it) and is **monotone** (refining the level moves pairs from obligation to proved).

## The seam (P13's finding — the approximation axis)

Neither rival basis could express this law: it is not an equivalence (fast ≢ slow — the fast path
is deliberately incomplete), not an admission gate, not a cost envelope. It is **sound
over-approximation with counted, conserved, monotone residue** — an order-theoretic object (the
module is explicit: no metric, no convergence, no contraction, no manifold; the lattice and its
Galois connection are the complete formal content). Recorded in the ledger as the approximation
axis's first sighting, mintable at the second.

## does_not_show

Completeness (the frontier is the point); any analytic structure (attractors would require a
contraction property NOT established); the semantic checkers' own guarantees (routed, not
re-proved); scheduling policy over the proved components. `integrity ≠ truth`.

## Falsifier

This brief cites `frontier-law`: component-commutation checked against semantics, conservation,
and monotonicity. If two cross-component edits stopped commuting, an obligation went missing from
the census, or refinement moved a pair backwards, that row reddens and this brief's central claim
dies with it.
