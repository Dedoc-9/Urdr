<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/calculationViz/machineshop/` — the Machine Shop kit (author → ground → bridge → game)

**Grade: presentation kit, `NOT_MEASURED`, off-gate.** A dedicated machine-shop authoring
surface that plugs into the game frontend (the **Urðr Designer**) through the *verified
bridge* — not by fusing code. It adds **0 gate rows / 0 falsifiers / 0 placements**.

## Index

| Path | What it is |
|---|---|
| [`machineshop.html`](machineshop.html) | The dedicated Machine Shop **launcher**: a landing page with the author→game workflow and a button that opens the CAD editor in machine-shop mode (`../calculation_viz.html#machineshop`) in a new tab. Reuses the same engine as `calculationViz` — one source of truth, no duplication. Opens in a browser; no server. |

Two files elsewhere do the actual work (the kit points at them, it does not re-implement them):

- [`../calculation_viz.html`](../calculation_viz.html) — the CAD editor (Topology tab): 3D
  wireframe build/drag, grid snap, exact-coordinate editor, mirror, measurements, multi-object,
  and the one-click **Export → game world (grounded)**.
- [`../bridge_to_world.py`](../bridge_to_world.py) — the file bridge: `URDR-COMPLEX-1` →
  `URDR-WORLD-3`, auto-grounded (`--rest-face` optional), integer authoring-snap.

## Whitepaper

"Welded to the frontend" is done the honest way. The machine shop is a **presentation** tool
(browser float, off-gate); the game frontend (`tools/editor/` Designer, `tools/netcode/worldstep`)
has its own **gated** formats with the integer `WORLD-REFUSE` law. Fusing the two would couple
off-gate presentation to the gated authoring pipeline and duplicate the Designer. Instead the weld
is a **data seam**: the shop authors an object, and the bridge *admits* it into the game —
projecting to a `URDR-WORLD-3` object, grounding it to the floor, and snapping float coordinates
to the integer grid (a float in the export is `WORLD-REFUSE`; the snap is the legitimate authoring
step, the runtime never rounds). That seam is the D14/D15 firewall working, and it is verified
end-to-end: a bridged object both renders in the Designer (`load_world.py` → URDRFB1 frame) and
loads in the gated netcode (`worldstep.world_from_export`, dynamic) with no refusal.

The kit **reuses** the engine rather than copying it. `machineshop.html` launches
`calculation_viz.html#machineshop`; the CAD math (camera, measurements, complex, world bridge) has
exactly one implementation, node-tested, shared. This is a deliberate engineering choice — a
second copy would drift out of sync with the verified original.

**Honest boundary.** The bridge carries **geometry + placement** — an object's shape and where it
stands. It does **not** carry topology: the object's Betti numbers / witness do not travel into the
game world (that stays behind `verify.py`). A pretty prop in the Designer is not a verified result.

## Dev notes

- **Run it:** open `machineshop.html` and click **Open editor** — it launches
  `../calculation_viz.html#machineshop` in a new tab (the `#machineshop` hash selects the CAD/Topology
  tab on load). It **launches rather than embeds** because browsers block `file://` iframes of local
  files; to embed inline instead, serve the folder over a local http server
  (`python3 -m http.server` from the repo root). The launcher needs no server.
- **The four-step flow:** build/measure → **Save JSON** (`complex.urdr.json`) → bridge
  (`bridge_to_world.py … --rest-face`) → **render/load** (`load_world.py`, or `worldstep` for a
  `--body dynamic` world). The in-app **Export → game world (grounded)** button does the bridge
  step in-browser (byte-identical geometry to the script).
- **Grounding modes:** default **lowest-point** (rests on its lowest vertex); **`--rest-face`**
  rotates the object so a stable convex-hull face (centroid projects inside it) lies flat on the
  floor, via a Rodrigues rotation, then snaps. Verified: a tetra bridges point-down by default and
  base-flat with `--rest-face`, and both render in the Designer.
- **Not fused into the frontend, by decision.** If you ever *do* want the shop hosted inside
  `urdr_designer.html`, the honest way is to keep the bridge as the boundary (import the
  `URDR-WORLD-3` the shop emits), not to share float presentation state with the gated authoring
  code. The next natural export is the OOB anti-cheat **arena** (a solid/free grid) — a different
  shape than a wireframe object, so it is a new bridge, not a reinterpretation.
