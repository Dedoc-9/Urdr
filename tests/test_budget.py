# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/budget.py — THE DEFECT BUDGET (URDRBGT1).

  SOUNDNESS RUNS THE RIGHT WAY — per-part charging never UNDER-charges (0 of 55), so a budget that
    survives per-part accounting survived the true total. The conservatism is priced, not hidden.
  EXACT ON PREFIX-DISJOINT SHARDS — 49 pairs, 0 exceptions, no slack. That is what makes tiling sound.
  REFUNDS VOID THE BOUND — 4 clean submissions buy a block the honest ledger refuses, and the
    reachable budget grows without limit: 100 clean -> 100, 1000 -> 1000, against a cap of 6.
  MODALITY CREDITS ARE A TYPED WORD — the same capture is admitted as "lidar" and refused as "rgb".
  PRIVILEGE IS A FIREWALL, NOT A FLAG — the authoritative verdict is a single value across every
    privilege setting, because the authority path cannot see it.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import budget as BG                                                # noqa: E402


class TheAccountingIsSound(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in BG.SCENES:
            self.assertEqual(BG.scene_result(n), BG.golden(n), n)
            self.assertEqual(BG.scene_result(n), BG.scene_result(n), n)
        self.assertTrue(BG.emitted_matches_pinned())

    def test_per_part_charging_never_undercharges(self):
        pairs, under, over, worst = BG.soundness_census()
        self.assertEqual(under, 0, "an under-charge would make the budget unsound")
        self.assertEqual((pairs, over, worst), (55, 2, 1))
        self.assertTrue(BG.accounting_is_sound())

    def test_the_conservatism_is_priced_not_hidden(self):
        """A scheme that silently drifts pessimistic eventually refuses honest work."""
        over_pairs, worst, pairs = BG.conservatism_is_priced()
        self.assertEqual((over_pairs, worst, pairs), (2, 1, 55))
        self.assertGreater(over_pairs, 0, "overlap must actually occur or the price is untested")

    def test_charging_is_exact_on_prefix_disjoint_shards(self):
        disjoint, exceptions, total = BG.exactness_on_disjoint_census()
        self.assertEqual(exceptions, 0, "disjoint supports contribute disjoint cells — no slack")
        self.assertEqual((disjoint, total), (49, 55))
        self.assertLess(disjoint, total, "and overlapping pairs exist, so the filter does work")
        self.assertTrue(BG.disjoint_charging_is_exact())

    def test_the_cost_cannot_be_supplied(self):
        """THE STRUCTURAL DEFENCE: charge_for takes a lattice, and there is no parameter through
        which a submitted number could enter the accounting."""
        import inspect
        sig = inspect.signature(BG.charge_for)
        self.assertEqual(list(sig.parameters), ["occupancy"])


class TheDescentIsWellFounded(unittest.TestCase):
    def test_exactly_budget_unit_charges_succeed(self):
        succeeded, refused, b = BG.unit_descent()
        self.assertTrue(refused, "the budget must terminate in a refusal")
        self.assertEqual(succeeded, b)
        self.assertEqual((succeeded, b), (6, 6))
        self.assertTrue(BG.descent_is_well_founded())

    def test_the_remainder_never_goes_negative(self):
        min_seen, all_nonneg = BG.remainder_never_goes_negative()
        self.assertTrue(all_nonneg)
        self.assertEqual(min_seen, 0, "a fully spent budget is 0; the NEXT charge is what refuses")

    def test_a_negative_charge_is_refused_as_a_refund(self):
        with self.assertRaises(BG.BudgetError):
            BG.charge(5, -1)

    def test_non_int_ledger_values_refuse(self):
        for bad in (("5", 1), (5, "1"), (None, 1), (5.0, 1)):
            with self.assertRaises(BG.BudgetError):
                BG.charge(*bad)

    def test_an_overdraw_raises_rather_than_clamping(self):
        with self.assertRaises(BG.Overdrawn):
            BG.charge(1, 2)
        self.assertEqual(BG.charge(2, 2), 0, "spending exactly to zero is legal")

    def test_jurisdictional_variation_is_server_side(self):
        """Location is read off the lattice, so a tighter region admits strictly fewer."""
        strict, loose = BG.jurisdictional_variation()
        self.assertLess(strict, loose)
        self.assertEqual((strict, loose), (1, 3))


class TheThreeCorrections(unittest.TestCase):
    def test_refunds_pump_the_budget(self):
        """CORRECTION 1 — a refund is not a tuning choice, it removes the bound."""
        clean_needed, bought, honest_refuses = BG.refund_pump()
        self.assertTrue(bought, "clean submissions buy spending power")
        self.assertTrue(honest_refuses, "which the monotone ledger refuses outright")
        self.assertEqual(clean_needed, 4)

    def test_refunds_void_the_bound_entirely(self):
        at100, at1000, cap = BG.refunds_void_the_bound()
        self.assertEqual((at100, at1000, cap), (100, 1000, 6))
        self.assertGreater(at1000, at100, "the reachable budget is unbounded in submissions")
        self.assertGreater(at100, cap, "and already exceeds the honest cap at 100")

    def test_modality_credit_moves_the_verdict_on_a_typed_word(self):
        """CORRECTION 2 — refused by the proposal's own safeguard."""
        lidar_admits, rgb_refuses, lattice_refuses = \
            BG.modality_credit_admits_what_the_lattice_refuses()
        self.assertTrue(lidar_admits, "the same capture passes when declared favourably")
        self.assertTrue(rgb_refuses, "and fails when declared otherwise")
        self.assertTrue(lattice_refuses, "while the lattice-only ledger refuses it either way")

    def test_authority_cannot_see_privilege(self):
        """CORRECTION 3 — a tier the authority path can read is a tier it can be talked into."""
        import inspect
        params = list(inspect.signature(BG.authoritative_admit).parameters)
        self.assertEqual(params, ["occupancy", "remaining"], "no privilege parameter exists")
        verdicts = BG.authority_is_invariant_under_privilege()
        self.assertEqual(len(verdicts), 1, "a single verdict across every privilege setting")
        self.assertEqual(verdicts, (False,))

    def test_the_lanes_are_separable_and_the_cosmetic_one_is_real(self):
        """Validity-not-outcome: if the cosmetic lane admitted nothing extra it would be decoration."""
        authority_refuses, cosmetic_admits = BG.the_lanes_are_separable()
        self.assertTrue(authority_refuses)
        self.assertTrue(cosmetic_admits, "the second-class lane must actually admit something more")

    def test_an_unknown_privilege_refuses(self):
        with self.assertRaises(BG.BudgetError):
            BG.cosmetic_admit(frozenset({(0, 0, 0)}), 5, "superuser")


class TheRefusalIsTyped(unittest.TestCase):
    def test_the_two_classes_are_distinct(self):
        self.assertNotEqual(BG.Overdrawn("x").code, BG.BudgetError("x").code)

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(BG.BudgetError):
            BG.golden("no_such_scene")


if __name__ == "__main__":
    unittest.main()
