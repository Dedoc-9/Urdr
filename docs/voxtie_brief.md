<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxtie-census -->

# `voxtie` (URDRVXT1) — design brief

*A rung built to justify a carve-out, which measured the thing and refused it.*

## Observe

`voxcand` left 661 impossible pixels. Two further candidate fixes take that to 152, and on one
two-cell scene thirteen survive. Thirteen pixels on a scene containing two voxels is a very
inviting number. The obvious move is to declare them a permanent geometric degeneracy, write a
contract clause saying visibility is unique off the degeneracy set and resolved by a deterministic
ownership convention on it, and let the visibility fact go green with a carve-out.

The one-sided limit test says why that would have been wrong.

Perturb the ray by a thousandth of a pixel either side of the exact sample, in both screen
directions, and ask the oracle. At **one** of the thirteen the answer never changes: same face at
minus epsilon, at the exact sample, at plus epsilon, in x and in y, and under all six single-axis
camera perturbations. There is no ambiguity to appeal to there. The rasteriser awards that pixel to
a face sandwiched between two solid cells anyway, because `(depth, face_key)` picks key 4710 over
5576. **That is a bug**, and a carve-out written on the count would have buried it.

## Orient

So the residual is classified rather than tallied, into three classes with a declared priority.

**Degenerate** — the exact ray enters through an edge or a corner, two or three lattice planes
crossed at one parameter, so the *oracle itself* is resolving by the convention `voxevent` named.
Geometric uniqueness is not available and no limit can appeal past it.

**Boundary** — a clean single-plane entry, but the answer differs across the sample. The pixel lies
on a visibility event surface and the two programs land on opposite sides of it.

**Stable** — the oracle gives the same answer everywhere around the sample. A disagreement here is a
defect.

Two perturbations, because they answer different questions. Moving the *screen sample* tells you
which side of a projected edge an integer pixel falls on. Moving the *camera* tells you whether the
viewpoint sits on a boundary in viewpoint space, which is what an aspect-cell or propagation census
would care about. A pixel can be on a projected edge without the viewpoint being anywhere near a
visibility-cell wall, and conflating the two would put a screen-space artefact into a viewpoint-space
census.

The one-sided sequence is recorded per pixel rather than summarised, because `A→B→B`, `A→B→C` and
`A→B→A` are three different situations and only the third would indict the oracle. Across the whole
classified population the only patterns that occur are `AAA`, `AAB` and `ABB`. **No `ABA` anywhere**
— the exact value always equals one of the two sides. The oracle is a function with no isolated
answers, and it is not uniformly right-continuous either; it takes whichever side the exact ray
falls on, which is what a well-defined function does at a discontinuity.

## Decide

Over the declared trace, 1137 disagreeing pixels classify as **378 stable, 198 boundary, 561
degenerate**. Among the 152 impossible-face pixels: **80 stable, 71 degenerate, 1 boundary**.

The carve-out is refused. Stable disagreements outnumber event-surface ones outright, and among the
impossible-face pixels they outnumber them eighty to one. The two-cell scene was misleading exactly
because it was two cells.

That law was first written with a threshold, and the data missed it by three pixels. The claim was
"a third of the disagreements are stable"; 378 of 1137 is 33.25%, so `stable * 3 > total` reads 1134
against 1137 and reddens. A fraction chosen because it sounded like the answer is a law fitted to a
hope. The repair was to delete the fraction rather than move it — what the measurement supports is a
comparison between two classes, which needs no number invented for it.

**Two more defects are isolated by the ladder, and neither is applied.** The projection's axes round
in opposite directions: `voxref` computes `cy - (cu*F)//cf`, negating *after* the floor, so screen Y
rounds toward +∞ where X rounds toward −∞. That is also the mechanism behind the `(-1,+1)`, `(0,+1)`,
`(-1,0)` bias `voxray` measured in its round-trip profile three rungs ago and could not explain. And
the projected vertex is quantised to whole pixels; carrying it at 1/64 closes the `aperture` scene
entirely while 1/256 buys nothing further, so the floor is measured rather than assumed.

**Four tie orderings are measured and none is adopted**, and the useful output is not a ranking but
a ceiling. The oracle's answer is among the tied candidates at exactly **one** of the thirteen
exact-depth ties, so no tie rule can score above 1/13 however cleverly it orders them — everywhere
else the correct face is not competing at that pixel at all and the disagreement is about coverage.
The committed `(depth, face_key)` scores **zero**; the geometric-ray-parameter and normal-opposition
orderings both reach the ceiling. So the committed rule is arbitrary *and* worse than available,
which turns "change the tiebreak" into a bounded proposal rather than an open-ended hope. Every
candidate preserves draw-order independence, checked by reversing the candidate list, because that
is the property the committed rule was built for and no replacement may cost it.

`does_not_show`: anything about performance. That any tie rule is correct — the geometric-parameter
ordering computes a ray/plane intersection inside the rasteriser, which makes it partly a ray tracer
and is exactly the kind of choice that needs deciding rather than defaulting. That the classification
generalises past the declared trace and the tie scenes. And it promotes nothing: `voxref` is
untouched as in `voxcand`, and the frozen census stays frozen.

## Act

`voxtie-census` holds the classified population, `voxtie-ladder` the four single-variable levels,
`voxtie-ties` the exact-depth population and the resolvable ceiling, `voxtie-selftest` the four
plants. The population digest is pinned rather than the count, because two different sets of 1137
pixels would tally the same and digest differently.

The falsifier naming this brief: a classifier that sorted every disagreement into `boundary` would
manufacture exactly the conclusion this rung was built to test, so at least one stable disagreement
must be found — and `voxtie-census` reddens if none is.
