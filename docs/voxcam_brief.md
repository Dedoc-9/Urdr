<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxcam-win -->

# `voxcam` (URDRVXB1) — design brief

*The candidate that works. It is still not the reference, and the distance between those two
sentences is the whole of this rung.*

## Observe

`voxsample` found the seam and refused to touch it. `voxref._project` turns the Q16 basis multiply
into an integer camera coordinate with a single `>> 16`, before any screen quantisation and before
the fill rule, and that shift pushes 91 pixels out of a face that geometrically contains them while
pulling 53 into one that does not. Naming a term is not fixing it, so that rung named it and stopped.

This rung moves the one variable. `control` is the committed coordinate — the shift, exactly as
`_project` performs it, asserted against that function rather than against a re-typed copy of its
body. `candidate` carries the multiply intact. Nothing else moves: the projection, the fill rule, the
depth comparison and the sample point are identical, because the ratio the projection forms is
scale-invariant.

There is one forced consequence, and it is the same variable written down twice rather than a second
one. The near plane is a constant in camera units, so changing the unit forces re-expressing the
constant. That is proved rather than argued — `cf >> 16 < NEAR` and `cf < NEAR << 16` must agree for
every integer, checked across the sign, across the shift boundary and on both sides of the plane,
because a near test that admitted or rejected one extra primitive would have put a second change
inside a single-variable arm.

|                    | control | candidate |
|--------------------|---------|-----------|
| agreeing pixels    | 45550   | 45889     |
| impossible faces   | 152     | 70        |
| gained             | —       | 357       |
| lost               | —       | 18        |

## Orient

**It wins, and `voxproj` did not.** That is the comparison worth making, because the two rungs are
the same shape: one variable, five predictions pinned as data before a frame was rendered, every one
scored. The rounding-direction candidate gained 23 and lost 34 and was refused for it. This one
gains 357 against 18 — nearly twenty to one — and drops the oracle-free impossible count by more than
half. `the_candidate_wins_on_evidence` asserts that as the measurement and reddens on the day it
stops winning, which is the day the finding must be revisited rather than quietly kept.

**Four of five predictions hit.** The 215 on-surface misses close at 214; the 103 sub-pixel misses at
88; the 56 winner-side at 53. Those were the three `voxsample` predicted from the truncation's
measured direction, and they land.

**The miss is the interesting one, and it does not contradict `voxwin`.** C5 said the 2 exact ties
and 2 phantoms would not close. Both ties closed. But what closed is the *depth* tie, not the
geometry: `voxwin` established in exact world space, with no truncation anywhere, that the ray at
those two pixels genuinely passes through an edge shared by two faces, and that remains true and is
not disturbed here. The interpolated depths were exactly equal only *after* the shift; at full
precision they separate and resolve in the oracle's favour at both. So the pixels are a real
geometric degeneracy **and** the rasteriser's tie at them was manufactured by the truncation, and
only the second of those is repaired. `voxtie`'s parked question keeps its two pixels and loses its
exact-depth character. The phantoms did not close, exactly as predicted.

**A rung that wins is the one most tempted to lose its miss somewhere between the measurement and
the record.** `every_prediction_has_a_verdict` requires the verdict set to equal the declared set and
`the_record_carries_hits_and_misses` requires both to be non-empty, so C5 is carried into the
committed artifact beside the four that hit.

## Decide

**It is not adopted, and that is not timidity.** Establishing a repair and promoting one are
different acts — `voxcand`'s doctrine, and the reason that rung exists. Promotion would move `O_t` on
every frame and invalidate the frozen census, the 1728-state census and the subdivision ladder at
once. And it would do more than that: carrying full precision scales every interpolated depth by
2^16, so the **depth** half of the observable moves even at pixels whose colour does not. That is a
contract change, not a bug fix. Whether the reference can carry full precision at all under its
integer contract is a design question this rung does not answer.

**What survives is named rather than rounded.** One on-surface, 15 sub-pixel, 3 winner-side, the two
phantoms still open, and 18 pixels that agreed under the control and now do not. Twenty-one of the
original 378 and eighteen new ones. `the_survivors_are_named_not_rounded` requires both halves of
that ledger to be non-empty and carried, because a candidate reporting only what it fixed would be
reporting the half it chose. This arc has not characterised that residue and this rung does not
pretend to.

`does_not_show`: anything about performance — carrying full precision widens every camera coordinate
and no cost in time or space is measured here. **That the candidate is correct**, only that it is
closer on the declared trace. Any mechanism for the 18 losses or the 21 survivors. And nothing is
promoted: `voxref` and `voxray` are untouched and the frozen census stays frozen.

## Act

`voxcam-arm` holds the single-variable check and the control's binding to the committed renderer,
`voxcam-win` the two readings and the scored predictions, `voxcam-residue` the survivors and the
refusal to promote, `voxcam-selftest` the plants.

The instrument is the committed rasteriser loop with the camera coordinate's precision as its only
parameter, bound in the one direction that matters: at `control` its winner must equal
`voxtie.render_level`'s at BEST on every declared frame, or the candidate would be measured against
a stranger. The five populations are **inherited** — `voxslack` classifies the on-surface and
sub-pixel misses, `voxwin` the winner-side misses and the ties, `voxslack` the phantoms — rather than
restated here, so no population can quietly change shape to suit the arm scoring against it.

The falsifier naming this brief: `voxcam-win` reddens if the candidate stops gaining more than five
times what it loses, or stops halving the impossible count, or if any prediction loses its verdict.
A rung whose headline is a win needs the law that takes the win away.
