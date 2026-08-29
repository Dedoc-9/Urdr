<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxsample-truncation -->

# `voxsample` (URDRVXA1) — design brief

*Are the rasteriser and the oracle talking about the same sample point? Not quite — and the real
seam turns out to be upstream of every rung this arc has run.*

## Observe

`voxproj` eliminated the rounding *direction* as the governing defect. The next question is not more
precision but whether the two programs are describing the same point at all. Three constructions,
compared exactly:

- **coverage** — the fill rule evaluates its edge functions at `(px·S, py·S)`: the screen point
  `(px, py)` and nothing else.
- **interpolation** — the depth barycentrics read the *same* three edge values, so the same point.
- **oracle** — `voxray.ray_for_pixel` inverts `(px, py)` through the camera basis.

**The answer is no, on three of the eight declared frames.** The integer camera basis is exactly
orthonormal on five of them and not on the other three: frames 4, 5 and 6 carry non-zero off-diagonal
dot products and three different row norms. So `ray_for_pixel` is an *approximate* inverse there, and
`voxray`'s docstring calls it a derivation by inversion without saying which frames that holds for.

The departure is bounded and now measured as an exact fraction rather than read off a float — the
quantity is smaller than a sub-pixel, and a float would be reporting its own rounding. Worst case:
under a quarter of one sub-pixel unit at S=64.

## Orient

But that is not the seam. Carry the Q16 basis multiply at **full precision** and project the faces
exactly:

    the oracle's face CONTAINS the sample at   316 of 318
    the winner's face EXCLUDES the sample at    56 of 56

The second agrees **pixel for pixel** with `voxwin`'s independent world-space ray/face test — two
exact computations, one in screen space and one in world space, reaching the same verdict on the
same pixels, asserted as set equality rather than a matching count. **The geometry is right.** The
projection is not lying about which face covers which pixel.

Now put back the one truncation `voxref._project` actually performs — the `>> 16` that turns the Q16
basis multiply into an integer camera coordinate, *before* any screen quantisation, *before* the fill
rule:

    the oracle's face:  316 inside  ->   10 inside, 215 ON THE EDGE, 93 OUTSIDE
    the winner's face:   56 outside ->   25 inside,  28 on the edge,  3 outside

**Ninety-one pixels are pushed out of a face that geometrically contains them, and fifty-three are
pulled into a face that does not, by a single shift.**

`voxcand` tested winding and weights. `voxfill` tested the fill rule. `voxconv` and `voxgrid` tested
the sample convention. `voxproj` tested the screen-space rounding direction. The camera-space
truncation was upstream of all of them.

## Decide

**And it explains the 215.** Under the truncation they land exactly *on* the edge — and they are
exactly the pixels `voxslack` measured at coverage slack −1, asserted as set equality against an
independently computed population.

The top-left convention is not creating that class. The truncation puts the sample precisely on the
edge and the convention then rejects it, which makes the convention the last step in a chain rather
than the cause — and vindicates `voxfill` and `voxconv` for exonerating it twice.

The prediction was written before the arm ran. Three of five hit:

| | | verdict | measured |
|---|---|---|---|
| **Q4** | the three constructions coincide exactly | **MISS** | 5 of 8 frames |
| **Q5a** | all 318 inside at full precision | **MISS** | 316 of 318 |
| **Q5b** | all 56 outside, set-equal to `voxwin` | **HIT** | 56 of 56 |
| **Q6** | the seam is the object, not the point | **HIT** | 91 out, 53 in |
| **Q7** | ties and phantoms quarantined | **HIT** | untouched |

`does_not_show`: anything about performance. **Any repair** — `_project` is untouched, no arm is run,
and naming a term is not fixing it. **Whether removing the truncation is affordable or even
coherent**: the reference is integer by contract and carrying full precision changes what the depth
buffer holds, so that is a design question and a separate rung. Any mechanism for the two exceptions
at full precision. And nothing is altered: the two ties and two phantoms stay quarantined, and the
frozen census stays frozen.

## Act

`voxsample-basis` holds the orthonormality audit and the exact round-trip bound,
`voxsample-geometry` the full-precision verdict and the set equality with `voxwin`,
`voxsample-truncation` the dominant term and the explanation of the 215, `voxsample-selftest` the
seven plants.

The falsifier naming this brief: `the_on_edge_class_is_made_by_the_truncation` asserts set equality
between the pixels the truncation puts exactly on an edge and `voxslack`'s slack −1 class. If the two
populations merely matched in size, it reddens — which is the difference between explaining a class
and finding a number that looks like it.
