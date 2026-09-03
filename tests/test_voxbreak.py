# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxbreak (URDRVXZ1) — the break-even ledger, and the gate that was proposed is the wrong one."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxbreak as VB                                         # noqa: E402
import voxmanifold as VM                                      # noqa: E402
import voxfriction as VF                                      # noqa: E402
import voxcond as VD                                          # noqa: E402
import voxwork as VO                                          # noqa: E402


class TheContract(unittest.TestCase):
    def test_the_observable_never_moves_under_any_rule(self):
        """A gate that changes what is seen is not a cheaper arrangement, it is a bug."""
        self.assertTrue(VB.the_observable_never_moves_under_any_rule())

    def test_every_rule_is_measured(self):
        self.assertEqual(len(VB.RULES), 5)
        self.assertEqual(sorted(VB.ADMIT), sorted(VB.RULES))

    def test_an_undeclared_rule_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.ledger("four")

    def test_the_accounts_are_never_fused(self):
        """A break-even question answered with one number cannot say which term is responsible."""
        for r in VB.RULES:
            a = VB.ledger(r)
            self.assertEqual(VB.spend(r), sum(a[k] for k in VB.ACCOUNTS))
            self.assertEqual(len(VB.ACCOUNTS), 5)


class TheBaselines(unittest.TestCase):
    def test_the_none_rule_is_exactly_the_cold_tiled_loop(self):
        self.assertTrue(VB.the_none_rule_is_exactly_the_cold_tiled_loop())

    def test_the_all_rule_is_exactly_the_committed_traversal(self):
        """This ledger is a DECOMPOSITION of a committed number, not a second measurement of it."""
        self.assertTrue(VB.the_all_rule_is_exactly_the_committed_traversal())

    def test_the_none_rule_pays_no_admission_read(self):
        """A statically empty gate never reads the tile; charging it would flatter every other rule."""
        self.assertEqual(VB.ledger("none")["recognise"], 0)
        for r in ("one", "two", "three", "all"):
            self.assertGreater(VB.ledger(r)["recognise"], 0)

    def test_retirement_is_baseline_minus_executed(self):
        for r in VB.RULES:
            self.assertEqual(VB.retired(r), VB.spend("none") - VB.spend(r))

    def test_the_reference_is_measured_over_these_same_states(self):
        self.assertEqual(VB.net("all"), VB.spend("all") - VM.reference_cost())


class TheRefutation(unittest.TestCase):
    def test_single_ownership_is_not_the_profitable_gate(self):
        """THE RESULT THIS RUNG EXISTS TO REPORT."""
        self.assertTrue(VB.single_ownership_is_not_the_profitable_gate())

    def test_the_single_owner_gate_declines_tiles_that_would_have_succeeded(self):
        self.assertGreater(VB.ledger("one")["execute"], VB.ledger("all")["execute"])

    def test_the_gates_whole_gain_is_waste_avoided(self):
        self.assertTrue(VB.the_gates_whole_gain_is_waste_avoided())

    def test_the_best_rule_is_not_the_proposed_one(self):
        self.assertNotEqual(VB.best(), "one")

    def test_the_two_and_three_owner_buckets_are_positive_in_the_earlier_rung(self):
        """The refutation's mechanism, read from `voxfriction`'s own committed surface."""
        s = VF.by_owner()
        self.assertGreater(s[2][2], 0)
        self.assertGreater(s[3][2], 0)


class TheBreakEven(unittest.TestCase):
    def test_the_inequality_has_no_solution_on_this_loop(self):
        self.assertTrue(VB.the_inequality_has_no_solution_on_this_loop())

    def test_the_gate_pays_but_only_against_the_loop_it_lives_in(self):
        self.assertTrue(VB.the_gate_pays_but_only_against_the_loop_it_lives_in())

    def test_the_deficit_is_the_scaffolding_and_not_the_certificate(self):
        self.assertTrue(VB.the_deficit_is_the_scaffolding_and_not_the_certificate())

    def test_friction_is_smaller_than_the_certificate_it_gates(self):
        """The first draft of this law claimed four orders and reddened at three hundred and sixty."""
        self.assertTrue(VB.friction_is_smaller_than_the_certificate_it_gates())

    def test_the_scaffolding_tax_is_the_cold_loop_over_the_reference(self):
        self.assertEqual(VB.scaffolding_tax(), VB.spend("none") - VM.reference_cost())


class TheDiscipline(unittest.TestCase):
    def test_the_refuted_hypothesis_carries_no_preregistration_credit(self):
        """PRE-REGISTRATION IS COMMIT ORDER OR IT IS NOTHING."""
        self.assertTrue(VB.the_refuted_hypothesis_carries_no_preregistration_credit())

    def test_the_prediction_ships_before_the_sweep(self):
        self.assertTrue(VB.the_prediction_ships_before_the_sweep())

    def test_the_prediction_names_no_result(self):
        self.assertTrue(VB.the_prediction_names_no_result())

    def test_the_prediction_declares_five(self):
        t = VB.prediction_text()
        self.assertEqual(sum(1 for ln in t.split("\n") if ln.startswith("predict ")), 5)

    def test_the_prediction_digest_is_pinned(self):
        self.assertEqual(VB.prediction_digest(), VB.golden("prediction"))

    def test_nothing_is_promoted(self):
        self.assertTrue(VB.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VB.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)

    def test_the_certificate_is_voxconds_and_no_new_one_is_invented(self):
        """Inventing a certificate here would have made this ledger measure two things at once."""
        self.assertTrue(VD.sound("P4"))
        for p in ("P2", "P3", "P5"):
            self.assertFalse(VD.sound(p))


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VB.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VB.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VB.a_tampered_row_refuses())

    def test_a_rule_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\nrule all 1 2 3\n")

    def test_a_total_row_naming_no_rule_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\ntotal seven 1 2 3\n")

    def test_a_tax_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\ntax 5\n")

    def test_a_best_row_naming_no_rule_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\nbest nine\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VB.generate(), VB._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VB.SCENES:
            self.assertEqual(VB.scene_result(name), VB.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.scene_case("ledger2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VB.VoxbreakError):
            VB.golden("nope")


if __name__ == "__main__":
    unittest.main()
