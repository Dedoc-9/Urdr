# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Adversarial / property hardening for urdr-physics (roadmap step 2).

Corpus conformance pins a handful of exact digests; these tests instead assert
INVARIANTS across many deterministically-generated scenarios — the confidence
that the exact engine behaves correctly beyond the pinned corpus, before any new
capability is added. Everything is deterministic: a fixed-seed integer LCG
generates the parameters (no real RNG anywhere in the authority path), so the
suite is fully reproducible.

Invariants:
  * random 2D/3D collisions conserve the momentum vector ALWAYS, conserve energy
    EXACTLY when elastic, and never increase it when inelastic;
  * a resting n-stack propagates to λ=[n, n-1, …, 1] exactly and complementary,
    for deep stacks (n up to 12);
  * a k-link articulated chain is held exactly (Jv=0) and conserves momentum,
    for long chains (k up to 15);
  * degenerate systems (redundant joints, inconsistent LCPs) REFUSE;
  * i64 overflow REFUSES;
  * a generated scene digests identically twice (determinism)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import dynamics_nd as ND                               # noqa: E402
import contact_lcp as L                                # noqa: E402
import articulated as J                                # noqa: E402
from dynamics_nd import Ball                           # noqa: E402
from contact_lcp import Contact                        # noqa: E402
from vecq import vec, Vec                              # noqa: E402
from rational import Q, Z, RationalError               # noqa: E402


class _LCG:
    """Deterministic linear-congruential generator — reproducible test inputs,
    no real randomness in any authority path."""
    def __init__(self, seed):
        self.x = seed

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + self.nxt() % (hi - lo + 1)


class RandomCollisions(unittest.TestCase):
    def test_momentum_and_energy_invariants(self):
        r = _LCG(20260710)
        collided = 0
        for _ in range(300):
            dim = 2 if r.rng(0, 1) == 0 else 3
            def rv():
                return Vec([Z(r.rng(-6, 6)) for _ in range(dim)])
            a = Ball(rv(), Z(1), rv(), r.rng(1, 6))
            b = Ball(rv(), Z(1), rv(), r.rng(1, 6))
            if a.x == b.x:
                continue                                  # coincident: no normal
            a2, b2, ap = ND.resolve_spheres(a, b, Z(1))   # elastic
            if ap:
                collided += 1
            self.assertTrue(ND.momentum_conserved([a, b], [a2, b2]))
            self.assertTrue(ND.energy_conserved([a, b], [a2, b2]))
            a3, b3, _ = ND.resolve_spheres(a, b, Z(0))     # inelastic
            self.assertTrue(ND.energy_nonincreasing([a, b], [a3, b3]))
        self.assertGreater(collided, 50)                   # non-vacuity


class DeepStacks(unittest.TestCase):
    def test_propagation_scales_to_deep_stacks(self):
        up = vec(1)
        for n in range(1, 13):
            vels = [vec(0)] + [vec(-1)] * n
            inv = [Z(0)] + [Z(1)] * n
            contacts = [Contact(0, 1, up)] + [Contact(i, i + 1, up) for i in range(1, n)]
            a, b = L.delassus(vels, inv, contacts)
            lam, w = L.solve_lcp(a, b)
            self.assertEqual(lam, [Z(n - i) for i in range(n)], f"rest{n} propagation")
            self.assertTrue(L.complementary(lam, w))


class LongChains(unittest.TestCase):
    def test_chain_held_and_momentum_conserved(self):
        for k in range(2, 16):
            p = [vec(i, 0) for i in range(k + 1)]
            vels = [vec(2, 0)] + [vec(0, 0)] * k
            inv = [Z(1)] * (k + 1)
            masses = [1] * (k + 1)
            rows = [J.distance_row(i, i + 1, p[i], p[i + 1]) for i in range(k)]
            new, lam = J.solve(vels, inv, rows)
            self.assertTrue(J.satisfied(new, rows), f"chain k={k} not held")
            self.assertEqual(J.momentum(vels, masses), J.momentum(new, masses))


class Degeneracy(unittest.TestCase):
    def test_redundant_joint_refuses(self):
        dup = [J.distance_row(0, 1, vec(0, 0), vec(1, 0)),
               J.distance_row(0, 1, vec(0, 0), vec(1, 0))]
        with self.assertRaises(RationalError) as ctx:
            J.solve([vec(1, 0), vec(0, 0)], [Z(1), Z(1)], dup)
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")

    def test_inconsistent_lcp_refuses(self):
        with self.assertRaises(RationalError):
            L.solve_lcp([[Z(0)]], [Z(-1)])

    def test_overflow_boundary_refuses(self):
        big = Q(1 << 40, 1)
        with self.assertRaises(RationalError):
            L.lin_solve([[Z(1), big], [big, Z(1)]], [Z(1), Z(1)])


class Determinism(unittest.TestCase):
    def test_generated_scene_digests_identically_twice(self):
        r = _LCG(42)
        bodies = [Ball(vec(r.rng(-4, 4), r.rng(-4, 4)), Z(1),
                       vec(r.rng(-3, 3), r.rng(-3, 3)), r.rng(1, 4)) for _ in range(3)]
        forces = [Vec([Z(0), Z(0)]) for _ in bodies]
        d1 = ND.state_digest(ND.step(bodies, forces, Z(1), Z(1)))
        d2 = ND.state_digest(ND.step(bodies, forces, Z(1), Z(1)))
        self.assertEqual(d1, d2)


if __name__ == "__main__":
    unittest.main()
