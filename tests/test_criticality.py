# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-criticality (`tools/physics/criticality.py`) — the deterministic
branching-diffusion / reactor-kinetics field: keff = 2.0 × Galton board + Doppler.

Pinned laws:
  * TRANSPORT CONSERVES EXACTLY — the flux-form Galton/diffusion step conserves total
    population bit-for-bit (reflecting), regardless of rounding, over a non-round IC;
  * VACUUM LEAKS — a vacuum boundary strictly loses population (leakage is real);
  * GALTON GOLDEN — a point source under pure transport reproduces the pinned distribution
    trace, deterministically twice;
  * EIGENVALUE — keff = 1 is stationary, keff < 1 decays, keff = 2 with NO regulator RAISES
    FIELD-REFUSE at the bound (supercritical refuses, never wraps);
  * DOPPLER REGULATES — supercritical k0 = 2.0 WITH Doppler converges to a bounded steady
    state and reproduces the pinned trace;
  * DOPPLER IS LOAD-BEARING (non-vacuity) — the SAME supercritical start without Doppler
    explodes to FIELD-REFUSE; the regulator is what makes keff = 2.0 stable."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "physics")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import criticality as C                                     # noqa: E402
from field import FixedPoint as FP, FieldError              # noqa: E402


def _golden(name):
    path = os.path.join(_ROOT, "tools", "physics", "conformance_criticality.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


class Transport(unittest.TestCase):
    def test_transport_conserves_exactly(self):
        n = [FP.unit(v, 7) for v in (3, 11, 29, 101, 7, 5, 88, 2, 50, 13, 64)]  # non-round
        t0 = C.total(n)
        for _ in range(50):
            n = C.transport(n, reflect=True)
        self.assertEqual(C.total(n), t0, "flux-form transport did not conserve exactly")

    def test_vacuum_boundary_leaks(self):
        n = C.seed_field(21, 1000)
        before = C.total(n)
        for _ in range(12):
            n = C.transport(n, reflect=False)
        self.assertLess(C.total(n), before, "a vacuum boundary did not leak")


class Galton(unittest.TestCase):
    def test_galton_golden_twice(self):
        t1 = C.run_trace(C.galton_scene())
        t2 = C.run_trace(C.galton_scene())
        self.assertEqual(t1, t2, "the Galton run is nondeterministic")
        self.assertEqual(t1, _golden("galton"), "the Galton distribution trace drifted from its golden")


class Eigenvalue(unittest.TestCase):
    def test_critical_is_stationary(self):
        states, _ = C.simulate(w=21, gens=40, k0n=1, k0d=1, reflect=True)  # keff = 1
        self.assertEqual(C.total(states[-1]), C.total(states[0]), "keff=1 was not stationary")

    def test_subcritical_decays(self):
        states, _ = C.simulate(w=21, gens=20, k0n=1, k0d=2, reflect=True)  # keff = 1/2
        self.assertLess(C.total(states[-1]), C.total(states[0]), "keff<1 did not decay")

    def test_supercritical_unregulated_refuses(self):
        with self.assertRaises(FieldError):                                # keff = 2, no Doppler
            C.simulate(**C.unregulated_scene())


class Doppler(unittest.TestCase):
    def test_regulated_golden_twice(self):
        t1 = C.run_trace(C.regulated_scene())
        t2 = C.run_trace(C.regulated_scene())
        self.assertEqual(t1, t2, "the Doppler-regulated run is nondeterministic")
        self.assertEqual(t1, _golden("doppler"), "the regulated trace drifted from its golden")

    def test_converges_to_bounded_steady_state(self):
        states, _ = C.simulate(**C.regulated_scene())
        tail = [C.total(s) for s in states[-6:]]
        self.assertEqual(len(set(tail)), 1, "the regulated population did not reach a steady state")

    def test_doppler_is_load_bearing(self):
        # the SAME supercritical k0=2.0: with Doppler it stays bounded; without it, FIELD-REFUSE.
        C.run_trace(C.regulated_scene())                                   # must NOT raise
        with self.assertRaises(FieldError):
            C.run_trace(C.unregulated_scene())                             # must raise


if __name__ == "__main__":
    unittest.main()
