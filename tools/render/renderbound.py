# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-render: the DEPTH-PATH ADMISSION BOUND (URDRRBD1) — decided, not chosen.

`raster.py` (rung 1) routes every 2D intermediate through `_g()`, so an i64 overflow
there is `RENDER-REFUSE`. **`raster3d.py` (rung 2) has no guard at all.** Its three
added products — the depth numerator `eb*z0 + ec*z1 + ea*z2`, the near/far clip
`znear*den <= num <= zfar*den`, and the depth test `num*cd < cn*den` — are plain
Python integers, and Python integers do not overflow. The Rust placement computes the
first two in native `i64` and widens only the third (`urdr_render.rs`:

    Some(cn) => (num as i128 * self.zden[i] as i128) < (cn as i128 * den as i128),

). So the binding term is NOT the cross-multiply. It is the pair that stays narrow.

**The divergence is executed, not feared.** `DepthFramebuffer(4096, 2, 0, 1<<40)` was
admitted by the old constructor, whose only size check was `w > 4096 or h > 4096`. On
one full-width triangle, 4088 fragments survive the near/far clip under exact
arithmetic and **0** survive under two's-complement i64: `zfar*den` wraps negative and
the clip rejects everything. Same input, two frames, no refusal on either side. The
README's "any i64 overflow is a REFUSAL, never a saturate" was true of rung 1 and false
of rung 2. The pinned corpus never saw it because every conformance scene is 16x16 with
`zfar <= 100` — `E_max*Zmax ~ 2**31`, thirty-two bits of headroom. `sample != universal`.

## The decision

For vertices and sample points drawn from a box `[0,Bx) x [0,By)`, the maximum magnitude
of the edge function `(bx-ax)(py-ay) - (by-ay)(px-ax)` is **exactly `(Bx-1)*(By-1)`**.
That is DECIDED — `edge_max_is_decided_exhaustively()` re-runs the full triple search
over every rectangle up to `DECISION_HI` on every gate run rather than trusting this
sentence — and it is **attained**, by `a=(0,0), b=(0,By-1), p=(Bx-1,0)`. A bound nothing
reaches cannot be tested at its boundary, so an unattained estimate is not admissible
here: `voxin` needs "one past refuses, exactly at admits" and only an attained maximum
lets you write the second half. The first estimate tried during derivation was
`2*(Bx-1)*(By-1)` — a true upper bound, and useless for exactly that reason.

Inside a triangle the three edge weights are non-negative and sum to `area`, so
`|eb*z0 + ec*z1 + ea*z2| <= area * Zmax <= E_max * Zmax`, and `|zfar*den| <= E_max*Zmax`
likewise. Hence the admission predicate, linear in each factor:

    (w*SUB - 1) * (h*SUB - 1) * max(|znear|, |zfar|)  <=  2**63 - 1

**A 2D-only screen bound cannot be sound.** `screen_bits <= 31`, hence `w <= 2**23` at
eight subpixel bits, is the correct ceiling for rung 1 and mentions no depth range at
all — it admits the 4096x2 scene above. Replacing an arbitrary `4096` with a
derived-LOOKING constant that is unsound in a dimension it never names is worse than
leaving `4096`, because `4096` at least advertises that nobody decided it.
`attestation != authority`.

## Two bounds, kept apart

`admits()` is a THEOREM: exceed it and a conforming i64 placement computes a different
frame. `ALLOC_MAX_PIXELS` is a DECLARED policy: a 100000x100000 buffer at `zfar=1`
satisfies the theorem and still exhausts memory. They are separated on purpose —
folding a resource limit into a correctness bound is how `4096` came to look like it
meant something.

## does_not_show

That any particular scene overflows — this bounds the worst case over the whole box, so
it refuses configurations a given triangle would survive. That the Rust placement wraps
rather than panics: release-mode `i64` wraps and debug-mode panics, and neither is
`RENDER-REFUSE`. The wrap here is modelled from the types read in `urdr_render.rs`, not
obtained by compiling it with this scene — `the_wrap_changes_the_frame()` is EXECUTED
against a two's-complement model, and the outstanding falsifier is to add the scene to
the Rust corpus and compare. No published conformance digest is affected.
"""
from raster import SUB, IMAX

# The exhaustive re-decision runs on every gate pass: 49 rectangles, every ordered
# triple in each, 0.26s. Set to the widest sweep that stays cheap rather than to the
# narrowest that passes — a decision recorded once and re-read is a comment.
DECISION_HI = 8

# DECLARED, not derived — a resource policy, deliberately not fused with the theorem.
ALLOC_MAX_PIXELS = 1 << 24


def _edge(a, b, p):
    """The reference edge function, written out locally FOR THE DECISION ONLY. The
    rasterizer's own `raster.edge` is i64-guarded and would refuse mid-search; the
    decision must be able to compute magnitudes it is in the business of rejecting."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def edge_max(bx, by):
    """Maximum |edge| over `[0,bx) x [0,by)`. DECIDED exhaustively; see the module
    docstring and `edge_max_is_decided_exhaustively`."""
    if bx < 1 or by < 1:
        raise ValueError("box side must be positive")
    return (bx - 1) * (by - 1)


def edge_max_witness(bx, by):
    """The triple that ATTAINS `edge_max`. A maximum with no witness is an estimate."""
    return ((0, 0), (0, by - 1), (bx - 1, 0))


def edge_max_is_decided_exhaustively(hi=DECISION_HI):
    """Re-run the full triple search over every rectangle up to `hi` and confirm the
    closed form is the MAXIMUM, not merely an upper bound. This is the row that would
    redden if the closed form were ever loosened to an estimate."""
    for bx in range(2, hi + 1):
        for by in range(2, hi + 1):
            pts = [(x, y) for x in range(bx) for y in range(by)]
            best = 0
            for a in pts:
                for b in pts:
                    for p in pts:
                        e = abs(_edge(a, b, p))
                        if e > best:
                            best = e
            if best != edge_max(bx, by):
                return False
    return True


def edge_max_witness_attains(hi=DECISION_HI):
    """The stated witness really reaches the stated maximum, for every rectangle."""
    for bx in range(2, hi + 1):
        for by in range(2, hi + 1):
            a, b, p = edge_max_witness(bx, by)
            if abs(_edge(a, b, p)) != edge_max(bx, by):
                return False
    return True


def zmax(znear, zfar):
    return max(abs(znear), abs(zfar))


def depth_intermediate_max(w, h, znear, zfar, sub=SUB):
    """The largest magnitude the rung-2 depth path can reach at this configuration:
    `E_max * Zmax`, from `|sum(e_i * z_i)| <= area*Zmax` and `|zfar*den| <= E_max*Zmax`."""
    return edge_max(w * sub, h * sub) * zmax(znear, zfar)


def admits(w, h, znear, zfar, sub=SUB):
    """THE THEOREM. False means a conforming i64 placement can compute a different frame."""
    return depth_intermediate_max(w, h, znear, zfar, sub) <= IMAX


def max_depth_range(w, h, sub=SUB):
    """The largest `Zmax` this framebuffer size admits. Derived, so the boundary test
    can be written: `max_depth_range(w,h)` admits and one past it refuses."""
    return IMAX // edge_max(w * sub, h * sub)


def bound_is_attained(w=16, h=16, sub=SUB):
    """`max_depth_range` is a BOUNDARY, not a wall one short of one: the configuration
    exactly at it is admitted and the next one is not."""
    z = max_depth_range(w, h, sub)
    return admits(w, h, 0, z, sub) and not admits(w, h, 0, z + 1, sub)


# -- the wrap, executed --------------------------------------------------------------
_M64 = 1 << 64


def wrap_i64(v):
    """Two's-complement i64, the semantics `urdr_render.rs` has for `num` and
    `zfar*den` (release-mode wrap; debug-mode panics — neither is RENDER-REFUSE)."""
    v &= _M64 - 1
    return v - _M64 if v >= (1 << 63) else v


def the_wrap_changes_the_frame(w=4096, h=2, zfar=1 << 40):
    """EXECUTED: at a configuration the OLD constructor admitted, exact arithmetic and
    i64 keep different fragment sets. Returns (exact_kept, wrapped_kept); they differ.

    This is the falsifier for the whole module. If it ever returned equal counts, the
    joint bound would be certifying a divergence that does not exist."""
    from raster import edge, HALF
    if admits(w, h, 0, zfar):
        raise AssertionError("fixture invalid: this configuration is inside the bound")
    x_hi, y_hi = w * SUB - 1, h * SUB - 1
    (x0, y0), (x1, y1), (x2, y2) = (0, 0), (x_hi, 0), (0, y_hi)
    if edge(x0, y0, x1, y1, x2, y2) < 0:
        (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
    area = edge(x0, y0, x1, y1, x2, y2)
    z0, z1, z2 = 0, zfar, zfar // 2
    kept = [0, 0]
    for py in range(h):
        sy = py * SUB + HALF
        for px in range(w):
            sx = px * SUB + HALF
            ea = edge(x0, y0, x1, y1, sx, sy)
            eb = edge(x1, y1, x2, y2, sx, sy)
            ec = edge(x2, y2, x0, y0, sx, sy)
            if not (ea > 0 and eb > 0 and ec > 0):
                continue
            num, hi = eb * z0 + ec * z1 + ea * z2, zfar * area
            if 0 <= num <= hi:
                kept[0] += 1
            if 0 <= wrap_i64(num) <= wrap_i64(hi):
                kept[1] += 1
    return tuple(kept)


def the_wrap_is_real():
    a, b = the_wrap_changes_the_frame()
    return a != b


def live_corpus_is_admitted():
    """Non-regression: every scene the gate already renders stays inside the theorem, so
    the bound refuses a real divergence rather than the repo's own corpus."""
    return all(admits(w, h, 0, z) for (w, h, z) in ((16, 16, 100), (16, 16, 4)))
