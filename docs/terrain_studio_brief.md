<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Terrain studio brief — the zyfod goal, inserted surgically (T-ladder)

Status: **T1 + T2 + S1 LANDED (stages `terrain` + `sea`: canon, URDROBJ2 bridge, and the masked-transport sea — all MEASURED at reference); the view panel (T3, idle law) and T4 remain PLAN.** The sea slice was renamed W → S to avoid the W1 winding-rung collision; its design verdict: not a detector, not bare reuse — an adapter plus a masked ADDITIVE step over the untouched frozen field substrate, digesting under the frozen URDRFLD1 law (no new witness class — a C8 datum). Authored 2026-07-16 against `terrains.zyfod.dev`
v0.20.0 (feature surface taken from operator screenshots; the site is a client-side JS
shell, so its internals are INFERRED, not read — stated where it matters). Written while
the desktop bridge was offline: the D14/D15/D16/D17 contracts this plan anchors on were
verified from staged copies this session; `tools/editor/` and `tools/calculationViz/`
internals are to be read before rung T2/T3 code is written. Per AGENTS rule 10, no document
may cite anything here as existing capability until its gate stage is green.

## 1. The build goal, decomposed

The zyfod studio's surface, by panel: terrain shape (preset, seed, height scale, sea level,
edge falloff incl. island); a noise-layer stack (base layer + up to 12, normalize min/max);
surface/erosion/import tabs; splines (roads, rivers); biomes (density, temperature,
moisture, snow line, slope thresholds); water (sea level, quality modes legacy→realistic,
reflection/detail/wave complexity, animation, deep/shallow/foam colors); skybox (time of
day, day/night cycle, brightness, haze, stars); lighting (sun azimuth/elevation/color/
intensity, fog, ambients); colors (16-biome palette, procedural palette generator with its
own color seed, presets); world (16×16 chunks × 128, 5×5 tile assembly, shared noise field,
joint export); visuals/post (exposure, contrast, saturation, vignette, bloom, sun rays);
performance (presets, backend selection, worker renderer, auto performance mode,
pause-when-idle, render scale); JSON project import/export.

## 2. Why the fans spin, and the law that replaces the toggle

Diagnosis (INFERRED from the visible panel + the standard architecture of such apps; their
code was not read): a continuous requestAnimationFrame loop re-renders the full canvas at
display rate — animated water on by default, procedural sky, and a post-processing chain
(bloom, rays, vignette) — even when nothing changes. On a 2013-class GPU (the operator's
panel shows ANGLE / Radeon R9 200, WebGL 2, 75 FPS, render scale 0.80) that is sustained
near-full GPU load; heat; fans. The site knows: its own "Pause When Idle" toggle is
documented as a "big GPU/battery/heat saving on weak machines" — idle burn is a known cost,
shipped as an opt-in saving rather than a default law.

Our version inverts that into a design law, not a preference:

> **The idle law: an idle view draws zero frames.** Rendering is event-driven — a frame is
> produced only when authoritative state, camera, or an explicitly enabled animation
> changes it. Animation (water, day cycle) is opt-in, time-budgeted, and off by default.
> A hidden or unfocused view renders nothing (mandatory, not a toggle). The AUTHORITY path
> never needs a GPU at all — terrain identity is computed and gate-checked in exact
> integer arithmetic on the CPU; the GPU is presentation only, and presentation is
> observational (D15).

This is enforceable in the consumer (invalidation-driven redraw; the repo's replay/editor
already renders from recorded witnesses rather than a free-running loop) and testable at
the seam: the view-export digest for an unchanged state must be byte-identical, so a
"frame" for an unchanged state is definitionally redundant work.

## 3. The surgical insertion point (the socket already exists)

`spec/D14-frontend-contract.md` §4 already reserves the row this studio fills:

    Procedural generator | seed + params | declared (reproducible seed) | DECLARED

The terrain studio IS that modality, built out and graded honestly. Nothing touches the
kernel; no new witness class is expected (one more C8 datum). Identity flows through the
same one-way boundaries every other front end uses: D14 in (assets), D15 out (views), D16
for tiling (already proven: regional composition reproduces the monolith witness).

## 4. The ladder

- **T1 — the deterministic heightfield canon (authority; the only rung with new laws).**
  `tools/terrain/heightfield.py`: an integer value-noise + FBM layer stack — seeded
  permutation derived via SHA-256 from the seed, fixed-point lattice interpolation
  (Q32.32-style integer math, D9 discipline: deterministic, rounds, refuses on overflow),
  layered like the zyfod noise stack but exact. Same (seed, params) → the same heightmap
  bytes on every host — the promise float JS cannot make. Height scale, sea level, edge
  falloff (none/island) as exact integer ops. Canon `URDRHF1` =
  SHA-256(magic | w,h | scale | heights). Corpus: pinned (seed, params) → digest goldens;
  defect: a wrong interpolation variant that must diverge; refusals `TERRAIN-REFUSE`
  (bad dims, non-integer params incl. bool, layer count over cap, overflow). Red-first
  falsifiers; gate stage `terrain` with the four D17-style rows; D5 entry; the D14
  procedural row graduates DECLARED → MEASURED (reference).
- **T2 — the D14 bridge (admission).** `to_object()`: heightfield → integer-snapped
  `URDROBJ2` wireframe grid (decimated) through the shared canon (`tools/frontend/
  canon_ref.py`), exactly as designer/tracer/SVG enter — so a generated island lands in
  the existing editor, renderer, and physics world with zero new identity laws. Provenance
  (seed, params, template name) is metadata, never identity (D14 clause 5). Golden: the
  pinned terrain's URDROBJ2 digest joins the frontend corpus.
- **T3 — presentation (view; observational only).** Biome classification (height/slope/
  moisture thresholds — the zyfod biome panel, computed exactly), palette (their color-seed
  idea, kept OUT of identity like all provenance), water plane, sky/lighting/post effects:
  all D15-side. A material change moves the VIEW digest and never the carried witness —
  already the frozen law. The browser terrain panel joins `tools/editor/` as a consumer in
  the `calculationViz` pattern (off-gate machine shop; the shape crosses the admission
  boundary, the witness stays behind `verify.py`), built under the idle law from its first
  line.
- **T4 — named, not scoped (each its own slice, each currently zero code):** splines/
  roads/rivers as authored `URDR-WORLD-3` statics; multi-tile worlds riding the D16 seam
  law (the composition theorem is already measured — T19); erosion as bounded-regime
  iterated integer transport (field/criticality territory: conservation rows, refusal at
  the bound); a worker/offscreen renderer for the panel.

## 5. Robustness deltas vs the goal, graded

Claimed (buildable and gate-checkable): bit-identical terrain from a seed across hosts
(theirs: float noise, no such promise); goldens + typed refusals where their UI silently
clamps; identity/presentation separation (palette and lighting can never move the terrain
digest); the idle law versus their opt-in toggle; provenance recorded, never trusted.

NOT claimed: feature parity. Realistic water shading, HDR skies, erosion visuals, and
post-FX polish are months of presentation work — DECLARED targets at best, and the D5
ledger will say exactly that if and when any of them start. Nothing in this plan makes the
studio "better rendered" than zyfod; it makes it *honest, reproducible, and cool-running*.

## 6. Open reads before building

`tools/editor/urdr_designer.html` + `replay.py` (how the consumer renders and invalidates),
`tools/calculationViz/` (the machine-shop panel pattern + bridge scripts), `tools/frontend/
canon_ref.py` (the exact URDROBJ2 canon call). To be read when the bridge returns; T1
depends on none of them.
