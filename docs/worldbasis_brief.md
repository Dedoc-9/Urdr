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

Neither reader is wrong. Each is self-consistent. **The defect is that nothing decided between
them**, because there was nowhere to say it.

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
