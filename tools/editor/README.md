<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/editor/` — Urðr Designer (an authoring front-end)

A small, self-contained editor for the deterministic pipeline: draw wireframe
objects, place them in a post-apocalyptic world, and hand the result to the exact,
cross-placed renderer.

| File | What it is |
|---|---|
| `urdr_designer.html` | A browser CAD/world editor — no install, no dependencies, works offline. Draw objects in 2D or 3D, place them on a highway, export the scene. |
| `load_world.py` | Renders an exported `urdr_world.json` through the **exact** perspective projector (`../render/perspective.py`) to a `URDRFB1` frame + digest + a viewable PGM image. Closes the loop from editor to engine. |

## Grade — honest scope

**`SPECULATIVE` / exploratory. This is NOT a gate-tested Urðr rung.** The editor is a
mouse-driven, floating-point browser tool; nothing here runs under `verify.py` and
nothing here is `MEASURED`. It is a *consumer* of the pipeline, useful for authoring,
not part of the certified core. See [`../../spec/D5-ledger.md`](../../spec/D5-ledger.md)
for what actually is measured.

## Why it fits the pipeline anyway — the honest boundary

The value is in the **data it produces**, which obeys the same discipline as the core:

- **Identity is content.** Every object is a canonical vertex/edge list with a
  SHA-256 **digest** — the same content-addressing the kernel uses. A world is just a
  list of placed digests + transforms. (Export writes `URDR-WORLD-2`.)
- **Author loosely → snap to the grid → the deterministic core owns the rest.** Mouse
  input and 3D preview are float (approximate). On **save** the geometry welds
  duplicate vertices, bakes any mirror, and snaps to the integer grid, so the digest is
  a clean, reproducible object. On **render** (`load_world.py`), scene composition is
  the float authoring step (snapped to integers), and the **projection to pixels is the
  exact floor-division projector** — the same `px = cx + floor(f·x/z)` law that is
  cross-placed bit-for-bit in Rust. So the frame digest is the deterministic Urðr
  identity of the scene — reproducible on every conforming host.

That boundary is the whole point: the same geometry, fed to the exact renderer and the
cross-placed physics, computes an identical frame and an identical collision on every
machine — which is what makes deterministic-lockstep multiplayer possible.

## Use it

Editor (double-click the file, or open it in any browser):

- **◇ Object** — draw with the **Line** tool (drag to draw an edge; start on a point to
  continue a shape). **Move** reshapes, **Erase** removes. **Transform** rotates about
  X/Y/Z in ½°/1° steps; **Scale · flip**; **Primitives** add round N-gons and rounded
  barriers. Select a point to set its **depth Z**. Toggle **◈ 3D** to orbit.
- **⛰ World** — pick an object, click the highway to place it, drag to move, the amber
  handle to rotate; select a placed object for fine rotate/scale. Toggle **◈ 3D** for a
  perspective preview down the road.
- **⤓ Save / ⤒ Open** — persist the whole project (objects + world) to a JSON file.
- **▸ Export world JSON** (World mode) — writes `urdr_world.json` for the renderer.

Render an exported world through the exact engine:

```
python3 load_world.py urdr_world.json urdr_frame.pgm
# prints the URDRFB1 frame digest and writes a viewable PGM image
```

## Next rungs (declared)

3D preview of the object through `perspective.py` (WYSIWYG with the engine); terrain /
road-spline "landscape" mode; a deterministic net of `urdr-world` instances so a shared
scene stays byte-identical across peers.
