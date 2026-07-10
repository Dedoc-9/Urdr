# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-physics rung 4 (exact articulated / joint constraints).

Pins the properties that make joint resolution a certified, reproducible solve:
  * each scene's solved-system digest is reproducible + matches its golden;
  * after the solve EVERY constraint velocity is exactly zero (the joint holds);
  * a rigid rod moves both bodies together; an all-dynamic system conserves the
    momentum vector; a rigid triangle stays rigid (its Jacobian IS the rigidity
    matrix);
  * a bob pinned to a static anchor is driven to rest (held);
  * NON-VACUITY: leaving velocities unsolved leaves a nonzero constraint velocity;
  * redundant/conflicting constraints (singular A) REFUSE (PHYS-REFUSE), never
    guess -- rank(A) is the uniqueness certificate;
  * i64 overflow refuses.
No float, no tolerance; each negative test asserts the wrong outcome would pass."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import articulated as J                                # noqa: E402
import joint_scenes                                    # noqa: E402
from vecq import vec                                   # noqa: E402
from rational import Q, Z, RationalError               # noqa: E402


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance_joint.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class Scenes(unittest.TestCase):
    def test_each_scene_reproducible_matches_golden_and_satisfied(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(joint_scenes.SCENES))
        for name in joint_scenes.SCENES:
            n1, l1, rows = joint_scenes.run(name)
            n2, l2, _ = joint_scenes.run(name)
            d1 = J.joint_digest(n1, l1)
            self.assertEqual(d1, J.joint_digest(n2, l2), f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")
            self.assertTrue(J.satisfied(n1, rows), f"{name} constraint not held")


class Rod(unittest.TestCase):
    def test_moves_together_and_conserves_momentum(self):
        vels, inv, masses, rows = joint_scenes.sc_rod()
        new, lam = J.solve(vels, inv, rows)
        self.assertEqual(new[0], new[1])                 # rigid: same along-rod velocity
        self.assertEqual(J.momentum(vels, masses), J.momentum(new, masses))
        self.assertTrue(J.satisfied(new, rows))


class Pendulum(unittest.TestCase):
    def test_bob_held_at_anchor(self):
        vels, inv, masses, rows = joint_scenes.sc_pendulum()
        new, lam = J.solve(vels, inv, rows)
        self.assertEqual(new[1], vec(0, 0))              # velocity driven to zero
        self.assertTrue(J.satisfied(new, rows))


class RigidTriangle(unittest.TestCase):
    def test_stays_rigid_and_conserves_momentum(self):
        vels, inv, masses, rows = joint_scenes.sc_triangle()
        new, lam = J.solve(vels, inv, rows)
        self.assertTrue(J.satisfied(new, rows))          # every edge-rate zero
        self.assertEqual(J.momentum(vels, masses), J.momentum(new, masses))


class NonVacuity(unittest.TestCase):
    def test_unsolved_leaves_nonzero_constraint_velocity(self):
        vels, inv, masses, rows = joint_scenes.sc_triangle()
        self.assertFalse(J.satisfied(vels, rows))        # before solving: not held
        new, lam = J.solve(vels, inv, rows)
        self.assertTrue(J.satisfied(new, rows))          # after: held


class Refusal(unittest.TestCase):
    def test_redundant_constraints_refuse(self):
        # the same rod twice -> singular A -> rank certificate of non-uniqueness.
        p0, p1 = vec(0, 0), vec(1, 0)
        rows = [J.distance_row(0, 1, p0, p1), J.distance_row(0, 1, p0, p1)]
        with self.assertRaises(RationalError) as ctx:
            J.solve([vec(1, 0), vec(0, 0)], [Z(1), Z(1)], rows)
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")

    def test_i64_overflow_refuses(self):
        big = Q(1 << 40, 1)
        # a distance row whose gradient magnitude makes A overflow the i64 bound.
        rows = [[(0, vec(0, 0).scale(Z(0)) + vec(1, 0).scale(big))]]
        with self.assertRaises(RationalError):
            J.solve([vec(1, 0)], [big], rows)


if __name__ == "__main__":
    unittest.main()
