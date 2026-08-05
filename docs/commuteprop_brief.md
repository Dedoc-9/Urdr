<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: commute-property -->
# `commuteprop` — design brief (URDRCPS1, Tier-2 property falsifier for the commute diamond)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P37 of batch 10
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**, the author's leading credence (40) correct.
Reading grade: **CONFIRMATION**.

## What it is

**A module whose entire purpose is to attack another module's law.** `commute` (T3.41) certifies the
commutation diamond on a pinned corpus — the proof-object turn. A pinned corpus proves the law holds
*there*; it cannot speak to configurations nobody thought to pin. `commuteprop` is the Tier-2 answer:
a seeded adversarial sweep that generates scenarios and demands the diamond survive all of them.

## The core law (what `commute-property` certifies)

**The diamond, against an independent oracle.** Across the seeded sweep, **every order lands one
head + field** — verified not against `commute`'s own reasoning but against a **brute-permutation
oracle** that simply enumerates the orders and compares results. Closure agrees; `predict` matches
**independent chunk geometry**; and every same-cell pair is checked. Nothing in the verification path
consults the thing being verified: the oracle is denied the shortcut that would let a shared bug hide
in both sides of the comparison.

`commute-property-selftest` is what makes the sweep evidence rather than decoration: a **mutated
`commute.predict` (always rank 0) makes the sweep raise `COMMUTEPROP-FALSIFIED`**, and the module
reads clean again after the revert. The generator provably bites, and it bites on a real mutation of
the module it guards.

## The seam (P37's finding)

**The falsifier's own non-vacuity is the load-bearing half — and it is discharged, so C-FLOOR did not
take the joint.** The freeze priced C-FLOOR at 20 on exactly this reasoning: a property-based
falsifier that never generates a biting case proves nothing, which is L61's shape (an empty answer is
indistinguishable from a correct one unless something asserts non-emptiness). The module answers that
directly with the mutation test, so the non-vacuity is *established* rather than *central*, and the
central law remains the equivalence itself. The unnamed gem is the **brute-permutation oracle** — the
neutral-ruler pattern's sixth instance (`mesh`'s monolith, `wardhom`'s three languages, `traj`'s
locally-derived truth, `cayley`'s two algorithms, `terraform`-as-oracle, and now this) — where the
checker is structurally denied the option of trusting what it checks.

## does_not_show

Coverage of the FULL configuration space — a seeded sweep is a sample, and a sample is not a
universal (L20); an adversary choosing configurations the seed never reaches is outside this evidence.
The pinned-corpus guarantees themselves (those are `commute`'s rows, not these); wall-clock or sweep
cost; that `COUNT` scenarios is the right number, which is a declared budget rather than a derived
one. A property that survives a sweep is not a proven theorem — it is an unfalsified one.
`integrity ≠ truth`.

## Falsifier

This brief cites `commute-property`: the diamond surviving the seeded adversarial sweep with every
order landing one head + field against the brute-permutation oracle, closure agreeing, and `predict`
matching independent chunk geometry. If any generated scenario produced order-dependent results, or
the sweep stopped being able to redden on a mutated `predict`, that row reddens and this brief's
central claim dies with it.
