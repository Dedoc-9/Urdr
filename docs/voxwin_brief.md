<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxwin-ties -->

# `voxwin` (URDRVXW1) — design brief

*Chase the winner. The 58 split exactly, the two exceptions turn out to be a question parked three
rungs ago, and the decomposition closes.*

## Observe

`voxslack` measured the *loser's* distance to every decision surface and found the 58
`depth_rejected` pixels are not a depth defect: they lose by a whole cell at the median, none should
have won, and their coverage slack is hugely positive. It then named the open question in its own
`does_not_show` — **which** face wrongly covers them — because chasing the winner is a different
experiment and combining the two is how a diagnosis stops being one.

This rung is that experiment.

    56    the ray through the pixel does not meet the winner's face at all
     2    the ray meets both faces, at exactly equal depth

The ray/face test is exact integer arithmetic and nothing else. The face is axis-aligned, so its
plane is a single lattice coordinate; the parameter is a rational, and every comparison multiplies
through by the denominator with the inequality flipped when that denominator is negative. No float,
no epsilon — an epsilon here would be a threshold nobody declared deciding the question the rung
exists to answer. A ray parallel to the plane answers *neither*, because reporting it as a hit or a
miss would be the instrument inventing an answer.

And it is planted in every direction: a ray down the middle hits, one aimed away misses, one behind
the eye misses, one parallel answers neither. A test that said "miss" everywhere would produce this
rung's headline by inability rather than by measurement.

## Orient

**The 56 are the coverage defect seen from the other side.** The rasteriser awards the pixel to a
face the ray geometrically misses. And the winner is the *oracle's own answer one pixel over* at all
56 — the same whole-pixel signature `voxfate` measured at 269 of 378 and `voxfill` traced to the
floored projected vertex. Nothing new is wrong here; the same displacement is being counted from the
winner's end.

**The 2 are a genuine geometric tie, and they merge a parked question.** Both are on frame 6, both
have the oracle naming a cell's top face while the rasteriser names the `+y` face of the cell
directly below — adjacent cells sharing an edge, the ray passing exactly through it, both faces met
at the same parameter, `(depth, face_key)` deciding.

They are **precisely** the two `exact_tie` pixels `voxslack` found, and the law asserts **set
equality**, not a matching count. Two independently computed classifications — one reading the depth
buffer, one computing an exact ray/plane intersection — pick out the same two pixels. A count would
pass while naming different ones.

That is the configuration `voxtie` measured a 1-of-13 resolvable ceiling on and declined to adopt a
rule for. The parked tie question is now a population of two on the declared trace, not an
open-ended hope.

## Decide

The decomposition closes, and it is tighter than the one it replaces:

| class    | count | what it is                                              |
|----------|-------|---------------------------------------------------------|
| coverage | 374   | 318 the oracle's face not claiming the pixel, 56 a wrong face claiming it |
| tie      | 2     | a true edge crossing, decided by an arbitrary convention |
| phantom  | 2     | the oracle returns nothing at all                        |

against `voxfate`'s 318 / 58 / 2. One mechanism accounts for 374 of 378, and the rest is two named
populations of two.

`does_not_show`: anything about performance. **Any repair** — no arm, no candidate, no altered
renderer, no moved convention; this rung finishes a diagnosis and starts nothing. Any mechanism for
the 2 phantoms, which stays refused at the size `voxslack` refused it. **That the 374 are one defect
rather than one class** — `voxconv` already showed 215 of the 318 are the corner sample and the
remainder is the floored vertex, so `coverage` holds at least two mechanisms and this rung does not
pretend otherwise. And nothing is altered: `voxref` and `voxray` are untouched, and the frozen census
stays frozen.

## Act

`voxwin-winners` holds the ray/face verdicts and the whole-pixel signature, `voxwin-ties` the set
equality with `voxslack`'s exact ties, `voxwin-closure` the closed decomposition, `voxwin-selftest`
the five plants. The two ties are pinned **as pixels** rather than as a count, because a count would
not say which two.

The falsifier naming this brief: `the_exceptions_are_exactly_the_exact_ties` asserts set equality
between the pixels whose ray meets the winner and the pixels whose depth slack is zero. If the two
classifications agreed only in size, it reddens — which is the whole difference between a
correspondence and a coincidence.
