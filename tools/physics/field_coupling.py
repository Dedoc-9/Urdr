# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Field → body momentum coupling — surface-tension force on a rigid body.

The complement of Marangoni self-advection: where `marangoni.py` lets the field
advect itself, here the field's surface-tension gradient pushes a BODY. A body at
grid cell i feels a Marangoni force proportional to the local surface-tension
gradient, `F = μ·∇σ` with `σ = c` (linear), evaluated by a central difference over
the frozen fixed-point field (zero-flux clamp at the boundary). The impulse
`J = F·Δt` is added to the body's momentum.

The honest, load-bearing property is EXACT BOOKKEEPING: momentum is carried as
Q32.32 integers, so the impulse is applied by an integer add and the body's
momentum change equals the injected impulse **exactly** (`Δp = J`, no drift) — the
same discipline that makes the field's mass exact. A UNIFORM field has zero
gradient, hence zero force (non-vacuity: the gradient is load-bearing); a field
rising in +x pushes the body toward higher surface tension (up-gradient). Force
and impulse ROUND (fixed-point `mul_k`), but the accounting does not; i64 overflow
is a typed `FIELD-REFUSE`.

Scope (honest): this is ONE-WAY forcing — the field pushes the body; the body does
not yet stir the field back (that reaction, and wiring `J` as an external term into
the LCP contact solve, are the next rungs). Deterministic Q32.32; extends the
frozen field; consumes no core; no new glyph."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from field import FixedPoint                             # noqa: E402  frozen field backend


def unit(num, den):
    """A Q32.32 field/force value num/den, via the frozen backend."""
    return FixedPoint.unit(num, den)


def gradient(grid, w, h, i, axis):
    """Central-difference surface-tension gradient `σ[right] − σ[left]` at cell i
    along `axis` (0 = x, 1 = y), σ = c. Zero-flux boundary: out-of-domain neighbours
    clamp to the edge cell. Exact fixed-point difference (the `/2` folds into μ)."""
    x, y = i % w, i // w
    if axis == 0:
        left = grid[y * w + max(x - 1, 0)]
        right = grid[y * w + min(x + 1, w - 1)]
    else:
        left = grid[max(y - 1, 0) * w + x]
        right = grid[min(y + 1, h - 1) * w + x]
    return FixedPoint.sub(right, left)


def force(grid, w, h, i, mu):
    """Marangoni force on a body at cell i: `μ·∇σ` per axis (fixed-point; rounds).
    `mu=(mn,md)` is the mobility × surface-tension slope. Points up-gradient."""
    mn, md = mu
    return (FixedPoint.mul_k(gradient(grid, w, h, i, 0), mn, md),
            FixedPoint.mul_k(gradient(grid, w, h, i, 1), mn, md))


def impulse(f, dt):
    """Impulse `J = F·Δt` (fixed-point; rounds). `dt=(dn,dd)`."""
    dn, dd = dt
    return (FixedPoint.mul_k(f[0], dn, dd), FixedPoint.mul_k(f[1], dn, dd))


def apply_impulse(momentum, j):
    """Add an impulse to a body's Q32.32 momentum by EXACT integer add: the
    returned momentum minus the input equals `j` exactly (no drift, no rounding)."""
    return (FixedPoint.add(momentum[0], j[0]), FixedPoint.add(momentum[1], j[1]))


def push(grid, w, h, i, mu, dt, momentum, steps):
    """Apply the field force to `momentum` for `steps` ticks in the static field."""
    for _ in range(steps):
        momentum = apply_impulse(momentum, impulse(force(grid, w, h, i, mu), dt))
    return momentum
