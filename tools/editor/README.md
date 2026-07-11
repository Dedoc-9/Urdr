<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/editor/` — Urðr Designer (an authoring front-end)

A small, self-contained editor for the deterministic pipeline: draw wireframe
objects, place them in a post-apocalyptic world, and hand the result to the exact,
cross-placed renderer.

| File | What it is |
|---|---|
| `urdr_designer.html` | A browser CAD/world editor — no install, no dependencies, works offline. Draw objects in 2D or 3D, place them on a highway, export the scene. |
| `load_world.py` | Renders an exported `urdr_world.json` through the **exact** perspective projector (`../render/perspective.py`) to a `URDRFB1` frame + digest + a viewable PGM image. Closes the loop from editor to engine. |
| `replay.py` | Runs the **exact** dynamics (`../physics/dynamics_nd.py`) forward and writes `urdr_replay.json` — a per-tick chain of canonical `URDRPN1` **state digests** (the deterministic replay witness) plus momentum/energy invariants and draw positions. Three modes: a built-in demo cascade, `--world urdr_world.json` to **simulate the authored scene** (every `dynamic` instance becomes an exact ball; statics are drawn, not collided), or `--stack N` to solve an **N-ball resting stack** through the exact contact LCP (`../physics/contact_lcp.py`) and surface the certified per-contact **λ**. Load the result in **▷ Replay** to scrub it. The engine is the sole authority; the browser only draws what it recorded. |

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
  continue a shape). **Move** reshapes points *and edges* (drag a line to move both ends);
  **Erase** removes. In **◈ 3D** you can now drag points and edges directly (screen-parallel)
  and orbit by dragging empty space. Select a point or an edge and **nudge it with the arrow
  keys** — Shift = 10, Alt = ½ — in either 2D or 3D. **Transform** rotates about X/Y/Z in
  ½°/1° steps; **Scale · flip**; **Primitives** add round N-gons and rounded barriers.
  Select a point to set its **depth Z**.
- **⛰ World** — pick an object, click the highway to place it, drag to move (children
  follow), the amber handle to rotate. The **Hierarchy** tree shows parent/child nesting
  with per-row show/hide and lock; the **Inspector** edits each placed object's physical
  state — body (static / dynamic / kinematic), collider, mass, restitution / friction,
  parent, tags, capabilities, visibility, lock, and constraints / joints to other objects.
  All of it serializes into the canonical world JSON; **no engine logic runs in the
  browser** — these are authored *intent*, which the runtime/engine validates for
  admissibility downstream. Toggle **◈ 3D** for a perspective preview down the road — where
  you can now drag whole objects on the ground plane too (children follow). Click the road
  to drop more copies, **⧉ Duplicate** (Ctrl+D) the selected object, **＋ New object** to
  draw a fresh one, and **nudge the selected object with the arrow keys** (children follow).
- **▷ Replay** — load a `urdr_replay.json` (made by `replay.py`) and scrub the timeline
  (play / step / start · end). Every frame shows its exact-state **URDRPN1 digest** and the
  conserved momentum + energy; scrubbing to a frame restores that exact state, bit-identical
  on every conforming host. The browser only *draws* engine-provided state — it never
  simulates. This is the deterministic-replay capability surfaced directly in the editor.
  **Overlays** draw per-body momentum vectors, the system centre of mass + Σp, and each
  resolved collision's contact point, normal and equal/opposite impulse — all read from the
  engine's recorded state (velocity, mass, and the exact Δv it applied), never recomputed.
  For a `--stack` replay, the **LCP λ** overlay shows the exact contact LCP's certified
  per-contact forces (larger toward the bottom of the stack).
- **⤓ Save / ⤒ Open** — persist the whole project (objects + world) to a JSON file.
- **▸ Export world JSON** (World mode) — writes `urdr_world.json` (`URDR-WORLD-3`): objects
  by digest + instances carrying their full physical state and hierarchy (`parent` + a
  `local` transform relative to that parent). Backward-compatible — it keeps
  `ground_x` / `ground_z` / `rot_deg`, so `load_world.py` still renders it.

Render an exported world through the exact engine:

```
python3 load_world.py urdr_world.json urdr_frame.pgm
# prints the URDRFB1 frame digest and writes a viewable PGM image
```

Run a deterministic replay through the exact physics, then scrub it in the editor:

```
python3 replay.py               # writes urdr_replay.json + prints the witness chain
#   ticks         : 73
#   frame 0 digest: 1f3c…   frame N digest: 9ab0…
#   witness chain : 73 digests
#   momentum      : conserved      2*KE : conserved
```

Then open the editor, switch to **▷ Replay**, and load `urdr_replay.json`. Because the
runtime uses the *exact* `dynamics_nd`, the state can hit the `i64` substrate limit; when it
does, the runtime records the frames up to that point plus an honest `refused` marker — the
exact engine **stops rather than approximate**, and the editor shows the refusal at the end
of the timeline. (The default scene is integer-exact, so it runs the full 72 ticks.)

Simulate your **own** authored scene (World mode → **▸ Export world JSON**):

```
python3 replay.py --world urdr_world.json     # simulates every dynamic body with the exact engine
```

Give at least one placed object `body: dynamic` and a nonzero **init vel** in the Inspector,
then Export and run this. Each dynamic instance becomes an exact ball (position from its
ground transform, radius from the object's bounding box × scale, mass + velocity from the
Inspector); static / kinematic bodies are drawn as fixed markers. Collision *against*
statics, joints/constraints, gravity, and per-material restitution are declared later rungs —
today the runtime resolves the dynamic bodies against each other, exactly and reproducibly.

See the exact contact forces in a resting stack (the frictionless LCP):

```
python3 replay.py --stack 3      # 3-ball stack → λ = [3, 2, 1] (bottom → top), certified
```

Load it in **▷ Replay** and turn on the **LCP λ** overlay: each contact shows the certified
normal impulse holding the stack up — larger toward the bottom, because each contact carries
the weight above it. The solution is the exact `contact_lcp` output with a `URDRLCP1`
witness, *complementary-certified*: every contact either carries λ > 0 and is exactly resting
(w = 0), or carries none and is separating — the solver proves it, or it refuses.

## Next rungs (declared)

The **▷ Replay** spine is the first of the "expose the deterministic engine" additions:
the editor authors, a runtime (`replay.py`) simulates with the exact engine and emits a
witness chain, and the editor scrubs it. Natural follow-ons, in order:

- the inspector + hierarchy (`URDR-WORLD-3`) and the authored-world runtime
  (`replay.py --world`) are *done* — **▷ Replay** now simulates your own scene
  deterministically (same witness chain on every machine). Next in the runtime: static
  colliders, joints/constraints, gravity, and per-material restitution;
- **physics-debug overlays**: centre of mass + Σp, per-body momentum vectors, contact
  points / normals / impulses, and **LCP λ over resting stacks** (`--stack`) are *done* — all
  read from recorded state. Next in the runtime: **static colliders** (authored barriers that
  actually stop bodies), **joints/constraints** (wire the `articulated` solver to the authored
  constraint list), and gravity — so authored highway scenes settle and collide;
- 3D preview of the object through `perspective.py` (WYSIWYG with the engine); terrain /
  road-spline "landscape" mode; a deterministic net of `urdr-world` instances so a shared
  scene stays byte-identical across peers.
