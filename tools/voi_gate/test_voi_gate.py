# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the VoI decision gate. This tool is FLOAT (entropy in bits) —
a runtime decision engine, NOT the Urðr integer language core and NOT sealed by
verify.py. It gets its own runner. Every test can fail; the gate is required to
go BOTH green and red (a decision boundary that cannot redden is ceremony)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voi_gate as G  # noqa: E402


class TestEntropyAndVoI(unittest.TestCase):
    def test_entropy_known_values(self):
        self.assertAlmostEqual(G.entropy([0.5, 0.5]), 1.0)
        self.assertAlmostEqual(G.entropy([1.0]), 0.0)
        self.assertAlmostEqual(G.entropy([0.25]*4), 2.0)

    def test_perfect_observation_yields_full_information(self):
        # a perfect test collapses X entirely: VoI = H(prior) = 1 bit at p=0.5
        self.assertAlmostEqual(G.binary_diagnostic_voi(0.5, 1.0, 1.0), 1.0)

    def test_useless_observation_yields_zero(self):
        # sensitivity = 1-specificity => O independent of X => VoI = 0
        self.assertAlmostEqual(G.binary_diagnostic_voi(0.5, 0.5, 0.5), 0.0)

    def test_voi_is_mutual_information_hence_nonnegative(self):
        # the fix for last turn: a SINGLE surprising obs can raise entropy, but
        # EXPECTED info gain (mutual information) is >= 0 for every parameter.
        for p in (0.05, 0.2, 0.5, 0.9):
            for sens in (0.1, 0.5, 0.7, 0.99):
                for spec in (0.1, 0.5, 0.7, 0.99):
                    self.assertGreaterEqual(
                        G.binary_diagnostic_voi(p, sens, spec), -1e-12)

    def test_voi_bounded_by_prior_entropy(self):
        # you cannot learn more than there was to know
        for p in (0.1, 0.3, 0.5):
            self.assertLessEqual(G.binary_diagnostic_voi(p, 0.9, 0.8),
                                 G.entropy([1-p, p]) + 1e-12)


class TestDecisionGate(unittest.TestCase):
    def test_gate_goes_green_and_red(self):
        # non-vacuity: the boundary MUST be able to do both
        green = G.Action("cheap_high_info", voi_bits=1.0, cost=0.1)
        red = G.Action("dear_low_info", voi_bits=0.04, cost=0.8)
        self.assertTrue(green.gate())
        self.assertFalse(red.gate())

    def test_margin_blocks_marginal_actions(self):
        a = G.Action("marginal", voi_bits=0.5, cost=0.4, margin=0.0)
        self.assertTrue(a.gate())                       # net 0.1 > 0
        b = G.Action("marginal", voi_bits=0.5, cost=0.4, margin=0.2)
        self.assertFalse(b.gate())                      # net 0.1 !> 0.2 (rho bites)

    def test_value_per_bit_is_an_explicit_exchange_rate(self):
        # bits and cost are different units; value_per_bit converts. At 0, bits
        # are worthless and everything is RED — the units are explicit, not hidden.
        a = G.Action("x", voi_bits=5.0, cost=0.1, value_per_bit=0.0)
        self.assertFalse(a.gate())
        b = G.Action("x", voi_bits=5.0, cost=0.1, value_per_bit=1.0)
        self.assertTrue(b.gate())

    def test_efficiency_in_unit_interval(self):
        a = G.Action("x", voi_bits=0.73, cost=0.12)
        self.assertGreaterEqual(a.efficiency(), 0.0)
        self.assertLessEqual(a.efficiency(), 1.0)
        # more value at same cost => higher efficiency
        b = G.Action("x", voi_bits=1.46, cost=0.12)
        self.assertGreater(b.efficiency(), a.efficiency())

    def test_report_has_the_three_outputs(self):
        r = G.Action("check", voi_bits=0.73, cost=0.12).report()
        self.assertEqual(set(r) >= {"uncertainty_removed_bits", "cost_units",
                                    "decision"}, True)
        self.assertIn(r["decision"], ("GREEN", "RED"))


class TestGateWorthRunning(unittest.TestCase):
    def test_ceremony_check_is_refused(self):
        # a check is worth running only if dH > cost + rho, else it is ceremony
        self.assertFalse(G.worth_running(delta_h_bits=0.02, cost=0.5, margin=0.0))
        self.assertTrue(G.worth_running(delta_h_bits=0.9, cost=0.1, margin=0.0))


class TestAttemptedClaim(unittest.TestCase):
    def test_proposes_never_grades(self):
        c = G.attempted_claim("test_suite_run", 0.73)
        self.assertEqual(c["requested_grade"], "MEASURED")   # REQUESTED, not held
        self.assertNotIn("grade", c)                          # never a granted grade
        self.assertNotIn("GROUNDED", repr(c))                 # never mints Grounded
        self.assertEqual(c["observed_delta_bits"], 0.73)


class TestFalsifierLedger(unittest.TestCase):
    def test_calibration_surface_exists_and_tallies(self):
        p = G.Pipeline()
        p.evaluate(G.Action("a", voi_bits=1.0, cost=0.1))   # GREEN
        p.evaluate(G.Action("b", voi_bits=0.02, cost=0.9))  # RED
        p.record_outcome("a", prevented_failure=True)
        p.record_outcome("b", prevented_failure=False)
        cal = p.calibration()
        self.assertEqual(cal["green_n"], 1)
        self.assertEqual(cal["green_prevented"], 1)
        self.assertEqual(cal["red_n"], 1)

    def test_determinism_same_inputs_same_bits(self):
        a = G.binary_diagnostic_voi(0.3, 0.9, 0.8)
        b = G.binary_diagnostic_voi(0.3, 0.9, 0.8)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
