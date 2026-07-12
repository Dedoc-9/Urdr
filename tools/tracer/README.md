<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/tracer/` — photo/still → wireframe design tracer

Turns a silhouette in an image into a content-addressed `URDROBJ2` design the browser
editor loads directly (⤒ Open) — a way to author more accurate, less-boxy objects than
hand-drawing, from a photo or a frame grabbed from an animation.

Stdlib-only, offline, **zero dependencies**: PNG is decoded from scratch via `zlib`
(all five scanline filters; grayscale / RGB / RGBA, 8-bit), the netpbm formats
(PGM/PPM binary) by hand. A format the stdlib cannot decode — JPEG (DCT), GIF (LZW) —
is a typed `TRACE-REFUSE`, never a silent dependency. Convert to PNG first.

## Use it

```
python3 photo_trace.py object.png [out.json] [--name NAME] [--verts N] [--invert] [--thresh T]
# writes a URDR-PROJECT-1; open it in urdr_designer.html via ⤒ Open. Prints the digest.
```

`--verts N` targets the simplified vertex count (default 24); `--invert` if the object
is lighter than its background; `--thresh T` overrides the automatic Otsu threshold.

## The pipeline (every step deterministic)

decode → grayscale → **Otsu** threshold → **largest 8-connected component** → **Moore**
boundary trace → **Ramer–Douglas–Peucker** simplify (deterministic ε binary-search to
the target vertex count) → **integer snap**. Authoring snaps to integers; the N4
runtime never rounds (`WORLD-REFUSE`), so every emitted coordinate is already an
integer here.

## The gate claim — and its honest boundary

The **aesthetic quality** of a trace is not gate-able and is **not claimed**. What *is*
gate-tested (`photo_trace` stage, `tests/test_photo_trace.py`) is the deterministic
core, and one invariant is load-bearing: identity is minted by the **same `URDROBJ2`
canon the editor uses** —
`SHA-256("URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…")`, edges min-first + lexically sorted — so a
CLI-traced design and the browser agree on the digest **bit-for-bit**. The golden
(`conformance_tracer.txt` `square_canon`) is the digest the *actual* browser
`canonBytes` produces; a drift in either canon reddens the gate. Decode determinism,
the typed refusals, integer output, and a non-vacuity defect (an un-normalized-edge
canon must diverge) are pinned alongside it.

**Grade:** deterministic core `MEASURED`; the tool overall is `SPECULATIVE` — an
authoring aid, like the editor it feeds. Single image → one design; multi-frame /
animation, and interior structure beyond the outer silhouette, are declared
extensions.
