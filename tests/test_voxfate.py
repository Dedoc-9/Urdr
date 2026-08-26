# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfate (URDRVXS1) — condition the population first, then ask what broke it."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxfate as VS                                         # noqa: E402
import voxmicro as VM                                        # noqa: E402
import voxtie as VT                                          # noqa: E402


class TheInstrument(unittest.TestCase):
    def test_the_third_transcription_is_bound_to_the_ladder(self):
        """A third copy of the loop must measure the SAME renderer, not a fourth one."""
        self.assertTrue(VS.the_instrument_matches_the_ladder())

    def test_the_fate_vocabulary_is_inherited_not_copied(self):
        self.assertIs(VS.FATES, VM.REJECTS)


class ThePopulation(unittest.TestCase):
    def test_the_population_is_exactly_the_conditioned_class(self):
        self.assertTrue(VS.the_population_is_exactly_the_conditioned_class())

    def test_the_population_is_a_strict_subset_of_the_residual(self):
        self.assertLess(len(VS.conditioned()), len(VT.census()))

    def test_the_conditioned_class_is_declared(self):
        self.assertIn(VS.CONDITION, VT.CLASSES)

    def test_every_conditioned_pixel_gets_exactly_one_fate(self):
        rows = VS.fates()
        self.assertEqual(len(rows), len(VS.conditioned()))
        self.assertEqual(sum(VS.distribution().values()), len(rows))


class TheAnswer(unittest.TestCase):
    def test_the_answer_does_not_split(self):
        """A spread would have to be preserved, not resolved into one invented mechanism."""
        self.assertTrue(VS.the_answer_does_not_split())

    def test_the_defect_is_coverage_not_depth(self):
        self.assertTrue(VS.the_defect_is_coverage_not_depth())

    def test_the_impossible_pixels_agree_with_the_whole(self):
        """The subset that needs no oracle to be called wrong must say the same thing."""
        d = VS.impossible_distribution()
        self.assertGreater(sum(d.values()), 0)
        self.assertEqual(max(d, key=lambda k: d[k]), VS.dominant())

    def test_the_contamination_is_demonstrated_not_argued(self):
        self.assertTrue(VS.the_contamination_is_demonstrated())

    def test_the_sampling_branch_absorbs_the_coverage_class(self):
        off, on = VS.distribution(False), VS.distribution(True)
        self.assertGreater(on["sampling_shift"], 0)
        self.assertEqual(off["sampling_shift"], 0)


class TheCounterexample(unittest.TestCase):
    def test_the_counterexample_is_minimal_and_real(self):
        self.assertTrue(VS.the_counterexample_is_minimal_and_real())

    def test_the_oracle_face_reached_the_pixel_loop(self):
        c = VS.minimal_counterexample()
        self.assertEqual(c["oracle_face_stage"], "rasterised")
        self.assertFalse(c["covers_this_pixel"])


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VS.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VS.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VS.a_tampered_row_refuses())

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VS.VoxfateError):
            VS.parse("# world x\nrumour 1 2 3\n")

    def test_a_fate_outside_the_vocabulary_refuses(self):
        with self.assertRaises(VS.VoxfateError):
            VS.parse("# world x\nfate not_a_fate 1 1 1\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VS.VoxfateError):
            VS.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VS.SCENES:
            self.assertEqual(VS.scene_result(name), VS.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VS.VoxfateError):
            VS.scene_case("fates")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VS.VoxfateError):
            VS.golden("nope")


if __name__ == "__main__":
    unittest.main()
