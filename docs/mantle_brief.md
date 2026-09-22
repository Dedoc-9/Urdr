<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: mantle-identity -->
# `mantle` — design brief (URDRMNT1, LANDSCAPE-3: the tile path)

**Layer:** VIEW (a view over a view). **Substrate:** `gamegen` (read), `vista` (the frame and its
geometry), `raster` (the URDRFB1 frame type), stdlib. **Refuses:** `MANTLE-REFUSE`; a view `vista`
refuses stays `VISTA-REFUSE`. **Gate rows:** `mantle:scenes`, `mantle-identity`, `mantle-coordinate`,
`mantle-oneway`. **Suite:** `tests/test_mantle.py`.

## 0. The one invariant

**The picture is the certified frame wearing a tile — the frame is read, never written, and the
identity tile is the frame itself.** Geometry is `vista`'s and is asked of no one; appearance is a
flat square; the two meet at an exact rational texture coordinate.

## 1. What was measured first, and what it ruled out

Two experiments preceded this rung (the ledger's LANDSCAPE-2 entries; `launcher/assets`). A
generator asked to overpaint the certified frame — the geometry-locked prompt over the flat frame
(v2) and over a 3-px structure plate (v2s) — kept the layout's topology and, with the plate, most of
its global geometry (drift 99 percent / −2 px), but not its metric geometry: 0.503 of columns within
8 px of the certified wall/floor boundary, the far corridor drawn 15–42 px short, and within one wall
primitive the boundary wandering 6–7 px, the width of a brush. The conclusion was ratified in these
words: *generative overpaint is a useful appearance generator but is not a geometry-preserving
renderer input.*

The measurement cycle before the build (TILE-0, scratch) then established the substrate this rung
stands on: `vista` holds, per column, the voxel, the entered face and the exact ray parameter `t`,
and per floor pixel the exact world point `E + D·EYE_Y/kk`; the hit point lies on the face plane
exactly in integer arithmetic (1920 of 1920 columns); the fractional parts of those very rationals
are texture coordinates that agree with `vista`'s own selections everywhere (1920 wall columns,
694,648 floor pixels); a synthetic oriented tile pushed through the lookup lands where its face is;
and — found on the way — the table's own colours as tiles reproduce the certified pixels exactly.
Only then was the rung LOCKED, as a direction with the geometry claim held as a hypothesis; this
module is the hypothesis under its own falsifiers.

## 2. The coordinate law, exact and view-independent

A wall column's hit point is `P = E + t·D`, `t = tn/td`. Its `u` is the world coordinate ALONG the
face (`z` for an x-face, `x` for a z-face), signed per entered face so that `u` grows to the right of
the viewer who faces that face head-on — face 1 (the −x face) `+z`, face 0 `−z`, face 5 (the −z face)
`−x`, face 4 `+x` — then taken modulo the cell: numerator `±P_along·td mod Q·td`, denominator
`Q·td`. A face is only ever entered from its outside, so the table is view-free and the texture
sticks to the wall. Its `v` is the height below the wall's top edge: the row centre projects to
`y = EYE_Y + (2CY − 2r − 1)·t`, and `v = (Q − y)/Q`, denominator `Q·td`. A floor pixel's `(u, v)` are
the fractional cell coordinates of the exact floor point, denominator `kk·Q` — fixed to the world's
grid, not to the view. The texel is `⌊T·num/den⌋` with `T = Q = 256`: **a texel is one world unit**,
and every index is an integer division of integers.

`a_texel_is_seen_where_its_face_is` reads the consequences off a frame rather than asserting them:
`u` never falls across a wall primitive (one period per voxel face) and falls at every coplanar seam
(the wrap is where the voxel edge is; on the witness frame 31 of 31 seams, 8 corners); `v` grows
downward; on the floor, in the rows one screen row samples finely enough (one row step moving the
floor point by at most half a cell on both axes — `4·EYE_Y·|D_axis| ≤ kk(kk+2)·Q`), the texel wraps
at a cell change and nowhere else. The mirrored sign table fails the monotone or the seam law — the
control that shows the law can fail.

## 3. The emission is the table's own arithmetic

The index frame is READ for class, light family and depth band, exactly as `lut` reads it. The texel
replaces the table's base colour and then receives the table's own operations, unchanged: the
achromatic depth tint, the floor's near-darkening, the achromatic haze by band. Because haze and tint
are achromatic, every channel goes through the same integer function, so the emission carries one
256-entry map per band per class — the LUT's formula evaluated for every byte instead of for one base
colour. Stairs, sky and ink keep the table. A wall material is one tile scaled ONCE per light family
by the table's own brightness ratios (`LIGHT_PERMILLE = 1000 / 828 / 607 / 429`, derived from
`WALL_RGB`, never invented); the floor tile is used as is.

## 4. The identity law — the regression falsifier this rung ships with

Take the table's colours as tiles: four flat wall tiles (one per light family) and the flat floor.
`the_identity_tiles_reproduce_the_frame`: the picture equals `vista.png_bytes`' pixels EXACTLY, on
every corpus frame; the cross-host witness frame (0xABCDE/1, (34, 28), W) pictures to the very pixel
sha256 the ledger's witness records, `0bef7c1e…`. The certified emission is therefore the tile path
at the identity, and the tile path a strict generalisation of it — any drift in the emission
arithmetic reddens this row. The planted control perturbs every flat tile by one unit and is caught.

## 5. The lookup moves no index

`the_lookup_moves_no_index`: after a picture, the frame it was made from carries the URDRFB1 digest
of a FRESH `vista.frame`, and the level's canonical bytes are unchanged; the positive control writes
ONE index into a copy of the frame and the digest moves — the witness is not vacuous. A mutated
texel changes pixels (its every appearance) and nothing else. Two witnesses sit side by side in every
scene row — the frame digest (geometry) and the picture's pixel sha256 (appearance) — never one.

## 6. The classes stay apart; a missing tile is the identity

`the_classes_stay_apart`: with a flat blue wall tile and a flat warm floor tile, EVERY wall pixel
reads cool and EVERY floor pixel warm after light and haze; the tiles swapped fail both — a wall
tile never lands on a floor pixel nor the reverse. `a_missing_tile_is_the_identity`: `tile_set()` IS
`identity_tiles()` byte for byte; a set with one class missing keeps the identity for that class; a
tile of the wrong size or type is refused typed, never silently substituted. This is the asset
contract LANDSCAPE-2's M1 found absent: no file, no crash, no different geometry. The plants (a
mirrored sign table, an emission without haze, an emission that writes the buffer, a class leak, a
silent substitution) were each run against the module before the goldens were pinned and each
reddened its law.

## 7. The membrane is one-way, and the live-core half is the gate's

Read off this module's own full AST: exactly the declared substrate; no transition, identity, log or
stream authority in any scope — not even `descent` or `voxray`, which `vista` already answers for;
no `.step`/`.dispatch`/`.apply`/`.d_n`/`.serialize`/`.restore`; positive controls; no CORE module
and not `vista` imports `mantle`. What the module cannot prove about itself the gate proves against
a live `enact`/`statecanon` core: a scripted run's per-turn `D_n` sequence and final level bytes are
byte-identical with a picture made after every turn and with none.

## 8. The consumer

`play.py` (off-gate): `photograph` and `--snapshot` now make the picture through `mantle` — the
tiles read from `launcher/assets/tiles/wall.png` and `floor.png` when present (a `T×T` RGB PNG, one
world unit per texel), the identity when absent, so a tree with no tiles photographs exactly what it
did before. The launcher prints both witnesses: the URDRFB1 frame digest and the picture's pixel
sha256. `launcher/assets/tilefit.py` (off-gate) is the validator a generated tile passes before it
is placed there: size, seam continuity across the wrap, the colour family, and a provenance record.

## 9. Where it stops (deferred on purpose)

Filtering: on one frame a screen column covers from a sixth of a texel (a frontal near face, blocky)
to fifty texels (a grazing far side face, aliasing), and one screen row skips more than half a cell of
floor beyond 15.7 cells of depth; an unfiltered lookup aliases there, and a deterministic level per
depth band is its own measured rung, not an implementation detail of this one. Any GENERATED tile
(none is consumed by the module; a tile is bytes, its file and its provenance are the launcher's).
Variety within a class (a VIEW-side function of (voxel, face), never a world attribute — `gamegen`'s
cells carry no material). Stairs, the sky, pitch, yaw, motion, any wall-clock.

## 10. Grade

MEASURED: the corpus pictures reproduce (pixel sha256 beside the URDRFB1 digest), hash-seed-
independent; the identity law with its planted control; the no-write law with its planted control;
the coordinate law with its mirrored control, over the corpus and a sweep; the class law with its
swapped control; the missing-tile contract; the live-core `D_n` identity. ESTABLISHED: the one-way
AST; no CORE import. DECLARED: the texel size, the sign table, the light ratios, the synthetic tiles.

## does_not_show

A generated tile; filtering; stairs, sky, pitch, yaw, motion; a second placement of this module; any
frame budget. That the picture is beautiful — the laws are floors, not a ceiling.

## Falsifier

`mantle-identity`: the identity tiles reproduce the certified frame exactly, the lookup moves no
index, a missing tile is the identity, and the witness frame pictures to the witnessed pixels.
Companion rows `mantle:scenes`, `mantle-coordinate`, `mantle-oneway`.
