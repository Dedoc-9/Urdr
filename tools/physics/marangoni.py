# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Marangoni transport — surface-tension-gradient-driven advection (continuum rung).

Extends the FROZEN `urdr-field` v0.1 (never mutates it): where the frozen `step`
advects a scalar with a *uniform* velocity, here the velocity is DERIVED from the
field itself via surface tension. With a linear surface-tension law σ(c) = c, the
Marangoni velocity across an edge is proportional to the surface-tension gradient,
`v = κ·(σ[b] − σ[a]) = κ·(c[b] − c[a])`, and fluid is dragged toward higher σ
(higher concentration). The advective flux is first-order upwind, `v·c_upwind`,
and — crucially — applied CONSERVATIVELY (`+` to one cell, `−` to its neighbour),
so **total mass is conserved EXACTLY even though the coupling is nonlinear**
(quadratic in c). Diffusion `k·Δc` is added as in the frozen field and opposes the
Marangoni sharpening.

This is the reactive-environment nonlinearity: the field transports itself up its
own gradient, so a concentration peak decays *slower* than under pure diffusion
(κ transports mass back toward the peak). It is deterministic Q32.32 fixed-point
(the frozen `FixedPoint` backend, round-to-nearest ties-away), bounded, and refuses
i64 overflow (`FIELD-REFUSE`) rather than wrapping.

Honesty boundaries. (a) Mass is exact; the field VALUES round (fixed-point), as
always. (b) Monotonicity (no negative concentration) holds only under a CFL-type
bound `|v| ≤ 1` (κ small relative to the gradient); a too-large κ overshoots into
negative cells — still mass-conserving, but unphysical — so callers keep κ within
bound (the gate proves both sides). (c) This is a Marangoni-TYPE scalar transport
(σ linear in c, single field), not full free-surface Navier–Stokes.

Consumes the frozen field backend; touches no core; no new glyph."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from field import FixedPoint, _rdiv, ONE, FieldError    # noqa: E402  frozen field v0.1
from field import digest as _field_digest, mass as _field_mass   # noqa: E402


def unit(num, den):
    """A Q32.32 value num/den (e.g. unit(1,1) == 1.0), via the frozen backend."""
    return FixedPoint.unit(num, den)


def _fp_mul(a, b):
    """Q32.32 value×value → value, round-to-nearest ties-away (the FROZEN rule).
    The nonlinear Marangoni term needs field×field, unlike the frozen field's
    value×rational `mul_k`. Overflow refuses `FIELD-REFUSE`."""
    return FixedPoint._g(_rdiv(a * b, ONE))


def marangoni_step(grid, w, h, k, kappa):
    """One conservative flux-form Marangoni step (FixedPoint backend).

    `grid` is a length-w*h row-major list of Q32.32 values; `k=(kn,kd)` the
    diffusion coefficient; `kappa=(cn,cd)` the Marangoni coupling (mobility ×
    surface-tension slope). Each interior edge (a,b) contributes a diffusion flux
    `k·(c_b − c_a)` and a Marangoni advection flux `κ·(c_b − c_a)·c_upwind`, both
    applied `+`/`−` so mass is conserved exactly. Zero-flux boundary (interior
    edges only). Reads from `grid`, writes to a fresh buffer (explicit scheme)."""
    kn, kd = k
    cn, cd = kappa
    new = list(grid)

    def edge(a, b):
        dc = FixedPoint.sub(grid[b], grid[a])
        fd = FixedPoint.mul_k(dc, kn, kd)                 # diffusion (smooths)
        new[a] = FixedPoint.add(new[a], fd)
        new[b] = FixedPoint.sub(new[b], fd)
        v = FixedPoint.mul_k(dc, cn, cd)                  # Marangoni velocity ∝ ∂σ = ∂c
        if v > 0:                                         # flow a→b (up-gradient): upwind a
            f = _fp_mul(v, grid[a])
            new[a] = FixedPoint.sub(new[a], f)
            new[b] = FixedPoint.add(new[b], f)
        elif v < 0:                                       # flow b→a: upwind b
            f = _fp_mul(-v, grid[b])
            new[b] = FixedPoint.sub(new[b], f)
            new[a] = FixedPoint.add(new[a], f)

    for y in range(h):
        for x in range(w - 1):
            edge(y * w + x, y * w + x + 1)
    for y in range(h - 1):
        for x in range(w):
            edge(y * w + x, (y + 1) * w + x)
    return new


def run(grid, w, h, k, kappa, steps):
    """Apply `marangoni_step` `steps` times (deterministic)."""
    for _ in range(steps):
        grid = marangoni_step(grid, w, h, k, kappa)
    return grid


def mass(grid):
    """Total scalar mass Σ cells — the exactly-conserved flux-form invariant."""
    return _field_mass(FixedPoint, grid)


def digest(grid, w, h):
    """Frame digest under the frozen URDRFLD1 / FIELDFP law (state, not dynamics)."""
    return _field_digest(FixedPoint, grid, w, h)
