<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxconv-census -->

# `voxconv` (URDRVXN1) — design brief

*`voxfill` wrote its own boundary. This is the debt paid, and the bill is nine tenths of the
population.*

## Observe

`voxfill` found that the reference's projection *floors* — mapping a screen position into a pixel
*region* — while its sample point is that region's *corner*, and that the oracle inherited the
corner convention from the projection's algebra rather than from its rounding. It then said plainly
what it could not claim: every count in `voxtie`, `voxfate` and `voxfill` was measured with the
corner sample, so none of them speaks for the aligned convention.

So the population is derived again from scratch — render, oracle, classifier and fate all moved
together — and the two are put side by side:

|                     | corner | centre |
|---------------------|--------|--------|
| disagreeing pixels  | 1137   | 104    |
| stable              | 378    | 89     |
| boundary            | 198    | 5      |
| degenerate          | 561    | 10     |
| impossible faces    | 152    | 4      |

The corner column is required to land on `voxtie`'s classified census, `voxfate`'s conditioned fate
distribution *and* `voxfill`'s rejection classification — all three, exactly. A re-derivation that
cannot reproduce the numbers it re-derives is measuring something else, and that binding is the only
thing that licenses reading the centre column at all.

## Orient

**The class that collapses hardest is the one no experiment could have argued with.** `degenerate`
means the exact ray crosses two or three lattice planes at one parameter, where the *oracle itself*
answers by the convention `voxevent` named and no limit can appeal past it. It is the class that
excused 561 disagreements from ever being called defects. It falls to 10.

Integer screen coordinates are precisely the rays that land on lattice-plane crossings. Offset the
sample by half a pixel and they almost all stop being degenerate. At this lattice the degeneracy is
not a property of the world; it is a property of *where the rays were aimed*.

**And the first version of this paragraph overstated it, green and pushed.** It said `voxevent`'s
20.1% edge-or-corner entry rate was a fact about the sampling grid rather than the lattice, with no
scale attached — and the answer depends on the scale. `voxgrid` re-derived `voxevent`'s whole ladder:
the artefact share is 96% at the base lattice (1017 crossings become 40) and 50% at scale 8 (11119
become 5507), because subdividing by *s* multiplies the plane density by *s* and a half-pixel offset
that dodged the coarse planes cannot dodge the fine ones. The census here is at the base lattice,
where the collapse is nearly total. The sentence generalised past it.

**The coverage diagnosis survives, and that is the point of asking.** Of the 89 surviving stable
disagreements: `not_covered` 74, `depth_rejected` 12, `phantom` 3. That is 83.1% coverage against
`voxfate`'s 84.1% on a population thirteen times larger. The population collapses and the *share*
does not move — which is what a real mechanism does and what an artefact does not. The law compares
the two shares by integer cross-multiplication, so no percentage is invented for it.

**And the ownership class vanishes entirely: `bias_only` 215 → 0.** `voxfill` refuted the top-left
hypothesis by re-scoring one arm under the aligned pairing. This rung refutes it a second time by a
completely different route — re-deriving the population from scratch and finding that the class that
arm was built to explain no longer exists. The 215 pixels were the corner sample landing on a
projected edge. The top-left rule is exonerated twice, independently.

## Decide

**What survives is one mechanism, and no arm has tested it.** Every surviving `not_covered` pixel is
`outside`, and every one of them by less than a pixel. `bias_only` and `bbox` are both empty. That
is the floored projected vertex and nothing else — a quantisation defect in the **projection**,
not a rule in the **fill**, which is a different place to look than any of `voxfill`'s three arms.

**And the impossible population is now too small to carry a claim.** Four pixels, of which three are
`depth_rejected` and one `not_covered` — an inversion of the corner reading's 78 and 2. Four is not
a distribution. `the_impossible_population_is_too_small_to_read` states that refusal *as a law*
rather than leaving it to judgement, and reddens if the population ever grows past the point where
the refusal was honest. A rung that had read a depth mechanism off four pixels would have been doing
exactly what `voxfate` was built to stop.

`does_not_show`: anything about performance. **Which convention is right** — this rung measures what
each implies and decides nothing, because adopting one changes what the *oracle* is and reaches
every record derived from `voxray`. That the centre convention is clean: it has 104 disagreements
and 4 impossible faces, which is better and is not zero. Any mechanism for the surviving 74. And
nothing is repaired — `voxref` and `voxray` are both untouched, and the frozen census stays frozen.

## Act

`voxconv-binding` holds the three-way reproduction and the transcription chain, `voxconv-census` the
two derivations, `voxconv-residue` the surviving mechanism and the stated refusal, `voxconv-selftest`
the seven plants.

The instrument is a **fifth** transcription of the same rasteriser loop, bound in both directions: at
zero offset its winner, stages *and* covered sets must equal `voxfate.instrument_level`'s, and at
either offset its winner must equal `voxfill.render_arm`'s. A chain this long is exactly how a rung
ends up measuring a renderer nobody declared, so it is checked rather than trusted. The two offsets
are the same half-pixel expressed in two denominators — the ladder carries vertices at 1/64 of a
pixel, the limit test perturbs at 1/1024 — and are never converted between them.

The falsifier naming this brief: the corner arm must reproduce three committed rungs exactly. If it
drifts, `voxconv-census` reddens and the centre column means nothing — which is the correct outcome,
because a comparison is only as good as the half of it you can already check.
