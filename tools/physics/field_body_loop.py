# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Two-way field ↔ body coupling — closing the reactive loop.

`field_coupling.py` made the field push a body (one way). This closes the loop:

    body motion ──▶ field update
        ▲                │
        └────────────────┘

A coupled step does four things, in order:
  1. **field → body force.** Each body in the field takes the surface-tension
     impulse `J = μ·∇σ·Δt` (converted from the fixed-point field to an exact `Q`)
     on its predicted velocity.
  2. **contacts.** The predicted velocities are resolved by the exact contact LCP
     (`contact_lcp`), so a body pushed by the field into a contact is held (the
     normal impulse `λ` counteracts the field force) and one pushed away releases.
  3. **body → field reaction (Newton's third law).** The total impulse the field
     handed to bodies is DEBITED from a field-momentum *reservoir*, so the whole
     coupled system conserves momentum EXACTLY: `Σ (m·v) + reservoir = const`, in
     exact `Q` — the same integer-ledger discipline that makes the field's mass
     exact, now spanning field and bodies.
  4. **body → field state (optional).** The body's motion advects the field via the
     frozen, cross-placed `field.step` (mass exact by the flux form) — the literal
     "body motion → field update" arrow, feeding the next step's gradient.

Honesty: the momentum ledger and contact resolution are EXACT (rational); the field
force conversion and the body-driven advection ROUND (fixed-point), as the substrate
always does. The reservoir is a bookkeeping quantity (the scalar field carries no
mechanical momentum of its own); the exact claim is the *ledger* Σp_body + reservoir,
whose non-vacuity is that dropping the reaction term makes it drift. Consumes the
frozen field + the exact LCP; touches no core; no new glyph."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rational import Q                                   # noqa: E402
from vecq import Vec                                     # noqa: E402
from contact_lcp import resolve, momentum                # noqa: E402
from field import FixedPoint, step as field_step         # noqa: E402
import field_coupling as FC                              # noqa: E402

ONE = 1 << 32


def field_impulse(grid, w, h, i, mu, dt):
    """The surface-tension impulse on a body at field cell i as an exact `Q` 2-vector:
    `J = μ·(∇σ)·Δt`, with the fixed-point gradient's radix (2^32) folded into the
    rational. `mu=(mn,md)`, `dt=(dn,dd)`."""
    mn, md = mu
    dn, dd = dt
    gx = FC.gradient(grid, w, h, i, 0)
    gy = FC.gradient(grid, w, h, i, 1)
    return Vec([Q(gx * mn * dn, md * ONE * dd), Q(gy * mn * dn, md * ONE * dd)])


def coupled_step(grid, w, h, vels, inv_mass, contacts, cells, mu, dt, reservoir,
                 body_advect=None):
    """One two-way coupled step. `vels` per-body velocity `Vec`s; `inv_mass` per-body
    `Q` (Z(0) for a static anchor); `cells[b]` the field cell of body b (or None);
    `reservoir` the field-momentum ledger `Vec`. If `body_advect=(vx,vy)` is given,
    the field is advected by it (frozen flux form, mass exact). Returns
    `(new_vels, lam, w_slack, new_grid, new_reservoir, total_impulse)`."""
    vpred = list(vels)
    tot_j = Vec([Q(0), Q(0)])
    for bi, ci in enumerate(cells):
        if ci is None or inv_mass[bi].is_zero():
            continue
        j = field_impulse(grid, w, h, ci, mu, dt)
        vpred[bi] = vpred[bi] + j.scale(inv_mass[bi])    # Δv = J·invm
        tot_j = tot_j + j
    vnew, lam, wsl = resolve(vpred, inv_mass, contacts)  # LCP resolves the field force
    new_reservoir = reservoir - tot_j                    # 3rd law: field loses what it gave
    new_grid = grid
    if body_advect is not None:
        vx, vy = body_advect
        new_grid = field_step(FixedPoint, grid, w, h, (0, 1), vx, vy)   # advect only (k=0)
    return vnew, lam, wsl, new_grid, new_reservoir, tot_j


def total_momentum(vels, masses, reservoir):
    """The conserved quantity of the coupled system: Σ dynamic-body momentum plus
    the field reservoir (exact `Q` vector)."""
    return momentum(vels, masses) + reservoir
