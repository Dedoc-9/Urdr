# tools/render — deterministic fixed-point rasterizer (urdr-render, rung 1)

The first **MEASURED** slice of the D11 §4 renderer contract: turn
`State ⟶ Framebuffer` into `Digest(Frame) = SHA-256(canon(Frame))`, reproducible
bit-for-bit by any conforming **integer** placement. No floating point anywhere;
any i64 overflow is `RENDER-REFUSE`, never a saturate.

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
