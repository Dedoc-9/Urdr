<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxray-oracle -->

# `voxray` (URDRVXR1) — design brief

*The geometric oracle: what does this camera ray actually hit first?*

## Observe

`voxref` froze an observable and proved a set of laws about it — determinism, coverage partition,
draw-order irrelevance, two digest witnesses. Every one is true. Every one still passes. They are
all properties of the **machinery**, and not one of them asks whether the machinery draws the right
thing, because until a second computation exists there is nothing to be right *about*.

The first reduction asked. Face culling changed `O_t` on six of eight declared frames, and one
differing pixel read:

    px(10,0) on open_air
      unculled : voxel (2,1,10) face +z, depth 4223   <- interior, solid directly above
      culled   : voxel (2,1,11) face -y, depth 4275

An interior top face, with a solid voxel sitting on it, beating that voxel's own exposed face. Not
surprising — impossible. Two hypotheses were tested; one survived (the orientation test selects the
wrong winding, confirmed on a single voxel from six directions) and one died (interpolating 1/z
instead of z changes nothing). A second defect was real and unexplained, and nothing in the tree
could say what the right answer *was*.

## Orient

The oracle's authority is deliberately narrow: **which solid voxel does a camera ray enter first,
through which face, at what t.** Exact integer voxel traversal, `t` as a rational compared by
cross-multiplication, no tolerance anywhere. No triangles, no edge functions, no depth buffer — a
second implementation of the same idea would fail the same way, and the point is different failure
modes.

It shares exactly two things with the reference, and both are the **scene** rather than the
renderer: the world's occupancy, and the camera basis. A camera the two disagreed about would make
every comparison meaningless.

It samples where the rasteriser samples — integer pixel coordinates, not pixel centres. Half a
pixel of disagreement would produce differences at every silhouette and drown the real defect in
artefacts of the comparison itself.

## Decide

**The oracle audits itself, because an oracle nobody checked is an opinion.** First-hit-is-first,
verified by independent fine sampling. The hit lies on its reported face and inside the voxel on
the other two axes. The entry direction agrees with the face normal. A miss really traverses
nothing. An interior origin gets **no invented face**. The probes contain both hits and misses.

**And the camera is a shared, audited contract.** A pixel's ray projects back to within one pixel
of itself. That law was first written as an *exact* inversion and was false: composing a Q16 basis
with two floor divisions is not an involution. 70.15% of pixel-rays return exactly; the rest land
one pixel away, systematically at (−1,+1), (0,+1) or (−1,0) — the signature of `//` truncating
toward negative infinity, not of geometry. **The bound is one pixel and it is checked as one pixel**,
and the distribution is pinned so the claim can never silently strengthen.

**The verdict on the disputed pixel is a third answer.** Voxel (2,0,10) face +z — one step nearer in
y than either arm. Both were wrong, which is why the oracle deserved building rather than a
tiebreaker between the two.

**The correspondence is reported, never certified.** As committed, 17.4% over the comparable frames.
With the six windings reversed — carried here as *declared data*, so the whole finding reproduces
from the committed tree rather than from an uncommitted edit — 87.0%. The one directional claim is
that the reversal moves the reference closer to geometric truth. Not that it is correct.

`does_not_show`, and these bound everything above. **The residue is an upper bound on defect, not a
measurement of it** — up to a pixel of ray/sample offset is folded into every figure. **No mechanism
is established** for what survives the reversal. **One declared frame is not comparable at all**:
`floor_flat`'s eye begins inside solid, so the oracle returns that voxel with no entry face for every
ray — legal, and in a different semantic domain from "which surface does the camera see". Which
definition an interior origin should get is an open question, and the frame is excluded by
*derivation*. And **the trace labels are wrong** — the frame named `floor_flat` is the buried one,
`buried` is not inside anything — recorded as a metadata defect rather than repaired, since renaming
would move `voxref`'s pinned scene for a cosmetic reason.

## Act

`voxray-oracle` holds the oracle's own audit and the shared camera contract, `voxray-correspondence`
the committed measurement and its bounds, `voxray-selftest` the plants. The falsifier naming this
brief: the projection-inversion law is shown to *reject* a ray built for the neighbouring pixel —
without that, a one-pixel tolerance would accept rays that were merely close, and the contract would
be looser than the prose claims.
