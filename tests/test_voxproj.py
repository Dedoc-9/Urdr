# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxproj (URDRVXP1) — the candidate law, predicted before it ran, and refused on evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxproj as VP                                         # noqa: E402
import voxref as VR                                          # noqa: E402


class TheSingleVariable(unittest.TestCase):
    def test_the_quantisation_is_the_only_variable(self):
        self.assertTrue(VP.the_quantisation_is_the_only_variable())

    def test_the_arms_never_differ_by_more_than_one_unit(self):
        S = VP._level()[2]
        for cf in (VR.NEAR, 97, 1001, 8191):
            a = VP.project("control", (137, cf, -71), S)
            b = VP.project("candidate", (137, cf, -71), S)
            self.assertLessEqual(abs(a[0] - b[0]), 1)
            self.assertLessEqual(abs(a[1] - b[1]), 1)

    def test_the_arms_agree_where_the_division_is_exact(self):
        S = VP._level()[2]
        self.assertEqual(VP.project("control", (0, 1, 0), S),
                         VP.project("candidate", (0, 1, 0), S))

    def test_an_unknown_arm_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.project("supersample", (0, 1, 0), 64)

    def test_the_control_arm_matches_the_ladder(self):
        self.assertTrue(VP.the_control_arm_matches_the_ladder())


class ThePrediction(unittest.TestCase):
    def test_every_prediction_has_a_verdict(self):
        """A rung cannot report its hits and lose its misses."""
        self.assertTrue(VP.every_prediction_has_a_verdict())

    def test_the_prediction_is_data_not_a_computation(self):
        for pid, text in VP.PREDICTION:
            self.assertIsInstance(pid, str)
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 40)

    def test_the_verdicts_carry_what_was_measured(self):
        for _pid, (ok, what) in VP.verdicts().items():
            self.assertIsInstance(ok, bool)
            self.assertTrue(any(ch.isdigit() for ch in what))

    def test_it_hit_some_and_missed_some(self):
        self.assertGreater(len(VP.misses()), 0)
        self.assertGreater(len(VP.hits()), 0)
        self.assertTrue(VP.the_prediction_was_mostly_wrong_and_that_is_recorded())


class TheRefusal(unittest.TestCase):
    def test_the_candidate_is_refused_on_evidence(self):
        """Reddens on the day the candidate starts winning."""
        self.assertTrue(VP.the_candidate_is_refused_on_evidence())

    def test_the_candidate_is_actually_worse(self):
        self.assertLess(VP.reading("candidate")[0], VP.reading("control")[0])

    def test_gained_and_lost_are_reported_separately(self):
        c = VP.reading("candidate")
        self.assertEqual(c[0] - VP.reading("control")[0], c[2] - c[3])
        self.assertGreater(c[2], 0)
        self.assertGreater(c[3], 0)

    def test_the_control_arm_moves_nothing(self):
        self.assertEqual(VP.reading("control")[2:5], (0, 0, 0))


class TheFindings(unittest.TestCase):
    def test_the_mechanism_reading_survives(self):
        """P2: not one on-surface miss closed, exactly as predicted."""
        self.assertTrue(VP.the_mechanism_reading_survives())

    def test_the_rounding_direction_is_eliminated(self):
        """Most of the sub-pixel residue survives round-to-nearest, so it is not a direction defect."""
        self.assertTrue(VP.the_rounding_direction_is_eliminated())

    def test_the_declared_populations_are_not_swallowed(self):
        self.assertTrue(VP.the_declared_populations_are_not_swallowed())

    def test_nothing_is_adopted(self):
        self.assertTrue(VP.nothing_is_adopted())

    def test_an_unknown_population_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.population("elsewhere")


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VP.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VP.the_record_is_bound_to_the_live_code())

    def test_the_record_carries_the_prediction_text(self):
        """The committed artifact carries what was CLAIMED as well as what was measured."""
        self.assertTrue(VP.the_record_carries_the_prediction_text())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VP.a_tampered_row_refuses())

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.parse("# world x\nverdict P9 HIT nothing\n")

    def test_an_arm_row_naming_no_arm_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.parse("# world x\narm supersample 1 2 3 4 5\n")

    def test_a_closed_row_naming_no_population_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.parse("# world x\nclosed control elsewhere 1\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VP.SCENES:
            self.assertEqual(VP.scene_result(name), VP.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.scene_case("arms2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VP.VoxprojError):
            VP.golden("nope")


if __name__ == "__main__":
    unittest.main()
