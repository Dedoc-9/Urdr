# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxsample (URDRVXA1) — are the rasteriser and the oracle talking about the same sample point?"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxsample as VA                                       # noqa: E402
import voxslack as VK                                        # noqa: E402
import voxwin as VW                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheExactTest(unittest.TestCase):
    def test_the_place_test_bites_in_every_direction(self):
        self.assertTrue(VA.the_place_test_bites_in_every_direction())

    def test_an_unknown_precision_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.vertex((0, 0, 0), (0, 0, 0), VR.basis(VR.TRACE[0][2]), "double")

    def test_an_unknown_population_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.population("elsewhere")

    def test_the_two_precisions_differ_only_by_the_shift(self):
        eye, fwd = VR.TRACE[5][1], VR.TRACE[5][2]
        m = VR.basis(fwd)
        v = (3 * VR.Q, 4 * VR.Q, 5 * VR.Q)
        a = VA.vertex(v, eye, m, "full")
        b = VA.vertex(v, eye, m, "committed")
        self.assertNotEqual(a, b)
        self.assertGreater(a[2], b[2])


class TheBasis(unittest.TestCase):
    def test_it_is_not_always_orthonormal(self):
        self.assertTrue(VA.the_basis_is_not_always_orthonormal())

    def test_the_orthonormal_frames_really_are(self):
        for f in VA.orthonormal_frames():
            d = VA.basis_dots(f)
            self.assertEqual(d[0], d[3])
            self.assertEqual(d[3], d[5])
            self.assertEqual((d[1], d[2], d[4]), (0, 0, 0))

    def test_the_others_really_are_not(self):
        rest = [f for f in range(len(VR.TRACE)) if f not in VA.orthonormal_frames()]
        self.assertGreater(len(rest), 0)
        for f in rest:
            d = VA.basis_dots(f)
            self.assertTrue(d[0] != d[3] or d[3] != d[5] or (d[1], d[2], d[4]) != (0, 0, 0))

    def test_the_round_trip_departure_is_bounded_and_nonzero(self):
        num, den = VA.round_trip_worst()
        self.assertGreater(num, 0)
        self.assertLess(num * 256, den)
        self.assertTrue(VA.the_round_trip_departure_is_bounded())


class TheGeometry(unittest.TestCase):
    def test_it_is_right_at_full_precision(self):
        self.assertTrue(VA.the_geometry_is_right_at_full_precision())

    def test_the_screen_and_world_tests_agree(self):
        """Set equality between two exact computations in different spaces."""
        self.assertTrue(VA.the_screen_and_world_tests_agree())

    def test_that_agreement_is_a_set_and_not_a_count(self):
        mine = {(r[0], r[1], r[2]) for r in VA.census()
                if r[3] == "winner" and r[4] == "outside"}
        self.assertEqual(mine, VA.population("winner"))
        self.assertGreater(len(mine), 0)


class TheSeam(unittest.TestCase):
    def test_the_camera_truncation_is_the_dominant_term(self):
        self.assertTrue(VA.the_camera_truncation_is_the_dominant_term())

    def test_the_on_edge_class_is_made_by_the_truncation(self):
        """The top-left convention is the last step in a chain, not the cause."""
        self.assertTrue(VA.the_on_edge_class_is_made_by_the_truncation())

    def test_that_explanation_is_a_set_and_not_a_count(self):
        mine = {(r[0], r[1], r[2]) for r in VA.census()
                if r[3] == "cover" and r[5] == "on_edge"}
        self.assertEqual(mine, VA.population("on_surface"))

    def test_the_places_partition_each_population(self):
        for w in ("cover", "winner"):
            for p in VA.PRECISIONS:
                d = VA.distribution(w, p)
                self.assertEqual(sum(d.values()),
                                 sum(1 for r in VA.census() if r[3] == w))


class TheQuarantine(unittest.TestCase):
    def test_the_ties_and_phantoms_are_quarantined(self):
        self.assertTrue(VA.the_ties_and_phantoms_are_quarantined())

    def test_nothing_is_altered(self):
        self.assertTrue(VA.nothing_is_altered())


class ThePrediction(unittest.TestCase):
    def test_every_prediction_has_a_verdict(self):
        self.assertTrue(VA.every_prediction_has_a_verdict())

    def test_the_record_carries_hits_and_misses(self):
        self.assertTrue(VA.the_record_carries_hits_and_misses())

    def test_the_prediction_is_data(self):
        for pid, text in VA.PREDICTION:
            self.assertIsInstance(pid, str)
            self.assertGreater(len(text), 40)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VA.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VA.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VA.a_tampered_row_refuses())

    def test_a_place_row_outside_the_vocabulary_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.parse("# world x\nplace cover double inside 1\n")

    def test_a_verdict_row_naming_no_prediction_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.parse("# world x\nverdict Q9 HIT nothing\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VA.SCENES:
            self.assertEqual(VA.scene_result(name), VA.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.scene_case("places2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VA.VoxsampleError):
            VA.golden("nope")


if __name__ == "__main__":
    unittest.main()
