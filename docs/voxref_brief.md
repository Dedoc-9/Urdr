<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxref-partition -->

# `voxref` (URDRVXF1) — design brief

*Rung zero of the voxel arc: the observable, frozen before any reduction exists.*

## Observe

The castle arc ran `recompute → incremental → span`, and each rung had something external it had
to preserve: the framebuffer digest. That worked, and it worked by **luck**. The digest was
inherited from the demo's replay DNA, built for a completely different purpose, and it happened to
be independent of every optimisation that came later.

The failure mode when it is not luck is circular and quiet: optimise the representation, define the
observable around the optimised representation, then prove the optimised representation preserves
the observable. That proves almost nothing, and nothing in the proof looks wrong.

A voxel world makes the trap easy to fall into, because the obvious candidates for an observable —
visible faces, depth ordering, work counts — are all **outputs of the reductions** that are about to
be built. Face culling changes what "visible" means. Greedy meshing changes what a primitive is.
Span traversal changes the order pixels are touched.

## Orient

What survives the test is what is a pure function of *(world state, camera)* and of nothing about
how the picture was computed. That is the two buffers, and nothing else:

    O_t = (H_C(colorbuffer), H_Z(depthbuffer))

Both, because neither dominates. A face wrongly dropped behind a same-coloured neighbour leaves the
colour buffer byte-identical and moves the depth buffer — which is the exact shape of an occlusion
bug and exactly what a colour-only observable would call a pass. The module ships a **constructed**
witness for that, two quads of one colour subtending the same screen rectangle at different
distances, rather than asserting such a pair must exist. A **mirror** witness gives the reverse —
two quads at one distance in different colours — so neither digest is a function of the other.

Both are constructed, and that is a repair rather than a preference. The first version read the
property off the corpus: two declared frames happened to share a depth digest, and the brief cited
it as evidence. Then the module's MAGIC collided with `voxlat`'s, the tree's own `magicuniq` stage
caught it, the world seed string changed with the rename — and the coincidence evaporated. The
prose had been asserting a property of one hash, not a property of the observable.

Everything else — visible-face counts, work populations, the ratio of examined to observable — is
**instrumentation**. In the castle arc the census could serve as an independent second witness to
the v1.19 equality precisely *because* it was never part of the criterion. Folding it into `O_t`
would have destroyed that.

## Decide

Two structural decisions, and the second was not in the plan.

**Coverage is a top-left partition.** The castle tests `w >= 0` on all three edges, which is a
COVER: a pixel on a shared edge satisfies both triangles. The castle never noticed, because the
loser failed a strict depth test and both triangles carried the same colour. That is an accidental
assumption about castle geometry, and a voxel world — where differently-coloured faces meet at
seams — would have inherited it and paid. Biasing each edge that is neither top nor left by −1
turns the test into a partition: every pixel claimed exactly once, integer, one subtraction per
edge. The law ships with its control: the same sample without the bias double-claims 50 pixels, so
the check is a statement about the rule and not about a sample that happens to have no shared edges.

**And a partition alone would not have been enough.** It fixes pixels shared by *adjacent*
triangles and does nothing about two *distinct* faces that are geometrically **coincident** — of
which the naive reference has 1058 pairs, because every two adjacent solid voxels contribute two
faces in the same plane. Those tie at exactly equal depth, and a plain `<` hands the pixel to
whoever was drawn first. Draw order would still have been observable, through a door the top-left
rule does not close. So the depth test compares `(depth, face_key)`, where the key is the voxel's
own coordinates and face index — a property of the **world**, not of traversal. That is what makes
the third line of the contract true rather than aspirational, and the corpus is checked to *contain*
coincidences, because a world without them would pass the order law with the tiebreak never
consulted.

The trace is **designed, not recorded**: buried, floor-grazing, section seam, wall-flat, open air,
oblique, corner, edge-on. The castle's evidence is 43 checkpoints of a human walk and `armpair`'s
`does_not_show` says so; a reduction that is wrong only where the trace never goes passes forever.

`does_not_show`: anything about performance — this renderer draws every face of every solid voxel
including buried ones, and is slow on purpose. That the observable is fine *enough* — the census
reports its coarseness rather than certifying it. Anything about face culling, greedy meshing,
T-junctions or LOD seams: those are the first reduction's problem, and a meshing equivalence claim
holds only for properly tiled uniform-resolution coplanar regions, because a T-junction leaves a
pixel claimed by nobody and a partition renders that as a crack. Building any of it here would mean
validating a semantic foundation with the first optimisation that depends on it.

## Act

`voxref-contract` holds the frozen observable and its corpus, `voxref-partition` the coverage rule
against its cover control, `voxref-order` the draw-order irrelevance against a corpus proved to
contain the case. The falsifier naming this brief: drop the top-left bias and `voxref-partition`
reddens with double-claimed pixels — the rule is the claim, and the control is what makes the claim
mean something.
