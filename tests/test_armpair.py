# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""armpair (URDRARM1) — the retired reference's equality, kept as committed records."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import armpair as A                                          # noqa: E402


class TheRecords(unittest.TestCase):
    def test_every_record_hashes_to_its_pin(self):
        for key in A.RECORDS:
            self.assertTrue(A.record(key))

    def test_there_are_sixteen_of_them_and_they_are_distinct(self):
        self.assertEqual(len(A.RECORDS), 16)
        self.assertEqual(len({A.record(k)["sha256"] for k in A.RECORDS}), 16)

    def test_a_tampered_record_refuses(self):
        self.assertTrue(A.a_tampered_record_refuses())

    def test_a_headerless_record_refuses(self):
        self.assertTrue(A.a_headerless_record_refuses())

    def test_a_record_without_a_workload_refuses(self):
        self.assertTrue(A.a_record_without_a_workload_refuses())

    def test_one_workload_ran_in_every_record(self):
        self.assertTrue(A.one_workload_ran_in_every_record())

    def test_every_record_declares_the_same_conditions(self):
        self.assertTrue(A.every_record_declares_the_same_conditions())


class TheEquality(unittest.TestCase):
    def test_every_arm_pair_is_chain_identical(self):
        self.assertTrue(A.every_arm_pair_is_chain_identical())

    def test_each_pair_carries_forty_three_checkpoints(self):
        for reach, castle in A.CELLS:
            for run in A.RUNS:
                a, b = A.arm_pair(reach, castle, run)
                self.assertEqual(len(a["chain"]), 43)
                self.assertEqual(len(b["chain"]), 43)

    def test_the_equality_is_not_vacuous(self):
        self.assertTrue(A.the_equality_is_not_vacuous())

    def test_one_flipped_digest_reddens_it(self):
        self.assertTrue(A.a_flipped_digest_reddens())

    def test_a_pair_crossed_between_cells_reddens_it(self):
        self.assertTrue(A.a_crossed_pair_reddens())


class TheSeparation(unittest.TestCase):
    def test_the_arms_separate_where_the_castle_is_on(self):
        self.assertTrue(A.the_arms_separate_where_the_castle_is_on())

    def test_the_control_is_neither_empty_nor_directional(self):
        self.assertTrue(A.the_control_is_not_silently_empty())
        self.assertTrue(A.the_control_has_no_direction())

    def test_the_control_band_is_smaller_than_every_castle_on_reading(self):
        band = A.control_band()
        for reach in ("r60", "r120"):
            for seg in A.TEST_SEGMENTS:
                self.assertGreater(A.separation(reach, seg), band)

    def test_a_segment_outside_the_frozen_set_is_not_consulted(self):
        self.assertNotIn(0, A.TEST_SEGMENTS)
        self.assertNotIn(21, A.TEST_SEGMENTS)


class TheRetirement(unittest.TestCase):
    def test_the_retired_paths_are_gone_from_the_source(self):
        self.assertTrue(A.the_retired_paths_are_gone_from_the_source())
        self.assertEqual(len(A.RETIRED_CFGS), 2)

    def test_a_restored_reference_reddens(self):
        self.assertTrue(A.a_restored_reference_reddens())

    def test_the_first_generation_cannot_name_its_arms(self):
        self.assertTrue(A.the_first_generation_cannot_name_its_arms())


class TheSecondGeneration(unittest.TestCase):
    def test_there_are_sixteen_of_them_and_they_are_distinct(self):
        self.assertEqual(len(A.RECORDS2), 16)
        self.assertEqual(len({A.record2(k)["sha256"] for k in A.RECORDS2}), 16)

    def test_the_arms_are_derived_from_the_bytes(self):
        self.assertTrue(A.the_second_generation_names_its_own_arms())

    def test_a_mislabelled_record_reddens(self):
        self.assertTrue(A.a_mislabelled_second_generation_record_reddens())

    def test_every_pair_is_chain_identical(self):
        self.assertTrue(A.every_second_generation_pair_is_chain_identical())

    def test_one_edited_digest_reddens_it(self):
        self.assertTrue(A.a_second_generation_digest_edit_reddens())

    def test_it_is_not_vacuous(self):
        self.assertTrue(A.the_second_generation_is_not_vacuous())

    def test_the_arms_separate_and_the_control_does_not(self):
        self.assertTrue(A.the_second_arms_separate_where_the_castle_is_on())
        self.assertTrue(A.the_second_control_has_no_direction())
        self.assertGreater(A.control_band2(), 0.0)

    def test_both_generations_ran_one_workload(self):
        self.assertTrue(A.the_two_generations_share_one_workload())

    def test_the_session_drift_is_derived_and_bounded(self):
        lo, hi = A.session_drift()
        self.assertLess(lo, 0.0)
        self.assertGreater(hi, 0.0)
        self.assertLess(max(abs(lo), abs(hi)), 10.0)


class TheGoldens(unittest.TestCase):
    def test_both_scenes_reproduce_their_goldens(self):
        for name in ("equality", "separation", "equality2", "separation2"):
            self.assertEqual(A.scene_result(name), A.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(A.ArmpairError):
            A.scene_case("nope")


if __name__ == "__main__":
    unittest.main()
