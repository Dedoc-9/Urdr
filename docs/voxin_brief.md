<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxin-law -->
# `voxin` — design brief (URDRVXI1, S1.1, the import boundary)

**Built**: 2026-08-06, as the first rung of the return to the city arc. Not read into the READ pass —
that pass closed at P63 and this module postdates it.

## What it is

**The front end the arc did not have.** `voxlat` (S1) certified the quantization boundary and named
this rung in its own `does_not_show`: *"any splat-to-occupancy derivation (the next rung)"*. That
successor was never built, and the consequence was structural rather than cosmetic — every
downstream stage of the arc (simulate, stream, network, witness, replay) begins at a synthetic scene
or a certified heightfield. **Nothing turned authored geometry into the lattice.** "Import a real
block" was not a slow path; it was an absent one. This module is that path.

## The core law (what `voxin-law` certifies)

**Occupancy is a function of the geometry alone**, and **the admission bound is derived, not chosen.**

The first clause is one sentence and it is the whole contract: permute the triangle list — reverse
it, rotate it — and the emitted Morton key set and its digest are byte-identical. That is what makes
an import *reproducible on another machine* rather than merely repeatable on this one, and it is the
property every downstream witness needs: two importers that agree on geometry must agree on bytes.

The second clause is the rung's real content. `voxlat` DECIDED the exact-integer triangle/box
overflow maximum to be `4*B³` and drew the corollary that a 64-bit placement admits
`3*coord_bits + 2 ≤ 64`, hence `coord_bits ≤ 20`. This module **reads that bound from `voxlat`**
rather than restating it — a bound written in two places is a bound that can disagree with itself —
and refuses any coordinate past it. The refusal is not a safety margin someone picked. It is the
theorem, applied to real data.

`voxin-property` checks the traversal against the **oracle**: every emitted voxel independently
satisfies `voxlat.tri_box_overlap`, and no overlapping voxel in the bounding box is omitted. The
check runs by an independent route rather than against this module's own loop, so a bug in the
traversal cannot hide behind its digest agreeing with itself (L23).

## The door, and why it is typed

`voxin-selftest` proves the door can CLOSE, three ways — an importer that admits everything has no
boundary to certify:

- **Geometry one past the derived bound** is `VOXIN-REFUSE`. This is the exact shape `voxlat`
  measured: at city scale the decided law needs 84 bits where the refuted quadratic estimate claims
  57, and shipping the estimate would give a lattice exact on small test scenes and silently wrong
  on a real city — whose symptom is mis-adjudicated hits at long range, indistinguishable from
  cheating.
- **A float coordinate** is refused and never rounded. Quantization is the CALLER's declared act,
  performed before admission and owned by whoever performed it, because a rounding this module did
  silently would be an authority act with no record.
- **A degenerate triangle** is refused.

## does_not_show

That the geometry is CORRECT, or that it resembles any real place — this admits geometry, it does
not validate it. Splat or point-cloud ingestion: the caller quantizes, and that reduction is not
performed here. Any renderer. Performance at city scale: the traversal is a bounding-box walk and
its cost has not been measured on anything large. **Cross-placement** — URDRVXI1 is a Python
reference with no Rust or C99 port, so every figure is single-implementation, exactly as `voxlat`'s
is. A world that imports is not a world that is right. `integrity ≠ truth`.

## Falsifier

This brief cites `voxin-law`: occupancy invariant under permutation of the triangle list, and the
coordinate bound read from `voxlat.max_tile_coord_bits()` rather than restated. If the emitted key
set ever depended on input ORDER, or the admission bound ever drifted from the one `voxlat` decided,
that row reddens and this brief's central claim dies with it.
