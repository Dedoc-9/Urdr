# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxwin (URDRVXW1) — chase the winner, and the decomposition closes."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxwin as VW                                          # noqa: E402
import voxslack as VK                                        # noqa: E402
import voxref as VR                                          # noqa: E402


class TheRayTest(unittest.TestCase):
    def test_it_is_planted_in_every_direction(self):
        self.assertTrue(VW.the_ray_test_is_exact_and_bites())

    def test_a_ray_down_the_middle_hits(self):
        cell = (5, 5, 5)
        eye = (5 * VR.Q + VR.Q // 2, 5 * VR.Q + VR.Q // 2, 20 * VR.Q)
        self.assertTrue(VW.ray_meets_face(eye, (0, 0, -1), cell, 4))

    def test_a_parallel_ray_answers_none_rather_than_guessing(self):
        cell = (5, 5, 5)
        eye = (5 * VR.Q + VR.Q // 2, 5 * VR.Q + VR.Q // 2, 20 * VR.Q)
        self.assertIsNone(VW.ray_meets_face(eye, (1, 0, 0), cell, 4))

    def test_a_face_behind_the_eye_is_a_miss(self):
        cell = (5, 5, 5)
        eye = (5 * VR.Q + VR.Q // 2, 5 * VR.Q + VR.Q // 2, 20 * VR.Q)
        self.assertFalse(VW.ray_meets_face(eye, (0, 0, 1), cell, 4))


class ThePopulation(unittest.TestCase):
    def test_it_is_voxslacks_depth_class(self):
        self.assertTrue(VW.the_population_is_voxslacks_depth_class())

    def test_every_pixel_gets_exactly_one_outcome(self):
        self.assertEqual(sum(VW.distribution().values()), len(VW.census()))


class TheFinding(unittest.TestCase):
    def test_the_winner_is_a_face_the_ray_misses(self):
        self.assertTrue(VW.the_winner_is_a_face_the_ray_misses())

    def test_the_winner_is_the_oracle_one_pixel_over(self):
        self.assertTrue(VW.the_winner_is_the_oracle_one_pixel_over())

    def test_the_exceptions_are_exactly_the_exact_ties(self):
        """Set equality between two independently computed classifications, not a count."""
        self.assertTrue(VW.the_exceptions_are_exactly_the_exact_ties())

    def test_the_tie_set_is_not_merely_the_same_size(self):
        mine = {(r[0], r[1], r[2]) for r in VW.census() if r[3] == "true_tie"}
        theirs = {(r[0], r[1], r[2]) for r in VK.census() if r[10] == "exact_tie"}
        self.assertEqual(mine, theirs)
        self.assertGreater(len(mine), 0)

    def test_the_ties_are_on_adjacent_cells(self):
        self.assertTrue(VW.the_ties_are_the_parked_question())


class TheDecomposition(unittest.TestCase):
    def test_it_closes(self):
        self.assertTrue(VW.the_decomposition_closes())

    def test_it_is_exhaustive_and_disjoint(self):
        dec = VW.decomposition()
        self.assertEqual(sum(dec.values()), len(VK.census()))
        self.assertEqual(set(dec), set(VW.CLASSES))

    def test_nothing_is_altered(self):
        self.assertTrue(VW.nothing_is_altered())


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VW.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VW.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VW.a_tampered_row_refuses())

    def test_an_outcome_row_naming_no_outcome_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.parse("# world x\noutcome elsewhere 5\n")

    def test_a_class_row_naming_no_class_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.parse("# world x\nclass nowhere 5\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VW.SCENES:
            self.assertEqual(VW.scene_result(name), VW.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.scene_case("winners2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VW.VoxwinError):
            VW.golden("nope")


if __name__ == "__main__":
    unittest.main()
