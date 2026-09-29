<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: bearing-anchors -->
# `bearing` — design brief (URDRBRG1, VIEW-YAW-0: the heading refinement)

**Layer:** VIEW. **Substrate:** `gamegen` and `descent` (read), `voxray` (the traversal), `raster` (the
URDRFB1 frame type), `vista` and `mantle` (the frozen law it reuses), stdlib. **Refuses:**
`BEARING-REFUSE`. **Gate rows:** `bearing:corpus`, `bearing-table`, `bearing-anchors`, `bearing-claw`,
`bearing-oneway`, and the placement's `bearing-placement`, `bearing-placement-selftest`. **Suite:**
`tests/test_bearing.py`. **Preregistration:** [`spec/D26-bearing-boundary.md`](../spec/D26-bearing-boundary.md),
committed before this module.

## 0. The one invariant

**A bearing is a registered rational direction, and at C = 1 the law is the frozen one.** An id names a
canonical primitive Pythagorean triple `(A, B, C)`; the renderer consumes the triple, never an angle; the
hypotenuse enters exactly four expressions; at the four anchors every expression is `vista`'s and
`mantle`'s, and the frames and pictures there are theirs byte for byte.

## 1. The OODA pass

**Observe.** `vista` renders from a cell and one of four cardinals; its brief names "a heading
refinement" as the next camera rung. Its ray is `right·a + forward·b` with integer unit vectors, and
every derived quantity is a floor of a rational. `voxray.first_hit` takes any integer direction. The
tree already owns a yaw identity: `frontfps` authors yaw as integer millidegrees in `[0, 360000)`,
out-of-range refused, never normalized.

**Orient.** A non-cardinal unit vector is irrational unless it is a rational point on the circle, and
those are exactly the Pythagorean directions `(A/C, B/C)`. Scaling the ray by `C` makes it an integer
vector again; the forward distance to the hit is then `t·b·C`, so `C` appears exactly where `vista`
turns `t` into a depth (the strip edges and the band), where `mantle` turns it into a height on the
wall, and where the floor's inverse projection divides by the forward component. Everything else —
the traversal, the entered face and its light, the wall coordinate from `P = E + t·D`, the sky, the
ink, the floor band, the table and the tiles — never sees `C`.

**Decide.** One vocabulary: the millidegree ids of `frontfps`, each naming the rational direction of
smallest stereographic denominator within a quarter millidegree of its ideal angle (the octant), its
mirror, and exact quarter turns. A coarse step (for instance 88 ids, 0.088°) is a consumer's input
choice over the same ids, not a second table. The table is committed data with a pinned sha256; the
program that chose it (`studio/bearing_octant_gen.py`, off-gate) is provenance.

**Act.** `bearing.frame` and `bearing.picture` are `vista.frame`'s and `mantle._emit`'s construction
at the triple, reusing every frozen helper that takes no facing.

## 2. The glyph ruling (D1 §20)

No glyph. A bearing is a tool-layer VIEW parameter, not a language primitive; the kernel is untouched.

## 3. What the gate holds it to

- **The table (`bearing-table`).** Checked by its own invariants over all 360,000 ids — canonical pairs,
  the anchors, Pythagorean and primitive triples, strictly clockwise order including every symmetry seam
  and the wrap — and never by regeneration. Five planted defects are refused by the structural checker
  alone; a missing or altered file refuses.
- **The anchors (`bearing-anchors`).** The frozen modules are computed live beside this one over
  `vista`'s corpus and the witness view, in both tile sets; a mirrored screen-right fails the law.
- **The C law (`bearing-claw`).** Every strip and a registered set of floor cells are recomputed from the
  hit point by the dot-product definition of the forward distance — a second computation; the frozen
  depth used off the anchors is caught at every adversarial bearing.
- **The corpus (`bearing:corpus`).** 13 adversarial bearings from two views, 26 cases, each pinning the
  triple, the frame and both pictures, with the table's digest folded into the identity.
- **One-way (`bearing-oneway`).** The full-AST guard, no CORE importer, and the live-core differential.
- **The placement (`bearing-placement`).** A std-only Rust port reproduces every corpus witness from the
  committed table with 128-bit arithmetic where a product needs it; a planted defect must move it.

## 4. Grade

MEASURED: the table law with its plants; the anchor law over the corpus; the C law read back with its
plant; the corpus reproduces (pinned). ESTABLISHED: the AST is one-way; no CORE module imports
`bearing`. DECLARED: the quarter-millidegree angle bound of the octant (its endpoints are irrational and
are not evaluated), and every constant `vista` and `mantle` declare.

## does_not_show

Movement between cell centres, pitch, eye height, motion or smoothness, any frame budget, that the table
is the best possible, and any wall-clock. A frame at a bearing is a photograph of the certified level.

## Falsifier

`bearing-anchors`: if a frame or a picture at an anchor is not `vista`'s or `mantle`'s byte for byte, or
the mirrored camera is not caught, the brief's central claim — that the heading refinement is the frozen
law at C = 1 — is false.
