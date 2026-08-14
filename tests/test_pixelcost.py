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
    def test_all_records_hash_to_their_pins(self):
        for i in range(len(PX.RECORDS)):
            self.assertTrue(PX.load(i))

    def test_the_digests_are_pairwise_distinct(self):
        import hashlib
        digs = [hashlib.sha256(PX.load(i).encode()).hexdigest()
                for i in range(len(PX.RECORDS))]
        self.assertEqual(len(set(digs)), len(digs))

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

    def test_a_chainless_v03_record_admits_but_supplies_no_present_evidence(self):
        parsed = PX.admit()
        self.assertTrue(PX.a_chainless_record_supplies_no_present_evidence(parsed[2]))
        self.assertTrue(PX.a_chainless_record_supplies_no_present_evidence(parsed[3]))

    def test_a_v05_record_supplies_present_bands_with_no_clicks(self):
        """v1.2: the cost band rides in every row; the click ritual is gone."""
        parsed = PX.admit()
        for q in (parsed[4], parsed[5]):
            self.assertEqual(len(q["chains"]), 0)
            s = PX.cell_summary(q)
            for name, v in s.items():
                self.assertIsNotNone(v["present_med"], name)

    def test_the_v04_record_is_refused_by_version_dispatch(self):
        """Preserved for the latency rung; its chain-presents may not re-enter the cost question
        the way v1.0 mixed them."""
        self.assertTrue(PX.a_v04_record_refuses())

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
        """All four records' residuals sit below the chord (the convex direction) and INSIDE the
        conservative ruler — and the four-cell records' rulers are dominated by 1080p's thermal
        spread, itself a finding."""
        f = PX.form_verdict(self.summaries)
        self.assertEqual(f["final"], "UNDETERMINED")
        self.assertTrue(f["sign_consistent"])
        self.assertEqual(len(f["per_run"]), 6)
        for r in f["per_run"]:
            self.assertLess(r["residual"], 0)
            self.assertLess(abs(r["residual"]), r["ruler"])
        self.assertGreater(f["per_run"][2]["ruler"], 3_000_000)   # the 1080p spread, visible

    def test_the_budget_at_120Hz_including_the_lawful_demotion(self):
        """v1.0 read 720p FITS-by-ceiling from two runs; run 3's own pass-0 ceiling crossed the
        slot, so the worst-record verdict is now MARGINAL — a verdict more evidence may lawfully
        demote (a claim is not a ratchet). 1080p EXCEEDS on raster alone: the one-sided verdict a
        missing present band still permits."""
        b = PX.budget_verdicts(self.summaries, self.parsed[0]["hz"])
        self.assertEqual(b["640x360"]["budget"], "FITS")
        self.assertEqual(b["960x540"]["budget"], "MARGINAL")
        self.assertEqual(b["1280x720"]["budget"], "MARGINAL")
        self.assertGreater(b["1280x720"]["hi_total"], b["1280x720"]["slot"])
        self.assertLessEqual(b["1280x720"]["med_total"], b["1280x720"]["slot"])
        self.assertEqual(b["1920x1080"]["budget"], "EXCEEDS")
        self.assertTrue(b["1920x1080"]["present_measured"])

    def test_the_60Hz_table_is_complete_and_1080p_closes_MARGINAL(self):
        """THE LAST UNDETERMINED CLOSES: 1080p60's median fits with ~3.2 ms of room and its
        worst-record ceiling does not — a median-viable, ceiling-risky operating point, said
        exactly that way. Nothing in either table reads UNDETERMINED."""
        b = PX.budget_verdicts(self.summaries, 60)
        for name in ("640x360", "960x540", "1280x720"):
            self.assertEqual(b[name]["budget"], "FITS", name)
        self.assertEqual(b["1920x1080"]["budget"], "MARGINAL")
        self.assertTrue(b["1920x1080"]["present_measured"])
        for hz in (120, 60):
            for v in PX.budget_verdicts(self.summaries, hz).values():
                self.assertNotEqual(v["budget"], "UNDETERMINED")

    def test_a_present_less_cell_cannot_read_FITS(self):
        self.assertTrue(PX.a_cell_without_present_cannot_read_FITS(
            self.summaries, self.parsed[0]["hz"]))

    def test_extrapolation_is_structurally_impossible(self):
        """The law moved to the next unrun rung: 1080p is measured now, 1440p is not, and 1440p
        has no verdict."""
        self.assertTrue(PX.extrapolation_is_structurally_impossible_check(
            self.summaries, self.parsed[0]["hz"]))

    def test_fewer_than_three_cells_cannot_bend(self):
        two = [{k: v for k, v in s.items() if k in ("640x360", "1280x720")}
               for s in self.summaries[:1]]
        with self.assertRaises(PX.PixelcostError):
            PX.form_verdict(two)

    def test_the_warmup_observation_is_reported_not_excluded(self):
        for p in self.parsed:
            obs = PX.warmup_observation(p)
            self.assertEqual(len(obs), len({r["cell"] for r in p["rows"]}))
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
