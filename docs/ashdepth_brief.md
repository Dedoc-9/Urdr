<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: ashdepth-law -->
# `ashdepth` — design brief (URDRASH1)

**Read**: 2026-08-04, the centrality-ordered READ pass — P17 of batch 3
(`../exe_epistemics/PREDICTIONS.md`), post-closure. Outcome: **C-FLOOR** — and the rung's content
is a refutation-by-measurement of the design it was handed. Reading grade: **CONFIRMATION** — the
module is what its rows certify, and what it certifies is an inversion.

## What it is

**The vacuity floor**: how far an abstraction may be coarsened before it stops saying anything,
and the tripwire that refuses silence. A handed-down design proposed an "ash-depth bound" k* — the
coarsest level at which P ⊆ γ_k(α_k(P)) still holds — reasoning that burning past it "collapses
the Galois connection into an unsound approximation." Measured, that is **backwards**, and the
correction is the whole rung.

## The core law (what `ashdepth-law` certifies)

**Soundness never breaks.** Coarsening is strictly more conservative (level monotonicity:
coarse-disjoint implies fine-disjoint), so a coarser abstraction admits strictly fewer pairs and
can never admit a wrong one — 0 unsound at every level, including the coarsest (0/12090 fast-path
at level 0; 4212 at level 1; 8580 at level 2). The proposed k* passes **vacuously at maximum
burn** — the exact point it was built to catch. The failure at full burn is not a lie: it is an
**empty fast path** — α collapses to a constant, and a constant abstraction is perfectly sound and
perfectly useless. *A void is sound.* The bound actually worth guarding is the other end:
k_min = min{k : α_k still distinguishes something}, guarded by a floor gate that refuses below it
(`guard_refuses_below_floor`), with `VacuityError` raised rather than a zero quietly returned, and
`EMPTY_CORPUS` pinned as a hard tripwire asset any future refinement that zeroes the fast path
must trip.

## The named law (the arc's characteristic failure, fourth appearance)

The module names what it fixed four times: *(1)* disjoint's first edit family (every pair
commuting trivially — the census would have confirmed the inverted predicate); *(2)* frontier's
greedy plant scoring zero on all-singleton batches; *(3)* the level table itself, first run on a
corpus with an empty fast path at every level — one keystroke from "soundness never breaks" as a
false finding; *(4)* the handed-down k*. **"In this architecture wrong answers are rare and empty
answers are common, and an empty answer is indistinguishable from a correct one unless something
asserts non-emptiness."** Every census carries a non-vacuity precondition.

## The seam (P17's finding)

A floor gate (measured distinguishing power vs a declared floor — the cost discriminator pointed
at *epistemic yield*), whose deepest content is approximation-axis material: the precision/vacuity
structure of the frontier/disjoint Galois stack. The freeze's mint trigger (an R-O) was not met by
the letter; the spirit-vs-letter question is recorded for checkpoint 4 rather than bent mid-run.
The vacuity law resonates far beyond the module: it is the epistemics ledger's own experience (an
instrument starved of events reads as consistent), stated as architecture.

## does_not_show

Which level is *optimal* (k_min is a floor, not a policy); the semantic checkers' guarantees
(routed); anything about corpora other than the pinned families — the levels table is
corpus-relative by construction. `integrity ≠ truth`.

## Falsifier

This brief cites `ashdepth-law`: soundness-never-breaks + the non-vacuous floor. If any level
admitted a non-commuting pair, or the guard stopped refusing below k_min, that row reddens and
this brief's central claim dies with it.
