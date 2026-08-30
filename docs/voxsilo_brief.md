<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxsilo-lattice -->

# `voxsilo` (URDRVXH1) — design brief

*Three silos, eight cells, and the full combination is not the best one. Siloing is normally an
organisational failure mode; the inversion works because the lateral contract is mechanical.*

## Observe

Phil Ensor named the functional silo syndrome in 1988: tall vertical structures with strong downward
communication and weak lateral feedback, where each function optimises locally because the only
channel between them runs through management authority rather than through anything measurable. The
pathology is not the separation. It is the *missing contract* across it.

So separate the renderer into optimisation silos deliberately, and replace the missing lateral
contract with one no silo can negotiate:

> The observable is byte-identical. Colour and depth, as lists, on every declared frame, in every one
> of the eight cells. A silo may change its implementation and may not change what is seen.

| arm | the one question it may answer |
|---|---|
| **G** | can a whole primitive be retired without examining any of its pixels? |
| **T** | can a whole tile be retired without examining any of its pixels? |
| **A** | can the same per-pixel answer be computed with fewer multiplies? |

## Orient

**The contract caught an unsound optimisation on its first run, and that is the first result.**

Every hierarchical-Z scheme rests on one premise: interpolated depth is a convex combination of the
vertex depths, so a triangle's nearest point is the nearest of its vertices, so a triangle whose
nearest vertex sits behind everything already in its box cannot win anywhere and may be dropped
untested. That premise is **false for this rasteriser**:

| | |
|---|---|
| covered pixels | 245183 |
| pixels where `d` < min vertex depth | 215300 (87%) |
| worst shortfall | 5129 — `zmin` 7783 → `d` 2654 |

The mechanism is the top-left fill rule. The interior test is `e + bias >= 0`, so the biased weights
sum to `area + B` with `B ∈ −3..0` — and the depth still divides by `area`. The interpolation is
scaled by `(area+B)/area` and is not a convex combination at all. On a large triangle that is a
rounding-level effect; on the witness, an area-3 sliver with `B = −2`, it is a factor of one third.

The repair is one line of algebra rather than a fudge factor: with every weight non-negative the sum
is at least `zmin·(area+B)`, giving `zmin + (zmin·B)//area`, checked against every covered pixel of
every walked triangle on every frame. The naive cull stays **runnable** as a plant that must still
move the observable, because a refutation that cannot be executed stops being evidence the day
someone edits around it.

**And the lattice says the obvious optimisation is the one that does not pay.** Reported as a panel
and never fused into one number, because a divide is not a multiply is not a compare and a sum would
invent a cost model nobody declared:

| cell | walked | covered | written | multiplies |
|---|---|---|---|---|
| — | 664553 | 245183 | 65893 | 6633411 |
| T | 569963 | 245183 | 65893 | 6493935 |
| G | 267485 | 98428 | 51712 | 3810738 |
| GT | 225384 | 98428 | 51712 | 3728136 |
| A | 664553 | 245183 | 65893 | 3139347 |
| TA | 569963 | 245183 | 65893 | 3810225 |
| **GA** | 267485 | 98428 | 51712 | **2396172** |
| GTA | 225384 | 98428 | 51712 | 2665590 |

`GA` is cheapest and `GTA` is dearer. Adding T to GA retires 42101 walked pixels and spends 269418
extra multiplies doing it — six and a half multiplies per pixel retired, at a moment when arm A has
already made a walked pixel cost *zero* multiplies. T is destructive in both places it occurs, which
is why both are asserted rather than one.

**The verdict is not that the tile test does not work.** It retires exactly what it claims to; the
*exchange rate* fails. And the mechanism is geometry rather than the test, on a number taken from the
ruler rather than from this rung's own arithmetic: 664553 walked pixels across 11867 walked triangles
is a mean bounding box of **56 against a tile of 64**. The average triangle is smaller than one tile,
so the per-tile setup amortises over almost nothing. This is a verdict about 56-pixel triangles.

Orthogonality on multiplies saved, as exact fractions — never decimals, because the quantity decides
whether two silos are redundant or destructive and a rounded one would report its own rounding:

| pair | Ω | reading |
|---|---|---|
| G,T | 56874/139476 | 0.41 — real overlap, both retire work |
| G,A | 2079498/2822673 | 0.82 — highly redundant |
| **T,A** | **810354/139476** | **5.81 — above one: not redundancy, subtraction** |

## Decide

**This rung makes no prediction claim, and that is a law rather than a sentence.** `voxproj` and
`voxcam` pinned their predictions as data before their arms ran and were entitled to score them. The
arms here ran first, so pinning a prediction now would be back-dating one — the L64 class exactly.
`the_rung_makes_no_prediction_claim` asserts this module declares no `PREDICTION`, so a later edit
cannot quietly add one and inherit a discipline this rung did not pay for. The next rung re-earns it.

`does_not_show`: nothing about time — no wall clock enters this rung, the rule `voxwork` made
structural and this rung is the first to inherit. Nothing about memory traffic, cache behaviour or
SIMD, which is precisely where a multiply count stops predicting a duration and this rung has no
instrument for any of them. **That GA is the fastest arrangement** — it is the cheapest in multiplies
on this trace at this resolution with this geometry. And no promotion: `voxref` is untouched and not
one of the eight cells is adopted.

## Act

`voxsilo-contract` holds the byte-identity of all eight cells and the unsoundness plant,
`voxsilo-premise` the convex-combination census and the corrected bound, `voxsilo-lattice` the panel,
the exchange rate and the orthogonality fractions, `voxsilo-selftest` the record plants.

The empty cell is bound to `voxwork`'s floor on five columns, so the lattice is measured against the
committed ruler rather than against a baseline this rung invented for itself — which is the whole
reason the ruler shipped a rung early.

The falsifier naming this brief: `voxsilo-lattice` reddens on the day stacking everything starts
winning. A rung whose headline is *the full combination loses* needs the law that takes that headline
away.
