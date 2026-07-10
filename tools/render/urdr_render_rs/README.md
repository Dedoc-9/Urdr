<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# urdr-render-rs — the independent rasterizer (D8 cross-placement, for pixels)

One self-contained Rust file (`urdr_render.rs`), std-only, **no crates, no cargo,
hand-rolled SHA-256** (lifted from `urdr-core-rs`, FIPS-checked at startup). It is
a faithful re-implementation of `tools/render/raster.py`'s rung-1 rasterizer in a
**different language / compiler / runtime**, judged solely by whether it
reproduces `tools/render/conformance.txt`.

This is the renderer's analog of `urdr-core-rs`: it turns *"the frame is
deterministic in our reference"* into *"the frame is bit-identical across
independent implementations."* That is the theorem worth having — the frame
digest is a property of the **specification**, not of one interpreter.

## Grade — read this before believing anything

- The Rust source existing: `IMPLEMENTED / DECLARED`.
- The **port logic** was cross-checked against the four goldens by mirroring this
  exact algorithm (its `fdiv`, byte layout, MAGIC) in Python: all four match,
  and the `--defect` MAGIC-corruption diverges on all — but that is still the
  *reference* language.
- **Convergence (`urdr-render-rs`): `SPECULATIVE` until the run below is green on
  a host with a toolchain.** An authoring sandbox without `rustc` cannot measure
  this. `declared ≠ verified`; `admitted ≠ trusted`.

## The run protocol (red-first — order matters)

PowerShell, from the repo root, `rustc >= 1.56` (any edition-2021 toolchain):

```powershell
# 0. build (plain rustc; no cargo, no crates)
rustc -O --edition 2021 -o urdr_render.exe tools\render\urdr_render_rs\urdr_render.rs

# 1. RED FIRST — the defect selftest must CATCH corrupted frames (exit 0 = caught)
.\urdr_render.exe --defect

# 2. the verdict — run it TWICE, identically (determinism is the floor)
.\urdr_render.exe
.\urdr_render.exe
```

Expected: `--defect` prints `[PASS] defect:<scene> divergence caught …` for all
four scenes and `URDR-RENDER-RS: defect caught`; the plain runs print
`[PASS] accept:<scene> digest …` for all four and `URDR-RENDER-RS: ADMITTED`,
identically both times.

`URDR-RENDER-RS: ADMITTED` twice + defect caught ⇒ **cross-placement MEASURED**:
a second, independent implementation reproduces every frame digest, and the
harness can redden. Paste the output back and the D5/D11 grade flips from
`SPECULATIVE` to `MEASURED` on your named host.

## What this does and does not establish

- **Does:** the four frame digests (`tri`, `tri_ndc`, `line_box`, `quad_two_tri`)
  are reproduced by an implementation that shares no code, language, or SHA-256
  with the reference — so they are not an artifact of Python.
- **Does not:** claim GPU determinism (there is no GPU), completeness for all
  scenes, or anything about depth/blend/perspective (still `DECLARED`, D11 §4).

## Files

- `urdr_render.rs` — the independent rasterizer + embedded corpus + `--defect`.
- Judged against `../conformance.txt` (the shared golden frame digests).
- Reference: `../raster.py`, `../scenes.py`; contract: `spec/D11-layer-contracts.md` §4.
