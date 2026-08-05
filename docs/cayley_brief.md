<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: cayley-law -->
# `cayley` — design brief (URDRCAY1, the coordinate-free realizability law)

**Read**: 2026-08-05, the READ pass under the successor selector — P35 of batch 9
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 10**. Outcome: **C-EQ**; the
author's leading credence (C-INV 35) missed, and C-EQ had been priced third at 22. Reading grade:
**CONFIRMATION**.

## What it is

**The Cayley–Menger determinant as an exact integer realizability test.** A claimed set of pairwise
distances must be geometrically POSSIBLE in 3-space, and the test is a polynomial identity in those
distances alone. It belongs in this arc *arithmetically*, not by analogy: CM consumes only SQUARED
distances and returns an exact integer, and this arc already computes in squared distances everywhere
(`perception`'s `d2`, `hitbox`'s `max_range2`, `audible`'s reach) precisely to keep square roots and
floats out of every authority path. CM is not an import into this arithmetic — it *is* this
arithmetic.

## The core law (what `cayley-law` certifies)

**Identities, verified rather than quoted.** Heron in determinant form reproduces an INDEPENDENTLY
computed area (−det(CM) == 16·area², checked on 3-4-5: 576); the simplex volume reproduces an
independently computed volume (det(CM) == 288·vol², checked: 373248); and the operative one — **any 5
points in 3-space span at most a degenerate 4-simplex, so their 6×6 determinant VANISHES
IDENTICALLY.** That last is a tautology every real configuration satisfies, without exception and
without reference to any coordinate frame. `cayley-property` holds it EXACTLY across every random
integer configuration in the sweep (one non-zero residue would falsify the implementation), and a
forged distance broke it every time; `cayley-selftest` proves the law is a live falsifier by showing a
credulous verifier admitting exactly what the determinant refuses.

## The seam (P35's finding)

**An identity that happens to police, not a police predicate built on an identity — and that is why
the leading call missed.** The prediction read "coordinate-free realizability" as a structural
invariant (C-INV, B-M′'s founding axis); the row certifies EQUALITIES against independently computed
quantities, which is the arc's C-EQ signature (`wardhom`'s three languages, `mesh` == monolith).
The unnamed gems: **two independent algorithms as oracles for each other** — `bareiss` (fraction-free
but it divides) and `leibniz_det` (division-free) must agree on every configuration, neither reading
the other's intermediate state, the neutral-ruler pattern a fifth time; the **Leibniz form is the one
that travels**, because integer division semantics differ between languages for negative operands, so
a division-free expansion is what cross-places to C99 or Rust with no rounding question to answer; and
the check asks a *strictly weaker* question than every other admission in the arc — not "is your
claimed POSITION lawful against the authoritative frame?" but "is your claimed set of RELATIONSHIPS
even possible?", needing no coordinates, no shared frame, and no trusted origin. A client reporting
distances to five landmarks is OVER-DETERMINED: the tenth distance is pinned by the other nine, and a
cheater fabricating one to appear nearer several things at once breaks the identity exactly (on the
ring scene, 0 → −8944).

## does_not_show

WHO the client is or whether the distances are truthfully measured — realizability says a set is
POSSIBLE, never that it is actual; a cheater whose fabrication happens to remain realizable passes.
Positions, orientation, or any coordinate reconstruction (the law is deliberately frame-free); more
than 3 dimensions; floating-point or non-integer distances; wall-clock. Passing the identity is a
necessary condition, never a sufficient one. `integrity ≠ truth`.

## Falsifier

This brief cites `cayley-law`: Heron and the simplex volume reproducing independently computed area
and volume, and the vanishing 6×6 determinant for five points in 3-space while a single fabricated
distance makes the set impossible. If an honest configuration ever produced a non-zero residue, or a
forged one a zero residue, that row reddens and this brief's central claim dies with it.
