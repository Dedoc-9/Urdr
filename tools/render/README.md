# tools/render — deterministic fixed-point rasterizer (urdr-render, rungs 1 & 2)

The first **MEASURED** slice of the D11 §4 renderer contract: turn
`State ⟶ Framebuffer` into `Digest(Frame) = SHA-256(canon(Frame))`, reproducible
bit-for-bit by any conforming **integer** placement. No floating point anywhere;
any i64 overflow is `RENDER-REFUSE`, never a saturate — **rung 1 enforces that
per-intermediate via `_g()`; rung 2 enforces it at the DOOR instead**, because its
depth arithmetic is unguarded and Python integers do not overflow (see
`renderbound.py`, and "the sentence this README used to carry" below). **Rung 1**
(`raster.py`) is flat 2D coverage; **rung 2** (`raster3d.py`) adds exact **3D
depth** — z-buffer occlusion + near/far/screen clipping.

## The sentence this README used to carry

The line above used to read, without qualification, that *any* i64 overflow is a
refusal. That was true of rung 1 and **false of rung 2**, which added three
products — `eb*z0 + ec*z1 + ea*z2`, the near/far clip `zfar*den`, and the depth
test `num*cd` — and guarded none of them. `DepthFramebuffer(4096, 2, 0, 2⁴⁰)` was
admitted by a constructor whose only size check was `w > 4096 or h > 4096`, and on
it **4088 fragments survive the near/far clip under exact arithmetic and 0 survive
under two's-complement i64**, with no refusal from either placement. Every
conformance scene is 16×16 with `zfar ≤ 100`, so the pinned corpus sat thirty-two
bits below the divergence and never saw it — `sample ≠ universal`. `renderbound.py`
replaces that constant with a decided joint bound
`(w·SUB−1)(h·SUB−1)·max(|znear|,|zfar|) ≤ 2⁶³−1` and a typed `RENDER-REFUSE`;
`docs/renderbound_brief.md` and gate stage `render_bound` carry the derivation.
**No conformance digest changed.**

## Rung 2 — exact 3D depth (`raster3d.py`)

True occlusion (objects hide what is behind them), still exact and deterministic
with **no float and no division**. Per-vertex integer depth; per-pixel depth is
the exact rational barycentric `(w0·z0+w1·z1+w2·z2)/(w0+w1+w2)` over the integer
edge-function weights; the **depth test is a cross-multiplication**
`num·den' < num'·den` (positive denominators), so the z-buffer stays exact.
Near/far clip keeps `znear·den ≤ num ≤ zfar·den`; screen clip never writes out of
bounds. Occlusion is **order-independent for distinct depths** (nearest wins) —
the frame is a function of the *set* of triangles **including at equal depth**, where
ownership goes to the smaller written datum rather than to whichever fragment arrived
first. That tie used to be resolved by draw order and was defended here as "the
non-vacuity proving depth is load-bearing" — which it never established, since order
dependence shows only that *something* order-sensitive exists. `render3d-selftest` now
perturbs depth and the tie-break separately at fixed submission order, and
`render3d-permutation` checks all six orderings of a three-fragment soup agree.
Keying on the *stored* datum is what makes the order total on outcomes: two fragments
equal in `(depth, value)` write identical bytes, so the residual tie is unobservable.
No pinned scene contains an equal-depth overlap, so no conformance digest moved.
Construction is admitted by the derived bound in `renderbound.py`, not by a chosen
constant. Scenes
(`scenes3d.py`) → `conformance3d.txt`; gated by `render3d`; falsified in
`tests/test_raster3d.py`; cross-placed by `urdr_render_rs` (`C3D` corpus). The
frame law is the same rung-1 `URDRFB1` color image. Scope: orthographic depth;
perspective-correct interpolation, blending, and geometric clip are a later rung.

## What is proven (rung 1)

Five of §4's eight obligations, **within the reference placement**:

- **fixed-point viewport transform** — NDC → subpixel via `urdr-math.floor_divmod`.
- **exact edge functions** — integer cross products, no epsilon.
- **top-left fill rule** — a shared edge is covered *exactly once* (two triangles
  tile a square: 0 gaps, 0 double-draws; the `closed` rule double-covers — the
  non-vacuity control).
- **deterministic sampling** — pixel-center, fixed scan order.
- **canonical serialization** — `MAGIC | W | H | C | row-major pixels` → SHA-256.

Plus integer, **endpoint-symmetric** line rasterization (`line(A,B) == line(B,A)`).

## What is NOT claimed (honest scope)

This is *implementation-agreement on a stated corpus and refusal set, in one
placement*. It is **not** a second-independent-rasterizer agreement (the D8
cross-placement rung — the next step), **not** GPU determinism (there is no GPU),
**not** completeness for all scenes. Depth buffering, blending, and
perspective-correct interpolation remain `DECLARED` (D11 §4).

## Files

- `raster.py` — the rasterizer: `viewport_x/y`, `edge`, `triangle_pixels`
  (`rule='topleft'`), `line_pixels`, `Framebuffer` (`serialize`, `digest`).
- `scenes.py` — the canonical corpus (`tri`, `tri_ndc`, `line_box`, `quad_two_tri`).
- `conformance.txt` — pinned frame-digest goldens (the witnesses).
- `../../tests/test_render.py` — the falsifiers (determinism, tiling, line
  coverage, overflow refusal, defect-caught).
- Gate: the `render` stage in `verify.py` (each scene reproduced twice + golden;
  corner-sample defect must diverge = non-vacuity).

## Run

    python3 tools/render/scenes.py      # print each scene's frame digest
    python3 -m unittest tests.test_render
    python3 verify.py                   # full gate (includes the render stage)

`every frame is a witness` — for these four frames, in this placement.
