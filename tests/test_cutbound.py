# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cutbound (URDRCBD1) — a refusal is a proof, and the production law was throwing it away."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import cohort as CO                                            # noqa: E402
import cutbound as CB                                          # noqa: E402
import shadowcut as SC                                         # noqa: E402


class TheRefusalIsAProof(unittest.TestCase):
    def test_the_refusal_is_a_proven_lower_bound(self):
        self.assertTrue(CB.the_refusal_is_a_proven_lower_bound())

    def test_every_interval_contains_its_witness(self):
        for c in CB.CASES:
            lo, hi = CB.interval(c)
            with self.subTest(case=c):
                self.assertLessEqual(lo, hi)
                self.assertEqual(hi, SC.shortest_cut(CO.spanning_wall(*c), c[0])[0])

    def test_a_refused_wall_has_the_cap_plus_one_as_its_floor(self):
        for c in CB.CASES:
            if CB.provenance(c) == "exhaustion":
                continue
            with self.subTest(case=c):
                self.assertEqual(CB.interval(c)[0], CO.CUT_SEARCH_MAX + 1)

    def test_the_exhaustion_and_the_witness_meet_one_wall_past_the_cap(self):
        self.assertTrue(CB.the_exhaustion_and_the_witness_meet_one_wall_past_the_cap())
        self.assertEqual(CB.interval((6, 4)), (4, 4))
        self.assertEqual(CB.provenance((6, 4)), "meeting")

    def test_the_theorem_is_only_needed_past_the_meeting_point(self):
        self.assertTrue(CB.the_theorem_is_only_needed_past_the_meeting_point())
        self.assertEqual(CB.provenance((6, 5)), "bracketed")
        self.assertEqual(CB.interval((6, 5)), (4, 5))

    def test_every_provenance_class_is_populated(self):
        self.assertTrue(CB.every_provenance_class_is_populated())

    def test_the_theorem_is_declared_as_an_argument(self):
        self.assertGreater(len(CB.THEOREM), 80)


class TheCorrections(unittest.TestCase):
    def test_the_charge_no_longer_reads_a_refusal_as_free(self):
        self.assertTrue(CB.the_charge_no_longer_reads_a_refusal_as_free())
        self.assertEqual(CO.charge_for_gap(None), 3)

    def test_the_undercharge_had_a_range_and_it_was_flattering(self):
        self.assertTrue(CB.the_undercharge_had_a_range_and_it_was_flattering())

    def test_the_old_branch_certified_a_wall_the_floor_refuses(self):
        self.assertTrue(CB.the_old_branch_certified_a_wall_the_floor_refuses())

    def test_the_floor_is_applied_to_the_bound_and_not_skipped(self):
        self.assertTrue(CB.the_floor_is_applied_to_the_bound_and_not_skipped())

    def test_both_corrected_consumers_carry_a_reason(self):
        self.assertEqual(set(CB.CORRECTED), {"charge_for_gap", "certifiable"})
        for name, why in CB.CORRECTED.items():
            with self.subTest(consumer=name):
                self.assertGreater(len(why), 60)

    def test_a_thick_wall_is_still_certifiable(self):
        """A wall comfortably above the floor still certifies. Checked on a wall the enumeration
        DECIDES: `certifiable` calls `min_cut` itself and cannot be handed a pinned answer, so
        asking it about a refused wall would spend 46 seconds every run to learn what the cheap
        wall already shows. The refused branch is covered separately and cheaply by
        `the_old_branch_certified_a_wall_the_floor_refuses`, which reproduces it with the cap
        lowered rather than with a bigger wall."""
        self.assertTrue(CO.certifiable(CO.spanning_wall(5, 3), 5))
        self.assertGreaterEqual(CO.min_cut(CO.spanning_wall(5, 3), 5), CO.WALL_MIN_K)

    def test_a_thin_wall_is_still_refused(self):
        with self.assertRaises(CO.TooThin):
            CO.certifiable(CO.spanning_wall(4, 1), 4)


class TheRepairMovesNothing(unittest.TestCase):
    def test_the_correction_changes_no_pinned_figure(self):
        self.assertTrue(CB.the_correction_changes_no_pinned_figure())

    def test_the_gap_table_is_unmoved(self):
        self.assertEqual(CO.gap_table(), ((3, 1, 1), (4, 1, 1), (4, 2, 2), (5, 1, 1), (5, 2, 2)))

    def test_the_charge_table_is_unmoved(self):
        self.assertEqual(CO.charge_table(),
                         ((0, 12), (1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)))

    def test_the_bound_is_still_inactive_on_the_pinned_corpus(self):
        self.assertTrue(SC.the_bound_is_inactive_on_the_pinned_corpus())


class TheVerdictIsRetain(unittest.TestCase):
    def test_no_new_algorithm_enters_the_production_path(self):
        self.assertTrue(CB.no_new_algorithm_enters_the_production_path())

    def test_the_subject_still_enumerates(self):
        self.assertTrue(CB.the_subject_still_enumerates())
        self.assertEqual(CO.CUT_SEARCH_MAX, 3)

    def test_no_wall_clock_enters(self):
        self.assertTrue(CB.no_wall_clock_enters_this_rung())

    def test_the_subject_is_asked_once(self):
        """Three walls come from `shadowcut`'s swept corpus rather than a second enumeration."""
        shared = [c for c in CB.CASES if c in SC.CASES]
        self.assertEqual(len(shared), 3)
        for c in shared:
            with self.subTest(case=c):
                b = SC.answer(c, "bounded")
                lo, hi = CB.interval(c)
                self.assertEqual(lo, b if b is not None else CO.CUT_SEARCH_MAX + 1)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(CB.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(CB.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(CB.a_tampered_row_refuses())

    def test_the_generated_record_is_the_committed_one(self):
        with open(os.path.join(_ROOT, CB.RECORD), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), CB.generate())

    def test_rows_of_unknown_kinds_refuse(self):
        head = "# world x\n"
        for bad in ("bracket 9 9 1 1 exhaustion", "bracket 5 2 2 2 wishful",
                    "corrected wishful", "rumour 1"):
            with self.subTest(row=bad):
                with self.assertRaises(CB.CutboundError):
                    CB.parse(head + bad + "\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(CB.CutboundError):
            CB.parse("corrected certifiable\n")

    def test_a_record_with_no_rows_refuses(self):
        with self.assertRaises(CB.CutboundError):
            CB.parse("# world x\n")

    def test_an_unknown_case_refuses(self):
        for call in (CB.bracket, CB.interval, CB.provenance):
            with self.assertRaises(CB.CutboundError):
                call((9, 9))

    def test_the_scenes_match_their_goldens(self):
        for n in CB.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(CB.scene_result(n), CB.golden(n))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(CB.CutboundError):
            CB.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(CB.CutboundError):
            CB.golden("wishful")


if __name__ == "__main__":
    unittest.main(verbosity=2)
