<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxmicro-scenes -->

# `voxmicro` (URDRVXM1) — design brief

*Qualifying the oracle on geometry small enough to check by hand, and turning a residue into a
distribution of named failures.*

## Observe

The previous rung ended with a number and a warning attached to it. Correspondence between the
reference renderer and the geometric oracle was 17.4% as committed and 87.0% with the six face
windings reversed, and the brief was careful to call the remaining 13% an **upper bound** on the
reference's defect rather than a measurement of it. That caution was correct and it was also the
end of the road: an upper bound on a residue is not a diagnosis, and three unrelated things were
stacked inside this one.

There was a real defect, still unexplained after the winding hypothesis accounted for most of the
disagreement. There was the ~1px ray/sample offset that the projection-inversion law had measured
and pinned — 70.15% of pixel-rays return exactly and the rest land one pixel away — folded into
every comparison the module made. And there was one declared frame excluded outright, because with
the eye inside solid the oracle answers in a different semantic domain and comparing the two
produces a 0% agreement that means nothing.

Three things, one number. Nothing downstream can be built on that.

## Orient

The stack comes apart along three seams, and each of them is a different kind of object.

**The excluded frame is a semantics question, and it has a right answer for a reason that is not
about the renderer.** With the eye inside matter, `opaque` semantics return the containing voxel
with no entry face — for every pixel, at *t* = 0, regardless of direction. That property is the
disqualification, and it is now a law rather than a paragraph: an oracle whose output does not
depend on the ray carries no information about the camera, so on such a frame it cannot separate a
correct renderer from a broken one. `transparent` semantics treat the eye's **own cell** — that one
cell, not the connected run it belongs to — as free space, and the answer becomes the first face
bounding the free space the ray can actually reach. Direction-dependence returns, and a second law
shows the choice moves nothing anywhere else: wherever the eye is outside solid the two semantics
agree pixel for pixel, on every scene and every declared frame. The excluded frame comes back
without disturbing the seven that were already there.

It also happens to agree with what the reference does from inside matter, and **that agreement is
not the reason**. A semantics adopted because it matches the renderer under test is exactly the
circularity the arc exists to avoid; the argument above is about what an oracle has to be able to
do, and it would hold with no renderer in the tree at all.

**The sampling offset is a property of the comparison, so it is subtracted first and by name.** A
disagreement counts as `sampling_shift` when the rasteriser's answer at this pixel is the oracle's
answer at one of the eight neighbours — the 3×3 block minus its centre, which is exactly the bound
the inversion law measured and no wider, so the subtraction cannot quietly absorb a defect two
pixels away. It is an **upper** bound on what sampling can explain, because a genuinely wrong
winner may coincide with a neighbour's answer by luck. That direction matters: it makes every
other class a **lower** bound on real defect, which is the conservative way round.

**And one measurement owes the oracle nothing at all.** Call a face *interior* when the voxel
across its outward normal is also solid. Such a face is sandwiched between two solid cells, so from
any eye outside the solid set every ray reaching it has already passed through one of them. No
exterior camera can see an interior face — ever, at any resolution, under any sampling rule. A
rasteriser whose winning face at some pixel is an interior one is therefore wrong, full stop, and
the count of such pixels carries none of the caveats that weaken a correspondence figure: no
ray/sample offset can produce it, no oracle need be trusted for it, and it needs no exclusions.

## Decide

Four things get built, and the fourth was not in the plan.

**Elementary scenes with expectations written before they run.** Twenty-four of them, fifty-six
declared expectations: one voxel from each axis, two voxels sharing a face on each axis, a direct
occluder, coplanar neighbours, edge-on and corner-on, a thin wall, a one-voxel aperture with a
target behind it, the eye inside matter, the eye exactly on a cell plane, a zero-extent quad, an
empty world. Every answer is checkable from the cell list and the camera before anything executes.
Fifty-five held exactly as written. The fifty-sixth demanded that moving the ray **origin** by one
unit leave the picture unchanged, which is false under perspective and has nothing to do with the
boundary the scene was built to probe; it is restated as what the boundary question actually is —
floor division puts an eye on a plane in the higher cell, and the zero-length first step neither
invents a crossing nor swallows one — with a control on the other side, where one unit *does*
change the silhouette. Restated, not relaxed.

One of the scenes records a limitation rather than a result. `voxref.basis` refuses a forward
vector parallel to `+z` by construction, so **the two z faces are never seen head-on anywhere** —
not in the micro-scenes and not in the declared trace. A refusal is an answer, and it is better
carried as a scene than discovered later as a gap.

**A fate for every disagreeing pixel.** The reference's own loop, instrumented: was the face never
generated, near-clipped, degenerate, backfacing, off-screen, rasterised but not covering this
pixel, or covering it and beaten on depth? The ladder is declared, including its one arbitrary
step — `backface` above `degenerate`, because the reference rejects both in the single test
`area <= 0` and a negative area is the informative half. `unknown` must be zero, and the selftest
shows a removed branch landing there, so a zero means the classifier looked rather than that it
never asked. A third transcription of the same inner loop is a drift risk, so it is bound in both
directions against `voxray`'s winner pass and against the colours `voxref.render` actually paints.

**Labels become claims.** Each of the eight frame names carries one checkable assertion about the
world, evaluated every gate run. This is not tidiness. `voxray` found two labels describing a world
that no longer existed after the MAGIC rename reseeded occupancy, and renaming them would have
prevented exactly nothing — the proof is that a **third** was wrong too: `wall_flat`'s comment said
"from the adjacent air voxel" and the wall is three voxels away. A claim the gate evaluates catches
that one; a corrected comment does not. The control is that restoring an old name reddens the row.

The interior-face detector needed one correction, and it was found by reading the committed record
rather than by any law. Its exception was written on the wrong side: it excluded faces *belonging
to* the eye's own cell and counted faces *pointing at* it. From inside cell A with a solid
neighbour B, A's face towards B is seen from behind and never drawn, while B's face towards A is
exactly what the camera sees and is interior only because A is solid — which for that ray is
declared not to be. The wrong version reported a whole framebuffer of impossible pixels, 6912 of
them and every one legitimate, on the scene built to exercise precisely that exception. Corrected,
the same scene separates the two windings cleanly: 6912 impossible pixels as committed, where the
renderer draws A's own hidden face, and zero reversed.

**And what the corpus still does not contain is stated rather than left as an absence.** No
declared frame stands on anything: all eight have empty space or the lattice exterior directly
below them, so grazing incidence over a supported surface — the case a fill rule breaks first — is
covered only by `edge_on`, which floats one cell above the slab. Two micro-scenes derived from the
real world by a canonical scan, and pinned, supply the vantage. Moving the frozen trace is the
re-freeze rung's business and is not smuggled in here.

`does_not_show`: anything about performance. Any claim that the oracle is **right** — it is audited
by `voxray`'s invariants and qualified here against elementary cases, which is much weaker and much
more honest than correctness. Any claim that the reversed winding is the correct repair: it is
measured to be closer and still wrong. And the micro-scenes are not a substitute for the declared
trace — they are deliberately trivial, and a reduction right on all of them can still be wrong on a
full lattice.

## Act

The residue is now a distribution. Over all eight declared frames, which are all comparable for
the first time, the reversed-winding disagreement is 6266 pixels of 55296 — 11.3%. At most 3391 of
those, 54.1% of the residue, is the measured ≤1px sampling offset. What remains is 1765
`depth_rejected`, 1097 `not_covered`, 11 `degenerate` and 2 `phantom`: two named mechanisms, one
about which face claims a pixel and one about which face survives the depth test, and neither of
them is a mystery any more. The as-committed arm decomposes just as cleanly — 46554 of its 46897
disagreeing pixels are `backface`, which is the winding defect, named and counted rather than
inferred.

And the sampling-immune figure: **14032 impossible interior-face pixels as committed, 2040 with the
winding reversed.** The second defect stops being an inference. It is 2040 pixels the reference
awards to faces that cannot be seen.

One more thing was found by building, and it is about this gate rather than about the renderer.
`specfreeze.lattice`'s coverage clause requires every module carrying both `scene_result` and
`SCENES` to sit in its sealed partition or its post-seal register. This module's first draft used
`SCENES` for the micro-scene register, and the clause noticed — but the three earlier modules of
this arc pin conformance scenes through `scene_result`/`golden` and name their register nothing at
all, so the clause has never seen any of them. It asked about this module on the strength of an
attribute *name*. The register here is renamed to the convention the rest of the tree uses, the
module is entered in the post-seal register, and the gap is asserted as a row rather than left in a
paragraph — it reddens when the clause is fixed to key on `golden`, which is a different rung.

`voxmicro-scenes` holds the elementary qualification and the origin decision, `voxmicro-labels` the
frame claims and the coverage gap, `voxmicro-residue` the record and the decomposition,
`voxmicro-selftest` the three plants. The falsifier naming this brief: break a scene's declared
faces and `voxmicro-scenes` reddens — the expectations are the claim, and a suite that only ever
recorded what happened would be evidence of nothing.
