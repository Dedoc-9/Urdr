<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: terrain:object -->
# `terrain_bridge` — design brief (URDROBJ2, T2, the D14 admission rung)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P59 of batch 17
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 18**. Outcome: **C-EQ**; the author
priced C-R 40 against C-EQ 24 and missed. Notable for a second reason: this module had been **silently
excluded** from the READ pass by a defective eligibility rule, and was recovered when that rule was
corrected. Reading grade: **CONFIRMATION**.

## What it is

**The bridge from a certified heightfield to a world object.** `heightfield` (T1) certifies terrain as
canonical bytes. Everything downstream wants an *object* — something with an identity that can be
referenced, compared and admitted. This rung is that conversion, and the D14 admission rung that
governs it.

## The core law (what `terrain:object` certifies)

**The island and blank presets bridge to pinned URDROBJ2 goldens ×2, the bridge's OWN canon is
IDENTICAL to `canon_ref`, and D14 ADMITs.** The load-bearing clause is the middle one: the bridge does
not merely *produce* an object, it produces one whose canonical form equals the independently held
reference canon — so the conversion cannot drift into its own private notion of canonical.

`terrain-object-provenance` carries the sharper law: **identical geometry with DIFFERING PROVENANCE
yields ONE URDROBJ2 identity** (D14 clause 5), and the row reddens with "provenance leaked into the
object identity" if it does not. Object identity is a function of geometry alone — *where the terrain
came from cannot change what it is*. `terrain-object-selftest` makes it bite: the max-first
edge-normalization defect diverges from the golden. And `terrain-refusal` is total and typed (6/6
`TERRAIN-REFUSE`: stride remainder · zero scale · dims · bool seed · stack cap · falloff) under a
principle stated in the row itself — **refuse, never clamp**.

## The seam (P59's finding)

**An identity behind an admission rung — and the role prose said "admission" outright.** The freeze
priced C-R at 40 on the role line ("the D14 *admission* rung"), and the central row certifies
`OWN canon ≡ canon_ref`. The admission verdict (D14 ADMIT) is the *consequence* of the identity
holding, not the law. This is the same shape that has cost several calls in this pass; it is recorded
descriptively here, and no claim is drawn from the recurrence, since the prediction that tried to
generalize it (FP-ROW) was falsified and retired.

The provenance-invariance clause is the module's real contribution and would be easy to miss:
**identity must not encode history**. A bridge that let provenance into the digest would make two
byte-identical terrains non-interchangeable, quietly breaking every downstream comparison — and the
gate names that failure rather than trusting the implementation to avoid it.

## does_not_show

That the geometry is CORRECT (that is `heightfield`'s T1 canon — this bridges it, and a faithful bridge
of a wrong field is faithfully wrong); presets beyond those pinned; the object's behaviour once
admitted; wall-clock. An admitted object is one whose canon matches the reference and whose identity
ignores its origin. `integrity ≠ truth`.

## Falsifier

This brief cites `terrain:object`: the island and blank presets bridging to pinned URDROBJ2 goldens
with the bridge's own canon identical to `canon_ref` and D14 admitting. If the bridge's canon ever
diverged from the reference canon — the conversion drifting into a private notion of canonical — that
row reddens and this brief's central claim dies with it.
