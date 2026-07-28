# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/patience.py — THE PRICE OF THE PRICE (URDRPAT1).

  THE STALL COLLAPSE — auditgraph's ladder 1/2/INFINITE holds exactly at T >= Delta and becomes
    0/0/0 below it, because the price was denominated in EXCLUDED CLIENTS and a staller excludes
    none. The patient row is cross-checked against auditgraph, not restated.
  THE UNBREAKABLE TOPOLOGY IS STALL-BREAKABLE — kappa INFINITE, visible cost 0, 3 edges silenced.
  KAPPA OR LAMBDA IS DECIDED BY ONE INEQUALITY — lambda was the right answer to a question the
    previous rung had not posed, so its plant verdict stands and its number returns.
  THE CLOSED FORM — ceil(log2(ceil(Delta/T0))) false alarms, integer-only, 0 exceptions over 512
    pairs, paid once and never again.
  A PLANT THAT IS SOUND AND LOSES ANYWAY — linear growth terminates and costs 199 where doubling
    costs 8. Unaffordable, not incorrect.

Every test can go red (L5); the three plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import auditgraph as AG                                            # noqa: E402
import patience as PT                                              # noqa: E402


class TheStallCollapse(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in PT.SCENES:
            self.assertEqual(PT.scene_result(n), PT.golden(n), n)
            self.assertEqual(PT.scene_result(n), PT.scene_result(n), n)

    def test_free_moves_vanish_exactly_at_delta(self):
        table = PT.free_moves_vanish_exactly_at_delta()
        self.assertEqual(table, ((1, 243, 256), (2, 176, 256), (3, 67, 256),
                                 (4, 0, 256), (5, 0, 256)))
        self.assertTrue(PT.separation_is_exactly_t_ge_delta())

    def test_both_directions_are_witnessed(self):
        """L19 — 'no free moves at T >= Delta' is free if there were never any free moves."""
        table = PT.free_moves_vanish_exactly_at_delta()
        self.assertTrue(any(w > 0 for _T, w, _t in table), "the attack must exist somewhere")
        self.assertTrue(any(w == 0 for _T, w, _t in table), "and vanish somewhere")

    def test_the_ladder_collapses_to_zero_then_returns(self):
        impatient, patient = PT.ladder_under_stall()
        self.assertEqual(impatient, (3, 0, 0, 0), "impatient: no topology has any price")
        self.assertEqual(patient, (4, 1, 2, AG.INFINITE))
        self.assertTrue(PT.ladder_collapses_then_returns())

    def test_the_patient_row_is_auditgraphs_own_numbers(self):
        """Cross-module: the restored ladder must be auditgraph's independent computation, not a
        constant retyped here."""
        k = PT.PINNED_K
        self.assertEqual(AG.exclusion_price(k, AG.path_graph(k)), 1)
        self.assertEqual(AG.exclusion_price(k, AG.ring_graph(k)), 2)
        self.assertIs(AG.exclusion_price(k, AG.complete_graph(k)), AG.INFINITE)

    def test_observation_is_a_function_of_delays_alone(self):
        """The Chandra-Toueg point: there is no field that records intent."""
        self.assertEqual(PT.observation_is_blind_to_cause((1, 5, 2)), (1, 5, 2))
        self.assertEqual(PT.observed_edges(((0, 1), (1, 2)), (1, 9), 3), ((0, 1),))


class TheUnbreakableIsStallBreakable(unittest.TestCase):
    def test_all_pairs_falls_to_patience(self):
        price, visible, silenced = PT.the_unbreakable_topology_is_stall_breakable()
        self.assertIs(price, AG.INFINITE, "no exclusion budget suffices")
        self.assertEqual(visible, 0, "and yet the visible cost of a stall is zero")
        self.assertEqual(silenced, 3)

    def test_kappa_and_lambda_are_two_questions(self):
        kc, lc, kr, lr, coincide = PT.lambda_was_the_answer_to_another_question()
        self.assertIs(kc, AG.INFINITE)
        self.assertEqual(lc, 3, "the complete graph is where they genuinely separate")
        self.assertEqual((kr, lr), (2, 2))
        self.assertTrue(coincide, "on the ring they coincide, which is why the witness is K_n")

    def test_auditgraphs_plant_verdict_still_stands(self):
        """The previous rung's finding is NOT retracted: lambda still over-prices the EXCLUSION
        question 15 times. Two questions, two answers, no contradiction."""
        lo, lu, do, du, total = AG.overprice_census()
        self.assertEqual((lo, lu, do, du, total), (15, 0, 15, 0, 767))

    def test_which_quantity_binds(self):
        table = PT.which_quantity_binds()
        self.assertEqual(table, (("path", 1, 1, 0, 1), ("ring", 2, 2, 0, 2),
                                 ("complete", AG.INFINITE, 3, 0, AG.INFINITE)))
        for _name, _kap, _lam, impatient, _patient in table:
            self.assertEqual(impatient, 0, "below Delta nothing costs the server anything")


class TheClosedForm(unittest.TestCase):
    def test_both_closed_forms_reproduce_their_simulations(self):
        agree, exc, total = PT.closed_form_census()
        self.assertEqual(exc, 0, "a closed form diverged from simulation")
        self.assertEqual((agree, total), (512, 512))
        self.assertTrue(PT.closed_forms_hold())

    def test_the_form_is_integer_only(self):
        """No float may enter an authority path — bit_length is the repo's ceil-log2."""
        for delta, t0, want in ((1, 1, 0), (2, 1, 1), (3, 1, 2), (4, 1, 2), (5, 1, 3),
                                (64, 1, 6), (64, 8, 3), (1000, 1, 10)):
            got = PT.false_alarms_doubling(delta, t0)
            self.assertIsInstance(got, int)
            self.assertEqual(got, want, (delta, t0))

    def test_stabilization_is_finite_and_permanent(self):
        worst, permanent = PT.stabilization_is_finite_and_permanent()
        self.assertEqual(worst, 6)
        self.assertTrue(permanent, "patience must never fall back below Delta once past it")

    def test_a_known_delta_costs_nothing_recurring(self):
        for delta in (1, 7, 64):
            self.assertEqual(PT.false_alarms_doubling(delta, delta), 0)

    def test_nonpositive_inputs_refuse(self):
        for bad in ((0, 1), (1, 0), (-3, 2)):
            with self.assertRaises(PT.PatienceError):
                PT.false_alarms_doubling(*bad)


class ThePlants(unittest.TestCase):
    def test_fixed_patience_never_stabilizes(self):
        """L15 — the difference is not magnitude but UNBOUNDEDNESS."""
        at100, at10000, doubling = PT.fixed_patience_never_stabilizes()
        self.assertEqual((at100, at10000, doubling), (100, 10000, 6))
        self.assertGreater(at10000, at100, "a fixed timeout pays forever")
        self.assertLess(doubling, at100)

    def test_guessing_delta_bites(self):
        exceeded, total = PT.guessing_delta_bites()
        self.assertEqual((exceeded, total), (56, 64))
        self.assertGreater(exceeded, 0, "under DLS the bound exists but is unknown")

    def test_the_linear_plant_is_sound_and_loses_anyway(self):
        """A PLANT CLASS THE REPO HAD NOT NAMED: correct, terminating, and unaffordable."""
        lin, dbl, both_terminate = PT.linear_plant_is_unaffordable_not_wrong()
        self.assertTrue(both_terminate, "it is not incorrect — that is the whole point")
        self.assertEqual((lin, dbl), (63, 6))
        self.assertGreater(lin, dbl)

    def test_the_gap_widens_without_bound(self):
        gap = PT.the_gap()
        self.assertEqual(gap, ((200, 1, 199, 8), (1000, 1, 999, 10),
                               (64, 1, 63, 6), (64, 8, 7, 3)))
        for _d, _t, lin, dbl in gap:
            self.assertGreaterEqual(lin, dbl)


class TheRefusalIsTyped(unittest.TestCase):
    def test_an_impatient_deployment_is_refused_not_downgraded(self):
        """Quoting kappa below the envelope is the inflation this rung exists to prevent."""
        self.assertTrue(PT.refuses_an_impatient_deployment())
        with self.assertRaises(PT.PatienceError):
            PT.require_patience_covers(10, 9)

    def test_a_patient_one_is_admitted(self):
        self.assertTrue(PT.admits_a_patient_one())
        self.assertTrue(PT.require_patience_covers(10, 11))

    def test_an_empty_topology_refuses(self):
        with self.assertRaises(PT.PatienceError):
            PT.free_moves(3, (), 1)

    def test_the_refusal_classes_stay_distinct(self):
        self.assertNotEqual(PT.PatienceError("x").code, AG.AuditGraphError("x").code)


if __name__ == "__main__":
    unittest.main()
