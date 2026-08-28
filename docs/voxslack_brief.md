<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxslack-depth -->

# `voxslack` (URDRVXK1) — design brief

*Diagnostic only. How far is each wrong pixel from the law that decided it — and one of the three
residual populations turns out to have been filed under the wrong mechanism.*

## Observe

`voxfate` split the 378 stable disagreements into 318 `not_covered`, 58 `depth_rejected` and 2
`phantom`, and every rung since has treated those as three mechanisms. This rung asks a question
none of them asked: for each pixel, how far *inside or outside* each of the rasteriser's own
decision surfaces does the oracle's face sit?

A wrong decision taken **on** a decision surface is a margin defect and a threshold change can
honestly address it. A wrong decision taken far from every surface is not, and no threshold change
can. The distinction is only visible if the distances are measured.

The sign convention is declared, not inferred: positive means the predicate is satisfied with that
much room, zero means the sample lies exactly on the surface, negative means it failed by that much.
Every slack is an exact integer in the units the reference itself computes in — edge function for
coverage, camera Q8 for depth. A pixel that never reached a surface records nothing, not a zero: a
zero would be a decision the reference never made.

    318 not_covered    coverage slack    -1 exactly            215
                                         within one pixel      103
                                         beyond                  0

     58 depth_rejected  depth slack      exact tie               2
                                         under one cell          8
                                         a whole cell or more   46
                                         should have won         0

      2 phantom         the oracle returns nothing at all

## Orient

**Every coverage miss is within one pixel of the surface. Not one is beyond it.** 215 fail by
exactly −1, which is the top-left bias and nothing else — the sample sits precisely on the edge. The
other 103 fail by a real but sub-pixel amount: the floored projected vertex. The split is between
two *mechanisms*, not two distances, and it maps onto `voxconv` exactly — under the aligned
convention the 215 vanish and a sub-pixel remainder survives.

**The first version of this law demanded a `beyond` class and reddened.** The probe behind it
bucketed on the raw edge-function magnitude and reported 95 pixels beyond a pixel. The edge function
is an *area*, not a distance; dividing by the edge length puts every one of them inside a pixel. The
law refused to be satisfied by a structure that was not there — **before the claim was written
down**. That is the first time in this arc the refusal has landed on the near side of a commit
rather than the far side.

The zero is planted, because a zero is only evidence if the instrument could have produced a
non-zero: `beyond` is demonstrated on a synthetic triangle rather than trusted.

## Decide

**The 58 depth rejections are not a margin defect at all, and that redirects a whole branch.** Had
they sat near zero slack, the depth comparison would be a rounding boundary worth attacking. They do
not: 46 of 58 lose by a whole cell or more, the median is 1.27 cells, the maximum 6.06, only 2 are
exact ties, and **not one should have won**.

Meanwhile their *coverage* slack is hugely positive — median 13552, deep inside the triangle — so
they are nowhere near a coverage boundary either. Both surfaces are clear. **The depth comparison is
doing its job**: the oracle's face really is farther away, and it loses honestly.

So what is wrong at those 58 is that a **nearer face covers the pixel at all**. They are the same
coverage defect seen from the winner's side rather than the loser's. `voxfate`'s decomposition —
318 coverage, 58 depth, 2 anomaly — is really **376 coverage and 2 anomaly**, with the 58 counted at
the wrong end. A rung that had read `depth_rejected` as a depth problem would have gone looking for
a defect in a comparison that is behaving correctly.

`does_not_show`: anything about performance. **Which** face wrongly covers those 58 — this rung
measures the loser's distance to every surface and does not chase the winner, because that is a
different experiment and combining them is how a diagnosis stops being one. Any mechanism for the
sub-pixel 103. Any reading of the 2 phantoms, refused as a law rather than left to judgement. And
nothing is altered: no arm, no candidate, no convention moved, no renderer changed; `voxref` and
`voxray` are untouched and the frozen census stays frozen.

## Act

`voxslack-coverage` holds the coverage slacks and the two-mechanism split, `voxslack-depth` the
finding that redirects, `voxslack-refusals` the phantoms and the untouched reference,
`voxslack-selftest` the eight plants.

The instrument is a **sixth** transcription of the same loop, kept because this rung needs the depth
buffer that `voxfate`'s does not return — and pinned to it three ways at once: winner, stages and
covered sets must all match on every declared frame.

The falsifier naming this brief: `the_depth_rejections_are_not_a_margin` asserts that most of them
lose by a whole cell or more. If the depth slacks had clustered near zero the law would redden and
the branch would stay a depth problem — which is the outcome this rung was built to be able to
report, and did not find.
