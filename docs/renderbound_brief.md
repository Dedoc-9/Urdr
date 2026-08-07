<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: renderbound-law -->
# `renderbound` — design brief (URDRRBD1, the rung-2 depth admission bound)

**Built**: 2026-08-07, as the first step of the coverage-witness arc. Not read into the READ
pass — that pass closed at P63 and this module postdates it.

## What it is

**The bound rung 2 shipped without.** `raster.py` (rung 1) routes every 2D intermediate
through `_g()`, so an i64 overflow there is `RENDER-REFUSE`. Rung 2 added three products —
the depth numerator `eb*z0 + ec*z1 + ea*z2`, the near/far clip `znear*den ≤ num ≤ zfar*den`,
and the depth test `num*cd < cn*den` — and guarded **none** of them. Python integers do not
overflow, so nothing complained. The Rust placement computes the first two in native `i64`
and widens only the third:

```rust
Some(cn) => (num as i128 * self.zden[i] as i128) < (cn as i128 * den as i128),
```

So the binding term is **not** the cross-multiply. It is the pair that stays narrow, and the
bound is linear in each factor rather than quadratic — the first derivation had it the other
way round, and the wrong version had the bigger number.

## The core law (what `renderbound-law` certifies)

**The maximum edge magnitude is decided, and it is attained.** Over a box `[0,Bx) × [0,By)`,
`max|(bx−ax)(py−ay) − (by−ay)(px−ax)| = (Bx−1)(By−1)` exactly. The gate **re-runs the full
triple search over all 49 rectangles on every pass** rather than citing this sentence, and
checks the stated witness `a=(0,0) b=(0,By−1) p=(Bx−1,0)` reaches it.

Attainment is not decoration. `voxin`'s door needs *one past the bound refuses, exactly at
the bound admits*, and the second half cannot be asserted about a magnitude nothing reaches.
The first estimate tried during derivation was `2(Bx−1)(By−1)` — a true upper bound, and
useless for exactly that reason. The form is also **rectangular**: `(Bx−1)²` passes every
square case, so a square-only sweep could not tell the two apart.

From the closed form, since the three edge weights inside a triangle are non-negative and
sum to `area`:

    (w·SUB − 1) · (h·SUB − 1) · max(|znear|, |zfar|)  ≤  2⁶³ − 1

## Why a resolution-only bound cannot be sound

`screen_bits ≤ 31`, hence `w ≤ 2²³` at eight subpixel bits, is the correct ceiling for the
rung-1 edge function. It mentions no depth range, and the divergence below is at `w = 4096`
— which it admits. **Replacing an arbitrary `4096` with a derived-*looking* constant that is
unsound in a dimension it never names is worse than leaving `4096` alone**, because `4096`
at least advertises that nobody decided it. `attestation ≠ authority`.

## The divergence, executed

`DepthFramebuffer(4096, 2, 0, 2⁴⁰)` was **admitted** by the old constructor, whose only size
check was `w > 4096 or h > 4096` and which raised an untyped `ValueError`. On one full-width
triangle, **4088 fragments survive the near/far clip under exact arithmetic and 0 survive
under two's-complement i64** — `zfar*den` wraps negative and the clip rejects everything.
Same input, two frames, no refusal on either side.

The pinned corpus never saw it: every conformance scene is 16×16 with `zfar ≤ 100`, so
`E_max·Zmax ≈ 2³¹` — thirty-two bits of headroom. The cross-placement agreement is certified
on a corpus, and the corpus is precisely the region where the unguarded arithmetic happens to
stay small. `sample ≠ universal` (L20), with a measured witness.

## Two bounds, kept apart

`admits()` is a **theorem**: exceed it and a conforming i64 placement computes a different
frame. `ALLOC_MAX_PIXELS` is a **declared policy**: `100000×100000` at `zfar=1` satisfies the
theorem and still exhausts memory. The refusal messages keep them distinguishable, because
fusing a resource limit into a correctness bound is how `4096` came to look like it meant
something.

## does_not_show

That any particular scene overflows — this bounds the worst case over the whole box, so it
refuses configurations a given triangle would survive. That `wrap_i64` describes every
toolchain: `-O` wraps, a debug build aborts, and the Python model is the former.

**The model is no longer the only evidence.** `urdr_render_rs/renderbound_falsifier.rs` is a
std-only Rust falsifier, sharing no code with the Python and live-compiled in **both
profiles** by gate stage `render_bound_placement`. Widened to `i128` it keeps **4088**
fragments — reproducing the Python exact count bit-for-bit, which is the control that makes
the fixture trustworthy — and in the `i64` the shipped placement actually uses for those two
expressions it keeps **0** under `-O` and **aborts** under debug (`attempt to multiply with
overflow`, exit 101). So the two Rust profiles disagree with each other as well as with
Python, and **an abort is not `RENDER-REFUSE`**: no code, no message, no witness, just an
absent frame. `renderbound-divergence` remains the model; `renderbound-placement` is the
measurement of it.

The scene is pinned inside the falsifier rather than passed in, because a falsifier whose
fixture is caller-supplied can be quietly aimed away from the defect. No published
conformance digest is affected; `conformance3d.txt` is unchanged. Nothing here is a renderer,
and nothing here says the frames are *right*. `integrity ≠ truth`.

## Falsifier

This brief cites `renderbound-law`: the exhaustive re-decision that `(Bx−1)(By−1)` is the
maximum and not merely an upper bound, together with its attaining witness. If the closed
form were ever loosened to an estimate, or the witness stopped reaching it, that row reddens
and this brief's central claim dies with it.
