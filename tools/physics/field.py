# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-field -- deterministic scalar-field transport (advection-diffusion).

A reactive-environment substrate: a scalar grid (heat / chemical concentration)
that evolves under diffusion + first-order upwind advection. The pipeline's
`exact vs scale` tradeoff is exposed as an explicit, user-selectable BACKEND, and
made honest by the four rules:

  1. The backend is part of STATE IDENTITY. The frame carries a backend tag, so a
     fixed-point field and an exact field are never conflated:
         [MAGIC "URDRFLD1"][BACKEND 8B "FIELDFP " | "FIELDQ  "]
         [W u32][H u32][per-cell canonical payload]
  2. The `FixedPoint` parameters are FROZEN SPEC: radix 2^32, round-to-nearest
     ties-away-from-zero — so every compiler/CPU truncates identically.
  3. Both backends are DETERMINISTIC and CROSS-PLACEABLE (bit-identical across
     placements). The choice only trades exactness vs scale, never determinism.
  4. `FixedPoint` is the load-bearing real-time path (BOUNDED, ROUNDS); `Exact`
     (reusing the physics rational `Q`) is EXACT but its denominators grow, so it
     REFUSES on any sizable/long field — a scoped, small, high-stakes option.

The step is a CONSERVATIVE FLUX FORM: each edge flux is computed once and applied
`+` to one cell and `-` to its neighbor, so total mass (Σ cells) is conserved
EXACTLY even in fixed-point (integer add/sub cancel the rounded flux). The
boundary is zero-flux (adiabatic): out-of-domain neighbors clamp to the edge cell,
so no mass leaves the grid. No float, no clock, no RNG. Consumes rational; touches
no core; no new glyph."""
import hashlib

from rational import Q as RQ, RationalError

ONE = 1 << 32                     # FixedPoint radix (Q32.32), FROZEN
IMAX = (1 << 63) - 1
MAGIC = b"URDRFLD1"


class FieldError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _rdiv(p, d):
    """Round p/d to nearest, ties away from zero (d > 0). The FROZEN rounding
    rule — every placement must evaluate this identically."""
    if p >= 0:
        return (2 * p + d) // (2 * d)
    return -((2 * (-p) + d) // (2 * d))


class FixedPoint:
    """Q32.32 fixed-point backend: bounded, deterministic, round-to-nearest.
    Reproducible across placements, but it ROUNDS — not exact."""
    tag = b"FIELDFP "
    ONE = ONE

    @staticmethod
    def _g(v):
        if v > IMAX or v < -IMAX:
            raise FieldError("FIELD-REFUSE", f"i64 overflow ({v})")
        return v

    @staticmethod
    def zero():
        return 0

    @staticmethod
    def unit(num, den):
        return FixedPoint._g(_rdiv(num * ONE, den))     # a value in units of 1.0

    @staticmethod
    def add(a, b):
        return FixedPoint._g(a + b)

    @staticmethod
    def sub(a, b):
        return FixedPoint._g(a - b)

    @staticmethod
    def mul_k(a, kn, kd):
        return FixedPoint._g(_rdiv(a * kn, kd))         # multiply by rational coeff; ROUNDS

    @staticmethod
    def is_zero(a):
        return a == 0

    @staticmethod
    def ser(a):
        return int(a).to_bytes(8, "big", signed=True)


class Exact:
    """Exact rational backend (reuses the physics `Q`): EXACT, but denominators
    grow — it REFUSES (PHYS-REFUSE) on any sizable/long field. Scoped-tiny."""
    tag = b"FIELDQ  "

    @staticmethod
    def zero():
        return RQ(0, 1)

    @staticmethod
    def unit(num, den):
        return RQ(num, den)

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def sub(a, b):
        return a - b

    @staticmethod
    def mul_k(a, kn, kd):
        return a * RQ(kn, kd)

    @staticmethod
    def is_zero(a):
        return a.is_zero()

    @staticmethod
    def ser(a):
        return a.n.to_bytes(8, "big", signed=True) + a.d.to_bytes(8, "big", signed=True)


def _clamp(i, n):
    return 0 if i < 0 else (n - 1 if i >= n else i)


def step(B, grid, w, h, k, vx, vy):
    """One conservative flux-form step over backend B. `grid` is a length-w*h
    list of B values (row-major). `k=(kn,kd)` diffusion coeff, `vx,vy` velocity
    (rational (num,den)). Diffusion flux `k·(c_b − c_a)`; first-order UPWIND
    advection flux `v·c_upwind`; each flux applied +to one cell, −to the neighbor
    (mass conserved exactly). Zero-flux boundary via edge clamping."""
    kn, kd = k
    vxn, vxd = vx
    vyn, vyd = vy
    new = list(grid)

    def ix(x, y):
        return _clamp(y, h) * w + _clamp(x, w)

    for y in range(h):
        for x in range(w - 1):
            a = ix(x, y)
            b = ix(x + 1, y)
            fd = B.mul_k(B.sub(grid[b], grid[a]), kn, kd)   # diffusion
            new[a] = B.add(new[a], fd)
            new[b] = B.sub(new[b], fd)
            if vxn > 0:                                     # upwind = left cell
                fu = B.mul_k(grid[a], vxn, vxd)
                new[a] = B.sub(new[a], fu)
                new[b] = B.add(new[b], fu)
            elif vxn < 0:                                   # upwind = right cell
                fu = B.mul_k(grid[b], -vxn, vxd)
                new[b] = B.sub(new[b], fu)
                new[a] = B.add(new[a], fu)
    for y in range(h - 1):
        for x in range(w):
            a = ix(x, y)
            b = ix(x, y + 1)
            fd = B.mul_k(B.sub(grid[b], grid[a]), kn, kd)
            new[a] = B.add(new[a], fd)
            new[b] = B.sub(new[b], fd)
            if vyn > 0:
                fu = B.mul_k(grid[a], vyn, vyd)
                new[a] = B.sub(new[a], fu)
                new[b] = B.add(new[b], fu)
            elif vyn < 0:
                fu = B.mul_k(grid[b], -vyn, vyd)
                new[b] = B.sub(new[b], fu)
                new[a] = B.add(new[a], fu)
    return new


def mass(B, grid):
    """Total scalar mass Σ cells (the exactly-conserved flux-form invariant)."""
    m = B.zero()
    for v in grid:
        m = B.add(m, v)
    return m


def digest(B, grid, w, h):
    """Digest(Field) = SHA-256(MAGIC | backend tag | W | H | per-cell payload).
    The backend tag is part of identity — FixedPoint and Exact never collide."""
    out = bytearray(MAGIC) + B.tag + w.to_bytes(4, "big") + h.to_bytes(4, "big")
    for v in grid:
        out += B.ser(v)
    return hashlib.sha256(bytes(out)).hexdigest()
