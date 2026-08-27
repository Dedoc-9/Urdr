# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfill (URDRVXL1) — the fill rule one variable at a time, and the arm that won was not on the list."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxfill as VL                                         # noqa: E402
import voxfate as VS                                         # noqa: E402
import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheControlArm(unittest.TestCase):
    def test_the_fourth_transcription_is_bound(self):
        self.assertTrue(VL.the_control_arm_matches_the_ladder())

    def test_each_arm_moves_exactly_one_variable(self):
        seen = {a: VL.arm_flags(a) for a in VL.ARMS}
        self.assertEqual(len(set(seen.values())), len(VL.ARMS))
        self.assertEqual(seen["committed"], (False, 0, 0))
        for a in ("inclusive", "wide_bbox", "centre"):
            self.assertEqual(sum(1 for x, y in zip(seen[a], seen["committed"]) if x != y), 1)

    def test_an_unknown_arm_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.arm_flags("supersample")

    def test_an_unknown_convention_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.ray_at(VR.TRACE[0][1], VR.TRACE[0][2], 0, 0, "gaussian")


class ThePopulation(unittest.TestCase):
    def test_the_decomposition_is_not_recombined(self):
        """318 not_covered, 58 depth_rejected, 2 phantom are three mechanisms, not one number."""
        self.assertTrue(VL.the_decomposition_is_not_recombined())

    def test_the_population_is_the_coverage_fate_only(self):
        self.assertEqual(len(VL.population()),
                         sum(1 for r in VS.fates() if r[3] == VL.FATE))

    def test_the_classification_is_exhaustive(self):
        self.assertTrue(VL.the_classification_is_exhaustive())

    def test_no_pixel_is_secretly_covered(self):
        self.assertTrue(VL.the_rejections_are_not_a_covering_failure())


class TheAlgebra(unittest.TestCase):
    def test_the_outside_rejections_are_sub_pixel(self):
        self.assertTrue(VL.the_outside_rejections_are_sub_pixel())

    def test_the_distance_test_takes_no_root_and_bites_both_ways(self):
        """A horizontal edge of length 64 sub-pixels: e = 64*63 is under a pixel, 64*65 is not."""
        S = VL._level()[2]
        self.assertTrue(VL._within_one_pixel(S * (S - 1), 0, 0, S, 0, S))
        self.assertFalse(VL._within_one_pixel(S * (S + 1), 0, 0, S, 0, S))

    def test_the_bbox_arm_is_inert_and_the_check_is_not_vacuous(self):
        """Padding must ADMIT the excluded pixels, or 'it changed nothing' proves nothing."""
        admitted, covered = VL.bbox_admitted_by_padding()
        self.assertEqual(admitted, VL.rejection_distribution()["bbox"])
        self.assertGreater(admitted, 0)
        self.assertEqual(covered, 0)
        self.assertTrue(VL.the_bbox_excludes_only_what_the_edges_reject())


class TheArms(unittest.TestCase):
    def test_the_ownership_arm_pays_for_what_it_buys(self):
        self.assertTrue(VL.the_ownership_arm_pays_for_what_it_buys())

    def test_the_cost_lands_on_the_parked_tie_rule(self):
        self.assertTrue(VL.the_cost_lands_on_the_parked_tie_rule())

    def test_every_arm_is_order_independent(self):
        """Corrects a belief carried since voxref: the (depth, face_key) tiebreak deletes draw
        order, not the top-left partition — so dropping the bias costs uniqueness, not determinism."""
        self.assertTrue(VL.every_arm_is_order_independent())

    def test_gained_and_lost_are_reported_separately(self):
        a = VL.arm_reading("inclusive", "corner")
        c = VL.arm_reading("committed", "corner")
        self.assertEqual(a[0] - c[0], a[4] - a[5])
        self.assertGreater(a[4], 0)
        self.assertGreater(a[5], 0)

    def test_the_control_arm_moves_nothing(self):
        self.assertEqual(VL.arm_reading("committed", "corner")[4:7], (0, 0, 0))


class TheConventionControl(unittest.TestCase):
    def test_the_centre_ray_is_the_corner_ray_shifted_half_a_pixel(self):
        self.assertTrue(VL.the_centre_ray_is_the_corner_ray_shifted_half_a_pixel())

    def test_the_conventions_must_agree(self):
        self.assertTrue(VL.the_conventions_must_agree())

    def test_the_sample_point_is_the_defect(self):
        """Oracle-free: impossible faces are a property of the rasteriser alone."""
        self.assertTrue(VL.the_sample_point_is_the_defect())

    def test_the_ownership_rescue_is_an_artefact(self):
        """This rung's own leading hypothesis, refuted by its own control."""
        self.assertTrue(VL.the_ownership_rescue_is_an_artefact())

    def test_nothing_is_adopted(self):
        self.assertTrue(VL.no_convention_is_adopted())


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VL.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VL.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VL.a_tampered_row_refuses())

    def test_an_arm_row_naming_no_arm_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.parse("# world x\narm supersample corner 1 2 3 4 5 6 7\n")

    def test_a_pair_row_naming_no_convention_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.parse("# world x\npair corner gaussian 1 2\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VL.SCENES:
            self.assertEqual(VL.scene_result(name), VL.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.scene_case("arms2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VL.VoxfillError):
            VL.golden("nope")


if __name__ == "__main__":
    unittest.main()
