<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D14 — The front-end admission contract

Status: **MEASURED** (the checkable core is gate-enforced; §obligations are normative).
This document states the single, testable criterion by which any authoring modality —
the designer, the photo tracer, a future SVG or CAD importer, a procedural generator —
becomes a first-class source of authoritative assets. It replaces bespoke
per-importer correctness arguments with one admission ladder.

The observation that earned this contract: multiple independent front ends have begun
converging on the same authoritative representation (`URDROBJ2`). When that happens,
the convergence itself deserves to be a law rather than a coincidence. `the engine
never knows — or needs to know — which authoring tool produced an object`.

## 1. The contract

> A front end is admitted into the authoritative asset pipeline **iff** it
> deterministically normalizes its input into the canonical `URDROBJ2`
> representation, reproduces the pinned canonical digest through its **own**
> implementation, emits **only integer-snapped** geometry, **refuses** ambiguous or
> unsupported constructs with typed refusals rather than approximating them, and
> leaves downstream physics, rendering, replay, and networking **unable to
> distinguish** which front end produced the object except through declared
> provenance metadata.

Five clauses, each a checked obligation:

1. **Deterministic normalization.** The same input produces the same object on every
   host — no float nondeterminism, no clock, no RNG, no iteration-order dependence in
   the path from input to canonical geometry.
2. **Reproduce the canon through its own implementation.** The front end computes the
   `URDROBJ2` digest itself and it agrees, bit-for-bit, with the reference
   (`tools/frontend/canon_ref.py`) and the browser editor. Independent implementations
   agreeing — the cross-placement discipline (D8), applied to front ends.
3. **Integer-snapped geometry only.** Every emitted coordinate is an integer;
   authoring snaps, the runtime never rounds. A non-integer coordinate is
   `CONTRACT-REFUSE`. (This is the N4/`WORLD-REFUSE` boundary seen from one layer up.)
4. **Typed refusal, never approximation.** A construct the front end cannot faithfully
   normalize (a JPEG the stdlib cannot decode; an SVG feature outside the stated
   subset; a degenerate silhouette) is a typed refusal, not a guess.
5. **Provenance is metadata, not identity.** Which tool made the object, its source
   file, an author — these may be carried alongside, but they never enter the digest.
   Two objects with identical geometry and different provenance are the **same**
   `URDROBJ2` object.

## 2. The canonical object law (`URDROBJ2`)

    Digest = SHA-256("URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…")

vertices in order (each `x,y,z` after integer snap); edges normalized min-first and
the edge list lexically sorted; joined by `|`. This is byte-identical to the editor's
`canonBytes` (`tools/editor/urdr_designer.html`) and to `canon_ref.canon`. Identity is
**geometry only** — the digest is a function of `(verts, edges)` and nothing else.

## 3. The admission ladder (every new front end)

1. Define deterministic normalization of the input.
2. Specify the refusal semantics (the typed codes; what is out of subset).
3. Produce canonical `URDROBJ2` through the front end's own code.
4. Match the pinned canon corpus (`tools/frontend/conformance_frontend.txt`).
5. Add red-first defect fixtures (a mis-normalization that must be caught).
6. Cross-place if the front end becomes load-bearing (a second implementation
   reproducing the corpus).
7. Admit — record the grade in D5, honestly.

Steps 1–5 are mandatory for any modality that claims to produce first-class assets;
6 escalates with importance, exactly as the placement ladder does.

## 4. Admitted modalities and their grades

| Front end | Input | Deterministic core | Grade |
|---|---|---|---|
| **Designer** (`urdr_designer.html`, incl. procedural primitives: N-gon, rounded barrier) | mouse / draw | canon = `canonBytes` | `MEASURED` (it defines the golden the others match) |
| **Photo tracer** (`tools/tracer/photo_trace.py`) | PNG / PGM / PPM still | Otsu → Moore → RDP → snap → canon | `MEASURED` (deterministic core; aesthetics out of scope) |
| **SVG importer** (`tools/frontend/svg_import.py`) | `.svg` vector paths (declared subset) | parse → flatten cubics at a fixed tolerance → snap → canon | `MEASURED` — three SVG constructs of one square reproduce the shared canon; cubic flatten pinned; out-of-subset → `SVG-REFUSE` |
| CAD / DXF importer | `.dxf` | declared | `DECLARED` |
| Procedural generator | seed + params | declared (reproducible seed) | `DECLARED` |
| Heightmap / point-cloud / multi-view / video-tracked | various | declared, deterministic-where-possible | `DECLARED` |

The reference (`canon_ref.py`) is the shared law; the browser and the tracer are two
independent implementations that reproduce it. The gate proves all three agree over a
four-shape corpus (`frontend_contract` stage), and that provenance is inert to
identity.

## 5. What is enforced now

`verify.py` stage `frontend-contract` (`tests/test_frontend_contract.py`):

- `frontend-contract:reference` — the reference canon reproduces the **browser**
  goldens over `{square, tri, penta, hex6}`;
- `frontend-contract:tracer` — the photo tracer's **independent** canon reproduces the
  same corpus (two implementations, one law);
- `frontend-contract-provenance` — identical geometry with differing provenance yields
  the identical digest (downstream cannot tell the front end apart);
- `frontend-contract-selftest` — non-integer geometry is `CONTRACT-REFUSE`, and a
  provenance-folding defect canon **diverges** from the golden (the invariant is real).

## 6. Honest scope

The contract certifies the **identity law and the admission obligations**, not the
**aesthetic quality** of any extraction — no gate can say a trace "looks like a
truck", and none claims to. A front end can be admitted (its output is a well-formed,
correctly-identified `URDROBJ2` object) while its extraction is crude; admission is
about authoritative interchangeability, not artistry. `once an asset satisfies this
contract, every downstream subsystem consumes the same authoritative object — a
stronger, more enduring property than any individual importer`.

## See also

- `spec/D8-portable-kernel.md` (the cross-placement discipline this generalizes)
- `spec/D12-versions.md` (the freeze manifest; `conformance_frontend.txt` is pinned)
- `tools/frontend/canon_ref.py` (the executable contract)
- `tools/tracer/`, `tools/editor/` (the two admitted implementations)
- `docs/THEOREMS.md` (the measured floor)
