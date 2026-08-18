<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The Ursprung bridge — reconnaissance for an authorable free-roam world

**Status: a NOTE, not a rung.** Nothing here is gated, nothing is measured, and no machinery is
built. Per the Discovery Membrane (`AGENTS.md` §4) a surprising observation earns a note, a v2
experiment, or a main-gate rung according to whether it can yet be stated as a test that could
fail. This is the survey that decides which. It reads code in two repositories and says what
exists, what is partial, what is absent, and what has never been measured — deliberately
refusing to invent machinery because a target picture contains it.

Read against: `github.com/Dedoc-9/Ursprung` at the tree cloned for this pass, and this
repository at the same moment. Paths are quoted so every claim below is checkable.

## The finding that reorders the plan

The obvious plan — "recover the old editor, save a world, load it in the demo" — assumes the
two repositories disagree about *tooling*. They do not. They disagree about **what a world
fundamentally is**, and each is right about its own half.

**Ursprung authors CAUSAL TOPOLOGY. Geometry is declared downstream and disposable.**
`weltwerk/authoring/world_spec.py` states it outright: text → causal topology, *not* text →
geometry, because "topology is cheap to change; geometry is expensive, so the causal topology
is the durable artifact and meshes are regenerable projections of it." A `.wrk` world
(`weltwerk/worlds/times_square.wrk`) declares zones, entities, health, and typed relations
(`powers`, `controls`, `feeds`, `depends_on`) — a city as a graph of what can affect what.
`weltwerk/render/geometry_boundary.py` then enforces the seam with the same invariant this
tree calls the D15 firewall: authority mutates only through `apply_event`, renderers receive a
frozen `Snapshot`, and "rendering does not change the authority" is machine-checked.

**Hainuwele authors TERRAIN, derived and certified. Entities barely exist.** The world here is
seeded noise reproduced digest-for-digest across two operating systems, with a reach ladder, a
bounded cache, and a frozen competitive budget. What it has never had is a *named entity with
relations standing on that terrain*.

So the two repositories are not duplicates competing for one role. They are the two halves of
one world that have never been introduced: **Ursprung has the entity/relation layer Hainuwele
lacks; Hainuwele has the certified spatial substrate Ursprung's entities float above.** The
bridge is therefore not an import of terrain, and not an editor bolted onto `fpsdemo`. It is a
*placement*: authored entities bound to certified ground.

## The seam's first hard problem, and it is not tooling

`weltwerk/authoring/world_format.py` carries `pos: tuple = (0.0, 0.0, 0.0)`, and
`weltwerk/worlds/times_square.wrk` writes `position: 2 0 -3`. `weltwerk/splat/splat_format.py`
encodes positions as `float32`. This tree refuses floats at the door — `field-domain` made
`FixedPoint.unit` and `mul_k` reject them, `boolport` refuses `bool`, and the whole
substrate is exact integers to the point that `noise16`'s floored divmod needed a selfcheck to
prove it identical on the canon domain.

**The two repositories disagree about number type exactly at the seam where they would meet.**
That is a concrete, falsifiable finding rather than an impression, and it is the first thing
any bridge must decide: authored positions must be encoded as exact integers on the tile
lattice (or as a declared rational with an exact conversion refusing anything it cannot
represent), or the certified substrate stops being certified the moment a world is loaded. A
float that reaches a product is precisely what `region.py`'s delta door exists to refuse.

## Gap table

Graded EXISTS / PARTIAL / ABSENT / NOT_MEASURED. "PARTIAL" means the machinery exists but is
not wired to the place the free-roam target needs it; "NOT_MEASURED" means it exists and works
but no committed record grades it.

### This repository (Urðr / Hainuwele)

| Capability | Grade | Where, and what is actually true |
|---|---|---|
| `fppose` / `fpclip` | **EXISTS** | Promoted into the demo at v1.13; both batteries run as selfcheck doors at every launch against the placements' own goldens; cross-OS identical in `scenecost` |
| Avatar geometry | **PARTIAL** | A five-joint capsule impostor (torso, head, two arms, no legs) — the certificate's geometry, declared as such. `tools/frontfps/frontfps.py` holds the real authoring canon (meshes, rigs, capsule hitboxes, actors, spawns, D16 seams under one world-identity law), unwired to the demo |
| Camera orientation / sensitivity | **EXISTS, FROZEN** | Certified quaternion rotation; sensitivity, pitch clamp, eye height and walk speed frozen as operator-confirmed since v1.9 |
| Terrain contact / grounded state | **PARTIAL** | The demo's eye and avatar ride exact bilinear ground. `tools/terrain/contact.py` (URDRCON1) carries the real support witness — source, cell, terrain revision, contact height, with `GEOMETRY_SUPPORTED` reserved and asserted unproduced — and is not wired to the demo |
| Input acquisition | **EXISTS** | Polled keyboard / mouse / XInput, all merging into one trace vocabulary; traces are committed records (`fpsrecord`) |
| Reach / LOD / cache rebasing | **EXISTS** | Derived ladder, resident ring grids, bounded cache with the derived rail; `reachenv` and `capcost` grade all of it from sealed bytes |
| Authored meshes / capsules / seams | **PARTIAL** | `tools/frontfps/` has the canon and its placements; `fpsdemo`'s raster path has never drawn one |
| `fpsdemo` raster path | **EXISTS** | Integer edge-function fill, z-buffer, ring ladder, avatar impostor, far field |
| VIEW / CORE boundary | **EXISTS** | D15 firewall, interpolation firewall, the observer laws in `planet.py` / `farfield.py`, and the pixel-ownership contract the sky and avatar both obey |
| Chunk / streaming / persistence | **PARTIAL** | `chunkload`, `chunkstate`, `persist`, `resurrect`, `terraform`, `worldregion`, `wire` are all gated — and none of them is connected to the demo, which streams nothing and saves nothing |
| A savable world artifact | **ABSENT** | The demo's world is `(seed, reach)`. There is no manifest, no chunk record, no world digest that a player's edits could land in |
| Free-roam control | **ABSENT** | `--play` records a trace and `--replay` drives one; there is no session that begins, wanders indefinitely, and ends with something durable |

### Ursprung (weltwerk)

| Capability | Grade | Where, and what is actually true |
|---|---|---|
| World authoring DSL | **EXISTS** | `authoring/world_spec.py`, `authoring/world_format.py`; a four-stage pipeline WorldSpec → CausalGraph → SpatialGraph → RuntimeWorld |
| Authored world files | **EXISTS** | `worlds/times_square.wrk`, `fps_demo/world.wrk` — real authored content, text, human-editable |
| Structural analysis of a world | **EXISTS** | `authoring/world_lint.py` — reachability, SCC, bottleneck; a world's feedback loops are found *before geometry exists* |
| World diff / events / validate / design | **EXISTS** | `authoring/world_diff.py`, `world_events.py`, `world_validate.py`, `world_design.py`, each with a test |
| Authority → renderer seam | **EXISTS** | `render/geometry_boundary.py`: frozen `Snapshot`, swappable adapters, and the tested invariant that rendering cannot mutate authority |
| Editors | **EXISTS (browser)** | `fps_demo/weltwerk_designer.html`, `weltwerk_studio.html`, `weltwerk_world.html`, `splat/weltwerk_splat_editor.html`; three.js, pointer-lock, live causal overlay |
| A spatial data contract | **EXISTS** | `splat/splat_format.py` — a verified 32-byte record whose JS mirror is byte-exact. Float32, and Gaussian splats rather than meshes |
| Chunked world + copy-on-write | **EXISTS as a probe** | `scale/cow_world.py`, with a real finding: *locality of effect requires locality of randomness* — a global RNG couples every chunk, so streams are keyed positionally. Explicitly "NOT the editable world" |
| Deterministic replayable world | **EXISTS** | `world.py` — the Weltlinie; `run(seed, N)` bitwise identical under `PYTHONHASHSEED=0`, committed vs speculative separated by `clone()`, canonical order-independent digest |
| Terrain / heightfield authoring | **ABSENT** | Entities carry positions; there is no terrain to author. This is precisely the half Hainuwele already has |
| Durable chunk-addressed world store | **ABSENT** | `world.py` digests committed state and `.wrk` is a text file; there is no manifest binding chunk records under their own addresses |
| Integer / exact numeric discipline | **ABSENT at the seam** | Positions are floats throughout the authoring and splat layers |

## What the table implies (candidates, not a plan)

1. **The bridge artifact is small.** Not a world format — a *binding*. A manifest that names a
   certified terrain (seed, canon parameters, reach), a `.wrk` spec by digest, and a placement
   table mapping each authored entity to an exact integer lattice position with its capsule.
   Everything else already exists on one side or the other.
2. **The float boundary must be settled first**, because it is the only item in either table
   that can silently corrupt a claim rather than merely be missing. An exact placement encoding
   with a refusing door is a small, falsifiable, gate-shaped piece of work.
3. **`cow_world`'s finding transfers directly.** Positional RNG streams keyed by chunk are what
   this tree already does for terrain (`noise16` over lattice coordinates) — the two
   repositories independently arrived at the same law, which is corroboration worth recording
   rather than a coincidence worth ignoring.
4. **The causal layer is the genuinely novel import.** A castle that *powers* a turret and
   *depends on* a bridge, whose blast radius is computable before it is modelled, is a
   capability this tree does not have in any form. It is also the one piece that cannot be
   faked by rendering harder.
5. **Two editors already run in a browser.** Whatever authoring UI eventually exists, it should
   be measured against what those already do rather than rebuilt from zero.

## What this note does not claim

It does not claim either repository's tests pass right now — none were run in this pass. It does
not grade Ursprung's evidence, which lives under its own discipline and its own gates. It does
not propose a schedule, a rung order, or an architecture as decided; the ordering above is a
reading of the code, and a reading is a hypothesis. It does not measure anything: every cost,
budget, and feasibility question raised here is `NOT_MEASURED` and would need its own record.
And it does not assume the free-roam target is reachable — that question belongs to the first
slice that tries it and reports what happened.
