<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: pixid-law -->
# `pixid` — design brief (URDRPID1, the primitive-ID buffer)

**Built**: 2026-08-07, as the rung the coverage-witness arc was aiming at. Not read into
the READ pass — that pass closed at P63 and this module postdates it.

## What it is

**A witness at pixel granularity.** `view_witness` cites the live scene digests once per
VIEW: it can say *this image was rendered from that world*. It cannot say *this pixel came
from that primitive*. `pixid` records, for every covered pixel, the `(instance, primitive)`
pair that owns it, so the question has an answer that can be checked rather than asserted.

## The core law (what `pixid-law` certifies)

**Ownership is a function of the SET of primitives, and it agrees with an oracle that
traverses differently.**

The first clause is `raster3d`'s new rule with the datum changed: nearest wins by exact
rational comparison, and an exact tie goes to the smaller `(instance, primitive)` pair.
The key **is** the written datum, which is what makes the order total *on outcomes* —
two fragments equal in `(depth, instance, primitive)` write identical bytes, so the
residual tie is unobservable. Ordering by submission index or by a hash of the vertices
would be deterministic without being total on what is stored, and the ambiguity would
resurface the moment two primitives shared the key.

The second clause is the one that earns trust. `agrees_with_oracle` recomputes every
pixel by scanning **all primitives against all pixels with no bounding box**, and compares
**both directions**: no covered pixel left empty, and no emitted id whose primitive fails
to own its sample point. It deliberately shares `raster.edge` — the defect class here is a
bounding-box walk that misses cells, which is exactly how `voxin` under-reported 20% of
its voxels, and an oracle that reimplemented the edge function would be testing two
arithmetics instead of one traversal. A bounding box shifted one subpixel column is
planted and observed failing.

## Occlusion subtracts

`instances(buffer) ⊆ instances(submitted)`: rasterization can hide an instance, never
invent one. Stated with a **proper**-subset witness, because subset-of holds trivially
when nothing is ever occluded (L61): the pinned scene puts instance 9 entirely behind
instance 7, and removing the occluder brings 9 back — so 9 is *hidden*, not absent. This
is the relation the view-granularity witness will be checked against when the two are
joined, and it is directional on purpose: equality would be the wrong law.

## The firewall, and where it actually lives

Perturbing a view knob must move the FRAME and leave the cited SCENE digest fixed, and
one moved scene integer must move BOTH. The second direction is not decoration — a
`scene_digest` that ignored the scene would satisfy the first perfectly.

Each knob is separately checked to be **live**, and that demand caught this module's own
first fixture: `zfar=50` changes nothing on a scene whose depths are 4, 9 and 12, and
`zfar=10` changes nothing either because the only primitive it clips is already hidden.
An inert knob satisfies the interesting half for free.

**But the guarantee is structural, not behavioural, and the tests say so on the syntax.**
A plant that mixed a view constant into `scene_digest` left every behavioural firewall
check green — correctly, because the citation still did not *vary* with the view. It
cannot: `scene_digest(primitives)` does not receive one. That is the sealed-observer
discipline (enforce structurally, never by comment), so an AST assertion pins the
signature and pins `witness` to handing it the primitives alone. Adding a parameter
reddens; no behavioural check can do that.

## does_not_show

That the image is CORRECT, or that the ids name anything real — this records which
*submitted* primitive owns a pixel, not that the primitive belongs there. No shading, no
blending, no perspective: it consumes screen-space primitives exactly as `raster3d` does,
so a perspective scene must be projected by `perspective` first and this rung does not
check that it was. **Cross-placement**: URDRPID1 is a Python reference with no Rust or
C99 port, so every figure here is single-implementation, as `voxin`'s and `voxlat`'s are.
The join to `view_witness` is NOT built — the subset relation is proved against the
submitted set, not yet against the view witness's cited instances, and that is the next
rung rather than a claim made here. Performance: the oracle is O(pixels × primitives) by
construction and is a checker, never a path. A buffer that cites is not a buffer that is
right. `integrity ≠ truth`.

## Falsifier

This brief cites `pixid-law`: permutation invariance of the buffer digest, and
bidirectional agreement with the no-bounding-box oracle over two scenes. If ownership
ever depended on submission order, or the traversal ever disagreed with a full scan in
either direction, that row reddens and this brief's central claim dies with it.
