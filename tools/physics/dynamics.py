# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics rung 1 -- exact 1D dynamic mechanics.

The core loop shifts from validating a static rigidity matrix to executing a
deterministic, time-linked equation of motion, exactly over Z:

    (X_t, V_t) + F  --semi-implicit Euler + exact 1-contact LCP + CCD-->  (X_t+1, V_t+1)

Everything is exact rational (rational.Q): no float, no clock, no RNG. Momentum
is conserved STRUCTURALLY (equal-and-opposite impulse); kinetic energy is the
discriminating witness (conserved iff elastic, strictly decreasing iff
inelastic). Overflow is a refusal. Consumes rational; touches no core.

Scope (honest): 1D, single earliest contact per step, restitution in [0,1].
General n-contact LCP (Lemke), 2D/3D, and a second placement are later rungs."""
import hashlib
import struct

from rational import Q, Z, RationalError


class Body:
    """A 1D body: position x (center), half-extent r, velocity v, mass m>0."""
    __slots__ = ("x", "r", "v", "m")

    def __init__(self, x, r, v, m):
        if m <= 0:
            raise RationalError("PHYS-REFUSE", "mass must be positive")
        self.x, self.r, self.v, self.m = x, r, v, m

    def inv_mass(self):
        return Q(1, self.m)

    def left(self):
        return self.x - self.r

    def right(self):
        return self.x + self.r

    def clone(self, x=None, v=None):
        return Body(self.x if x is None else x, self.r,
                    self.v if v is None else v, self.m)


# -- invariants (exact) --------------------------------------------------------
def momentum(bodies):
    p = Z(0)
    for b in bodies:
        p = p + Z(b.m) * b.v
    return p


def two_kinetic(bodies):
    """2*KE = sum m v^2, kept exact (the factor 1/2 is dropped, order-preserving)."""
    e = Z(0)
    for b in bodies:
        e = e + Z(b.m) * b.v * b.v
    return e


# -- integrator: semi-implicit (symplectic) Euler ------------------------------
def integrate(body, force, dt):
    v2 = body.v + force * body.inv_mass() * dt
    x2 = body.x + v2 * dt
    return body.clone(x=x2, v=v2)


# -- 1-contact LCP kernel: exact normal impulse with complementarity -----------
def resolve_contact(b1, b2, restitution):
    """Exact impulse for a single normal contact (b1 left of b2, normal +x).
    Complementarity (the 1x1 LCP w = M z + q, w,z>=0, w z = 0): an impulse is
    applied ONLY if the bodies are approaching; then j>=0 and the post-contact
    relative velocity is separating (elastic: reflected; plastic: zero).
    Returns (b1', b2', j, applied). Momentum is conserved by construction."""
    vrel = b2.v - b1.v                       # >0 separating, <0 approaching
    if not (vrel < Z(0)):
        return b1, b2, Z(0), False           # not approaching: z = 0
    inv = b1.inv_mass() + b2.inv_mass()
    j = (Z(0) - (Z(1) + restitution)) * vrel / inv     # >= 0
    b1p = b1.clone(v=b1.v - j * b1.inv_mass())
    b2p = b2.clone(v=b2.v + j * b2.inv_mass())
    return b1p, b2p, j, True


def separating(b1, b2):
    return (b2.v - b1.v) >= Z(0)


# -- conservation witnesses (falsifiers) ---------------------------------------
def momentum_conserved(before, after):
    return momentum(before) == momentum(after)


def energy_conserved(before, after):
    return two_kinetic(before) == two_kinetic(after)


def energy_nonincreasing(before, after):
    return two_kinetic(after) <= two_kinetic(before)


# -- CCD: exact time-of-impact (the geometric witness) -------------------------
def time_of_impact(b1, b2, dt):
    """Earliest exact time t in [0,dt] at which b1.right meets b2.left, given
    constant velocities (right edge of 1 catches left edge of 2). Returns the
    exact rational t, or None if they do not close within dt. This is what makes
    a fast body UNABLE to tunnel through a thin wall: the impact time is found
    exactly, not sampled."""
    gap = b2.left() - b1.right()             # current separation (>=0 apart)
    rel = b1.v - b2.v                         # closing speed of the edges
    if not (rel > Z(0)):
        return None                           # not closing
    t = gap / rel
    if Z(0) <= t and t <= dt:
        return t
    return None


# -- the step function: (X_t, V_t) + F -> (X_t+1, V_t+1) ------------------------
def step(bodies, forces, dt, restitution):
    """One deterministic step. Integrate velocities (semi-implicit); find the
    EARLIEST contact time by CCD; if a collision occurs within dt, advance every
    body to that fractional time, resolve the contact exactly, then integrate the
    remaining slice. Single earliest contact per step (rung-1 scope). Pure and
    exact: identical inputs -> identical (X_t+1, V_t+1)."""
    # 1. apply forces to velocities (positions provisional).
    moved = [integrate(b, f, dt) for b, f in zip(bodies, forces)]
    vel = [m.v for m in moved]
    # 2. earliest CCD time over ordered adjacent pairs, at the NEW velocities.
    at_start = [b.clone(v=vel[i]) for i, b in enumerate(bodies)]
    earliest, pair = None, None
    for i in range(len(at_start) - 1):
        t = time_of_impact(at_start[i], at_start[i + 1], dt)
        if t is not None and (earliest is None or t < earliest):
            earliest, pair = t, i
    if earliest is None:
        return moved                          # no contact: plain integration
    # 3. advance ALL bodies to the impact time (fractional slice).
    sliced = [b.clone(x=b.x + vel[i] * earliest, v=vel[i])
              for i, b in enumerate(bodies)]
    # 4. resolve the earliest contact exactly.
    i = pair
    b1p, b2p, _j, _ap = resolve_contact(sliced[i], sliced[i + 1], restitution)
    sliced[i], sliced[i + 1] = b1p, b2p
    # 5. integrate the remaining time slice with the post-contact velocities.
    rest = dt - earliest
    return [b.clone(x=b.x + b.v * rest) for b in sliced]


# -- canonical state digest (a reproducible witness of (X,V)) ------------------
def state_digest(bodies):
    """Digest(State) = SHA-256(canonical serialization). Bodies are serialized in
    given order as signed 8-byte big-endian integer fields of their EXACT rational
    coordinates -- so identical state -> identical digest on any placement."""
    out = bytearray(b"URDRPH1")
    out += struct.pack(">i", len(bodies))
    for b in bodies:
        for val in (b.x.n, b.x.d, b.r.n, b.r.d, b.v.n, b.v.d):
            out += struct.pack(">q", val)
        out += struct.pack(">q", b.m)
    return hashlib.sha256(bytes(out)).hexdigest()
