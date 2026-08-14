# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pixelcost (URDRPXC1) — the resolution decision, derived from committed records."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import pixelcost as PX                                       # noqa: E402


class TheRecords(unittest.TestCase):
    def test_both_records_hash_to_their_pins(self):
        self.assertTrue(PX.load(0))
        self.assertTrue(PX.load(1))

    def test_the_digests_are_distinct(self):
        import hashlib
        d0 = hashlib.sha256(PX.load(0).encode()).hexdigest()
        d1 = hashlib.sha256(PX.load(1).encode()).hexdigest()
        self.assertNotEqual(d0, d1)

    def test_a_flipped_byte_refuses(self):
        raw = PX.load(0)
        bad = raw[:200] + ("0" if raw[200] != "0" else "1") + raw[201:]
        with self.assertRaises(PX.PixelcostError):
            PX.load(0, text=bad)

    def test_a_duplicate_record_refuses(self):
        """THE WILD-CAUGHT LAW. The operator's Copy-Item produced two identical files and only
        the transcript showed why; an analyzer that accepted them would trust a between-run
        spread of exactly zero (URDRRPT1)."""
        self.assertTrue(PX.a_duplicate_record_refuses())

    def test_a_condition_less_record_refuses(self):
        self.assertTrue(PX.a_condition_less_record_refuses())

    def test_an_earlier_probe_version_refuses(self):
        self.assertTrue(PX.a_v01_record_refuses())

    def test_a_chainless_record_refuses(self):
        raw = PX.load(0)
        head = raw.split("click chains")[0]
        with self.assertRaises(PX.PixelcostError):
            PX.parse(head)

    def test_a_malformed_cell_row_refuses(self):
        with self.assertRaises(PX.PixelcostError):
            PX.parse(PX.load(0) + "cell 1x1 pass 0\n")

    def test_a_thin_row_is_excluded_by_its_own_n(self):
        """The live case: run 2's 720p pass 3 ran TWO frames before ESC. In the record, out of
        the aggregation, counted — never silently dropped (L44)."""
        parsed = PX.admit()
        self.assertTrue(PX.a_thin_row_is_excluded_by_its_own_n(parsed[1]))


class TheVerdicts(unittest.TestCase):
    def setUp(self):
        self.parsed = PX.admit()
        self.summaries = [PX.cell_summary(p) for p in self.parsed]

    def test_the_form_is_undetermined_and_says_so_precisely(self):
        """Both runs' residuals sit below the chord (the convex direction) and INSIDE the
        conservative ruler: the verdict is UNDETERMINED with sign-consistency reported, which is
        the honest reading — not affine-confirmed, not convex-confirmed."""
        f = PX.form_verdict(self.summaries)
        self.assertEqual(f["final"], "UNDETERMINED")
        self.assertTrue(f["sign_consistent"])
        for r in f["per_run"]:
            self.assertLess(r["residual"], 0)
            self.assertLess(abs(r["residual"]), r["ruler"])

    def test_the_budget_fits_all_three_measured_cells(self):
        """The demo arc's first evidence-derived resolution decision: every measured cell fits
        the 120 Hz slot, 1280x720 by CEILING on the worst run."""
        b = PX.budget_verdicts(self.summaries, self.parsed[0]["hz"])
        for name, v in b.items():
            self.assertEqual(v["budget"], "FITS", name)
        self.assertLess(b["1280x720"]["hi_total"], b["1280x720"]["slot"])

    def test_extrapolation_is_structurally_impossible(self):
        """1080p is the question everyone wants answered and it has NO verdict, because it was
        not run — with CONVEX unrefuted, a linear guess would be inflation."""
        self.assertTrue(PX.extrapolation_is_structurally_impossible(
            self.summaries, self.parsed[0]["hz"]))

    def test_fewer_than_three_cells_cannot_bend(self):
        two = [{k: v for k, v in s.items() if k != "960x540"} for s in self.summaries]
        with self.assertRaises(PX.PixelcostError):
            PX.form_verdict(two)

    def test_the_warmup_observation_is_reported_not_excluded(self):
        for p in self.parsed:
            obs = PX.warmup_observation(p)
            self.assertEqual(len(obs), 3)
        # med-of-meds is lower-middle and therefore robust to the one elevated pass:
        s = PX.cell_summary(self.parsed[0])
        self.assertLess(s["640x360"]["med"], 1500000)


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in PX.SCENES:
            with self.subTest(name):
                self.assertEqual(PX.scene_result(name), PX.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(PX.PixelcostError):
            PX.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main(verbosity=2)
