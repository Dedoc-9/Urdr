<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: worldbasis-conformance -->
# `worldbasis` — design brief (URDRWBS1)

## The decision it records

The authorable-world arc reached a dimensional fork: either the simulated world gains a second
**horizontal** axis, or the walker projects into the existing netcode plane. **The world gains
the axis.** Projection would make one coordinate carry two incompatible physical meanings — a
walker moving north would change the component gravity acts on — and terrain height would still
need somewhere to live, recreating the seam it was meant to close. Projection hides the mismatch;
it does not remove it.

    X = horizontal (east)    Y = VERTICAL (gravity acts here, and only here)    Z = horizontal

## What this module is

Not the 3D world. The **contract**, plus a census of who obeys it — the part that can exist
before the migration, and the part that makes the migration checkable. Axis meaning becomes data
the architecture certifies rather than knowledge each subsystem remembers separately.

**The basis** is which axis means what, falsifiable: a world whose gravity touches a horizontal
axis violates it *by measurement*, not by review.

**The anchor** is origin, scale, and the **sample convention** — does an integer coordinate name a
CELL (constant across it) or a LATTICE POINT (interpolated between neighbours)?

## The anchor earned itself on arrival

`glide` reads a height as the ground under an actor, constant over the cell it stands in — its own
docstring says *the EXACT floor-sampled cell height*. `terrain_bridge` reads **the same array** as
vertices, emitting a surface interpolated between lattice points. Measured on the island preset:
**3 878 of 3 969 cells differ**, mean 3.33 and worst 17.50 height units against a height_scale of
420. The actor floats or sinks relative to the terrain it is drawn on in ~98 % of cells.

Neither reader is wrong. Each is self-consistent. **The defect was that nothing decided between
them**, because there was nowhere to say it.

## Settled from the repo's own layering

`glide` reads a height to decide where an actor stands and whether a rise exceeds `MAX_STEP` —
that is a **law**, and laws are authority. `terrain_bridge` emits URDROBJ2 for a front end and says
so in its first line — that is a **view**. This is the render arc's observer seam one layer down.

So the divergence is not a bug to eliminate. It is a **projection**, and the honest treatment of a
projection is to declare it, **bound** it, and forbid the feedback: worst **41 permille** of the
height range, mean 7, with the heightfield proved **bit-identical after bridging** — the same
cardinal invariant the ownership witness carries.

Eliminating it instead would mean rendering terrain as steps, or changing a frozen movement law to
flatter a picture. Neither is warranted by a number, and both would be a subsystem answering a
question that belongs to the architecture.

## Grade

The basis is **DECLARED** — a contract is not a measurement. **Conformance is MEASURED**: gravity's
axes, the walker's movement axes and both sample conventions are read from the live modules on the
run. Today **nothing conforms**, and that is the honest starting state: `worldstep` is 2D by design
and says so, and the walker spends axis 1 on N/S where the basis reserves axis 2. A census showing
everything already conforming would mean the contract had been written to fit.

`does_not_show`: that a conforming subsystem is *correct* — this certifies agreement about what a
coordinate means, never that the physics using it is right; that the non-conforming ones are
broken; that either sample convention is the bug.

Row `worldbasis-conformance`; falsifiers in `tests/test_worldbasis.py`.

## The camera basis — exact integer orientation

The first picture stopped at a top-down view because `perspective.project` is a pinhole with **no
rotation**, and there was no camera orientation anywhere in the repo. A rotation *looks* like it
needs sines, and sines are where a float would enter a path that has none.

It does not. An orientation must be **orthogonal, not orthonormal**, and integer matrices with
`M Mᵀ = k² I` are abundant — every Pythagorean triple is one, so the available pitches are dense
enough for any camera. **And the scale cancels**: a perspective divide is `X/Z` with both scaled
by `k`, so the projection is exact and no normalization is ever performed. An exact integer camera
is the same construction with the division deferred.

The four yaws are the walker's four facings, read from `stance.DIRS` on the run rather than
maintained by hand. Composition preserves orthogonality — the scales multiply.

**Both framing failures were measured before `horizon_row` existed.** A pitch rotating the *wrong
way* gave 93 % sky with the ground thrown thousands of pixels below the image — the inverted-sign
class this module exists to catch, caught by looking at a frame. A pitch too *steep* for the focal
length gave 100 % ground. `horizon_row` now predicts both (−80 for the 3/4 pitch, 67 for 7/24 in a
320-pixel frame) rather than leaving them to be rediscovered.
