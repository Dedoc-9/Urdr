<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxcoarse-binding -->

# `voxcoarse` (URDRVXC1) — design brief

*How coarse the frozen observable is, measured before anything leans on it.*

## Observe

`voxref` froze `O_t = (H_C(colorbuffer), H_Z(depthbuffer))` and reported a census over its eight
adversarial frames: eight states, eight distinct observables, no collisions. That was **plumbing,
not evidence**, and it was labelled as such — but labelling a gap is not closing it.

Eight frames chosen to be *maximally different from one another* are close to the worst possible
sample for detecting collisions. An injective result on them establishes exactly one thing: on
those eight, none was seen. It says nothing about the size or the structure of the fibres of
`state → O_t`. And the whole point of freezing an observable is that later reductions are obliged
to preserve it. An obligation whose discriminating power nobody measured is an obligation of
unknown strength.

## Orient

Three decisions, and the first is the one that keeps the answer honest.

**The lattice is declared before the answer is known, and regular rather than curated.** Six
positions per axis sweeping from well outside the world to buried inside it, eight forward
directions, 1728 states. Picking states after seeing which ones collide is picking the answer.

**The record is the artifact and the gate re-derives from it.** Rendering 1728 states is minutes,
which is not a gate budget, so the census is generated once and committed. But a committed table of
digests is worth nothing alone — it could describe any renderer at all. So the gate re-derives every
reported figure from the record's rows, and **re-renders a declared sample through the live
`voxref`**, requiring the record's digests to match. That second half is what binds the table to the
code. Without it the record is a rumour.

**And the distinction the whole rung turns on is state equality against observable equality.** Two
different states sharing an `O_t` are two states the criterion cannot tell apart, and a reduction
that behaves differently on them is untested by either. That is not a defect — a render map is
supposed to forget things — it is a boundary, and boundaries are worth knowing before they are
trusted.

## Decide

The result, and the part that needed decomposing rather than reporting.

Over the whole lattice: **1728 states → 558 distinct observables**, and the largest fibre is
**1125**. Taken alone that number reads as a devastating verdict on the observable. It is not. That
fibre is the **empty view** — the lattice reaches far outside the world, and every position out
there looking away produces background everywhere and no depth written. It is a fact about where
the declared positions happen to be.

The lattice is **not redesigned** to remove them. Instead the empty view is identified as a category
*derivable from the renderer* — render an empty primitive list and you get those bytes by
construction — rather than by taking the biggest fibre and naming it afterwards, which would be
reading the answer off the data. Then the census is reported twice:

    whole lattice     1728 states → 558 distinct, largest fibre 1125 (the empty view)
    seeing something   603 states → 557 distinct, 68 collide (11.3%), largest fibre 13

So the observable is **sharp** where it has anything to look at: 535 of the 603 non-empty states
are uniquely identified, and the worst genuine collision class holds thirteen. That is the number
the reduction rungs inherit.

A defect worth keeping: the state count was taken from `len(rows)` under both censuses. Filtering the
empty fibre removes *fibres*, not rows, so the collided ratio was divided by 1728 instead of by 603
and read **3.9% where the answer is 11.3%**. A denominator that does not move with its numerator is
the quietest way to publish a wrong ratio, and the regression is in the suite.

`does_not_show`: coarseness over the whole camera state space — the lattice is finite and regular,
and its limits are visible in its own result. Coarseness under any distribution of real camera
motion. Whether a collision corresponds to semantically equivalent *views* — two cameras that both
see one flat face at the same distance produce the same bytes, and whether that ought to count as
the same observation is a question this census does not answer and does not need to. And nothing
about reductions: no culling, no meshing, only the reference's own observable.

## Act

`voxcoarse-census` holds the fibre structure and its decomposition, `voxcoarse-binding` the record's
tie to the live renderer, `voxcoarse-selftest` the plants. The falsifier naming this brief: flip one
digest in the record and the re-render binding reddens — the census is a claim about what *this*
renderer does, and a table nobody re-renders is a table about nothing.
