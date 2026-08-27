<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxfill-conventions -->

# `voxfill` (URDRVXL1) — design brief

*Three mechanisms went in. The answer was a fourth thing that was not on the list, and the arm with
the most evidence behind it turned out to be the artefact.*

## Observe

`voxfate` left the defect named but not explained: 318 of the 378 stable disagreements are
`not_covered` — the oracle's face was generated, front-facing, on screen, reached the pixel loop,
and did not claim the pixel. Three mechanisms inside a fill rule can do that, and each is varied
alone: drop the top-left bias (edge ownership), pad the candidate box (which pixels enter the loop),
move the sample point (where the rule reads the triangle).

Before any arm runs, every rejection is classified by reading the three edge functions of the
oracle's own face at the exact sample:

    bias_only   215   every rejecting edge has e == 0 — the sample sits exactly on the edge
    outside     100   some rejecting edge has e < 0 — genuinely outside the triangle
    bbox          3   never entered the candidate loop at all

That classification predicts the arms rather than summarising them, which is the difference between
an experiment and a sweep.

The 100 `outside` are outside by almost nothing: 99 fall short by less than one pixel, typically by
a single sub-pixel unit at S=64 — the quantum of the floor in the projection itself. The distance is
compared as an exact integer by squaring, `e² < S²(dx² + dy²)`, taking no square root and
constructing no float, because a measurement that rounds cannot be evidence about a defect one
sub-pixel unit wide.

## Orient

**The bounding box is eliminated, and by a stronger statement than the one first written.** The law
began as "the `bbox` class is empty, so padding can rescue nothing" — and the data refused it at
three pixels. All three sit exactly one pixel right of the box; padding admits all three; all three
still fail the edge test. So the box is not merely tight, it is a conservative superset of the
pixels the edges accept, and `wide_bbox` moves not one pixel anywhere on screen. The repair was to
measure what the padding actually admitted rather than to shrink the claim: without that check,
"the arm changed nothing" would have been green whether the padding reached those pixels or not.

**The ownership arm looks like the answer and its ledger says otherwise.** `inclusive` rescues 204
of the 318 and drops impossible faces from 152 to 59. Net agreement is +58 — from +396 gained
against 338 lost, and 236 of those losses are pixels that become exact-depth ties, because dropping
the bias turns the partition into a cover and hands them to the `(depth, face_key)` rule `voxtie`
measured at zero of its own resolvable ceiling. Gained and lost are reported separately and never
netted; a rung reporting only the rescue would be reporting the half of the ledger it chose. The
combined arm is deliberately not run, because a two-variable change explains nothing.

One belief is corrected along the way. Draw order stays unobservable under every arm, including the
one that abolishes the partition — because the `(depth, face_key)` tiebreak already deletes draw
order on a written datum. The top-left rule was introduced to stop draw order reaching the screen;
it is not what stops it.

## Decide

**The deciding experiment varies the oracle's convention too, which no earlier rung of this arc has
done.** The oracle's ray through pixel (px, py) is *derived* from the rasteriser's own projection,
so a convention error is invisible to any experiment that holds one side fixed — and every rung so
far has held the oracle fixed and asked what the rasteriser got wrong.

|                    | corner-ray oracle | centre-ray oracle |
|--------------------|-------------------|-------------------|
| **corner sample**  | 45550             | 41861             |
| **centre sample**  | 42744             | **46567**         |

Both consistent pairings beat both mixed ones. That is the shape of a convention error, not of a
renderer defect: neither side is wrong alone. The reference's projection *floors* — it maps a screen
position into a pixel *region* — while its sample point is that region's *corner*, and the oracle
inherited the corner convention from the projection's algebra rather than from its rounding. The
two are inconsistent by half a pixel.

**The strongest number here needs no oracle at all.** `impossible` counts pixels awarded to a face
sandwiched between two solid cells; it is a property of the rasteriser alone, and no convention
choice can argue with it. It falls **152 → 4 on the sample point alone**.

**And that refutes this rung's own leading hypothesis.** Re-run `inclusive` with the conventions
aligned and it is *worse*: 46560 against 46567, impossible 7 against 4. The same single change,
opposite sign. The 215 `bias_only` pixels were an artefact of sampling a floored triangle at its
corner, not evidence against the top-left rule — which is exonerated. The arm that won looked like
the weakest of the three when scored against the misaligned oracle, because it moves the whole
picture and the misaligned oracle counted that as 3739 losses.

`does_not_show`: anything about performance. That centre sampling is **correct** — it is better on
both metrics under the pairing that assumes it, and adopting it changes what the *oracle* is,
reaching every record derived from `voxray`; that is a contract decision of exactly the kind
`voxtie` refused to take by default. That the coverage diagnosis survives the convention change: the
population itself was selected under the corner convention, so re-deriving it under the centre
convention is the next rung and is not claimed here. Why the one remaining whole-pixel `outside`
rejection survives. And nothing is repaired — `voxref` **and** `voxray` are both untouched, and the
frozen census stays frozen.

## Act

`voxfill-rejections` holds the algebraic classification and the bbox elimination,
`voxfill-arms` the four arms with the two-sided ledger and the tie decomposition,
`voxfill-conventions` the 2×2 and the control that refutes the headline, `voxfill-selftest` the six
plants. The instrument is a **fourth** transcription of the same rasteriser loop and its control arm
is required to reproduce `voxtie`'s ladder winner on every declared frame.

The falsifier naming this brief: `the_ownership_rescue_is_an_artefact` requires the same single
change to *gain* under one convention and *lose* under the other. A rung that had simply adopted the
largest class would redden there — which is precisely what this rung was about to do.
