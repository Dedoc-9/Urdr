# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-physics rung 1 (exact 1D dynamic mechanics).

Pins the properties that make the step function a deterministic equation of
motion with witnessed conservation laws:
  * a free body conserves momentum; the step digest is reproducible;
  * an ELASTIC contact conserves momentum AND kinetic energy exactly;
  * an INELASTIC contact conserves momentum but strictly LOSES energy, and the
    relative velocity goes to zero (complementarity: bodies separate/rest);
  * momentum is conserved even by a WRONG impulse (equal/opposite is structural),
    so the ENERGY witness is what catches a bad impulse (non-vacuity);
  * CCD finds the exact time-of-impact so a fast body cannot tunnel a thin wall;
  * i64 overflow is a REFUSAL, never a wrap.
No floating point anywhere; each negative test asserts the wrong outcome would
have passed (non-vacuity)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import dynamics as D                                  # noqa: E402
import phys_scenes as scenes                          # noqa: E402  (unique basename)
from dynamics import Body                             # noqa: E402
from rational import Q, Z, RationalError              # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class StepDeterminism(unittest.TestCase):
    def test_each_scene_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(scenes.SCENES))
        for name in scenes.SCENES:
            d1 = D.state_digest(scenes.run(name))
            d2 = D.state_digest(scenes.run(name))
            self.assertEqual(d1, d2, f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")


class FreeBody(unittest.TestCase):
    def test_constant_velocity_and_momentum(self):
        b = [Body(Z(0), Z(0), Z(3), 2)]
        nb = D.step(b, [Z(0)], Z(1), Z(1))
        self.assertEqual(nb[0].v, Z(3))
        self.assertEqual(nb[0].x, Z(3))
        self.assertTrue(D.momentum_conserved(b, nb))


class ElasticContact(unittest.TestCase):
    def setUp(self):
        self.b1 = Body(Z(0), Z(1), Z(2), 3)
        self.b2 = Body(Z(5), Z(1), Z(-1), 5)

    def test_momentum_and_energy_conserved_exactly(self):
        p1, p2, j, ap = D.resolve_contact(self.b1, self.b2, Z(1))
        self.assertTrue(ap and j.n > 0)
        self.assertTrue(D.momentum_conserved([self.b1, self.b2], [p1, p2]))
        self.assertTrue(D.energy_conserved([self.b1, self.b2], [p1, p2]))
        self.assertTrue(D.separating(p1, p2))     # complementarity: w >= 0


class InelasticContact(unittest.TestCase):
    def setUp(self):
        self.b1 = Body(Z(0), Z(1), Z(2), 3)
        self.b2 = Body(Z(5), Z(1), Z(-1), 5)

    def test_momentum_conserved_energy_strictly_lost(self):
        q1, q2, _j, _ap = D.resolve_contact(self.b1, self.b2, Z(0))
        self.assertTrue(D.momentum_conserved([self.b1, self.b2], [q1, q2]))
        self.assertTrue(D.two_kinetic([q1, q2]) < D.two_kinetic([self.b1, self.b2]))
        self.assertEqual(q2.v - q1.v, Z(0))       # perfectly plastic

    def test_wrong_impulse_conserves_momentum_but_violates_energy(self):
        # non-vacuity: momentum alone cannot catch a bad impulse; energy can.
        p1, p2, j, _ = D.resolve_contact(self.b1, self.b2, Z(1))
        jb = j + Z(1)
        w1 = self.b1.clone(v=self.b1.v - jb * self.b1.inv_mass())
        w2 = self.b2.clone(v=self.b2.v + jb * self.b2.inv_mass())
        self.assertTrue(D.momentum_conserved([self.b1, self.b2], [w1, w2]))
        self.assertFalse(D.energy_conserved([self.b1, self.b2], [w1, w2]))


class ContinuousCollision(unittest.TestCase):
    def test_exact_toi_prevents_tunneling(self):
        fast = Body(Z(0), Z(0), Z(10), 1)
        wall = Body(Z(5), Z(0), Z(0), 1000000)
        t = D.time_of_impact(fast, wall, Z(1))
        self.assertEqual(t, Q(1, 2))              # exact rational
        stepped = D.step([fast, wall], [Z(0), Z(0)], Z(1), Z(1))
        self.assertTrue(stepped[0].x <= wall.x)   # did NOT pass through
        self.assertNotEqual(stepped[0].v, Z(10))  # collision changed velocity

    def test_slow_body_has_no_impact(self):
        # non-vacuity: a body that cannot reach the wall in dt has no TOI.
        slow = Body(Z(0), Z(0), Z(3), 1)
        wall = Body(Z(5), Z(0), Z(0), 1000000)
        self.assertIsNone(D.time_of_impact(slow, wall, Z(1)))


class Refusal(unittest.TestCase):
    def test_i64_overflow_refuses(self):
        with self.assertRaises(RationalError) as ctx:
            Q(1 << 62, 1) * Q(1 << 62, 1)
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")
        self.assertEqual((Q(6, 4)).pair(), (3, 2))   # non-vacuity: normal op works

    def test_zero_mass_refuses(self):
        with self.assertRaises(RationalError):
            Body(Z(0), Z(0), Z(0), 0)


if __name__ == "__main__":
    unittest.main()
