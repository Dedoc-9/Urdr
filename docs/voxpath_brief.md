<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxpath-coherence -->

# `voxpath` (URDRVXJ1) — design brief

*A second declared trace, and the measurement it exists for says the certificate arc was aiming at
the wrong quantity.*

## Observe

The conditional-certificate arc wants to know how much work survives from one frame to the next.
That question cannot be asked of `voxref.TRACE`, and the reason is a compliment to it: those eight
frames were designed to be maximally uncorrelated adversarial cases with no camera continuity
anywhere. Measuring temporal coherence on them would report a number near zero and it would be a
fact about the trace's design, not about renderers.

So a second trace is declared, and declaring one is a contract act rather than a convenience. The
path is **one continuous walk** — every episode begins exactly where the previous one ended, in
position and orientation, so the only discontinuity in the whole trace is the one that is declared.
An episode boundary that jumped would be an undeclared teleport, and the continuity law would then
be measuring the episodes rather than the path.

The route is a real corridor, chosen from the world before the path was written: the column
`(x=10, z=1)` is open for ten consecutive cells — the longest run in this world — with the floor slab
solid beneath its whole length, so no frame is ever aimed at nothing. **The eye never enters matter.**
`voxref.TRACE` already owns the buried case, and a walk that buried itself would contribute blank
frames, identical to one another, flattering every coherence figure here by being trivially
unchanged. Two earlier drafts of this path did exactly that, and the distinctness law caught both.

| episode | frames | what it attacks |
|---|---|---|
| still | 4 | the control — the camera does not move at all |
| creep | 5 | 1/32 of a voxel per frame |
| pan | 5 | a slow turn, position held |
| whip | 4 | a hard turn, position held |
| sprint | 3 | two voxels per frame, driving in |
| aperture | 4 | a gap in the right wall opening, closing, opening |
| graze | 4 | alongside the left wall, looking across it |
| teleport | 2 | the control at the other end — one declared discontinuity |

## Orient

**There is no temporal coherence in the observable to exploit, at any speed.** At a thirty-second of
a voxel per frame — the gentlest motion this trace contains:

| | unchanged | of 6912 |
|---|---|---|
| colour buffer | 6900 | 99.8% |
| **exact observable** | **811** | **11.7%** |

Depth is a continuous function of camera position and `O_t` contains it exactly, so the depth half
moves at nearly every pixel however small the step. A certificate of the form *"this pixel is
unchanged"* certifies almost nothing, and the 95–99% sparsity the arc was hoping for does not exist.

**This is a result and not an obstacle.** It says the certificate must be about **ownership** — which
face owns the pixel — with depth *reconstructed* from the owner rather than remembered. The two
halves are measured apart here precisely so the next rung cannot assume the wrong quantity is stable.

And the colour figure is an **upper bound** on ownership survival, never a measurement of it: distinct
primitives can share a colour, so a pixel whose colour survives may have changed owner underneath.
Measuring ownership needs the winner buffer, which is the next rung's job. The bound is asserted in
the one direction it can be checked — colour never survives less often than the pair.

The plant has its witness inside this rung's own trace: there is a `creep` pair whose colour buffer is
unchanged at *every* one of the 6912 pixels while the observable is unchanged at barely one in eight.
A colour-only accounting would have called that pair perfectly coherent and licensed reusing a frame
whose depth had moved almost everywhere.

**And the reversed winding collapses a declared case.**

| primitive set | distinct `O_t` |
|---|---|
| `voxref.primitives()` | 8 of 8 |
| `primitives_with("reversed")` | **7 of 8** — `enclosed` == `buried` |

`voxref.every_declared_case_is_distinct` renders with the committed winding and is correct — and it is
*run* here, not merely cited. But every rung from `voxtie` onward, this arc included, renders with the
reversed set, and under that set two of the eight frames are byte-identical in colour and depth. The
performance arc has been measuring a seven-case trace while calling it eight. Both halves are asserted
so the finding stays scoped to the variant it is about rather than reading as a defect in the
reference.

## Decide

**The prediction for the next rung ships in this commit, one commit before any arm exists.**

`voxsilo` had to admit it could make no prediction claim: its arms ran first, and pinning a prediction
afterwards would have been back-dating one. The only mechanism that actually proves a prediction came
first is commit order. The five conditional predicates and the five predictions `voxcond` must score
are committed here as `spec/attest/voxcond-prediction.txt`, with their digest pinned as this rung's
`prediction` golden. The arms land in a later commit and are required to score exactly that set
against exactly that digest. Two of the five predict *failure*, which is the point — the obvious
conditional predicates are expected not to work, and saying so before running is the only version of
that claim worth anything.

`does_not_show`: nothing about certificates — not one is built, costed or exploited here. Nothing about
time, and no wall clock enters; a trace rung is exactly where a stopwatch would slip in. That the path
is representative of any real player: it is designed, like `voxref.TRACE` before it. That high colour
coherence implies retirable work — `voxsilo` already showed a frame can change little and still need
most of its computation, and that gap is the next rung's whole subject. Ownership survival, which is
bounded above by the colour figure and not measured. And nothing is altered: `voxref.TRACE` is pinned
by digest and untouched.

## Act

`voxpath-walk` holds the continuity, the episode structure and the two distinctness laws,
`voxpath-coherence` the two accountings and the plant, `voxpath-winding` the collapsed case and the
committed law run beside it, `voxpath-prereg` the pre-registration, `voxpath-selftest` the record
plants.

The falsifier naming this brief: `voxpath-coherence` reddens if the exact observable ever starts
carrying the coherence the colour half has — which would mean depth had stopped depending on the
camera, and would invalidate the reason this rung exists.
