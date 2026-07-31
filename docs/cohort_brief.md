# Agreement across a peer cohort (URDRCOH1): a design pass

<!-- brief-falsifier: cohort-plan -->

The rung that turned a THRESHOLD into a THEOREM. Every number in this module that once looked like a
tuning constant is now either derived from a graph-theoretic minimum or refuted and removed.

## OODA

**Observe.** A verifier deciding whether a cohort agrees needs a rule for when disagreement is
possible at all. The handed-down design used a fraction — a two-thirds agreement bar — which is a
number nobody could derive and which the arc's own measurements did not support.

**Orient.** The question "how many cells must change before the verdict can flip" is not statistical.
It is the minimum vertex cut of the wall between the two faces: Menger's 1927 theorem says the minimum
cut equals the maximum number of internally vertex-disjoint paths, so the gap is a graph invariant and
not a threshold.

**Decide — the law.** `k = min-cut(wall)`. Below the gap, disagreement is IMPOSSIBLE, and that is a
theorem rather than an observation. At or above it, disagreement becomes possible. The verdict itself
is CONNECTIVITY of free space between the two faces — one flood fill on the integer lattice, no
division and no bar anywhere.

**Act.** Rows: `cohort:scenes`, `cohort-plan`, `cohort-gap`, `cohort-impossible`, `cohort-outcomes`,
`cohort-refuted`, `cohort-policy`. Measured per wall: `(n, thick, k)` = (3,1,1) (4,1,1) (4,2,2)
(5,1,1) (5,2,2) — a 1-thick spanning wall has k=1, a 2-thick wall has k=2.

## The laws

1. **The gap is a min-cut, not a fraction.** `k = min-cut(wall)`, by Menger duality equal to the
   maximum number of internally vertex-disjoint paths across it.
2. **Sub-gap disagreement is impossible.** Census (2, 32, 0): zero exceptions, and the zero is a
   theorem's consequence rather than a lucky sample.
3. **At or above the gap it becomes possible.** (2, 496, 16). Both halves are asserted, because a law
   that only ever forbids is indistinguishable from a law nobody tested.
4. **Four measurands were REFUTED and removed**, not weakened. A measurand that cannot separate two
   situations with opposite verdicts may not gate a fetch.
5. **`WALL_MIN_K = 2` and `charge_for_gap = B // max(k, 1)`** — the budget charge is derived from the
   gap rather than chosen.

## The glyph verdict: NO new glyph (kernel frozen)

Integer flood fill and an exact min-cut. No kernel surface is touched; D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

The screening law is measured on a fixture where the wall IS the entire occupancy, so it does not by
itself distinguish `min-cut(wall)` from `min-cut(occupancy)` — `autoroute` had to measure that
separately and found the subregion's k conservative but not free. This does not show that agreement
means the peers are HONEST: it shows their verdicts coincide, which is why `autoroute` needs a
separate peer-fault path. k beyond `CUT_SEARCH_MAX` is decided by inheritance rather than by search.

## Where this sits

Above `inputset` (whose LATTICE-tier decision it enforces) and below `autoroute`, which generalizes
the enforcement from one tier to four.
