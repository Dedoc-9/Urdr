<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/frontend — the authoring & view surface (D14 admission + D15 view contract)

The layer between humans/tools and the sealed authority: multiple authoring modalities
converge on ONE canonical object (`URDROBJ2`, D14), and one one-way bridge exports the
authoritative frame to any replaceable renderer (`URDR-VIEW-1`, D15). Nothing here is
authority — it feeds it (admission) or depicts it (view).

## Index

- `canon_ref.py` — executable form of the **D14** front-end admission contract: the
  reference canon every front end must reproduce bit-for-bit, plus the obligations a
  design must satisfy to be admitted. Gate stage `frontend_contract`.
- `svg_import.py` — an **SVG → `URDROBJ2`** importer admitted under D14 (deterministic
  parse, fixed-tolerance flatten, integer snap, shared canon; a declared subset that
  *refuses* rather than approximates). Gate stage `svg_import`.
- `rigidity_verdict.py` — an **exact** rigidity certificate for a canonical object
  (a 2D framework): RIGID/FLEXIBLE + rank + degrees of freedom + which vertices move,
  over ℤ, via the cross-placed `tools/intla/rigidity`. Gate stage `rigidity_verdict`.
- `view_export.py` — the **D15** view-export contract (layer 2): derives a
  `URDR-VIEW-1` frame that CARRIES the authoritative witness. Gate stage `view_export`.
- `view_viewer.html` — an independent three.js **reference viewer** (D15 placement):
  consumes a view export, proves the contract is renderer-agnostic.
- `canon_ref` also underpins `tools/frontfps` (the FPS/MMO authoring line) and the
  photo tracer (`tools/tracer`).
- `conformance_frontend.txt`, `conformance_svg.txt`, `conformance_rigidity.txt`,
  `conformance_view.txt` — pinned goldens for the four gate stages.
- `hw_view.json` — a sample `URDR-VIEW-1` export instance.

## Whitepaper

**The convergence claim (D14).** Authoring is a *many-to-one* problem: a designer, an
SVG file, a traced photo, a future CAD/procedural importer must all mean the same
object or none of them can be trusted. `canon_ref` is the reference the way the Python
placement is the reference for C99/Rust — every modality's output is canonicalized and
identity is minted here, so two front ends agree bit-for-bit or the gate reddens.
Identity is **geometry only**: provenance (which tool drew it) is excluded from the
digest by law, so a re-import through a different modality is the *same* object.

**The firewall (D15).** Three layers, one-way: **Authority** (Urðr) → **View contract**
(`view_export`) → **Presentation** (three.js/Unreal/Godot/Vulkan — replaceable). A view
frame is a *lossy projection* that carries the authoritative witness as a bound
reference; there is no inverse back to authority (two authority states can collapse to
one view). The renderer can never feed authority — that one-way property is a gate row,
not a comment.

**Observability that is authority, not decoration (`rigidity_verdict`).** Because a
canonical object *is* a rigidity framework, the exact-integer rigidity layer answers
"does this structure flex, and where?" as an exact ℤ verdict (rank + dof + moving
vertices), not a float readout — cross-placed through urdr-math so the answer is
identical across languages.

**Grade.** All four surfaces are `MEASURED (reference)` via their gate stages with
red-first falsifiers; `rigidity` is additionally cross-placed (C99 + Rust via
urdr-math). The native renderer downstream of D15 is out of scope by its own law and
stays `NOT_MEASURED` for performance until the sealed bench protocol runs.

## Dev notes

- Run any surface directly, e.g. `python tools/frontend/svg_import.py <in.svg>`; the
  editor (`tools/editor`) and the CLI import share `canon_ref`, so their digests match.
- **Refuse, never approximate:** the SVG importer rejects out-of-subset input with a
  typed refusal — extend the *declared subset* deliberately, never silently widen it.
- **Provenance is not identity:** if you touch the canon, keep provenance out of the
  digest or you will fork every modality's identity (a `world_digest` fold defect is
  the pinned falsifier for exactly this).
- View exports must remain a strict projection — if you can reconstruct authority from a
  view frame you have broken the firewall; the lossiness test is in the gate.
- Cross-placement of the rigidity certificate lives in `tools/intla/rigidity_c` and
  `rigidity_rs` (via `urdr_math_c`/`urdr_math_rs`).
