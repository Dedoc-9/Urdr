# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcand (URDRVXD1) — the repair candidate, and the fact that stays red."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxcand as VC                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class TheCandidateIsNotTheReference(unittest.TestCase):
    def test_the_committed_arm_reproduces_the_reference(self):
        """The transcription is bound, or every number is about a fourth renderer nobody runs."""
        self.assertTrue(VC.the_committed_arm_reproduces_the_reference())

    def test_the_candidate_differs_from_the_committed_observable(self):
        self.assertTrue(VC.the_candidate_is_not_the_committed_reference())

    def test_the_digest_namespaces_cannot_collide(self):
        """A candidate figure must not be pasteable where a frozen O_t is expected."""
        self.assertTrue(VC.the_candidate_digest_is_not_an_observable())

    def test_the_committed_reference_is_untouched(self):
        self.assertTrue(VC.the_committed_reference_is_untouched())

    def test_voxref_still_declares_the_committed_winding(self):
        import voxray as VX
        self.assertEqual(VR.primitives()[0], VX.primitives_with("as-committed")[0])

    def test_an_unknown_weight_treatment_refuses(self):
        with self.assertRaises(VC.VoxcandError):
            VC.render_arm([], (0, 0, 0), (0, 1, 0), "sideways")


class TheFactorial(unittest.TestCase):
    def test_the_fixes_are_not_independent(self):
        """The weight fix applied alone to the wrong winding is HARMFUL — that is the finding."""
        self.assertTrue(VC.the_fixes_are_not_independent())

    def test_the_weight_fix_alone_moves_no_agreeing_pixel(self):
        t = VC.totals()
        self.assertEqual(t[("as-committed", "unbiased")]["agree"], t[VC.COMMITTED]["agree"])

    def test_the_candidate_is_the_best_corner(self):
        t = VC.totals()
        self.assertEqual(min(t, key=lambda k: t[k]["impossible"]), VC.CANDIDATE)
        self.assertEqual(max(t, key=lambda k: t[k]["agree"]), VC.CANDIDATE)

    def test_the_perspective_hypothesis_stays_refused(self):
        self.assertTrue(VC.the_perspective_hypothesis_stays_refused())


class TheFourFacts(unittest.TestCase):
    def test_orientation_is_demonstrated_not_argued(self):
        for name, impossible in VC._orientation_readings():
            self.assertEqual(impossible, 0, name)

    def test_six_single_voxel_scenes_are_present(self):
        """Orientation correctness on fewer than six directions would not be orientation."""
        self.assertEqual(len(VC._orientation_readings()), 6)

    def test_the_third_fact_is_still_red(self):
        self.assertTrue(VC.the_third_fact_is_still_red())

    def test_exactly_one_fact_is_red(self):
        v = VC.fact_verdicts()
        self.assertEqual([f for f in VC.FACTS if not v[f]], ["visibility"])

    def test_the_census_may_not_be_regenerated_yet(self):
        self.assertTrue(VC.the_census_may_not_be_regenerated_yet())

    def test_the_residual_is_localized_not_vague(self):
        imp, _agree, _tot, bad = VC.micro_impossible()
        self.assertGreater(imp, 0)
        self.assertEqual(sum(n for _s, n in bad), imp)
        self.assertLessEqual(len(bad), 3)


class ThePreservationChain(unittest.TestCase):
    def test_determinism(self):
        self.assertTrue(VC.the_candidate_is_deterministic())

    def test_the_coverage_partition_with_its_control(self):
        self.assertTrue(VC.the_candidate_keeps_the_coverage_partition())

    def test_order_permutation_irrelevance(self):
        self.assertTrue(VC.the_candidate_keeps_order_irrelevance())

    def test_both_digest_witnesses(self):
        self.assertTrue(VC.the_candidate_keeps_both_witnesses())


class TheRecord(unittest.TestCase):
    def test_the_record_is_exactly_the_derived_grid(self):
        self.assertTrue(VC.the_record_is_exactly_the_derived_grid())

    def test_the_record_names_this_world(self):
        self.assertTrue(VC.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VC.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VC.a_tampered_row_refuses())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VC.SCENES:
            self.assertEqual(VC.scene_result(name), VC.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VC.VoxcandError):
            VC.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
