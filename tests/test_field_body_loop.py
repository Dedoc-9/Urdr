# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the two-way field ↔ body coupling loop.

  * TOTAL MOMENTUM EXACT: for two free bodies in contact with the field pushing
    one of them, `Σ (m·v) + reservoir` is conserved bit-exactly across the step
    (the field↔body ledger), and the contact resolution is a valid LCP.
  * REACTION LOAD-BEARING (red-first non-vacuity): dropping the reservoir debit
    (one-way) makes the total DRIFT — so Newton's third-law term is real.
  * LCP RESOLVES THE FIELD FORCE: a body pushed by the field INTO a wall is held
    at rest and the contact impulse λ exactly balances the field impulse; a field
    pushing AWAY releases the contact (λ = 0) and the body accelerates off.
  * BODY → FIELD: advecting the field by the body's motion conserves field mass
    exactly (frozen flux form) — the loop's return arrow.
  * DETERMINISM."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

from rational import Q                                   # noqa: E402
from vecq import Vec                                     # noqa: E402
from contact_lcp import Contact, complementary           # noqa: E402
from field import FixedPoint                             # noqa: E402
import field_body_loop as L                              # noqa: E402


def _ramp():
    grid = [FixedPoint.unit(1, 10), FixedPoint.unit(2, 10), FixedPoint.unit(4, 10),
            FixedPoint.unit(7, 10), FixedPoint.unit(10, 10)]
    return grid, 5, 1


def _rest():
    return [Vec([Q(0), Q(0)]), Vec([Q(0), Q(0)])]


class TotalMomentum(unittest.TestCase):
    def test_field_plus_body_reservoir_conserved_exactly(self):
        grid, w, h = _ramp()
        vels, masses, invm = _rest(), [1, 1], [Q(1), Q(1)]
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]     # A→B normal +x
        cells, r0 = [2, None], Vec([Q(0), Q(0)])
        p0 = L.total_momentum(vels, masses, r0)
        vnew, lam, wsl, _, r1, j = L.coupled_step(grid, w, h, vels, invm, contacts,
                                                  cells, (1, 4), (1, 2), r0)
        p1 = L.total_momentum(vnew, masses, r1)
        self.assertEqual(p1, p0)                          # exact
        self.assertTrue(complementary(lam, wsl))          # valid LCP certificate
        self.assertFalse(j == Vec([Q(0), Q(0)]))          # the field actually pushed

    def test_dropping_reservoir_drifts_non_vacuity(self):
        grid, w, h = _ramp()
        vels, masses, invm = _rest(), [1, 1], [Q(1), Q(1)]
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]
        cells, r0 = [2, None], Vec([Q(0), Q(0)])
        p0 = L.total_momentum(vels, masses, r0)
        vnew, _, _, _, _, _ = L.coupled_step(grid, w, h, vels, invm, contacts,
                                             cells, (1, 4), (1, 2), r0)
        p_oneway = L.total_momentum(vnew, masses, r0)     # reservoir NOT debited
        self.assertNotEqual(p_oneway, p0)                 # one-way drifts


class LcpResolvesField(unittest.TestCase):
    def test_pushed_into_wall_rests_and_lambda_balances(self):
        grid, w, h = _ramp()                              # gradient +x
        vels, invm = _rest(), [Q(1), Q(0)]                # body 0, static wall 1
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]     # wall normal +x
        vnew, lam, wsl, _, _, j = L.coupled_step(grid, w, h, vels, invm, contacts,
                                                 [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
        self.assertTrue(vnew[0].c[0].is_zero())           # body held at rest (v_x = 0)
        self.assertEqual(lam[0], j.c[0])                  # contact impulse == field impulse
        self.assertTrue(complementary(lam, wsl))

    def test_pushed_away_releases_contact(self):
        grid, w, h = _ramp()
        rev = list(reversed(grid))                        # gradient now −x at cell 2
        vels, invm = _rest(), [Q(1), Q(0)]
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]
        vnew, lam, wsl, _, _, _ = L.coupled_step(rev, w, h, vels, invm, contacts,
                                                 [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
        self.assertTrue(lam[0].is_zero())                 # contact releases
        self.assertLess(vnew[0].c[0].n, 0)                # body accelerates away (−x)


class BodyToField(unittest.TestCase):
    def test_body_advection_conserves_field_mass(self):
        grid, w, h = _ramp()
        vels, invm = _rest(), [Q(1), Q(0)]
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]
        m0 = sum(grid)
        _, _, _, ngrid, _, _ = L.coupled_step(grid, w, h, vels, invm, contacts,
                                              [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]),
                                              body_advect=((1, 4), (0, 1)))
        self.assertEqual(sum(ngrid), m0)                  # field mass exact under body drift


class Determinism(unittest.TestCase):
    def test_deterministic(self):
        grid, w, h = _ramp()
        vels, invm = _rest(), [Q(1), Q(1)]
        contacts = [Contact(0, 1, Vec([Q(1), Q(0)]))]
        args = (grid, w, h, vels, invm, contacts, [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
        a = L.coupled_step(*args)
        b = L.coupled_step(*args)
        self.assertEqual(a[0][0], b[0][0])
        self.assertEqual(a[4], b[4])


if __name__ == "__main__":
    unittest.main()
