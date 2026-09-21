<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: vista-readback -->
# `vista` — design brief (URDRVIS1, LANDSCAPE-1: the first-person frame)

**Layer:** VIEW. **Substrate:** `gamegen` + `descent` (read), `voxray` (the certified ray oracle),
`raster` (the URDRFB1 frame), stdlib. **Refuses:** `VISTA-REFUSE`. **Gate rows:** `vista:scenes`,
`vista-readback`, `vista-contract`, `vista-oneway`. **Suite:** `tests/test_vista.py`.

## 0. The one invariant

**The frame is a function of `(level, pos, facing)` that reads back to the level and changes
nothing.** Destroy every frame and the run is the same run. A frame is a photograph of the certified
level from a cell, not a loop and not a state.

## 1. What it is, and what was measured first

The game layer had one depiction — the text grid `play.py` prints — and the repository separately
owned a certified integer rasteriser (`tools/render`, URDRFB1, cross-placed in Rust) and a certified
ray oracle (`voxray.first_hit`, the exact Amanatides–Woo traversal that judged `voxref`'s winding
defect) that nothing had ever pointed at a level: the seventeen game-layer modules have zero import
edges into any renderer. The measurement pass (LANDSCAPE-0) also read the world a camera must frame —
a fixed 48×32 grid, three-quarters rock, always eight rooms, median 286 exposed wall cells, spawn
always on `<` — and quantified the reference picture the user chose: far light / near dark
(luminance 112 → 66 across thirds), distance desaturates (0.33 → 0.50 saturation near), key light
from screen-left, a warm/cool two-family palette (0.39 of hue mass at 0–30°, 0.28 at 180–210°), ink
outlines and one red accent.

`vista` composes the two certified substrates over the certified level: one ray per column, the strip
height an exact floor division, the floor an exact inverse projection, and the picture an 8-bit INDEX
frame whose colour is a separate table. It is the Wolfenstein construction (id Software, 1992) —
walls one cell tall on a grid, eye at half height, no pitch — reproduced, not discovered.

## 2. The eye is taken, never derived; the facing is view state

`frame(level, pos, facing)` receives an integer cell and a cardinal. Its signature cannot receive a
`D_n`, a stream or a log (`vantage`'s law, arriving one world over). A wall cell is refused, not
rendered from inside. The authority has no heading — a MOVE is an absolute cardinal — so the camera's
heading lives with the camera: the launcher keeps it beside the game dict, never inside it, and
`default_facing(level)` (toward the landmark `>`, a pure function of the level) lets a first frame need
no history.

## 3. The camera, as declared constants

1920×1080; focal = half the width (a 90° horizontal field); a cell is `Q = 256` world units; the eye
stands at `EYE_Y = 128`, half a wall's height. The column `c` ray is the pixel centre, `(2c+1−W,
2·FOCAL)` in camera space, carried into the level's axes by the facing's right/forward pair; depth
along the view axis is `2·FOCAL·t` for the oracle's exact `t = (num, den)`; the wall's edges project
`h = FOCAL·EYE_Y/depth = 64·den/num` about the horizon and a row belongs to the strip iff its centre
lies between them (`CY − ⌊h+½⌋ ≤ row ≤ CY + ⌊h−½⌋`, exact floors). Below the strip, the row whose
centre is `kk/2` below the horizon sees depth `2·FOCAL·EYE_Y/kk`, hence the cell
`⌊(eye·kk + D·EYE_Y)/(kk·Q)⌋` — the floor of a rational, no float anywhere. Occlusion is the
oracle's (first hit); there is no z-buffer because a grid of unit walls needs none.

## 4. The imaging contract is a table

The frame is indices: ink; sky bands by row; floor / `<` / `>` by depth band; walls by (entered face,
depth band), the entered face standing in for a fixed key light from the south-west. `lut(depth)` is
the ONLY place colour exists. Haze is achromatic and at most 55 % at the far band; the depth tint is
an achromatic darkening; so a class's hue family never moves with distance or level depth —
`the_lut_keeps_classes_apart` reads that off the table (floor `R ≥ B+4`, every wall entry `B ≥ R+4`,
`>` teal, `<` magenta, at every band and depth) with a planted floor-warm wall entry refused. The
reference's warm-light / cool-shadow could not be applied ACROSS classes without destroying
readability, so hue encodes class and value/saturation encode light and distance. PNG is a container
over the index frame (`png_bytes`), never an identity: the identity is `raster`'s URDRFB1 digest.

## 5. The read-back law, and why it infers nothing

`the_centre_column_is_a_straight_walk` recomputes, by a plain walk over `level.cells` in the facing
direction, which wall the centre ray must hit `k` cells ahead, and reads the frame's centre column
back: the strip's voxel is that wall; its rows are exactly those whose centres fall between the
projected edges `960/(2k−1)`; every floor row below the strip carries the class of the walked cell at
that row's depth. The walk is a second computation; the depth-to-row map is the camera's definition,
shared. It is a check ON the picture, FROM the world — its verdict flows nowhere, so no gameplay
semantics are ever inferred from geometry. The positive control renders from the cell behind the eye
and fails the law (caught on all 48 posable spawn/facing pairs of the sweep). The law holds over the
corpus, a gate sweep of two more levels under all four facings, and a 192-frame measurement sweep.

## 6. The framing census accepts and bites

`census_verdict` is `framing`'s DOMINANCE rule on this frame: WELL_FRAMED, or DEGENERATE named by the
class holding ≥ 900 ‰ of the pixels. The corpus carries both verdicts on purpose: three well-framed
frames that are populated (sky, wall, floor all present) and one deliberately point-blank frame,
`DEGENERATE:wall`, so the rule is seen to reject as well as accept. Over the measurement sweep, 38 of
192 spawn/mid × four-facing frames were point-blank — a fact about grid dungeons, reported, not hidden.

## 7. The membrane is one-way, and the live-core half is the gate's

Read off this module's own full AST (function-local imports included): exactly the declared
substrate, no transition/identity/log/stream authority in any scope, no `.step`/`.dispatch`/
`.apply`/`.d_n`/`.serialize`/`.restore`, with positive controls; no CORE module imports `vista`.
What the module cannot prove about itself the gate proves against a live `enact`/`statecanon` core:
a scripted run's per-turn `D_n` sequence and final level bytes are byte-identical with a frame
rendered after every turn (facing carried beside the run) and with none.

## 8. The consumer

`play.py` (off-gate) gains `--snapshot PATH` and the in-game key `P`: after `enact` has adjudicated
the turn, the launcher renders `vista.frame` from the new state and its own view-side facing (the last
MOVE's cardinal, `default_facing` at a new level) and writes a PNG under `launcher/assets/`. The
launcher's digest self-check extends to `vista`. The frame is also the `--image` reference for any
later generative dressing, so the layout in every dressed picture is the certified one.

## 9. Where it stops (deferred on purpose)

Pitch and free yaw (the `vantage` PITCH set and a heading refinement are the next camera rungs);
smooth motion (`kinema` Frames as input); textures, props, wall relief and sky detail (visual-only,
`procedural-geometry`'s sub-domains A–C over these walls); a second placement of `vista` itself (only
its substrate is cross-placed); any wall-clock — a frame costs ~0.7 s in the reference placement and
is a photograph, not a loop.

## 10. Grade

MEASURED: the corpus frames reproduce (URDRFB1 digests pinned), hash-seed-independent; the read-back
law with its planted control; the table's class separation with its planted control; population and
the census verdicts; the live-core `D_n` identity. ESTABLISHED: the one-way AST; no CORE import.
DECLARED: frame size, focal, cell subdivision, eye height, band count, face-light order, palette.

## does_not_show

Pitch, yaw, motion, texture, props, a second placement of this module, any frame budget. That the
picture is beautiful — the read-back and the table are readability floors, not a ceiling.

## Falsifier

`vista-readback`: the centre column IS the straight walk, the planted eye is caught, and the frame is a
function of the view. Companion rows `vista:scenes`, `vista-contract`, `vista-oneway`.
