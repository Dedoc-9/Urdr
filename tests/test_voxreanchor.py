# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxreanchor (URDRRAN1) — amortization works and the predecessor is not what pays."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import attributed as AT                                      # noqa: E402
import voxreanchor as RA                                     # noqa: E402
import voxref as VR                                          # noqa: E402
import voxrun as RN                                          # noqa: E402


class TheSafetyContract(unittest.TestCase):
    def test_every_arm_reproduces_the_observable_exactly(self):
        """The precondition of every number in this rung — and NOT a scored prediction, which is
        what R5 forgot."""
        self.assertTrue(RA.the_arms_reproduce_the_observable_exactly())

    def test_each_arm_reconstructs_the_reference_map_as_a_list(self):
        p, n = RA._pairs()[0]
        pk, ck = RN.owner_map(RA.CORPUS, p), RN.owner_map(RA.CORPUS, n)
        pruns = RN.runs(pk)
        for name, out in (("baseline", RA.run_baseline(ck)[1]),
                          ("whole_run", RA.run_whole_run(ck, pruns)[1]),
                          ("reanchor", RA.run_reanchor(ck, pruns)[1]),
                          ("coherent", RA.run_coherent(ck)[1])):
            with self.subTest(arm=name):
                self.assertEqual(out, list(ck))

    def test_no_arm_is_promoted(self):
        self.assertTrue(RA.nothing_is_promoted())

    def test_the_reference_is_only_read_for_its_dimensions_and_world(self):
        self.assertEqual(set(RA.REFERENCE_USES), {"H", "W", "world_digest"})

    def test_no_wall_clock_enters(self):
        self.assertTrue(RA.no_wall_clock_enters_this_rung())


class TheControl(unittest.TestCase):
    def test_the_control_cannot_receive_a_predecessor(self):
        """Proved on the AST. A control that could see the previous frame is worth nothing."""
        self.assertTrue(RA.the_control_takes_no_predecessor())

    def test_the_control_is_declared_and_is_one_of_the_arms(self):
        self.assertIn(RA.CONTROL, RA.ARMS)
        self.assertEqual(RA.CONTROL, "coherent")

    def test_the_control_obtains_almost_all_of_the_result(self):
        self.assertGreater(RA.spend(RA.CONTROL, RA.WORK), 0)
        self.assertGreater(100 * RA.spend(RA.CONTROL, RA.WORK),
                           98 * RA.spend("reanchor", RA.WORK))

    def test_the_control_runs_on_both_corpora(self):
        for c in RN.CORPORA:
            with self.subTest(corpus=c):
                tot, obs = RA.control_on(c)
                self.assertGreater(obs, 0)
                self.assertGreater(tot[RA.WORK], 0)
                self.assertLess(tot[RA.WORK], obs)

    def test_the_lattice_flatters_the_control_too(self):
        """`does_not_show` made checkable: the control retires a larger share on the lattice than on
        the corpus built to be hard."""
        lat, lo = RA.control_on("lattice")
        adv, ao = RA.control_on("adversarial")
        self.assertGreater(lat[RA.WORK] * ao, adv[RA.WORK] * lo)

    def test_an_unknown_corpus_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.control_on("wishful")


class TheFinding(unittest.TestCase):
    def test_the_predecessor_does_not_pay(self):
        self.assertTrue(RA.the_predecessor_does_not_pay())

    def test_the_control_has_the_loosest_break_even_bar(self):
        bars = {a: RA.breakeven_permille(a) for a in RA.ARMS if a != "baseline"}
        self.assertEqual(max(bars, key=bars.get), RA.CONTROL)

    def test_the_predecessor_buys_something_and_it_is_small(self):
        self.assertTrue(RA.the_predecessor_buys_something_and_it_is_small())

    def test_the_predecessor_costs_more_anchors_than_it_saves_discoveries(self):
        saved = RA.spend(RA.CONTROL, "discover") - RA.spend("reanchor", "discover")
        extra = RA.spend("reanchor", "construct") - RA.spend(RA.CONTROL, "construct")
        self.assertGreater(saved, 0)
        self.assertGreater(extra, saved)

    def test_re_anchoring_beats_whole_run_on_retirement(self):
        self.assertGreater(RA.spend("reanchor", RA.WORK), RA.spend("whole_run", RA.WORK))

    def test_the_named_mechanism_is_a_minority_of_the_retirement(self):
        """R2's stated reason accounts for less than three quarters of what R2 predicted."""
        self.assertLess(4 * RA.retired_under_the_original_owner(),
                        3 * RA.spend("reanchor", RA.WORK))
        self.assertGreater(RA.retired_under_the_original_owner(), 0)

    def test_whole_run_retires_exactly_the_surviving_share(self):
        self.assertTrue(RA.whole_run_retires_exactly_the_surviving_share())
        self.assertEqual(RA.spend("whole_run", RA.WORK), 43178)

    def test_no_arm_satisfies_the_admissibility_inequality(self):
        self.assertTrue(RA.no_arm_satisfies_the_admissibility_inequality())


class TheAccounts(unittest.TestCase):
    def test_the_baseline_pays_for_every_observation_and_retires_nothing(self):
        self.assertEqual(RA.spend("baseline", "discover"), VR.W * VR.H * len(RA._pairs()))
        self.assertEqual(RA.spend("baseline", RA.WORK), 0)

    def test_the_work_account_is_not_a_cost_account(self):
        self.assertNotIn(RA.WORK, RA.ACCOUNTS)

    def test_every_arm_accounts_for_every_observation(self):
        """Each observation is either retired or discovered, in every arm."""
        obs = RA.observations()
        for a in RA.ARMS:
            with self.subTest(arm=a):
                self.assertEqual(RA.spend(a, "discover") + RA.spend(a, RA.WORK), obs)

    def test_a_reanchor_costs_a_discovery(self):
        """The anchor is always paid for, which is what keeps this a certificate rather than a
        precomputed answer table."""
        self.assertEqual(RA.spend("reanchor", "reanchor"), RA.spend("reanchor", "discover"))

    def test_whole_run_never_reanchors(self):
        self.assertEqual(RA.spend("whole_run", "reanchor"), 0)

    def test_the_arms_are_seeded_by_the_predecessor(self):
        self.assertTrue(RA.the_arms_are_seeded_by_the_predecessor_and_never_by_the_current_map())

    def test_the_accounts_are_summed_only_by_the_declared_convention(self):
        self.assertTrue(RA.no_economics_are_claimed_beyond_the_declared_convention())

    def test_an_unknown_arm_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.spend("wishful")

    def test_an_unknown_account_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.spend("reanchor", "wishful")

    def test_the_baseline_has_no_break_even(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.breakeven_permille("baseline")

    def test_an_unknown_yield_threshold_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.anchor_yield(3)

    def test_the_anchor_yield_is_monotone_decreasing(self):
        vals = [RA.anchor_yield(t) for t in RA.YIELDS]
        self.assertEqual(vals, sorted(vals, reverse=True))
        self.assertLessEqual(vals[0], RA.predecessor_runs())


class TheDisposition(unittest.TestCase):
    def test_every_registered_prediction_has_exactly_one_disposition(self):
        self.assertTrue(RA.every_registered_prediction_has_exactly_one_disposition())

    def test_the_registered_identifiers_come_from_the_record(self):
        self.assertTrue(RA.the_registered_identifiers_are_the_records_own())

    def test_the_original_record_is_unmodified(self):
        self.assertTrue(RA.the_original_record_is_unmodified())

    def test_the_original_record_is_not_rewritten_by_this_rung(self):
        """It must still contain the predictions this rung declares void and withdrawn."""
        txt = RN.prediction_text()
        self.assertIn("predict R3", txt)
        self.assertIn("predict R5", txt)
        self.assertIn("THE SAFETY CONTRACT IS NOT A PREDICTION AND IS NOT SCORED", txt)

    def test_r5_contradicts_the_header_that_governs_it(self):
        """The withdrawal is a fact about the record, not an opinion about it: the header excludes
        the observable contract from scoring and R5 registers exactly that as a prediction."""
        txt = RN.prediction_text()
        self.assertIn("IS NOT A PREDICTION AND IS NOT SCORED", txt)
        r5 = [ln for ln in txt.split("\n") if ln.startswith("predict R5")][0]
        self.assertIn("moves the observable", r5)
        self.assertEqual(RA.VERDICT["R5"][0], "withdrawn")

    def test_r3_names_a_corpus_with_no_adjacency(self):
        r3 = [ln for ln in RN.prediction_text().split("\n") if ln.startswith("predict R3")][0]
        self.assertIn("adversarial", r3)
        self.assertEqual(RA.VERDICT["R3"][0], "void")

    def test_the_mechanism_is_scored_apart_from_the_outcome(self):
        self.assertTrue(RA.the_mechanism_is_scored_apart_from_the_outcome())

    def test_two_hits_came_from_a_mechanism_they_did_not_name(self):
        self.assertEqual(RA.VERDICT["R2"][:2], ("hit", "not_as_stated"))
        self.assertEqual(RA.VERDICT["R4"][:2], ("hit", "not_as_stated"))

    def test_every_disposition_carries_a_reason(self):
        for r in RA.REGISTERED:
            with self.subTest(prediction=r):
                self.assertGreater(len(RA.VERDICT[r][2]), 40)

    def test_no_disposition_names_an_unregistered_prediction(self):
        self.assertEqual(set(RA.VERDICT), set(RA.REGISTERED))

    def test_void_and_withdrawn_are_neither_hits_nor_misses(self):
        for r in ("R3", "R5"):
            with self.subTest(prediction=r):
                self.assertNotIn(RA.VERDICT[r][0], ("hit", "miss"))
                self.assertEqual(RA.VERDICT[r][1], "not_scored")


class ThePercentages(unittest.TestCase):
    def test_the_prose_percentages_are_the_measured_ones(self):
        self.assertTrue(RA.the_percentages_in_the_prose_are_the_measured_ones())

    def test_this_module_is_audited_by_the_shared_law_without_being_listed(self):
        """The coverage clause is derived, so declaring `PERCENTS` is enough to be audited."""
        self.assertIn("voxreanchor", AT.SUBJECTS)
        self.assertIn("voxreanchor", AT.declaring_modules())

    def test_every_rendering_is_the_exact_truncation(self):
        for n in RA.PERCENTS:
            with self.subTest(percent=n):
                self.assertTrue(AT.truncates(RA.percent_text(n), *RA.percent_exact(n)))

    def test_the_declared_percentages_are_pairwise_distinct(self):
        vals = [RA.percent_text(n) for n in RA.PERCENTS]
        self.assertEqual(len(set(vals)), len(vals))

    def test_an_undeclared_percentage_refuses(self):
        for call in (RA.percent_text, RA.percent_exact):
            with self.assertRaises(RA.VoxreanchorError):
                call("wishful")


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world_and_the_original(self):
        self.assertTrue(RA.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(RA.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(RA.a_tampered_row_refuses())

    def test_the_generated_record_is_the_committed_one(self):
        with open(os.path.join(_ROOT, RA.RECORD), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), RA.generate())

    def test_rows_of_unknown_kinds_refuse(self):
        head = "# world x\n# original y\n"
        for bad in ("dispose R9 hit as_stated why", "dispose R1 wishful as_stated why",
                    "dispose R1 hit wishful why", "arm wishful discover=1",
                    "breakeven baseline 1", "breakeven wishful 1", "yield 3 1", "rumour 1"):
            with self.subTest(row=bad):
                with self.assertRaises(RA.VoxreanchorError):
                    RA.parse(head + bad + "\n")

    def test_a_record_naming_no_world_or_no_original_refuses(self):
        for bad in ("dispose R1 miss as_stated why\n", "# world x\ndispose R1 miss as_stated why\n"):
            with self.subTest(text=bad):
                with self.assertRaises(RA.VoxreanchorError):
                    RA.parse(bad)

    def test_a_record_with_no_rows_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.parse("# world x\n# original y\n")

    def test_the_scenes_match_their_goldens(self):
        for n in RA.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(RA.scene_result(n), RA.golden(n))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(RA.VoxreanchorError):
            RA.golden("wishful")


class TheDependency(unittest.TestCase):
    def test_the_corpus_and_traversal_are_inherited(self):
        self.assertEqual(RA.CORPUS, "lattice")
        self.assertEqual(RA._pairs(),
                         tuple((RN.Z3_PRED[n], n) for n in RN.Z3_ORDER if RN.Z3_PRED[n] is not None))
        self.assertEqual(len(RA._pairs()), 15)

    def test_the_run_decomposition_is_the_census_s_own(self):
        p = RA._pairs()[0][0]
        self.assertEqual(RN.runs(RN.owner_map(RA.CORPUS, p)),
                         RN.runs(RN.owner_map(RA.CORPUS, p)))
        self.assertEqual(RA.predecessor_runs(), sum(RN.survival()[f][0] for f in RN.FATES))


if __name__ == "__main__":
    unittest.main(verbosity=2)
