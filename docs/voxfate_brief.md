<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxfate-conditioned -->

# `voxfate` (URDRVXS1) — design brief

*Condition the population, then ask what broke it. The other order has been wrong for four rungs.*

## Observe

`voxmicro` answered the fate question three rungs ago and the answer was a spread: some pixels lost
to coverage, some to depth, some to a sub-pixel sampling offset, some to nothing nameable. A spread
is not a mechanism. It is what a mechanism looks like when it has been averaged with two other
mechanisms.

Because that is what the population was. `voxmicro` classified the *whole* residual, and the whole
residual is three unrelated things stacked: pixels where the rasteriser is wrong, pixels sitting on
a visibility event surface where two correct programs may legitimately land on opposite sides, and
pixels whose ray enters a lattice cell through an edge or a corner, where the *oracle itself* is
answering by the convention `voxevent` named rather than by geometry. Asking "what broke these" of
that mixture asks what broke an average.

`voxtie` separated them. 1137 disagreeing pixels: 378 stable, 198 boundary, 561 degenerate. Stable
means the oracle gives the same answer at the exact sample, at a thousandth of a pixel either side
in both screen directions, and under six single-axis camera perturbations. Those are the pixels
where a disagreement admits no appeal to ambiguity — a defect there is a defect.

## Orient

So the fate question is asked of those 378 and of nothing else, and the answer does not split:

    not_covered      318   84.1%     the oracle's face WAS rasterised and did not claim the pixel
    depth_rejected    58   15.3%     it claimed the pixel and lost the depth test
    phantom            2    0.5%     the rasteriser drew where the oracle finds nothing

Of the 80 stable pixels awarding an *impossible* face — one sandwiched between two solid cells,
which needs no oracle to be called wrong — 78 are `not_covered`. The two populations that could
have disagreed do not.

The law asserts dominance as a measurement rather than as an assumption, because the interesting
outcome was the other one. Had the fates spread evenly the honest move would have been to preserve
the spread and say the reference has several independent defects, not to pick the largest bar and
call it the mechanism. `the_answer_does_not_split` reddens on a spread.

**`voxmicro`'s sampling branch is disabled here, and that is the whole methodological point.** That
branch tests first whether the rasteriser's answer at a pixel equals the oracle's answer at an
integer *neighbour*, and subtracts those as explained by the ≤1px offset measured two rungs ago. On
this population the subtraction is circular: these pixels are already known stable under sub-pixel
perturbation, so a neighbour agreeing is not evidence that sampling explains anything — it is the
question restated. The contamination is *demonstrated* rather than argued: the same classifier runs
over the same pixels with the branch enabled, 269 of the 378 are absorbed into `sampling_shift`,
and the coverage signal disappears entirely. A claim that conditioning matters is worth nothing
without the unconditioned run pinned beside it, so both distributions are in the golden.

**And the two facts together say something neither says alone.** Sub-pixel stable, yet the
rasteriser's answer equals the oracle's answer one whole pixel over at 269 of 378. That is not a
sub-pixel ambiguity being resolved differently. It is a whole-pixel coverage displacement: the fill
rule is claiming pixels for a face that the ray through the integer coordinate does not meet.

## Decide

The surviving defect is **coverage**. Not depth ordering, which `voxcand`'s winding fix already
addressed and which accounts for 58 pixels here. Not the projection, whose axis asymmetry and vertex
quantisation `voxtie` isolated and closed. Not the tie convention, whose ceiling `voxtie` measured
at 1/13. The next experiment lives entirely inside the fill rule.

**And the minimal counterexample is the pixel this whole arc started from.** Six rungs ago a
face-culling experiment disagreed with the reference at frame 4, pixel (10, 0), and tracing it
produced an unculled winner of voxel (2,1,10)'s *interior* top face beating voxel (2,1,11)'s own
exposed face — impossible rather than merely surprising, and the reason an oracle had to exist at
all. `voxray` then found the oracle names a third answer there, voxel (2,0,10), which neither arm
had. That pixel is now the first instance of the dominant class: the oracle's face is generated, is
front-facing, is on screen, reaches the pixel loop, and does not claim the pixel. The investigation
returns to where it began with the mechanism named.

`does_not_show`: anything about performance. **Why** the coverage displaces — this rung localises
the class and does not explain it. The candidates are the half-open top-left convention, the
bounding-box derivation, and the sample point the fill rule effectively uses; choosing between them
is a binary experiment and is deliberately not attempted here, because a rung that localised *and*
explained in one step would have no falsifiable middle. That the split generalises past the declared
trace. And nothing is repaired: `voxref` is untouched as in `voxcand` and `voxtie`, and the frozen
census stays frozen.

## Act

`voxfate-conditioned` holds the conditioned population and both distributions, `voxfate-counterexample`
the pixel and the state of the oracle's own face at it, `voxfate-cache` the census materialisation
that makes conditioning affordable, `voxfate-selftest` the four plants.

The instrument is a **third** transcription of the same rasteriser loop, and is required to
reproduce `voxtie`'s ladder winner on every declared frame — otherwise a chain of transcriptions is
exactly how a rung ends up measuring a fourth renderer nobody declared.

The falsifier naming this brief: the conditioned population must be a strict subset of the residual
and exactly the rows `voxtie` calls stable, so a drifted conditioning reddens rather than quietly
re-answering a different question — and `voxfate-conditioned` reddens if it is not.
