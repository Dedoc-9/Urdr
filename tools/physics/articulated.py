# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics rung 4 -- exact articulated / constraint systems (joints).

Contacts (rung 3) were INEQUALITY constraints (an LCP). Joints -- hinges,
sliders, rods, skeletons -- are EQUALITY (bilateral) constraints: the constraint
velocity must be exactly zero. That removes the complementarity entirely and
leaves a plain exact LINEAR system, which fits the exactness discipline perfectly:

    build the Jacobian J   (one row per scalar constraint),
    form the constraint-space mass  A = J M^{-1} J^T,
    solve   A lambda = -J v   (exact rational linear solve),
    apply   v <- v + M^{-1} J^T lambda,
    certify   J v_new = 0     (the constraint holds, to the last bit),
    emit a deterministic witness digest.

The uniqueness-by-certificate principle is literal here: rank(A) decides local
uniqueness. Full rank -> a unique lambda holds every constraint. Rank-deficient
-> the constraints are redundant or conflicting, and the solver REFUSES
(PHYS-REFUSE) with that as the witness of non-uniqueness, rather than guessing.

Exact over Q, no float, no tolerance, no heuristic ordering: gradients are
UN-NORMALIZED (a distance constraint's gradient is the center-difference p_a-p_b,
rational -- the same row the rigidity matrix uses, so this bridges static
rigidity and dynamics). Momentum is conserved by construction for all-dynamic
systems (each impulse is applied along +/- the gradient to the two bodies). A
static body (an anchor/rail) has inverse mass 0. Reuses contact_lcp.lin_solve;
consumes vecq + rational; touches no core. Scope (honest): velocity-level
holonomic equality constraints, no drift stabilization (Baumgarte), frictionless;
rotational inertia and a second placement are later rungs."""
import hashlib
import struct

from rational import Q, Z, RationalError
from vecq import Vec
from contact_lcp import lin_solve


# A `row` is a scalar equality constraint: a list of (body_index, gradient Vec).
# A `system` is a list of rows.  inv_mass[b] == Z(0) marks a static body.

def distance_row(a, b, pa, pb):
    """A rigid-rod / distance constraint between bodies a and b at positions
    pa, pb: the length-rate is (pa-pb)·(v_a - v_b). Gradient (un-normalized) is
    n = pa - pb on a and -n on b -- exactly a rigidity-matrix row."""
    n = pa - pb
    return [(a, n), (b, n.scale(Z(-1)))]


def pin_rows(anchor, body, dim):
    """A pin/hinge: body coincides with anchor -> its velocity relative to the
    anchor is zero in every axis. `dim` scalar rows (one per coordinate)."""
    rows = []
    for k in range(dim):
        e = [Z(1) if i == k else Z(0) for i in range(dim)]
        ev = Vec(e)
        rows.append([(anchor, ev.scale(Z(-1))), (body, ev)])
    return rows


def build_system(vels, inv_mass, rows):
    """(A, b) with A = J M^{-1} J^T (constraint-space mass) and b = J v."""
    m = len(rows)
    A = [[Z(0)] * m for _ in range(m)]
    b = [Z(0)] * m
    for i, ri in enumerate(rows):
        bi = Z(0)
        for (body, g) in ri:
            bi = bi + g.dot(vels[body])
        b[i] = bi
        for j, rj in enumerate(rows):
            aij = Z(0)
            for (bi_, gi) in ri:
                for (bj_, gj) in rj:
                    if bi_ == bj_:
                        aij = aij + inv_mass[bi_] * gi.dot(gj)
            A[i][j] = aij
    return A, b


def solve(vels, inv_mass, rows):
    """Solve the equality-constraint system exactly. Returns (new_vels, lambda).
    Raises PHYS-REFUSE if A is singular (redundant/conflicting constraints)."""
    A, b = build_system(vels, inv_mass, rows)
    lam = lin_solve(A, [Z(0) - x for x in b])          # A lambda = -b
    if lam is None:
        raise RationalError("PHYS-REFUSE",
                            "singular constraint system (redundant or conflicting)")
    out = list(vels)
    for i, ri in enumerate(rows):
        for (body, g) in ri:
            out[body] = out[body] + g.scale(inv_mass[body] * lam[i])
    return out, lam


def constraint_velocities(vels, rows):
    """J v -- the certificate value. All entries are Z(0) iff every constraint
    is exactly satisfied at the velocity level."""
    out = []
    for ri in rows:
        s = Z(0)
        for (body, g) in ri:
            s = s + g.dot(vels[body])
        out.append(s)
    return out


def satisfied(vels, rows):
    return all(x.is_zero() for x in constraint_velocities(vels, rows))


def momentum(vels, masses):
    """Total momentum over DYNAMIC bodies (a static anchor is an external hold)."""
    dyn = [i for i, m in enumerate(masses) if m is not None]
    p = vels[dyn[0]].scale(Z(0))
    for i in dyn:
        p = p + vels[i].scale(Z(masses[i]))
    return p


def joint_digest(new_vels, lam):
    """Digest(solution) = SHA-256 of the canonical serialization of the solved
    velocities and impulses -- a reproducible witness of the exact constraint solve."""
    out = bytearray(b"URDRJNT1")
    out += struct.pack(">ii", len(new_vels), len(lam))
    for v in new_vels:
        for comp in v.c:
            out += struct.pack(">qq", comp.n, comp.d)
    for q in lam:
        out += struct.pack(">qq", q.n, q.d)
    return hashlib.sha256(bytes(out)).hexdigest()
