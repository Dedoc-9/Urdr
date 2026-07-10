# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics rung 3 -- the exact n-contact constraint solver (frictionless LCP).

Pairwise dynamics (rungs 1-2) resolved ONE contact at a time. Real worlds have
SIMULTANEOUS contacts -- resting stacks, multi-body impacts -- where the impulses
are coupled and must be solved together. That is a linear complementarity problem:

    find  lambda >= 0  such that  w = A lambda + b >= 0  and  w . lambda = 0

where lambda are the normal contact impulses, b the pre-impulse relative normal
velocities, and A the Delassus operator (the effective-mass coupling between
contacts). Complementarity encodes the physics: a contact either carries a
positive impulse and is exactly resting (w_i = 0), or carries none and is
separating (w_i >= 0). This *certifies* the resolution rather than assuming it
(the uniqueness-by-certificate principle): the solver returns a lambda that
provably satisfies every LCP condition, or it REFUSES.

Exact over Z/Q, no float, no iterative tolerance, no heuristic ordering:
  * normals are UN-NORMALIZED (the center-difference vector d for a sphere, an
    axis vector for a wall) -- rational for both, so A and b are rational and the
    |d| that would need a square root never appears;
  * the solver is a DIRECT active-set method: enumerate candidate active sets in
    a CANONICAL order (increasing size, then lexicographic), solve the equality
    subsystem A_SS lambda_S = -b_S by exact rational elimination with a
    deterministic pivot, and return the first set that satisfies lambda_S >= 0
    and w >= 0. No convergence loop, no tolerance;
  * a singular subsystem is skipped; if no feasible nonsingular active set exists
    the whole solve REFUSES (PHYS-REFUSE) -- a degenerate/inconsistent contact
    system is refused, not guessed. i64 overflow refuses through Q.

Momentum is conserved by construction (each impulse lambda_k d_k is applied
equal-and-opposite to its two bodies). Scope (honest): frictionless normal
contacts; small contact counts (enumeration is exponential -- Lemke/principal
pivoting is the same exact answer, faster, a later optimization); a static body
is one with inverse mass 0. Rotational inertia, friction, and a second placement
(urdr-physics-rs) are later rungs. Consumes vecq + rational; touches no core."""
import hashlib
import struct
from itertools import combinations

from rational import Q, Z, RationalError
from vecq import Vec


# -- exact rational linear solve (deterministic pivot; None if singular) --------
def lin_solve(A, b):
    """Solve A x = b exactly over Q by Gaussian elimination with a deterministic
    first-nonzero pivot (no heuristic ordering). Returns x, or None if singular."""
    n = len(A)
    M = [[A[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if not M[r][col].is_zero():
                piv = r
                break
        if piv is None:
            return None                          # singular
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [v / pv for v in M[col]]
        for r in range(n):
            if r != col and not M[r][col].is_zero():
                f = M[r][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


# -- exact LCP: w = A lambda + b, w,lambda >= 0, w . lambda = 0 -----------------
def solve_lcp(A, b):
    """Direct active-set solve. Returns (lambda, w) with every LCP condition
    satisfied exactly, in a canonical (deterministic) search order. Raises
    PHYS-REFUSE if no feasible nonsingular active set exists."""
    n = len(b)
    idx = list(range(n))
    for k in range(n + 1):
        for S in combinations(idx, k):
            if k > 0:
                Ass = [[A[i][j] for j in S] for i in S]
                bs = [Z(0) - b[i] for i in S]
                lam_s = lin_solve(Ass, bs)
                if lam_s is None or any(l < Z(0) for l in lam_s):
                    continue                     # singular or infeasible impulse
            else:
                lam_s = []
            full = [Z(0)] * n
            for t, i in enumerate(S):
                full[i] = lam_s[t]
            w = []
            ok = True
            for i in idx:
                wi = b[i]
                for j in idx:
                    wi = wi + A[i][j] * full[j]
                if wi < Z(0):
                    ok = False
                    break
                w.append(wi)
            if ok:
                return full, w
    raise RationalError("PHYS-REFUSE",
                        "no feasible nonsingular active set (degenerate/inconsistent LCP)")


def complementary(lam, w):
    """The certificate: lambda,w >= 0 and lambda_i w_i = 0 for every i."""
    return all(l >= Z(0) and wi >= Z(0) and (l * wi).is_zero()
               for l, wi in zip(lam, w))


# -- frictionless normal-contact model (un-normalized normals) -----------------
class Contact:
    """A normal contact between body a and body b, normal Vec d pointing a->b
    (un-normalized: the center-difference for spheres, an axis for a wall)."""
    __slots__ = ("a", "b", "d")

    def __init__(self, a, b, d):
        self.a, self.b, self.d = a, b, d


def delassus(vels, inv_mass, contacts):
    """Build (A, b) for the contact set. `vels` and `inv_mass` are per-body lists
    (a static body has inv_mass Z(0)); each contact carries its normal d. All
    rational: b_k = (v_b - v_a)·d_k ; A_kl = d_k · (Δv_b - Δv_a from unit λ_l)."""
    n = len(contacts)
    A = [[Z(0)] * n for _ in range(n)]
    b = [Z(0)] * n
    for k, ck in enumerate(contacts):
        b[k] = (vels[ck.b] - vels[ck.a]).dot(ck.d)
        for l, cl in enumerate(contacts):
            # unit impulse λ_l along d_l: body b_l gets +invm[b_l] d_l, a_l gets -invm[a_l] d_l
            def dv(body):
                acc = ck.d.scale(Z(0))            # zero vector, right dim
                if body == cl.b:
                    acc = acc + cl.d.scale(inv_mass[cl.b])
                if body == cl.a:
                    acc = acc - cl.d.scale(inv_mass[cl.a])
                return acc
            A[k][l] = ck.d.dot(dv(ck.b) - dv(ck.a))
    return A, b


def apply_impulses(vels, inv_mass, contacts, lam):
    """Return new velocities after applying the solved normal impulses."""
    out = list(vels)
    for l, cl in enumerate(contacts):
        if lam[l].is_zero():
            continue
        out[cl.b] = out[cl.b] + cl.d.scale(lam[l] * inv_mass[cl.b])
        out[cl.a] = out[cl.a] - cl.d.scale(lam[l] * inv_mass[cl.a])
    return out


def momentum(vels, masses):
    """Total momentum vector over the DYNAMIC bodies (static ones excluded --
    a static wall is an external anchor, it does not carry momentum)."""
    dyn = [i for i, m in enumerate(masses) if m is not None]
    p = vels[dyn[0]].scale(Z(0))
    for i in dyn:
        p = p + vels[i].scale(Z(masses[i]))
    return p


def resolve(vels, inv_mass, contacts):
    """Solve the contact LCP and apply it. Returns (new_vels, lam, w)."""
    A, b = delassus(vels, inv_mass, contacts)
    lam, w = solve_lcp(A, b)
    return apply_impulses(vels, inv_mass, contacts, lam), lam, w


# -- canonical digest of the certified impulse solution ------------------------
def lcp_digest(lam, w):
    """Digest(solution) = SHA-256 of the canonical serialization of the certified
    (lambda, w) -- a reproducible witness of the exact contact resolution."""
    out = bytearray(b"URDRLCP1")
    out += struct.pack(">i", len(lam))
    for q in lam:
        out += struct.pack(">qq", q.n, q.d)
    for q in w:
        out += struct.pack(">qq", q.n, q.d)
    return hashlib.sha256(bytes(out)).hexdigest()
