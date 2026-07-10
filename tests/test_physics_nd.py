# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-physics rung 2 (exact n-D vector dynamics, 2D & 3D).

Pins the properties that make 2D/3D dynamics exact and reproducible:
  * each scene's post-step state digest is reproducible + matches its golden;
  * a 2D/3D ELASTIC ball collision conserves the momentum VECTOR and kinetic
    energy EXACTLY over Q (no square root) and leaves the TANGENTIAL velocity
    untouched (correct oblique physics);
  * an INELASTIC collision conserves momentum but strictly loses energy;
  * momentum is structural (a wrong impulse still conserves it) so ENERGY is the
    discriminating witness (non-vacuity);
  * plane CCD (ball vs axis-aligned wall) finds the exact rational time-of-impact
    so a fast ball cannot tunnel;
  * i64 overflow refuses through the vector dot.
No float anywhere; each negative test asserts the wrong outcome would have passed."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import dynamics_nd as D                                # noqa: E402
import nd_scenes                                       # noqa: E402
from dynamics_nd import Ball                           # noqa: E402
from vecq import vec, Vec                              # noqa: E402
from rational import Q, Z, RationalError               # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance_nd.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class StepDeterminism(unittest.TestCase):
    def test_each_scene_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(nd_scenes.SCENES))
        for name in nd_scenes.SCENES:
            d1 = D.state_digest(nd_scenes.run(name))
            d2 = D.state_digest(nd_scenes.run(name))
            self.assertEqual(d1, d2, f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")


class ObliqueElastic2D(unittest.TestCase):
    """A genuinely diagonal normal d=(3,3): tangential is (1,-1)."""
    def setUp(self):
        self.a = Ball(vec(0, 0), Z(1), vec(2, 1), 2)
        self.b = Ball(vec(3, 3), Z(1), vec(-1, -1), 4)

    def test_momentum_and_energy_exact_and_tangential_preserved(self):
        a2, b2, ap = D.resolve_spheres(self.a, self.b, Z(1))
        self.assertTrue(ap)
        self.assertTrue(D.momentum_conserved([self.a, self.b], [a2, b2]))
        self.assertTrue(D.energy_conserved([self.a, self.b], [a2, b2]))
        tang = Vec([Z(1), Z(-1)])                        # perpendicular to d=(1,1)
        self.assertEqual((a2.v - self.a.v).dot(tang), Z(0))
        self.assertEqual((b2.v - self.b.v).dot(tang), Z(0))

    def test_wrong_impulse_conserves_momentum_but_breaks_energy(self):
        a2, b2, _ = D.resolve_spheres(self.a, self.b, Z(1))
        d = self.b.x - self.a.x
        dd = d.dot(d)
        vn = (self.b.v - self.a.v).dot(d)
        kbad = (Z(0) - Z(2) * vn / (dd * (self.a.inv_mass() + self.b.inv_mass()))) * Q(3, 2)
        p = d.scale(kbad)
        w1 = self.a.clone(v=self.a.v - p.scale(self.a.inv_mass()))
        w2 = self.b.clone(v=self.b.v + p.scale(self.b.inv_mass()))
        self.assertTrue(D.momentum_conserved([self.a, self.b], [w1, w2]))
        self.assertFalse(D.energy_conserved([self.a, self.b], [w1, w2]))


class Oblique3D(unittest.TestCase):
    def test_momentum_and_energy_conserved_exactly(self):
        a = Ball(vec(0, 0, 0), Z(1), vec(1, 2, 3), 2)
        b = Ball(vec(2, 2, 2), Z(1), vec(-1, 0, -1), 3)
        a2, b2, ap = D.resolve_spheres(a, b, Z(1))
        self.assertTrue(ap)
        self.assertTrue(D.momentum_conserved([a, b], [a2, b2]))
        self.assertTrue(D.energy_conserved([a, b], [a2, b2]))


class Inelastic(unittest.TestCase):
    def test_momentum_conserved_energy_strictly_lost(self):
        a = Ball(vec(0, 0), Z(1), vec(2, 1), 2)
        b = Ball(vec(3, 3), Z(1), vec(-1, -1), 4)
        a2, b2, _ = D.resolve_spheres(a, b, Z(0))
        self.assertTrue(D.momentum_conserved([a, b], [a2, b2]))
        self.assertTrue(D.two_kinetic([a2, b2]) < D.two_kinetic([a, b]))


class PlaneCCD(unittest.TestCase):
    def test_exact_toi_prevents_tunneling(self):
        ball = Ball(vec(0, 0), Z(0), vec(10, 0), 1)
        t = D.toi_wall(ball, 0, Z(5), Z(1))
        self.assertEqual(t, Q(1, 2))
        stepped = D.step([ball], [vec(0, 0)], Z(1), Z(1), ((0, Z(5)),))
        self.assertTrue(stepped[0].x.c[0] <= Z(5))       # did NOT pass through
        self.assertTrue(stepped[0].v.c[0] < Z(0))        # bounced back

    def test_slow_ball_has_no_impact(self):
        slow = Ball(vec(0, 0), Z(0), vec(3, 0), 1)
        self.assertIsNone(D.toi_wall(slow, 0, Z(5), Z(1)))


class Refusal(unittest.TestCase):
    def test_i64_overflow_refuses_through_dot(self):
        with self.assertRaises(RationalError) as ctx:
            Vec([Q(1 << 62, 1)]).dot(Vec([Q(1 << 62, 1)]))
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")

    def test_dimension_mismatch_refuses(self):
        with self.assertRaises(RationalError):
            Ball(vec(0, 0), Z(1), vec(1, 0, 0), 1)


if __name__ == "__main__":
    unittest.main()
