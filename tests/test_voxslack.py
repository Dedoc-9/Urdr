# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxslack (URDRVXK1) — how far is each wrong pixel from the law that decided it?"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxslack as VK                                        # noqa: E402
import voxfate as VS                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class TheInstrument(unittest.TestCase):
    def test_the_sixth_transcription_is_bound(self):
        """Winner, stages AND covered sets, all three."""
        self.assertTrue(VK.the_instrument_matches_the_ladder())

    def test_the_population_reproduces_voxfate(self):
        self.assertTrue(VK.the_population_reproduces_voxfate())

    def test_an_unknown_predicate_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.reached("stencil")

    def test_an_unbucketed_field_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.distribution("area")


class TheSignConvention(unittest.TestCase):
    def test_the_depth_bucket_bites_in_every_direction(self):
        self.assertEqual(VK._depth_bucket(-1), "should_have_won")
        self.assertEqual(VK._depth_bucket(0), "exact_tie")
        self.assertEqual(VK._depth_bucket(VR.Q - 1), "under_one_cell")
        self.assertEqual(VK._depth_bucket(VR.Q), "a_whole_cell_or_more")

    def test_a_pixel_that_reached_no_surface_records_none(self):
        """A zero would be a decision the reference never made."""
        for r in VK.census():
            if r[3] == "phantom":
                self.assertIsNone(r[4])

    def test_only_covered_pixels_have_a_depth_slack(self):
        self.assertEqual(VK.reached("depth"),
                         sum(1 for r in VK.census() if r[3] == "depth_rejected"))


class TheCoverage(unittest.TestCase):
    def test_the_residue_is_entirely_within_one_pixel(self):
        """The first version of this law demanded a `beyond` class and reddened."""
        self.assertTrue(VK.the_coverage_residue_is_entirely_within_one_pixel())

    def test_beyond_is_reachable(self):
        """Otherwise the zero above is a limitation of the bucketer, not a measurement."""
        S = VK._level()[2]
        self.assertEqual(
            VK._cover_bucket(-2, ((0, 0, 0), (S, 0, 0), (S, S, 0), (0, 0, 0), (0, 0, 0, 0)),
                             3, 3, S), "beyond")

    def test_the_residue_splits_at_the_bias(self):
        self.assertTrue(VK.the_residue_splits_at_the_bias())

    def test_the_on_surface_class_is_exactly_the_bias(self):
        self.assertTrue(VK.the_on_surface_class_is_exactly_the_bias())

    def test_the_buckets_partition_the_coverage_population(self):
        d = VK.distribution("coverage")
        self.assertEqual(sum(d.values()),
                         sum(1 for r in VK.census() if r[3] == "not_covered"))


class TheDepth(unittest.TestCase):
    def test_the_depth_rejections_are_not_a_margin(self):
        """The finding that redirects a branch: they lose by a whole cell, not by a rounding."""
        self.assertTrue(VK.the_depth_rejections_are_not_a_margin())

    def test_no_stable_pixel_should_have_won_on_depth(self):
        self.assertTrue(VK.no_stable_pixel_should_have_won_on_depth())

    def test_the_depth_rejections_are_deep_inside_coverage(self):
        self.assertTrue(VK.the_depth_rejections_are_deep_inside_coverage())

    def test_the_depth_population_is_the_depth_rejected_fate(self):
        d = VK.distribution("depth")
        self.assertEqual(sum(d.values()),
                         sum(1 for r in VK.census() if r[3] == "depth_rejected"))


class TheRefusals(unittest.TestCase):
    def test_the_phantoms_are_too_few_to_read(self):
        self.assertTrue(VK.the_phantoms_are_too_few_to_read())

    def test_nothing_is_altered(self):
        self.assertTrue(VK.nothing_is_altered())


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VK.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VK.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VK.a_tampered_row_refuses())

    def test_a_reached_row_naming_no_predicate_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.parse("# world x\nreached stencil 5\n")

    def test_a_cover_row_in_no_declared_bucket_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.parse("# world x\ncover elsewhere 5\n")

    def test_a_depth_row_in_no_declared_bucket_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.parse("# world x\ndepth nowhere 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VK.SCENES:
            self.assertEqual(VK.scene_result(name), VK.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.scene_case("slack2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VK.VoxslackError):
            VK.golden("nope")


if __name__ == "__main__":
    unittest.main()
