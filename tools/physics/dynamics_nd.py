# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics rung 2 -- exact n-dimensional dynamic mechanics (2D & 3D).

Generalizes the 1D step to vectors, staying EXACT over Z. The key result: a
sphere/ball collision RESPONSE is exact in any dimension WITHOUT a square root.
The contact normal is the center-difference vector d = c2 - c1; the |d| from
projecting the relative velocity onto the unit normal cancels the |d| from the
impulse being along that unit normal, leaving only d·d (exact). So the impulse
vector is

    P = -(1+e) (v_rel · d) / ( (d·d) (1/m1 + 1/m2) ) · d          (exact over Q)

Momentum (a VECTOR) is conserved by the equal-and-opposite P; kinetic energy is
the discriminating witness (conserved iff elastic, strictly decreasing iff
inelastic), and the TANGENTIAL velocity is untouched (correct oblique physics).

EXACTNESS BOUNDARY (honest): a *continuous* sphere-sphere time-of-impact solves
|d0 + w t|^2 = (r1+r2)^2, a quadratic whose root carries a square root and is
therefore generally IRRATIONAL -- exact rational CCD is NOT available for
curved-vs-curved continuous collision. So sphere-sphere collision uses DISCRETE
overlap detection (exact: d·d <= (r1+r2)^2) + exact response, while CCD (the
anti-tunneling witness) is provided for LINEAR impact conditions -- a ball vs an
axis-aligned wall, whose TOI is a rational linear solve.

Scope (honest): spheres + axis-aligned walls; single earliest event per step;
restitution in [0,1]. General n-contact LCP, arbitrary convex shapes, rotational
inertia, sphere-sphere continuous CCD, and a second placement are later rungs."""
import hashlib
import struct

from rational import Q, Z, RationalError
from vecq import Vec, zero


class Ball:
    """An n-D ball: center x (Vec), radius r (Q), velocity v (Vec), mass m>0."""
    __slots__ = ("x", "r", "v", "m")

    def __init__(self, x, r, v, m):
        if m <= 0:
            raise RationalError("PHYS-REFUSE", "mass must be positive")
        if x.dim() != v.dim():
            raise RationalError("PHYS-REFUSE", "position/velocity dimension mismatch")
        self.x, self.r, self.v, self.m = x, r, v, m

    def inv_mass(self):
        return Q(1, self.m)

    def clone(self, x=None, v=None):
        return Ball(self.x if x is None else x, self.r,
                    self.v if v is None else v, self.m)


# -- invariants (exact) --------------------------------------------------------
def momentum(bodies):
    p = zero(bodies[0].v.dim())
    for b in bodies:
        p = p + b.v.scale(Z(b.m))
    return p


def two_kinetic(bodies):
    """2*KE = sum m (v·v), exact rational."""
    e = Z(0)
    for b in bodies:
        e = e + b.v.dot(b.v) * Z(b.m)
    return e


# -- integrator: semi-implicit (symplectic) Euler ------------------------------
def integrate(body, force, dt):
    v2 = body.v + force.scale(body.inv_mass() * dt)
    x2 = body.x + v2.scale(dt)
    return body.clone(x=x2, v=v2)


# -- exact sphere-sphere collision response (no square root) --------------------
def overlapping(b1, b2):
    d = b2.x - b1.x
    rr = b1.r + b2.r
    return d.dot(d) <= rr * rr


def approaching(b1, b2):
    return (b2.v - b1.v).dot(b2.x - b1.x) < Z(0)


def resolve_spheres(b1, b2, restitution):
    """Exact impulse for a ball-ball contact. Applied only when approaching;
    momentum conserved by construction. Returns (b1', b2', applied)."""
    d = b2.x - b1.x                       # un-normalized normal
    dd = d.dot(d)
    if dd.is_zero():
        return b1, b2, False              # coincident centers: no normal
    vrel = b2.v - b1.v
    vn = vrel.dot(d)                       # (v_rel · unit_n) * |d|
    if not (vn < Z(0)):
        return b1, b2, False              # separating/resting
    k = (Z(0) - (Z(1) + restitution)) * vn / (dd * (b1.inv_mass() + b2.inv_mass()))
    p = d.scale(k)                        # impulse VECTOR (exact)
    n1 = b1.clone(v=b1.v - p.scale(b1.inv_mass()))
    n2 = b2.clone(v=b2.v + p.scale(b2.inv_mass()))
    return n1, n2, True


# -- conservation witnesses (falsifiers) ---------------------------------------
def momentum_conserved(before, after):
    return momentum(before) == momentum(after)


def energy_conserved(before, after):
    return two_kinetic(before) == two_kinetic(after)


def energy_nonincreasing(before, after):
    return two_kinetic(after) <= two_kinetic(before)


# -- exact CCD for a LINEAR impact condition: ball vs axis-aligned wall ---------
def toi_wall(ball, axis, wall, dt):
    """Earliest exact rational time t in [0,dt] at which the ball's leading edge
    on `axis` meets the wall plane at coordinate `wall` (ball moving +axis).
    Linear -> rational; a fast ball cannot tunnel. None if it does not reach."""
    va = ball.v.c[axis]
    if not (va > Z(0)):
        return None
    t = (wall - ball.r - ball.x.c[axis]) / va
    if Z(0) <= t and t <= dt:
        return t
    return None


# -- the step function: (X_t, V_t) + F -> (X_t+1, V_t+1) ------------------------
def step(bodies, forces, dt, restitution, walls=()):
    """One deterministic n-D step. Integrate (semi-implicit); if a ball meets an
    axis-aligned wall first (exact CCD), advance ALL bodies to that fractional
    time, reflect that ball's normal-axis velocity (elastic wall scaled by
    restitution), and integrate the remainder; otherwise resolve the first
    overlapping, approaching ball-ball pair exactly (discrete). Single earliest
    event per step. Pure and exact. `walls` is a tuple of (axis, coord)."""
    moved = [integrate(b, f, dt) for b, f in zip(bodies, forces)]
    vel = [m.v for m in moved]
    # 1. earliest wall CCD over balls x walls, at the new velocities.
    at_start = [b.clone(v=vel[i]) for i, b in enumerate(bodies)]
    earliest, hit_i, hit_axis = None, None, None
    for i, b in enumerate(at_start):
        for (axis, coord) in walls:
            t = toi_wall(b, axis, coord, dt)
            if t is not None and (earliest is None or t < earliest):
                earliest, hit_i, hit_axis = t, i, axis
    if earliest is not None:
        sliced = [b.clone(x=b.x + vel[i].scale(earliest), v=vel[i])
                  for i, b in enumerate(bodies)]
        hb = sliced[hit_i]
        refl = list(hb.v.c)
        refl[hit_axis] = -(restitution) * refl[hit_axis]   # reflect normal component
        sliced[hit_i] = hb.clone(v=Vec(refl))
        rest = dt - earliest
        return [b.clone(x=b.x + b.v.scale(rest)) for b in sliced]
    # 2. first overlapping, approaching ball-ball pair (discrete), exact response.
    n = len(moved)
    for i in range(n):
        for j in range(i + 1, n):
            if overlapping(moved[i], moved[j]) and approaching(moved[i], moved[j]):
                a, b, _ap = resolve_spheres(moved[i], moved[j], restitution)
                out = list(moved)
                out[i], out[j] = a, b
                return out
    return moved


# -- canonical state digest (reproducible witness of n-D (X,V)) ----------------
def state_digest(bodies):
    """Digest(State) = SHA-256(canonical serialization). Dimension + each ball's
    exact rational fields (center comps, radius, velocity comps, mass) as signed
    8-byte big-endian integers -- identical state -> identical digest anywhere."""
    dim = bodies[0].x.dim() if bodies else 0
    out = bytearray(b"URDRPN1")
    out += struct.pack(">i", dim)
    out += struct.pack(">i", len(bodies))
    for b in bodies:
        for comp in b.x.c:
            out += struct.pack(">qq", comp.n, comp.d)
        out += struct.pack(">qq", b.r.n, b.r.d)
        for comp in b.v.c:
            out += struct.pack(">qq", comp.n, comp.d)
        out += struct.pack(">q", b.m)
    return hashlib.sha256(bytes(out)).hexdigest()
