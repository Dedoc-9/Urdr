# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxconv (URDRVXN1) — the population derived twice, because most of it was the convention."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxconv as VN                                         # noqa: E402
import voxfate as VS                                         # noqa: E402
import voxfill as VL                                         # noqa: E402
import voxtie as VT                                          # noqa: E402


class TheParameterisation(unittest.TestCase):
    def test_both_offsets_are_the_same_half_pixel(self):
        self.assertTrue(VN.the_two_offsets_are_the_same_half_pixel())

    def test_an_unknown_convention_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.offsets("gaussian")

    def test_the_vocabularies_are_inherited_not_copied(self):
        self.assertIs(VN.CLASSES, VT.CLASSES)
        self.assertIs(VN.FATES, VS.FATES)
        self.assertIs(VN.REJECTIONS, VL.REJECTIONS)


class TheInstrument(unittest.TestCase):
    def test_the_fifth_transcription_is_bound_in_both_directions(self):
        """At zero offset it must equal voxfate's; at either offset, voxfill's winner."""
        self.assertTrue(VN.the_instrument_is_bound_in_both_directions())


class TheBinding(unittest.TestCase):
    def test_the_corner_arm_reproduces_the_committed_rungs(self):
        """A re-derivation that cannot reproduce what it re-derives is measuring something else."""
        self.assertTrue(VN.the_corner_arm_reproduces_the_committed_rungs())

    def test_the_corner_census_is_voxties_census(self):
        self.assertEqual(VN.summary("corner")[0], len(VT.census()))

    def test_the_corner_fates_are_voxfates_fates(self):
        self.assertEqual(VN.summary("corner")[2], VS.distribution(False))

    def test_the_corner_rejections_are_voxfills_rejections(self):
        live = VL.rejection_distribution()
        mine = VN.summary("corner")[3]
        for c in VN.REJECTIONS:
            self.assertEqual(mine[c], live[c])


class TheResult(unittest.TestCase):
    def test_the_population_was_mostly_the_convention(self):
        self.assertTrue(VN.the_population_was_mostly_the_convention())

    def test_the_degeneracy_was_the_integer_sample(self):
        """The class that excused 561 disagreements was where the rays were aimed."""
        self.assertTrue(VN.the_degeneracy_was_the_integer_sample())

    def test_the_coverage_diagnosis_survives(self):
        """The population collapses thirteenfold and the coverage share does not move."""
        self.assertTrue(VN.the_coverage_diagnosis_survives())

    def test_the_ownership_class_vanishes(self):
        """The top-left rule exonerated a second time, by a route voxfill did not take."""
        self.assertTrue(VN.the_ownership_class_vanishes())

    def test_the_residue_is_pure_quantisation(self):
        self.assertTrue(VN.the_residue_is_pure_quantisation())

    def test_the_oracle_is_still_a_function(self):
        self.assertTrue(VN.the_oracle_is_still_a_function())

    def test_the_classes_partition_each_census(self):
        for c in VN.CONVENTIONS:
            n, cls, _f, _r, _i = VN.summary(c)
            self.assertEqual(sum(cls.values()), n)

    def test_nothing_is_adopted(self):
        self.assertTrue(VN.nothing_is_adopted())


class TheRefusal(unittest.TestCase):
    def test_the_impossible_population_is_too_small_to_read(self):
        """An anti-inflation law: four pixels is not a distribution, and the refusal is stated."""
        self.assertTrue(VN.the_impossible_population_is_too_small_to_read())

    def test_the_refusal_is_about_this_population_and_not_a_constant(self):
        self.assertGreater(VN.summary("corner")[4], 10)
        self.assertLess(VN.summary("centre")[4], 10)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VN.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VN.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VN.a_tampered_row_refuses())

    def test_a_row_naming_no_convention_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.parse("# world x\ncount gaussian 1 2\n")

    def test_a_class_row_in_no_declared_class_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.parse("# world x\nclass corner elsewhere 1\n")

    def test_a_fate_row_in_no_declared_fate_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.parse("# world x\nfate corner nowhere 1\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.parse("# world x\nrumour corner 1 2\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.parse("digest deadbeef\n")


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VN.SCENES:
            self.assertEqual(VN.scene_result(name), VN.golden(name))

    def test_the_population_is_pinned_not_the_counts(self):
        """Two different sets of 104 pixels would tally the same and digest differently."""
        self.assertEqual(VN.scene_result("population"), VN.golden("population"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.scene_case("census2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VN.VoxconvError):
            VN.golden("nope")


if __name__ == "__main__":
    unittest.main()
