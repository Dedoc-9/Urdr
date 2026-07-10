# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-physics rung 3 (the exact n-contact frictionless LCP).

Pins the properties that make simultaneous-contact resolution a certified,
reproducible solve:
  * known LCPs solve to their exact lambda;
  * a resting stack propagates exactly: lambda = [n, n-1, ..., 1] and every
    body comes to rest (w = 0 at active contacts);
  * the complementarity certificate holds (lambda,w >= 0, lambda_i w_i = 0);
  * a WRONG lambda fails the certificate (non-vacuity);
  * an isolated (all-dynamic) multi-contact impact conserves the momentum vector;
  * the solve is deterministic (same digest twice);
  * a degenerate/inconsistent LCP REFUSES (PHYS-REFUSE), never guesses;
  * i64 overflow refuses.
No float, no tolerance; each negative test asserts the wrong outcome would pass."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import contact_lcp as L                                # noqa: E402
import lcp_scenes                                      # noqa: E402
from contact_lcp import Contact                        # noqa: E402
from vecq import vec                                   # noqa: E402
from rational import Q, Z, RationalError               # noqa: E402


def _M(rows):
    return [[Z(v) for v in r] for r in rows]


def _V(vs):
    return [Z(v) for v in vs]


def _load_goldens():
    out = {}
    with open(os.path.join(_PDIR, "conformance_lcp.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dg = ln.split()
                out[name] = dg
    return out


class KnownLCPs(unittest.TestCase):
    def test_coupled_solution(self):
        lam, w = L.solve_lcp(_M([[2, 1], [1, 2]]), _V([-3, -3]))
        self.assertEqual(lam, [Z(1), Z(1)])
        self.assertTrue(L.complementary(lam, w))

    def test_one_active_one_separating(self):
        lam, w = L.solve_lcp(_M([[1, 0], [0, 1]]), _V([-1, 2]))
        self.assertEqual(lam, [Z(1), Z(0)])
        self.assertEqual(w, [Z(0), Z(2)])

    def test_all_separating_zero_impulse(self):
        lam, w = L.solve_lcp(_M([[1, 0], [0, 1]]), _V([2, 3]))
        self.assertEqual(lam, [Z(0), Z(0)])


class Scenes(unittest.TestCase):
    def test_each_scene_reproducible_and_matches_golden(self):
        goldens = _load_goldens()
        self.assertEqual(set(goldens), set(lcp_scenes.SCENES))
        for name in lcp_scenes.SCENES:
            l1, w1 = lcp_scenes.run(name)
            l2, w2 = lcp_scenes.run(name)
            d1 = L.lcp_digest(l1, w1)
            self.assertEqual(d1, L.lcp_digest(l2, w2), f"{name} nondeterministic")
            self.assertEqual(d1, goldens[name], f"{name} != golden")
            self.assertTrue(L.complementary(l1, w1), f"{name} certificate fails")

    def test_stack_propagates_and_rests(self):
        vels, inv, _m, contacts = lcp_scenes.sc_rest3()
        new, lam, w = L.resolve(vels, inv, contacts)
        self.assertEqual(lam, [Z(3), Z(2), Z(1)])        # exact propagation
        # every ball comes exactly to rest (velocity 0 in 1D)
        for i in (1, 2, 3):
            self.assertEqual(new[i], vec(0))


class NonVacuity(unittest.TestCase):
    def test_wrong_lambda_fails_certificate(self):
        A, b = _M([[2, 1], [1, 2]]), _V([-3, -3])
        lam, w = L.solve_lcp(A, b)
        self.assertTrue(L.complementary(lam, w))
        bad = [lam[0] + Z(1), lam[1]]                    # perturb an impulse
        wbad = []
        for i in range(2):
            wi = b[i]
            for j in range(2):
                wi = wi + A[i][j] * bad[j]
            wbad.append(wi)
        self.assertFalse(L.complementary(bad, wbad))     # the certificate bites


class MomentumConserved(unittest.TestCase):
    def test_all_dynamic_chain_conserves_momentum(self):
        # three DYNAMIC balls in a row, b0 -> b1 -> b2, two contacts, no static body.
        vels = [vec(2), vec(0), vec(0)]
        inv = [Z(1), Z(1), Z(1)]
        masses = [1, 1, 1]
        up = vec(1)
        contacts = [Contact(0, 1, up), Contact(1, 2, up)]
        before = L.momentum(vels, masses)
        new, lam, w = L.resolve(vels, inv, contacts)
        after = L.momentum(new, masses)
        self.assertEqual(before, after)                  # isolated system: exact
        self.assertTrue(L.complementary(lam, w))


class Refusal(unittest.TestCase):
    def test_inconsistent_lcp_refuses(self):
        # A=[[0]], b=[-1]: no impulse can make w>=0 and the active solve is singular.
        with self.assertRaises(RationalError) as ctx:
            L.solve_lcp(_M([[0]]), _V([-1]))
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")

    def test_i64_overflow_refuses_in_solve(self):
        # a solve whose elimination product (2^40 * 2^40 = 2^80) exceeds i64 must
        # refuse, not wrap. (Q/Vec overflow is also gated in the physics suites.)
        big = Q(1 << 40, 1)
        with self.assertRaises(RationalError) as ctx:
            L.lin_solve([[Z(1), big], [big, Z(1)]], [Z(1), Z(1)])
        self.assertEqual(ctx.exception.code, "PHYS-REFUSE")


if __name__ == "__main__":
    unittest.main()
