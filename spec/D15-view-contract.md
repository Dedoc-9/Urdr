<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D15 — The view-export contract (authority → renderer)

Status: **MEASURED** (checkable core gate-enforced); **NOT yet frozen** — the contract
freezes once an independent consumer (a three.js reference viewer) reproduces the
exported state, per the admission ladder.

The engine is three layers, one-way:

```
    Authoring → Canonical assets (D14) → Authority (Urðr) → Witnesses
                                                                  │
                                                                  ▼
                                                          View contract (D15)
                                                                  │
                        ┌──────────────┬──────────────┬──────────┴───────┬─────────────┐
                        ▼              ▼              ▼                  ▼             ▼
                    three.js       Unreal          Godot            Vulkan       Blender / sci-viz
```

Layer 1 (authority) is the project's unique, gate-proven contribution. Layer 3
(presentation renderer) is **replaceable and need not be unique** — a studio can keep
Unreal's renderer while replacing only simulation and networking with this authority
layer, or prototype in the browser and move native later, without touching simulation.
Layer 2 — this contract — is the bridge that makes that true and keeps it true.

## 1. The load-bearing invariant

> **Presentation outputs are OBSERVATIONAL ONLY.** Any gameplay-affecting data must
> enter the authority layer as explicit inputs or be deterministically recomputed
> within it.

This one sentence prevents years of architectural drift. Modern engines routinely
blur the line — GPU particle collisions affecting gameplay, compute-shader physics,
GPU-driven destruction, occlusion influencing AI, visibility-based gameplay,
physics-assisted animation. Under D15, none of that may flow from the renderer back
into authority. If a renderer computes something the simulation must know, that
result is not authoritative until it re-enters the authority layer as an explicit
input or is recomputed there deterministically.

The invariant is made **falsifiable** (not aspirational): a view frame CARRIES the
authoritative witness, and changing any presentation field (material, light, camera)
moves the **view** digest — presentation is visible to renderers — but never the
carried **witness**, which is a function of authoritative state alone. A defect
exporter that folds a presentation field into the witness is caught by the gate.

## 2. The view frame (`URDR-VIEW-1`)

A view frame is derived from an authoritative frame plus declared static scene
metadata. Per frame it exposes (extensible; all presentation):

- `witness` — the authoritative frame's digest. **Binds** the view: a renderer checks
  `verify_binding` to refuse depicting a frame it is not bound to.
- `tick` — the replay timestamp.
- `bodies` — `[{obj: canonical URDROBJ2 id, material: id, x, y}]`. The **transform is
  read from the authoritative frame** — a scene cannot relocate a body the authority
  placed, nor depict a body count the authority does not have (`VIEW-REFUSE`).
- `lights`, `cameras` — declared scene data (authoring; presentation).
- `contacts` (optional) — debug witnesses read from the recorded frame (observational).

Serialization is canonical and deterministic; `view_digest` is its SHA-256, and it
moves when presentation moves. The `witness` is included as a **bound reference**,
never recomputed from presentation.

## 3. What is enforced now

`verify.py` stage `view-export` (`tests/test_view_export.py`):

- `view-export:canonical` — deterministic export to a pinned golden
  (`conformance_view.txt`);
- `view-export-binding` — the view carries and is bound to the authoritative witness;
  a view claiming a different authoritative frame fails the binding;
- `view-export-observational` — a material change moves the VIEW digest but leaves the
  carried witness unchanged, **and** a defect that folds the material into the witness
  is detectably different (the invariant is real, not incidental);
- `view-export-refusal` — a scene depicting a different body count than the
  authoritative frame is `VIEW-REFUSE`.

## 4. The admission ladder for this layer

1. Define the view-frame schema + canonical serialization (this document; `view_export.py`).
2. Implement an **independent consumer** — a three.js reference viewer that reproduces
   the exported state in a real browser.
3. **Freeze** the schema, serialization, and the binding/observational-only laws once
   that consumer agrees (the D8 cross-placement discipline, applied to the view layer).
4. Every future renderer (Unreal, Godot, Vulkan, offline Blender) is then an
   interchangeable client of the frozen contract; upgrading or replacing the renderer
   never changes gameplay or replay validity.

**Step 2 landed:** `tools/frontend/view_viewer.html` is the independent consumer — a
**self-contained** viewer (no CDN, no Web Crypto — it **hand-rolls SHA-256** exactly
like the Rust/C placements, and renders on a plain canvas, so it runs from a
double-clicked `file://`). It loads a `URDR-VIEW-1` document, **recomputes each frame's
`view_digest` with its own code** (byte-identical to `view_export.py`, confirmed in
node over the real 121-frame highway export), verifies the witness binding, and
**refuses to render any document with an unverified frame**. It emits a verification
report (contract version, frame count, witnesses verified, frames refused, export
digest, viewer version) — a participant in the verification story, not merely a display.
It is observational-only by construction: it never writes back to authority. The
reference viewer is deliberately dependency-free, matching the whole repo; the heavy
layer-3 renderers the contract *enables* (three.js, Unreal, Godot, Vulkan, offline
Blender) are downstream clients of the same `URDR-VIEW-1` documents — and D15 is what
makes them safe, since none of them can leak upward.

We are at step 2 (an independent placement exists and reproduces the digest in node).
**Step 3 — freeze — waits for the browser viewer to report all-frames-verified on a
host** (the D8 discipline: a placement is admitted when it reproduces on a named host).
Until then the schema is MEASURED, not frozen.

## 5. Honest scope

D15 says **what** to draw and **binds** it to authority; it says nothing about **how
well** it is drawn. Renderer quality — PBR, HDR, shadows, GI, ray tracing — is entirely
layer 3, out of scope here, and the correct place for the large AAA rendering effort
*if and when a product needs it*. The distinctive, gate-provable property is the
one-way dependency: `replacing or upgrading the renderer never changes gameplay or
replay validity — because the renderer was never a source of truth`.

## See also

- `spec/D14-frontend-contract.md` (the input-side contract this mirrors)
- `spec/D7-execution-geometry.md`, `spec/D11-layer-contracts.md` (renderer as consumer)
- `tools/frontend/view_export.py` (the executable contract)
- `docs/THEOREMS.md` (the measured floor)
