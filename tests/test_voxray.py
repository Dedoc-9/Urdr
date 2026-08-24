# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxray (URDRVXR1) — the geometric oracle, and what it says about the reference."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheOracleIsAuditable(unittest.TestCase):
    def test_the_first_hit_is_first(self):
        self.assertTrue(VX.the_first_hit_is_first())

    def test_the_hit_lies_on_its_face(self):
        self.assertTrue(VX.the_hit_lies_on_its_face())

    def test_the_face_agrees_with_the_entry_direction(self):
        self.assertTrue(VX.the_face_agrees_with_the_entry_direction())

    def test_a_miss_really_traverses_nothing(self):
        self.assertTrue(VX.a_miss_really_traverses_nothing())

    def test_a_started_inside_voxel_has_no_entry_face(self):
        self.assertTrue(VX.a_started_inside_voxel_has_no_entry_face())

    def test_a_zero_direction_refuses(self):
        self.assertTrue(VX.a_zero_direction_refuses())

    def test_the_probe_set_has_both_hits_and_misses(self):
        self.assertTrue(VX.the_probe_set_is_not_vacuous())


class TheCameraIsShared(unittest.TestCase):
    def test_rays_invert_the_projection_to_within_one_pixel(self):
        self.assertTrue(VX.the_rays_invert_the_projection_to_within_one_pixel())

    def test_the_round_trip_is_mostly_exact(self):
        self.assertTrue(VX.the_round_trip_is_mostly_exact())

    def test_the_inversion_law_bites(self):
        self.assertTrue(VX.a_shifted_ray_fails_the_inversion())

    def test_the_bound_is_one_pixel_and_is_not_exact(self):
        """The law was first written as an EXACT inversion and that was false. The profile is
        pinned so the claim can never silently become stronger than the arithmetic."""
        prof = dict(VX.round_trip_profile())
        self.assertNotIn("degenerate", prof)
        self.assertGreater(prof.get((0, 0), 0), 0)
        self.assertGreater(len(prof), 1)
        for k in prof:
            self.assertLessEqual(max(abs(k[0]), abs(k[1])), 1)


class TheComparison(unittest.TestCase):
    def test_the_winner_pass_agrees_with_the_render(self):
        self.assertTrue(VX.the_winner_pass_agrees_with_the_render())

    def test_the_record_is_exactly_the_declared_grid(self):
        self.assertTrue(VX.the_record_is_exactly_the_declared_grid())

    def test_the_record_names_this_world(self):
        self.assertTrue(VX.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VX.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VX.a_tampered_row_refuses())

    def test_the_winding_reversal_improves_correspondence(self):
        self.assertTrue(VX.the_winding_reversal_improves_correspondence())

    def test_no_law_asserts_that_the_reference_is_right(self):
        """The whole point of shipping this REPORTED: correspondence is a number, not a verdict."""
        _ok, _tot, pc = VX.correspondence("reversed")
        self.assertLess(pc, 100.0)


class TheExcludedFrame(unittest.TestCase):
    def test_floor_flat_is_excluded_by_derivation(self):
        names = [n for n, _e, _f in VR.TRACE]
        self.assertNotIn(names.index("floor_flat"), VX.comparable_frames())

    def test_every_other_frame_is_comparable(self):
        self.assertEqual(len(VX.comparable_frames()), len(VR.TRACE) - 1)

    def test_the_trace_labels_are_known_wrong(self):
        self.assertTrue(VX.the_trace_labels_are_known_wrong())


class TheCounterexample(unittest.TestCase):
    def test_the_oracle_names_a_third_answer(self):
        hit = VX.counterexample_verdict()
        self.assertIsNotNone(hit)
        self.assertNotEqual((hit[0], hit[1]), VX.COUNTEREXAMPLE[2])
        self.assertNotEqual((hit[0], hit[1]), VX.COUNTEREXAMPLE[3])


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in ("oracle", "counterexample", "correspondence"):
            self.assertEqual(VX.scene_result(name), VX.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VX.VoxrayError):
            VX.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
