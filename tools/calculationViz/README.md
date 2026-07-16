<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/calculationViz/` — exploratory math visualizer (presentation, off-gate)

**Grade: presentation layer, `NOT_MEASURED`, outside the URDR gate.** This tool adds
**0 gate rows / 0 unit falsifiers / 0 placements**. It renders in browser IEEE double
(float); nothing it draws is an authoritative or MEASURED result. It exists to *depict* and
to *teach*, never to *feed* the authority. Where this note and `spec/D5-ledger.md` disagree,
D5 wins.

## Index

| Path | What it is |
|---|---|
| [`calculation_viz.html`](calculation_viz.html) | A single-file, dependency-free page. A dropdown of "kinds of math"; user-entered equations passed through a **bounded admission grammar** (typed `VIZ-REFUSE`, never a silent approximation); 2D/3D rendering on a canvas; a read-only **window onto the verified topology module** (`URDRPD1`); and a **topology wireframe editor** (build/drag/save complexes). Opens straight in a browser — no server, no build, no backend. |
| [`verify_complex.py`](verify_complex.py) | The **real authority bridge**: reads a `URDR-COMPLEX-1` JSON saved by the editor and runs the **gated** module (`urdr_homology.betti ∘ close_faces`) to print the authoritative Betti/χ, and whether the browser PREVIEW agreed. This is the MEASURED path the in-app "Verify" button stands in for. |
| [`bridge_to_world.py`](bridge_to_world.py) | The **game-designer bridge**: reads a `URDR-COMPLEX-1` object and emits a `URDR-WORLD-3` authored world for the **Urðr Designer** (`tools/editor/load_world.py`) and the gated netcode (`tools/netcode/worldstep.py`). Carries the 3D wireframe (verts + edges), **auto-grounds** it base-on-the-floor, and does the integer authoring snap the format requires. Verified end-to-end: the output both renders in the designer and loads in `worldstep` with no `WORLD-REFUSE`. |

The page has three kinds of "domain":

- **Toy graphers (standalone, float).** `2D function y=f(x)`, `2D vector field (Fx,Fy)`,
  `2D parametric (x(t),y(t))`, and `3D surface z=f(x,y)` with a **free-fly perspective orbit
  camera** (drag to orbit to any angle, wheel to zoom, shift-drag to pan, double-click to
  reset; depth-sorted shaded facets so it reads from any side). The user types their own
  expression; the parser admits or refuses it; the canvas plots the admitted expression in
  browser float. Clearly labelled *exploratory / NOT MEASURED*.
- **Verified window (read-only).** `Persistent homology (URDRPD1)` displays the *actual*
  goldens produced by `tools/homology/urdr_homology.py` — known-answer Betti numbers, the
  square-Rips persistence diagram, and the anti-cheat / OOB free-space decomposition — each
  with its witness digest. The values are **baked verbatim from the module** (reproduced C99
  `homology_c` + Rust `homology_rs`, gate stage `homology`). The page *shows* them; it does
  not recompute them in the browser.
- **Topology editor (authoring surface → authority).** `Topology wireframe editor` — build a
  simplicial complex (vertices / edges / faces) with the free-fly orbit camera: click to add,
  connect edges/faces, drag vertices in 3D, delete. **Starters** (all Betti/χ verified against
  the module before baking): tetrahedron & octahedron → S² `[1,0,1]`, triangle → S¹ `[1,1,0]`,
  cylinder → annulus `[1,1,0]`, torus → T² `[1,2,1]`, **projective plane → RP² `[1,1,1]`** (the
  𝔽₂ showcase), plus two-edges and figure-8. **Multiple objects, one file**: an *append (merge)*
  toggle drops a starter into the current scene (reindexed + offset) instead of replacing, and
  `+Edge`/`+Face` connect vertices across components; everything saves to one `URDR-COMPLEX-1`
  JSON. **Machine-shop tools**: a selected-vertex **exact-coordinate editor**, **grid snap** (on
  place/drag + snap-all), **mirror X/Y/Z** for symmetry, and a live **measurements** panel (edge
  lengths min/max/mean + bounding box W×H×D). The topology readout (`V/E/F`, `χ`, `β`) uses the
  module's own **division-free 𝔽₂ XOR** (BigInt), verified under node to reproduce
  `urdr_homology.py` bit-for-bit — yet graded **PREVIEW — not the gated witness** (JS is not a
  gated placement); coordinates and lengths are browser float, labelled as such. **Verify** is
  now *wired*: it shows the exact 𝔽₂ result, the real command against `verify_complex.py`, and a
  paste-back box that confirms browser == engine — an honest loop, no faked backend call.
  **Export → game world** bridges the object into the Urðr Designer: a one-click
  `URDR-WORLD-3` export (mirroring `bridge_to_world.py`) that carries the wireframe,
  **auto-grounds** it base-on-the-floor, and integer-snaps it — verified to render in the
  designer and load in the gated netcode.

## Whitepaper

The engine's authority is exact integer / fixed-point math whose every transition is
content-addressed and cross-checked behind `verify.py`. A visualizer cannot share that
authority: a browser plots in float, non-deterministically across machines. So the honest
placement — and the one the D15 view contract already prescribes — is **layer 3,
presentation, behind the one-way firewall**: `calculationViz` may *depict* authority (the
homology window) or offer *exploratory* float math (the graphers), but it can never feed
either back into the gate. Presentation ≠ authority. That is why the whole tool is graded
`NOT_MEASURED` and lives outside the gate on purpose, exactly like `tools/editor/` and
`tools/frontend/view_viewer.html`.

The one place `calculationViz` *does* honor the engine's discipline is the **"scoped
bounds"** on user equations. Rather than `eval`-ing arbitrary strings or silently coercing
malformed input, every expression passes through a small recursive-descent parser with a
**declared grammar** — a whitelisted set of operators, functions, constants, and
per-domain variables, plus hard length / depth / node ceilings. Anything outside those
bounds is rejected with a **typed `VIZ-REFUSE` and a human reason** (`unknown function
'foo'`, `variable 'y' is not in scope here`, `nesting too deep`, …). This is the D14 /
`frontfps_text` admission law applied to equation entry: **refuse, never approximate.** The
grammar is pure and deterministic — given `(expression, allowed-vars)` it returns the same
admit/refuse verdict everywhere — so the *bounds themselves are testable* even though the
*rendering* is not gate-provable. A node harness (see Dev notes) re-runs the in-page
self-check cases to prove it.

The design is **adaptable-first**. Every "kind of math" is one object in a `DOMAINS`
registry: a label, an input schema (which fields, which variables each admits), default
bounds, and a `render(compiled)` function. Adding a new area — a Marangoni/fluid window, a
soft-body sandbox, a new grapher — is *pushing one object*, not rewiring the tool. The
first slice ships five domains precisely to exercise the registry across different input
shapes (one scalar function, a two-component vector field, a parametric pair, a 3D height
field, and a zero-input verified window), so the extension surface is proven, not asserted.

The honest boundary between admission and runtime is kept explicit. **Admission** is
*syntactic + scope*: can this expression be accepted at all? **Runtime range** is separate:
an admitted expression may still evaluate to ∞/NaN at some sample (`1/x` at 0, `log` of a
negative), and the plotter simply shows a *gap* there — it does not retroactively refuse.
Conflating the two would make the bounds dishonest; they are deliberately distinct.

The **Topology editor** is the one domain that touches the authority boundary — and it does so
the honest way, as a **D14-style authoring surface**. It *produces* a canonical complex (the
`URDR-COMPLEX-1` JSON, whose `maximal` simplices are the identity — geometry excluded); the
gated module `urdr_homology.py` is what turns that complex into the certified Betti/witness. The
in-browser readout is genuinely exact (the module's division-free 𝔽₂ XOR, reimplemented in
BigInt and verified equal under node), but exactness is *not* authority: JS is not a gated,
cross-placed, frozen placement, so the readout is graded **PREVIEW** and the coordinates are
flagged **browser float, not Q32.32**. "Verify with Engine" shows the seam rather than faking it.
Nothing feeds back into the gate — the editor only ever emits an admissible artifact. The same
authoring→authority *discipline* extends to the game formats already built (authored worlds
`URDR-WORLD-3`; the OOB anti-cheat arena in the homology module). Those are different data shapes
— an AABB set, a solid/free grid — not a simplicial complex, so a future editor **export mode**
that emits them (not a direct reinterpretation of `maximal`) is the next bridge to wire.

## Dev notes

- **Run it:** open `calculation_viz.html` in any browser. No server, no dependencies.
- **The scoped bounds** (declared constants of the grammar):
  operators `+ - * / %` and `^` (or `**`), right-associative power; constants `pi e tau`;
  functions `sin cos tan asin acos atan atan2 sinh cosh tanh exp log ln log10 log2 sqrt
  cbrt abs sign floor ceil round min max pow mod hypot`; variables are per-domain (`x`;
  `x,y`; `t`); ceilings `≤ 512` chars, `≤ 48` nesting depth, `≤ 2000` nodes. Everything else
  is a typed `VIZ-REFUSE`.
- **Explicit multiplication only, by decision.** `3*x` is admitted; `3x` is *refused*
  (`unexpected 'x'`). Implicit multiplication is ambiguous (`e2`, `sin2`) so it is out of
  the bounded grammar — a deliberate "refuse, don't guess," not a gap.
- **Re-verify the bounds under node** (the parser is pure; this is a presentation self-test,
  *not* the authority gate):

  ```sh
  cd tools/calculationViz
  awk '/\/\/==CALCVIZ-CORE-START==/{f=1} f{print} /\/\/==CALCVIZ-CORE-END==/{f=0}' \
      calculation_viz.html > /tmp/core.js
  node -e 'var C=require("/tmp/core.js");var s=C.runSelfCheck();
           console.log(s.pass+"/"+s.total,s.fail?"FAIL":"PASS");process.exit(s.fail?1:0)'
  ```

  The same self-check runs in-page (the collapsible **Parser self-check** panel) on load.
- **The 3D orbit camera is real perspective + free-fly** — drag to orbit to any angle, wheel
  to zoom, shift-drag to pan, double-click to reset; facets are depth-sorted (painter's) and
  two-side shaded so the surface reads from any viewpoint. Its pure math lives between the
  `//==CALCVIZ-CAM-…==` markers (no DOM refs) and is node-tested the same way the parser is —
  basis orthonormality, `target → screen center`, `+y → right`, `+z → up`, depth ordering,
  behind-camera clipping, and pole-guard finiteness at `pitch = ±π/2`:

  ```sh
  awk '/CALCVIZ-CAM-START/{f=1} f{print} /CALCVIZ-CAM-END/{f=0}' \
      calculation_viz.html > /tmp/cam.js   # then require("/tmp/cam.js").CAM and assert invariants
  ```

  It stays presentation float — orbiting is not a MEASURED capability, just a nicer window.
- **Topology editor — the authoring→authority bridge.** The `Topology` domain builds a complex
  and saves `URDR-COMPLEX-1` JSON: `{ vertices:[[x,y,z]…] (float, presentation), maximal:[[i]…,
  [i,j]…, [i,j,k]…] (the canonical combinatorial identity), edges, faces, preview:{V,E,F,chi,
  betti,grade:"PREVIEW-NOT-GATED"} }`. The Betti preview uses the module's exact division-free
  𝔽₂ XOR (BigInt) — extract the `//==CALCVIZ-TOPO-…==` block and it reproduces
  `urdr_homology.py` bit-for-bit (verified: sphere `[1,0,1]`, figure-8 `[1,2,0]`, isolated
  `[3,0,0]`, octahedron `[1,0,1]`, cylinder `[1,1,0]`, torus `[1,2,1]`, RP² `[1,1,1]`). Geometry
  helpers (edge lengths / bbox / grid snap) live in the `//==CALCVIZ-MEAS-…==` block, also
  node-tested — those are float **design aids**, not authority.
- **Verify is wired (honestly), without a backend.** The button computes the exact 𝔽₂ result
  in-browser and offers a **paste-back** check; the authoritative MEASURED verdict is one command
  against the real bridge script:

  ```sh
  PYTHONHASHSEED=0 PYTHONUTF8=1 python3 tools/calculationViz/verify_complex.py complex.urdr.json
  ```

  It prints the module's Betti/χ and whether the browser PREVIEW agreed. The **next rung**
  (unbuilt, `DECLARED`): fold that into a gated `load_complex` + Q32.32 conversion + a red-first
  witness test, promoting the JSON to an officially authority-ingestible input (the
  D14-for-complexes admission).
- **Bridge to the game designer (`bridge_to_world.py` + the in-app "Export → game world"
  button).** Emits a `URDR-WORLD-3` object the Urðr Designer renders and the gated netcode
  loads. It carries the wireframe (3D verts + edges), **auto-grounds** it (in URDR-WORLD-3
  object-local coords larger-y is *lower* and `load_world` stands the base on the road, so the
  bridge maps `local_y = up_max − up` — the lowest source point becomes the base, on the floor),
  and does the integer **authoring snap** the format demands (a float in the export is
  `WORLD-REFUSE`; snapping is the legitimate authoring step, not a runtime round). Honest scope:
  it carries *geometry + placement*, **not topology** — Betti/witness do not travel; that stays
  behind `verify.py`. Two grounding modes: default **lowest-point** (rests on its lowest vertex),
  or **`--rest-face`** which rotates the object to sit flat on a stable face (a convex-hull face
  whose centroid projects inside it, made horizontal via a Rodrigues rotation, then snapped).

  ```sh
  python3 tools/calculationViz/bridge_to_world.py complex.urdr.json world.json          # static prop, lowest-point
  python3 tools/calculationViz/bridge_to_world.py complex.urdr.json world.json --rest-face   # sits flat on a face
  python3 tools/editor/load_world.py world.json frame.pgm                               # designer renders it
  python3 tools/calculationViz/bridge_to_world.py complex.urdr.json wdyn.json --body dynamic
  #   -> feed wdyn.json to worldstep.world_from_export (gated N4) — loads, no WORLD-REFUSE
  ```

  Verified end-to-end: the bridge output renders through `load_world.py` (URDRFB1 frame) **and**
  loads in `worldstep` (dynamic). The in-app button's `WORLD` block (`//==CALCVIZ-WORLD-…==`,
  node-tested) produces **byte-identical geometry** to the script at the same `--scale`
  (digests differ only in scheme: FNV in-browser vs SHA-256 in the script — both are internal
  object ids). The OOB anti-cheat arena (a solid/free grid) remains a separate future export.
- **Add a math area (the registry contract).** Append one object to `DOMAINS`:
  `{ id, label, note, inputs:[{key,label,vars,def}], bounds:{xmin,xmax,ymin,ymax},
  render(compiled) }`, where `compiled[key].eval(env)` is the admitted evaluator (or
  `{kind:"verified", render}` for a read-only module window). Nothing else changes.
- **Homology goldens are baked, not recomputed.** They come from
  `PYTHONHASHSEED=0 PYTHONUTF8=1 python3 tools/homology/urdr_homology.py`. If that module's
  laws change, re-run it and update the `HOM` block — the digests are the provenance.
- **The honest next rung (unbuilt, `DECLARED`).** If the *bounds* should be gate-enforced
  rather than presentation-tested, the move is a **Python reference grammar** with the same
  admit/refuse law plus a `tests/test_calcviz_grammar.py` falsifier set mirroring these
  cases — the generalized front-end-admission (D14-family) pattern. That would put the
  *bounds* under the gate; the *rendering* stays presentation forever. Not built here; named
  so the boundary is honest.
