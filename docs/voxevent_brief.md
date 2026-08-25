<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxevent-ladder -->

# `voxevent` (URDRVXE1) — design brief

*Does the visible surface grow with the geometry, or with the incidences? And what does it cost to
ask the question with a fixed number of rays?*

## Observe

A rasteriser's cost scales with primitives. The thing a camera can observe does not. The visible
surface is a lower envelope, and Sharir's 1994 bound puts the complexity of the lower envelope of
*n* surface patches in three dimensions at O(n^(2+ε)); the arrangement of viewpoints above it is
degree six or worse, tight at Θ(n⁴k²) orthographic and Θ(n⁶k³) perspective for *k* convex polyhedra
of total complexity *n* (Aronov, Brönnimann, Halperin and Schiffenbauer, 2001). A world of 803 solid
voxels is exactly *k* convex polyhedra, so that ceiling is not an object anyone enumerates — which
is the real reason `voxcoarse` sampled the viewpoint space rather than constructing it.

The gap between those two exponents is the only compression axis worth building an architecture on,
and nothing in this tree had measured where a real scene sits inside it.

Two constraints shaped where the measurement could be taken. The first is that `voxmicro` left 2040
pixels the reference still awards to faces no exterior camera can see, so a compression law derived
from the rasteriser today would be a compression law about a wrong answer. The second is that the
empirical half of this question is not new: Zhang, Everett, Lazard, Weibel and Whitesides measured
the 3D visibility skeleton in 2008 and found roughly C·k·√(nk) against a proven tight worst case of
Θ(n²k²) — sparsity in practice, documented, with the note that worst cases "rarely occur." They
used random and structured scenes. Nobody built the degenerate case on purpose.

## Orient

Everything here reads `voxray.first_hit`, which is audited, qualified against twenty-four elementary
scenes, and takes its occupancy and its lattice as parameters. No renderer runs in this module at
all, so every figure is a property of the world and the camera.

The instrument is a **subdivision ladder**. Splitting every solid cell into s³ cells of the same
material multiplies primitives by s³ and moves not one world point: the solid region is the same
set, so a ray's first entry into it is the same entry, at the same parameter, through the same face,
reported by a cell that must be a subcell of the coarse one. That is asserted across all four scales
before any number is read from them, because without it the four arms would be four different scenes
wearing one name. It has a trap in it worth writing down: `first_hit` returns an *unreduced* rational
whose representation depends on the cell size, so two equal parameters compare unequal as tuples.
The first version of the probe was wrong in exactly that way, and every comparison here is by cross
multiplication.

The quantity that should be invariant is not the visible face count — a face splits into subfaces —
but the **merged region count**: maximal connected coplanar same-material regions of the visible
surface. That relation is greedy meshing's own, and this module computes it only to count it.
Letting the merged representation become the thing rendered is the reduction redefining the
observable, which is the circularity `voxref` was frozen to prevent. The relation is defined on the
visible set alone and is given no knowledge of the subdivision, so it cannot be accused of finding
the structure it was handed.

## Decide

Seven predictions, written before the ladder ran. Four held. Three did not, and the third is worth
more than the four that did.

**P5's wall camera clipped the wall it was predicting about.** A 4×4 wall at that distance subtended
96 pixels of a 72-pixel-high frame, so a whole row of faces never entered the visible set and five of
the twenty-five corners went with them. The count is a claim about a wall the camera can *see*, so
the scene now carries that precondition explicitly instead of the prediction being relaxed to
whatever the clipped view produced.

**P7 asserted the wrong thing entirely.** The oracle's traversal compares with a strict `<`, so when
a ray crosses two lattice planes at exactly one parameter it keeps the lowest axis index — a
convention `voxray` never declared. The law fired a tying ray into the frozen world and demanded an
x face. It got a y face, correctly: a tie decides which axis *steps*, not which face the eventual hit
reports, and a ray that ties at every step alternates until something stops it. Rebuilt so the tie
itself resolves the hit, the control turned out sharper than the law. Remove the winning candidate
and the ray does not report the loser — **it misses it entirely**, because the tie sent the traversal
down the other axis and out of the column. The convention decides which cell is *reached*, not which
label is printed, and 20.1% of the declared rays enter through an edge or a corner at the finest
scale. An undeclared rule with that blast radius is now a row.

**And P3 missed for a reason that changes what this rung is about.** Visible faces grew 22.4×, not
the predicted 30–70. The shortfall is not geometry. A frame has W·H rays and no more, so the number
of distinct faces any census can observe is capped by the ray budget however fine the lattice
becomes. The hit count is *identical* at every scale — 46685 across the eight frames, the same rays
finding the same solid — while the share of hits landing on a distinct face climbs from 1.7% to
37.9%. Past the first rung, this census is measuring the **sampler** as much as the scene.

That is `sealframe-cost-surface`'s defect arriving from the opposite direction. That rung found
every ns/pixel figure had been taken with scene complexity frozen, so "a 1080p frame" meant a 1080p
frame of four triangles. This one freezes resolution and varies complexity. Neither is a two-axis
measurement, and resolution cannot be raised here because W and H belong to a frozen contract.

So the claim is the **first** rung and not the last: eight times the primitives moves the merged
visible regions by three per cent, measured where the visible set still covers each face densely.
The 512× figure is reported and is not the claim.

`does_not_show`: anything about performance. Any *bound* — a growth rate measured on one scene family
says nothing about the family that was not built, which is the whole reason the degeneracy scenes
exist and the reason they are still a measurement rather than a theorem. Any certificate: counting
how few regions the visible surface has is not producing a witness that proves the rest invisible,
and that rung waits for the reference repair. And the second axis, which this rung does not have.

## Act

`voxevent-ladder` holds the subdivision census and the confound inside it, `voxevent-degeneracy` the
four families where a sparse representation goes dense — coincident corners along a run, four-face
fan-in on a coplanar wall, three concurrent edges at a corner-on cube, simultaneous crossings down a
lattice diagonal — `voxevent-ties` the convention `voxray` never named, and `voxevent-selftest` the
four plants. The falsifier naming this brief: break the subdivision map by one cell and
`voxevent-ladder` reddens, because a ladder that would accept any occupancy is not an instrument and
every growth rate read from it would be a number about nothing.
