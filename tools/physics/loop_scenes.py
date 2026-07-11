# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical two-way field↔body loop scenes → URDRLOOP digests.

Each scene runs one coupled step (`field_body_loop.coupled_step`) and serializes
the exact-`Q` coupled STATE — new body velocities, the contact impulses `λ`, and
the field-momentum reservoir — to a SHA-256 digest. Everything is exact rational,
so the digest is reproducible; an independent placement (`urdr_physics_rs/`) must
reproduce it bit-for-bit.

  * `loop_push2`   — two free bodies in contact; the field pushes one.
  * `loop_wall`    — a body pushed by the field into a static wall (held; λ
                     balances the field impulse).
  * `loop_chain3`  — three bodies, two contacts; the field pushes the first and
                     the impulse propagates through the chain (multi-contact).

Serialization: `MAGIC "URDRLOOP" | u8 nbodies | per-body (vx,vy as Q pairs) |
u8 ncontacts | per-contact λ (Q pair) | reservoir (vx,vy as Q pairs)`, each `Q`
as two signed i64 big-endian (n, d), canonically reduced."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rational import Q                                   # noqa: E402
from vecq import Vec                                     # noqa: E402
from contact_lcp import Contact                          # noqa: E402
from field import FixedPoint                             # noqa: E402
import field_body_loop as L                              # noqa: E402

MAGIC = b"URDRLOOP"


def _ser_q(q):
    return q.n.to_bytes(8, "big", signed=True) + q.d.to_bytes(8, "big", signed=True)


def _ser_vec(v):
    out = bytearray()
    for c in v.c:
        out += _ser_q(c)
    return bytes(out)


def digest_state(vels, lam, reservoir):
    """The URDRLOOP digest of a coupled state (velocities, λ, reservoir)."""
    out = bytearray(MAGIC)
    out.append(len(vels))
    for v in vels:
        out += _ser_vec(v)
    out.append(len(lam))
    for l in lam:
        out += _ser_q(l)
    out += _ser_vec(reservoir)
    return hashlib.sha256(bytes(out)).hexdigest()


def _ramp():
    grid = [FixedPoint.unit(1, 10), FixedPoint.unit(2, 10), FixedPoint.unit(4, 10),
            FixedPoint.unit(7, 10), FixedPoint.unit(10, 10)]
    return grid, 5, 1


def _rest(n):
    return [Vec([Q(0), Q(0)]) for _ in range(n)]


def scene_push2():
    grid, w, h = _ramp()
    vn, lam, _, _, r1, _ = L.coupled_step(
        grid, w, h, _rest(2), [Q(1), Q(1)], [Contact(0, 1, Vec([Q(1), Q(0)]))],
        [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
    return digest_state(vn, lam, r1)


def scene_wall():
    grid, w, h = _ramp()
    vn, lam, _, _, r1, _ = L.coupled_step(
        grid, w, h, _rest(2), [Q(1), Q(0)], [Contact(0, 1, Vec([Q(1), Q(0)]))],
        [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
    return digest_state(vn, lam, r1)


def scene_chain3():
    grid, w, h = _ramp()
    cc = [Contact(0, 1, Vec([Q(1), Q(0)])), Contact(1, 2, Vec([Q(1), Q(0)]))]
    vn, lam, _, _, r1, _ = L.coupled_step(
        grid, w, h, _rest(3), [Q(1), Q(1), Q(1)], cc,
        [2, None, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
    return digest_state(vn, lam, r1)


SCENES = {"loop_push2": scene_push2, "loop_wall": scene_wall, "loop_chain3": scene_chain3}


def digests():
    return {name: fn() for name, fn in SCENES.items()}


if __name__ == "__main__":
    for name, dig in digests().items():
        print(f"{name:12s} {dig}")
