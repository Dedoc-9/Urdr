# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cutpin (URDRCPN1) — the expensive half of a proof is pinned, and what is trusted is one integer."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import cohort as CO                                            # noqa: E402
import cutpin as CP                                            # noqa: E402


class TheProvenance(unittest.TestCase):
    def test_the_pin_is_current(self):
        self.assertTrue(CP.the_pin_is_current())

    def test_the_provenance_binds_live_source(self):
        """Every bound source is a real attribute of the subject, so the digest cannot bind nothing."""
        for name in CP.BOUND_SOURCES:
            with self.subTest(source=name):
                self.assertTrue(hasattr(CO, name))

    def test_a_changed_source_moves_the_digest(self):
        """THE PLANT FOR THE GUARANTEE: perturb what the digest binds and it must move."""
        before = CP.provenance_digest()
        saved = CO.CUT_SEARCH_MAX
        try:
            CO.CUT_SEARCH_MAX = saved + 1
            self.assertNotEqual(CP.provenance_digest(), before)
        finally:
            CO.CUT_SEARCH_MAX = saved
        self.assertEqual(CP.provenance_digest(), before)

    def test_a_stale_provenance_refuses(self):
        self.assertTrue(CP.a_stale_provenance_refuses())

    def test_a_stale_pin_refuses_to_answer(self):
        """`refusal` must REFUSE rather than hand back a cached answer when the pin is stale."""
        saved = CO.CUT_SEARCH_MAX
        try:
            CO.CUT_SEARCH_MAX = saved + 1
            with self.assertRaises(CP.CutpinError):
                CP.refusal(CP.EXPENSIVE[0])
        finally:
            CO.CUT_SEARCH_MAX = saved
        self.assertIsNone(CP.refusal(CP.EXPENSIVE[0]))


class TheTrustedIncrement(unittest.TestCase):
    def test_the_trusted_increment_is_one_integer(self):
        self.assertTrue(CP.the_trusted_increment_is_one_integer())
        self.assertEqual(CP.pinned_sizes(), (3,))
        self.assertEqual(CP.REPROVED, (1, 2))

    def test_the_affordable_exhaustion_is_reproved(self):
        self.assertTrue(CP.the_affordable_exhaustion_is_reproved())

    def test_the_reproved_sizes_are_strictly_below_the_pinned_ones(self):
        self.assertLess(max(CP.REPROVED), min(CP.pinned_sizes()))
        self.assertEqual(max(CP.pinned_sizes()), CO.CUT_SEARCH_MAX)

    def test_the_pin_records_only_refusals(self):
        self.assertTrue(CP.the_pin_records_only_refusals())

    def test_every_pinned_wall_is_one_the_subject_refuses(self):
        for case in CP.EXPENSIVE:
            with self.subTest(case=case):
                self.assertIsNone(CP.answer_for(case))


class TheTranscription(unittest.TestCase):
    def test_the_transcription_agrees_with_the_subject(self):
        self.assertTrue(CP.the_transcribed_exhaustion_agrees_with_the_subject())

    def test_the_transcription_finds_a_cut_that_exists(self):
        """Non-vacuity: the walk must be able to say NO as well as yes."""
        n = 5
        holed = CO.spanning_wall(n, 2) - frozenset({(1, 2, 2)})
        self.assertFalse(CP.no_cut_of_size(holed, n, 1))
        self.assertEqual(CP.reconstruct(holed, n, CO.CUT_SEARCH_MAX), 1)

    def test_a_breached_wall_reconstructs_as_zero(self):
        n = 4
        partial = frozenset((1, y, z) for y in range(n - 1) for z in range(n))
        self.assertEqual(CP.reconstruct(partial, n, CO.CUT_SEARCH_MAX), 0)


class TheConsumers(unittest.TestCase):
    def test_an_unpinned_wall_goes_to_the_subject(self):
        case = (5, 2)
        self.assertNotIn(case, CP.EXPENSIVE)
        self.assertEqual(CP.answer_for(case), CO.min_cut(CO.spanning_wall(*case), case[0]))

    def test_an_unpinned_wall_refuses_from_refusal(self):
        with self.assertRaises(CP.CutpinError):
            CP.refusal((5, 2))

    def test_the_consumers_see_the_same_answers(self):
        """The pin changed WHERE the answer comes from, not WHAT it is."""
        import shadowcut as SC
        for case in CP.EXPENSIVE:
            if case in SC.CASES:
                with self.subTest(case=case):
                    self.assertEqual(SC.answer(case, "bounded"), CP.answer_for(case))


class TheRecord(unittest.TestCase):
    def test_a_tampered_record_refuses(self):
        self.assertTrue(CP.a_tampered_record_refuses())

    def test_rows_of_unknown_kinds_refuse(self):
        head = "# provenance x\n"
        for bad in ("refused 9 9 3", "refused 6 4 99", "rumour 1"):
            with self.subTest(row=bad):
                with self.assertRaises(CP.CutpinError):
                    CP.parse(head + bad + "\n")

    def test_a_record_naming_no_provenance_refuses(self):
        with self.assertRaises(CP.CutpinError):
            CP.parse("refused 6 4 3\n")

    def test_a_record_with_no_rows_refuses(self):
        with self.assertRaises(CP.CutpinError):
            CP.parse("# provenance x\n")

    def test_an_unknown_pinned_wall_refuses(self):
        with self.assertRaises(CP.CutpinError):
            CP.refusal((9, 9))

    def test_the_scenes_match_their_goldens(self):
        for n in CP.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(CP.scene_result(n), CP.golden(n))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(CP.CutpinError):
            CP.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(CP.CutpinError):
            CP.golden("wishful")


if __name__ == "__main__":
    unittest.main(verbosity=2)
