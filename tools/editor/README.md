<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/editor/` — Urðr Designer (an authoring front-end)

A small, self-contained editor for the deterministic pipeline: draw wireframe
objects, place them on a plain ground grid, and hand the result to the exact,
cross-placed renderer and the gated netcode runtime.

| File | What it is |
|---|---|
| `urdr_designer.html` | A browser CAD/world editor — no install, no dependencies, works offline. Draw objects in 2D or 3D, place them on the ground grid, fly the world first-person, export the scene. |
| `load_world.py` | Renders an exported `urdr_world.json` through the **exact** perspective projector (`../render/perspective.py`) to a `URDRFB1` frame + digest + a viewable PGM image. Closes the loop from editor to engine. |
| `replay.py` | Runs the **exact** dynamics (`../physics/dynamics_nd.py`) forward and writes `urdr_replay.json` — a per-tick chain of canonical `URDRPN1` **state digests** (the deterministic replay witness) plus momentum/energy invariants and draw positions. Five modes: a built-in demo cascade, `--world urdr_world.json` (collide dynamic + static via the exact LCP; `--g N` for gravity), `--stack N` (an **N-ball resting stack**, exact contact LCP, certified **λ**), `--joints [--world file]` (an **articulated system** — the authored hinge/rod/weld/slider constraints — via the exact equality solver, certified `URDRJNT1`), or `--fp [bounce|stack|swing|world file.json]` (**bounded Q32.32 fixed-point** time-stepping via `../physics/field.py` — a gravity+bounce box, a **settling stack** (contact LCP → sequential-impulse), a **swinging pendulum** (articulated → squared-length Baumgarte), or **your authored `--world` export run long** (general PGS collisions with un-normalized normals + restitution `--e` + optional `--g` gravity that **settles** the scene in an implicit box) — all animate for as long as you like **without overflowing**, where exact-ℚ refuses). Load any of these in **▷ Replay** to scrub it. The engine is the sole authority; the browser only draws what it recorded. |

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
- **⛰ World** — pick an object, click the ground to place it, drag to move (children
  follow), the amber handle to rotate. The **Hierarchy** tree shows parent/child nesting
  with per-row show/hide and lock; the **Inspector** edits each placed object's physical
  state — body (static / dynamic / kinematic), collider, mass, restitution / friction,
  parent, tags, capabilities, visibility, lock, and constraints / joints to other objects.
  All of it serializes into the canonical world JSON; **no engine logic runs in the
  browser** — these are authored *intent*, which the runtime/engine validates for
  admissibility downstream. Toggle **◈ 3D** for a **free-fly first-person editing view**
  (WASD fly · Q/E vertical · Shift fast · drag = look · wheel = fly speed) over a plain
  ground grid — over, around, and through the scene; the placement/export mapping is
  unchanged (view only). You can drag whole objects on the ground plane (children follow). Click the ground
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
- **⨀ Walk** — a first-person preview: click to capture the mouse, then WASD + mouselook
  through your authored world (silhouettes standing base-on-ground, `load_world.py` convention)
  or — with a replay loaded — through the **engine's witnessed frames**, bodies drawn at their
  recorded positions with the frame's URDR digest on the HUD (R plays, `[` `]` step). Eye
  height, move speed, focal (FOV), and replay scale are sliders; Shift runs, Q/E fly, wheel
  scales speed. Honest scope, on-screen and here: this is a **float projection** in the same
  pinhole family as the exact renderer — it edits nothing, simulates nothing, and the
  deterministic runtime + witness chain remain the sole authority. Concept-merge note: the
  first-person/"text is authority; render is its projection" ideas arrive from the Weltwerk
  workbench demos; what crossed over is the *discipline-compatible* part (a view over recorded
  authority), not the rendering tech.
- **Compare (A/B)** — in ▷ Replay, load a **second** replay doc as run B: a strip under the
  arena turns green where the two recorded witness chains agree and rust where they diverge,
  the **first desync** is marked with a jump button, B's bodies ghost over A's, and the
  current frame shows both digests side by side (≡ A / ≠ A). This is `first_desync` — the
  frozen netcode localization law — made visible; the browser compares recorded chains as
  strings and re-simulates nothing. Try it: generate run A from the canonical export, copy
  the world, move the median, generate run B — the strip stays green until a car reaches
  where the barrier used to be, then goes rust forever. That edge is the physics divergence,
  localized to the tick.
- **⤓ Save / ⤒ Open** — persist the whole project (objects + world) to a JSON file.
- **▸ Export world JSON** (World mode) — writes `urdr_world.json` (`URDR-WORLD-3`): objects
  by digest + instances carrying their full physical state and hierarchy (`parent` + a
  `local` transform relative to that parent). Backward-compatible — it keeps
  `ground_x` / `ground_z` / `rot_deg`, so `load_world.py` still renders it.

Import geometry from a photo or an SVG (both mint the same `URDROBJ2` identity the
designer does — D14):

```
python3 ../tracer/photo_trace.py object.png --verts 32   # PNG/PGM/PPM silhouette → design
python3 ../frontend/svg_import.py object.svg             # SVG vector paths → design
# each writes a URDR-PROJECT-1; open it via ⤒ Open and the wireframe is in the palette
```

Export authoritative state to any renderer via the **D15 view contract**, then view it:

```
python3 ../frontend/view_export.py urdr_replay.json out_view.json   # URDR-VIEW-1 doc
# open ../frontend/view_viewer.html and ▷ Load it — a self-contained viewer (no CDN, works
# from file://) that verifies every frame's witness binding + recomputed digest before
# rendering, and refuses mismatches.
```

Annotate a project with **exact rigidity verdicts** (authority computes; the editor displays):

```
python3 ../frontend/rigidity_verdict.py urdr_project.json urdr_project_rigid.json
# prints ● rigid / ◍ flexible (dof, moving vertices) / ⊘ refuse per design — a CERTIFICATE
# over ℤ, reproducible on every host — and writes recorded verdicts the palette shows as badges.
```

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
then Export and run this. Each dynamic instance becomes an exact ball; each `static` /
`kinematic` instance becomes a fixed collider (inverse mass 0). Every step, **all
simultaneous contacts** — dynamic-vs-dynamic and dynamic-vs-static — are resolved together by
the exact frictionless LCP, so bodies stop against barriers and pile up instead of passing
through. Add `--g N` for gravity (things fall and settle). Turn on the **contacts + impulses**
overlay to see the resolved contact impulses. Honest scope: frictionless + inelastic at the
normal, discrete overlap (no CCD); joints/constraints, restitution / elastic multi-contact,
and exact long-run gravity (the ℚ i64 limit) are later rungs — the runtime **refuses** rather
than approximate when the exact state overflows.

See the exact contact forces in a resting stack (the frictionless LCP):

```
python3 replay.py --stack 3      # 3-ball stack → λ = [3, 2, 1] (bottom → top), certified
```

Load it in **▷ Replay** and turn on the **LCP λ** overlay: each contact shows the certified
normal impulse holding the stack up — larger toward the bottom, because each contact carries
the weight above it. The solution is the exact `contact_lcp` output with a `URDRLCP1`
witness, *complementary-certified*: every contact either carries λ > 0 and is exactly resting
(w = 0), or carries none and is separating — the solver proves it, or it refuses.

Solve authored **joints / constraints** (the exact articulated equality solver):

```
python3 replay.py --joints                            # built-in chain: 4 balls linked by rods, one end pushed
python3 replay.py --joints --world urdr_world.json    # solve YOUR Inspector constraint list
```

Add a **hinge / rod / weld / slider** between two placed objects in the Inspector (Constraints
/ joints), Export, and run the second form. The solver returns the unique constraint impulses
that hold every joint exactly — **J·v = 0**, certified, with a `URDRJNT1` witness — or it
**refuses** if the constraints are redundant or conflicting (a singular system, by the
uniqueness-by-certificate principle). The links are drawn in Replay; the momentum overlay
shows the rigid velocity transmission. Honest boundary: iterated joint *dynamics* overflow the
ℚ i64 limit in ~2 exact steps, so joints are surfaced as a certified single solve, not a
time-stepped animation — animated linkages need a bounded fixed-point substrate (a later
rung). `spring` / `motor` are soft/driven and stay declared, not solved.

Watch physics **animate without overflow** — the bounded fixed-point substrate:

```
python3 replay.py --fp 4        # 4 balls fall + bounce in a box, 240 ticks, Q32.32 fixed-point
```

This is the scene exact-ℚ **refused** — the very first gravity sim overflowed i64 after a
handful of steps. Fixed-point (`field.py`'s frozen **Q32.32**, round-to-nearest ties-away) is
BOUNDED and ROUNDS, so it time-steps as long as you like, deterministic and bit-identical
across placements, with a per-frame `URDRFPB1` witness. It's the counterpart to the exact
single-solves: **exact where affordable, bounded fixed-point where you need long animation.**
Load it in **▷ Replay** and scrub — the balls fall, bounce (restitution ¾), and settle.

The same substrate now runs the **ported solvers** — the exact contact and articulated solves,
time-stepped in fixed-point:

```
python3 replay.py --fp stack 3     # a 3-ball stack falls and SETTLES (PGS contacts, ground-up projection)
python3 replay.py --fp swing       # a pendulum SWINGS (articulated distance constraint, Baumgarte on d·d)
```

These are the animated counterparts to the exact single-solves: `--stack`'s certified λ becomes
a stack you watch settle, and `--joints`'s certified J·v = 0 becomes a pendulum you watch swing —
both bounded, deterministic and reproducible, with no overflow and **no sqrt** (the pendulum
stabilizes on the *squared* length, so it never leaves i64). Exact remains the proof;
fixed-point is the live animation.

Run your authored scene in the **gated N4 netcode runtime** — the same `worldstep` engine the
netcode stack certifies (URDRLST1 witnesses, one URDRLSTT trace, cross-placed in Rust):

```
python3 replay.py --net urdr_world.json    # authored world, GATED runtime, witness chain + trace
```

The doc it writes scrubs in **▷ Replay** like any other; the printout includes the URDRLSTT
trace digest and an in-process deterministic-×2 self-check. Honest scope: display floats are
derived from the Q32.32 words for drawing only; N4 mass is inert, so bodies carry display mass
1 and the momentum/energy overlays are not meaningful in this mode — **the witness chain is the
authority**. Export note: the designer integer-snaps every runtime-consumed field (including
`scale`) at export, because the N4 loader `WORLD-REFUSE`s non-integers — authoring snaps, the
runtime never rounds.

And you can run **your own authored scene** on the fixed-point substrate — the bounded long-run
counterpart to the exact `--world`:

```
python3 replay.py --fp world urdr_world.json     # authored collisions, time-stepped without overflow
```

Same scene, same dynamic-vs-dynamic and dynamic-vs-static contacts (general 2D, resolved with
**un-normalized normals** so there's no sqrt), but it runs as long as you like — where the exact
LCP eventually refuses on i64 overflow, this stays bounded and deterministic. Exact for the
proof, fixed-point for the endurance. Add `--e N` (percent) for **restitution**: `--e 0` is a
perfectly inelastic pile-up, `--e 90` a lively bounce, `--e 100` conserves energy (velocities
reverse) — the target normal velocity becomes −e·v_approach, applied at the velocity level only.
Add `--g N` for **gravity**: the scene falls and **settles** in an implicit box (floor + side
walls) with light linear damping — an authored pile coming to rest, bounded and deterministic.
(A frictionless pile can't settle tangentially, so the damping is an honest stand-in until
Coulomb friction lands.)

## Next rungs (declared)

The **▷ Replay** spine is the first of the "expose the deterministic engine" additions:
the editor authors, a runtime (`replay.py`) simulates with the exact engine and emits a
witness chain, and the editor scrubs it. Natural follow-ons, in order:

- the inspector + hierarchy (`URDR-WORLD-3`) and the authored-world runtime
  (`replay.py --world`) are *done* — **▷ Replay** now simulates your own scene
  deterministically (same witness chain on every machine). Next in the runtime: static
  colliders, joints/constraints, gravity, and per-material restitution;
- the fixed-point substrate now runs authored worlds fully: `--fp world <export> [--e N] [--g N]`
  collides **and settles** (gravity + an implicit box + damping), on top of `--fp stack` /
  `--fp swing` — all bounded and deterministic. The stepper is now a **gated rung**:
  `../physics/fp_dynamics.py` (rung 5) with a frozen `URDRFPT1` golden, a `verify.py`
  `physics_fp` stage (determinism + settle + non-vacuous defect self-test) and
  `tests/test_fp_dynamics.py` — **reproducibility MEASURED** (this editor's `replay.py` is the
  exploratory consumer of the same approach). The independent Rust placement
  `../physics/fp_dynamics_rs/fp_dynamics.rs` reproduced both `URDRFPT1` goldens ADMITTED 2/2 on
  Windows/`rustc`, so the stepper's **cross-placement is now MEASURED** (two placements). Next:
  continuous collision (CCD) for fast / thin bodies and Coulomb friction (so piles rest without
  the damping stand-in);
- the deterministic net of authored scenes is now REAL and gated — rung **N4**
  (`tools/netcode/worldstep.py`, `MEASURED` both placements, frozen in D12): an exported
  `URDR-WORLD-3` scene runs in the same loop as lockstep/rollback/authenticated inputs, and
  `replay.py --net` surfaces its witness chain here. Next in that line: N2/N3 composition over
  authored scenes and body-body contact (unlocks the inert instance mass);
- 3D preview of the object through `perspective.py` (WYSIWYG with the engine); terrain /
  road-spline "landscape" mode.
