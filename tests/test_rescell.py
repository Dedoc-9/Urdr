# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rescell (URDRRSC1) — the resolution ladder as gate-read evidence."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import rescell as R                                          # noqa: E402


class TheRecords(unittest.TestCase):
    def test_both_records_hash_to_their_pins(self):
        for which in R.RECORDS:
            self.assertTrue(R.load_log(which))

    def test_a_flipped_byte_refuses(self):
        self.assertTrue(R.a_flipped_byte_refuses())

    def test_a_duplicate_record_refuses(self):
        self.assertTrue(R.a_duplicate_record_refuses())

    def test_an_anonymous_record_refuses(self):
        self.assertTrue(R.an_anonymous_record_refuses())

    def test_an_undeclared_cell_refuses(self):
        self.assertTrue(R.an_undeclared_cell_refuses())


class TheLadder(unittest.TestCase):
    def test_the_admitted_ladder_matches_the_golden(self):
        self.assertEqual(R.scene_result("ladder"), R.golden("ladder"))

    def test_the_120hz_verdicts_agree_and_read_fits_fits_exceeds(self):
        r1, r2 = R.admit()
        self.assertEqual(R.ladder_120(r1, r2),
                         {"640x360": "FITS", "1280x720": "FITS", "1920x1080": "EXCEEDS"})

    def test_1080p_medians_break_the_slot_in_both_runs(self):
        r1, r2 = R.admit()
        for r in (r1, r2):
            self.assertTrue(any(row["med"] > R.SLOT_120_NS
                                for row in r["cells"]["1920x1080"]))

    def test_the_late_counters_corroborate_the_classification(self):
        r1, r2 = R.admit()
        self.assertTrue(R.late_corroboration(r1, r2))

    def test_a_flipping_verdict_refuses_to_speak(self):
        self.assertTrue(R.a_flipping_verdict_refuses_to_speak())


class TheSixtyHertzPair(unittest.TestCase):
    def test_a_one_run_fits_is_caught_by_the_pair(self):
        self.assertTrue(R.a_one_run_fits_is_caught_by_the_pair())

    def test_the_conservative_verdict_is_marginal_not_fits(self):
        r1, r2 = R.admit()
        self.assertEqual(R.ladder_60(r1, r2)["1920x1080"]["verdict"], "MARGINAL")

    def test_the_smaller_cells_fit_60hz_in_both_runs(self):
        r1, r2 = R.admit()
        l60 = R.ladder_60(r1, r2)
        for c in ("640x360", "1280x720"):
            self.assertEqual(l60[c]["verdict"], "FITS")


class TheConvexityCaution(unittest.TestCase):
    def test_the_affine_prediction_undershoots_in_both_runs(self):
        r1, r2 = R.admit()
        holds, k1, k2 = R.affine_undershoots(r1, r2)
        self.assertTrue(holds)
        self.assertGreater(k1, 1000)
        self.assertGreater(k2, 1000)


if __name__ == "__main__":
    unittest.main()
